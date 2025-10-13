Parece que el error de sintaxis está en una versión del script que tienes guardada localmente, y no es visible en el código que me has proporcionado.

Para solucionar tu error de manera definitiva, te voy a dar de nuevo el script completo y funcional, con la corrección del cursor (DictCursor) y asumiendo que la línea 283 en tu archivo local debía ser una asignación a la variable services.

Por favor, reemplaza todo el contenido de tu archivo main.py con este código.

Python

from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
# Nota: La importación de MySQLdb ya no es necesaria si usas flask_mysqldb

app = Flask(__name__)

# --- CONFIGURACIÓN DE LA APLICACIÓN ---
app.config['SECRET_KEY'] = 'b1f8e7c9-4a2e-4d8b-9f3c-2e7a6c1d8e5f'
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'admin123'
app.config['MYSQL_DB'] = 'agendanails'
app.config['MYSQL_PORT'] = 3307
# --- CORRECCIÓN CRUCIAL: Usa DictCursor para obtener resultados como diccionarios ---
app.config['MYSQL_CURSORCLASS'] = 'DictCursor' 

mysql = MySQL(app)

def get_cursor():
    return mysql.connection.cursor()

# Rutas principales
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        cur = get_cursor()
        cur.execute("SELECT * FROM usuarios WHERE username = %s", (username,))
        usuarios = cur.fetchone()
        cur.close()
        
        # 'usuarios' es un diccionario gracias a DictCursor
        if usuarios and check_password_hash(usuarios['password'], password):
            session['user_id'] = usuarios['id']
            session['username'] = usuarios['username']
            session['is_admin'] = usuarios['is_admin']
            flash('¡Inicio de sesión exitoso!', 'success')
            return redirect(url_for('index'))
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
            
        cur = get_cursor()
        
        # Verificar usuario y email
        cur.execute("SELECT * FROM usuarios WHERE username = %s", (username,))
        if cur.fetchone():
            flash('El nombre de usuario ya existe', 'error')
            cur.close()
            return render_template('register.html')
            
        cur.execute("SELECT * FROM usuarios WHERE email = %s", (email,))
        if cur.fetchone():
            flash('El email ya está registrado', 'error')
            cur.close()
            return render_template('register.html')
            
        password_hash = generate_password_hash(password)
        
        cur.execute("INSERT INTO usuarios (username, email, password, is_admin, created_at) VALUES (%s, %s, %s, %s, %s)",
                    (username, email, password_hash, False, datetime.now()))
        mysql.connection.commit()
        cur.close()
        
        flash('¡Registro exitoso! Ahora puedes iniciar sesión', 'success')
        return redirect(url_for('login'))
        
    return render_template('register.html')


@app.route('/logout')
def logout():
    session.clear()
    flash('Has cerrado sesión', 'info')
    return redirect(url_for('index'))


@app.route('/catalogo')
def catalogo():
    if 'user_id' not in session:
        flash('Debes iniciar sesión para ver el catálogo', 'error')
        return redirect(url_for('login'))
        
    cur = get_cursor()
    cur.execute("SELECT * FROM service")
    services = cur.fetchall()
    cur.close()
    
    return render_template('catalogo.html', services=services)


@app.route('/book_appointment/<int:service_id>', methods=['GET', 'POST'])
def book_appointment(service_id):
    if 'user_id' not in session:
        flash('Debes iniciar sesión para reservar un turno', 'error')
        return redirect(url_for('login'))
        
    cur = get_cursor()
    cur.execute("SELECT * FROM service WHERE id = %s", (service_id,))
    service = cur.fetchone()
    
    if not service:
        cur.close()
        flash('Servicio no encontrado', 'error')
        return redirect(url_for('catalogo'))
        
    if request.method == 'POST':
        date_str = request.form['date']
        time_str = request.form['time']
        
        try:
            appointment_datetime = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
            
            if appointment_datetime < datetime.now():
                flash('No puedes reservar turnos en el pasado', 'error')
                cur.close()
                return render_template('book_appointment.html', service=service, today=datetime.now().strftime('%Y-%m-%d'))
                
            # Verificar disponibilidad
            cur.execute("SELECT * FROM appointment WHERE appointment_date = %s", (appointment_datetime,))
            if cur.fetchone():
                flash('Este horario ya está ocupado', 'error')
                cur.close()
                return render_template('book_appointment.html', service=service, today=datetime.now().strftime('%Y-%m-%d'))
                
            # Insertar turno
            cur.execute("INSERT INTO appointment (user_id, service_id, appointment_date, status, created_at) VALUES (%s, %s, %s, %s, %s)",
                        (session['user_id'], service_id, appointment_datetime, 'pending', datetime.now()))
            mysql.connection.commit()
            
            flash('¡Turno reservado exitosamente!', 'success')
            cur.close()
            return redirect(url_for('my_appointments'))
            
        except ValueError:
            flash('Fecha u hora inválida', 'error')
            
    cur.close()
    return render_template('book_appointment.html', service=service, today=datetime.now().strftime('%Y-%m-%d'))


@app.route('/my_appointments')
def my_appointments():
    if 'user_id' not in session:
        flash('Debes iniciar sesión para ver tus turnos', 'error')
        return redirect(url_for('login'))
        
    cur = get_cursor()
    cur.execute("SELECT a.*, s.name as service_name FROM appointment a JOIN service s ON a.service_id = s.id WHERE a.user_id = %s ORDER BY a.appointment_date", (session['user_id'],))
    appointments = cur.fetchall()
    cur.close()
    
    return render_template('my_appointments.html', appointments=appointments)


@app.route('/cancel_appointment/<int:appointment_id>')
def cancel_appointment(appointment_id):
    if 'user_id' not in session:
        flash('Debes iniciar sesión', 'error')
        return redirect(url_for('login'))
        
    cur = get_cursor()
    cur.execute("SELECT * FROM appointment WHERE id = %s", (appointment_id,))
    appointment = cur.fetchone()
    
    if not appointment:
        cur.close()
        flash('Turno no encontrado', 'error')
        return redirect(url_for('my_appointments'))
        
    # Verificar permisos
    if appointment['user_id'] != session['user_id'] and not session.get('is_admin'):
        cur.close()
        flash('No tienes permisos para cancelar este turno', 'error')
        return redirect(url_for('my_appointments'))
        
    # Cancelar turno
    cur.execute("UPDATE appointment SET status = 'cancelled' WHERE id = %s", (appointment_id,))
    mysql.connection.commit()
    cur.close()
    
    flash('Turno cancelado exitosamente', 'success')
    return redirect(url_for('my_appointments'))

# Rutas de administrador

@app.route('/admin')
def admin():
    if 'user_id' not in session or not session.get('is_admin'):
        flash('Acceso denegado', 'error')
        return redirect(url_for('index'))
        
    cur = get_cursor()
    # Obtener citas con nombres de servicio y cliente
    cur.execute("SELECT a.*, s.name as service_name, u.username as client_username FROM appointment a JOIN service s ON a.service_id = s.id JOIN usuarios u ON a.user_id = u.id ORDER BY a.appointment_date")
    appointments = cur.fetchall()
    
    cur.execute("SELECT * FROM service")
    services = cur.fetchall() # <--- Si la línea 283 era esta y estaba incompleta, ahora está correcta.
    
    cur.execute("SELECT * FROM usuarios") 
    users = cur.fetchall()
    cur.close()
    
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
        
        cur = get_cursor()
        cur.execute("INSERT INTO service (name, description, price, duration, image_url) VALUES (%s, %s, %s, %s, %s)",
                    (name, description, price, duration, image_url))
        mysql.connection.commit()
        cur.close()
        
        flash('Servicio agregado exitosamente', 'success')
        return redirect(url_for('admin'))
        
    return render_template('add_service.html')


@app.route('/admin/confirm_appointment/<int:appointment_id>')
def confirm_appointment(appointment_id):
    if 'user_id' not in session or not session.get('is_admin'):
        flash('Acceso denegado', 'error')
        return redirect(url_for('index'))
        
    cur = get_cursor()
    cur.execute("UPDATE appointment SET status = 'confirmed' WHERE id = %s", (appointment_id,))
    mysql.connection.commit()
    cur.close()
    
    flash('Turno confirmado exitosamente', 'success')
    return redirect(url_for('admin'))


# Función para crear datos de ejemplo en MySQL
def create_sample_data():
    cur = get_cursor()
    
    # 1. Insertar servicios si no existen
    services = [
        ('Manicure Básica', 'Limpieza, corte y esmaltado de uñas', 25.00, 30, '/static/images/manicure.jpg'),
        ('Pedicure Completa', 'Limpieza, corte, exfoliación y esmaltado de pies', 35.00, 45, '/static/images/pedicure.jpg'),
        ('Uñas Acrílicas', 'Aplicación de uñas acrílicas con diseño', 45.00, 60, '/static/images/acrylic.jpg'),
        ('Gelish', 'Esmaltado semipermanente con gel', 30.00, 40, '/static/images/gelish.jpg')
    ]
    for s in services:
        cur.execute("SELECT * FROM service WHERE name = %s", (s[0],))
        if not cur.fetchone():
            cur.execute("INSERT INTO service (name, description, price, duration, image_url) VALUES (%s, %s, %s, %s, %s)", s)
            
    # 2. Insertar usuario administrador si no existe
    cur.execute("SELECT * FROM usuarios WHERE username = 'admin'")
    if not cur.fetchone():
        cur.execute("INSERT INTO usuarios (username, email, password, is_admin, created_at) VALUES (%s, %s, %s, %s, %s)",
                    ('admin', 'admin@nailstudio.com', generate_password_hash('admin123'), True, datetime.now()))
                    
    mysql.connection.commit()
    cur.close()

if __name__ == '__main__':
    with app.app_context():
        try:
            create_sample_data()
            print("Datos de ejemplo creados/verificados exitosamente.")
        except Exception as e:
            # Esto ayuda a diagnosticar si el error es de conexión a la DB y no de sintaxis.
            print(f"ERROR: No se pudo conectar a la base de datos o crear datos de ejemplo. Detalle: {e}")
            
    app.run(debug=True)