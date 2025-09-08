from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'tu_clave_secreta_aqui'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///nail_salon.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Modelos de la base de datos
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Service(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Float, nullable=False)
    duration = db.Column(db.Integer, nullable=False)  # duración en minutos
    image_url = db.Column(db.String(200))

class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'), nullable=False)
    appointment_date = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, confirmed, completed, cancelled
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref=db.backref('appointments', lazy=True))
    service = db.relationship('Service', backref=db.backref('appointments', lazy=True))

# Rutas principales
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            session['user_id'] = user.id
            session['username'] = user.username
            session['is_admin'] = user.is_admin
            flash('¡Inicio de sesión exitoso!', 'success')
            return redirect(url_for('catalog'))
        else:
            flash('Usuario o contraseña incorrectos', 'error')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        if password != confirm_password:
            flash('Las contraseñas no coinciden', 'error')
            return render_template('register.html')
        
        if User.query.filter_by(username=username).first():
            flash('El nombre de usuario ya existe', 'error')
            return render_template('register.html')
        
        if User.query.filter_by(email=email).first():
            flash('El email ya está registrado', 'error')
            return render_template('register.html')
        
        password_hash = generate_password_hash(password)
        new_user = User(username=username, email=email, password_hash=password_hash)
        
        db.session.add(new_user)
        db.session.commit()
        
        flash('¡Registro exitoso! Ahora puedes iniciar sesión', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Has cerrado sesión', 'info')
    return redirect(url_for('index'))

@app.route('/catalog')
def catalog():
    if 'user_id' not in session:
        flash('Debes iniciar sesión para ver el catálogo', 'error')
        return redirect(url_for('login'))
    
    services = Service.query.all()
    return render_template('catalog.html', services=services)

@app.route('/book_appointment/<int:service_id>', methods=['GET', 'POST'])
def book_appointment(service_id):
    if 'user_id' not in session:
        flash('Debes iniciar sesión para reservar un turno', 'error')
        return redirect(url_for('login'))
    
    service = Service.query.get_or_404(service_id)
    
    if request.method == 'POST':
        date_str = request.form['date']
        time_str = request.form['time']
        
        try:
            appointment_datetime = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
            
            # Verificar que la fecha no sea en el pasado
            if appointment_datetime < datetime.now():
                flash('No puedes reservar turnos en el pasado', 'error')
                return render_template('book_appointment.html', service=service, today=datetime.now().strftime('%Y-%m-%d'))
            
            # Verificar que no haya conflictos de horario
            existing_appointment = Appointment.query.filter_by(
                appointment_date=appointment_datetime
            ).first()
            
            if existing_appointment:
                flash('Este horario ya está ocupado', 'error')
                return render_template('book_appointment.html', service=service, today=datetime.now().strftime('%Y-%m-%d'))
            
            new_appointment = Appointment(
                user_id=session['user_id'],
                service_id=service_id,
                appointment_date=appointment_datetime
            )
            
            db.session.add(new_appointment)
            db.session.commit()
            
            flash('¡Turno reservado exitosamente!', 'success')
            return redirect(url_for('my_appointments'))
            
        except ValueError:
            flash('Fecha u hora inválida', 'error')
    
    return render_template('book_appointment.html', service=service, today=datetime.now().strftime('%Y-%m-%d'))

@app.route('/my_appointments')
def my_appointments():
    if 'user_id' not in session:
        flash('Debes iniciar sesión para ver tus turnos', 'error')
        return redirect(url_for('login'))
    
    appointments = Appointment.query.filter_by(user_id=session['user_id']).order_by(Appointment.appointment_date).all()
    return render_template('my_appointments.html', appointments=appointments)

@app.route('/cancel_appointment/<int:appointment_id>')
def cancel_appointment(appointment_id):
    if 'user_id' not in session:
        flash('Debes iniciar sesión', 'error')
        return redirect(url_for('login'))
    
    appointment = Appointment.query.get_or_404(appointment_id)
    
    if appointment.user_id != session['user_id'] and not session.get('is_admin'):
        flash('No tienes permisos para cancelar este turno', 'error')
        return redirect(url_for('my_appointments'))
    
    appointment.status = 'cancelled'
    db.session.commit()
    
    flash('Turno cancelado exitosamente', 'success')
    return redirect(url_for('my_appointments'))

# Rutas de administrador
@app.route('/admin')
def admin():
    if 'user_id' not in session or not session.get('is_admin'):
        flash('Acceso denegado', 'error')
        return redirect(url_for('index'))
    
    appointments = Appointment.query.order_by(Appointment.appointment_date).all()
    services = Service.query.all()
    users = User.query.all()
    
    return render_template('admin.html', appointments=appointments, services=services, users=users)

@app.route('/admin/add_service', methods=['GET', 'POST'])
def add_service():
    if 'user_id' not in session or not session.get('is_admin'):
        flash('Acceso denegado', 'error')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        price = float(request.form['price'])
        duration = int(request.form['duration'])
        image_url = request.form['image_url']
        
        new_service = Service(
            name=name,
            description=description,
            price=price,
            duration=duration,
            image_url=image_url
        )
        
        db.session.add(new_service)
        db.session.commit()
        
        flash('Servicio agregado exitosamente', 'success')
        return redirect(url_for('admin'))
    
    return render_template('add_service.html')

@app.route('/admin/confirm_appointment/<int:appointment_id>')
def confirm_appointment(appointment_id):
    if 'user_id' not in session or not session.get('is_admin'):
        flash('Acceso denegado', 'error')
        return redirect(url_for('index'))
    
    appointment = Appointment.query.get_or_404(appointment_id)
    appointment.status = 'confirmed'
    db.session.commit()
    
    flash('Turno confirmado exitosamente', 'success')
    return redirect(url_for('admin'))

# Función para crear datos de ejemplo
def create_sample_data():
    # Crear servicios de ejemplo
    services = [
        {
            'name': 'Manicure Básica',
            'description': 'Limpieza, corte y esmaltado de uñas',
            'price': 25.00,
            'duration': 30,
            'image_url': '/static/images/manicure.jpg'
        },
        {
            'name': 'Pedicure Completa',
            'description': 'Limpieza, corte, exfoliación y esmaltado de pies',
            'price': 35.00,
            'duration': 45,
            'image_url': '/static/images/pedicure.jpg'
        },
        {
            'name': 'Uñas Acrílicas',
            'description': 'Aplicación de uñas acrílicas con diseño',
            'price': 45.00,
            'duration': 60,
            'image_url': '/static/images/acrylic.jpg'
        },
        {
            'name': 'Gelish',
            'description': 'Esmaltado semipermanente con gel',
            'price': 30.00,
            'duration': 40,
            'image_url': '/static/images/gelish.jpg'
        }
    ]
    
    for service_data in services:
        existing_service = Service.query.filter_by(name=service_data['name']).first()
        if not existing_service:
            service = Service(**service_data)
            db.session.add(service)
    
    # Crear usuario administrador
    admin_user = User.query.filter_by(username='admin').first()
    if not admin_user:
        admin_user = User(
            username='admin',
            email='admin@nailstudio.com',
            password_hash=generate_password_hash('admin123'),
            is_admin=True
        )
        db.session.add(admin_user)
    
    db.session.commit()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        create_sample_data()
    
    app.run(debug=True)
