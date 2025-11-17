from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import json

try:
    import MySQLdb.cursors
except ImportError:
    print("Advertencia: No se encontró 'MySQLdb.cursors'.")

app = Flask(__name__)
app.config['SECRET_KEY'] = 'b1f8e7c9-4a2e-4d8b-9f3c-2e7a6c1d8e5f' 
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'admin123'
app.config['MYSQL_DB'] = 'agendanails'
app.config['MYSQL_PORT'] = 3307

mysql = MySQL(app)

def get_cursor(dictionary=False):
    """Obtiene un cursor de la base de datos"""
    if dictionary:
        try:
            return mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        except AttributeError:
            print("Error al usar DictCursor.")
            return mysql.connection.cursor()
    else:
        return mysql.connection.cursor()

# -----------------------------
# Rutas principales
# -----------------------------

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        cur = get_cursor(dictionary=True)
        cur.execute("SELECT id_Usuario, username, password_hash, is_admin FROM usuarios WHERE username = %s", (username,))
        usuario = cur.fetchone()
        cur.close()

        if usuario and check_password_hash(usuario['password_hash'], password):
            session['user_id'] = usuario['id_Usuario']
            session['username'] = usuario['username']
            # Convertir is_admin a boolean correctamente
            session['is_admin'] = bool(usuario.get('is_admin', 0))
            
            flash('¡Inicio de sesión exitoso!', 'success')
            
            # Redirigir según el tipo de usuario
            if session.get('is_admin'):
                return redirect(url_for('admin'))
            else:
                return redirect(url_for('catalogo'))
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
        cur.execute("INSERT INTO usuarios (username, email, password_hash, is_admin, created_at) VALUES (%s, %s, %s, %s, %s)",
                    (username, email, password_hash, 0, datetime.now()))
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
    """Muestra el catálogo de servicios desde la base de datos"""
    if 'user_id' not in session:
        flash('Debes iniciar sesión para ver el catálogo', 'error')
        return redirect(url_for('login'))
        
    cur = get_cursor(dictionary=True)
    cur.execute("SELECT * FROM servicios ORDER BY id_Servicios")
    services = cur.fetchall()
    cur.close()
    
    servicios_formateados = []
    for service in services:
        servicios_formateados.append({
            'id': service['id_Servicios'],
            'nombre': service['Tipo_de_servicio'],
            'descripcion': service['Descripcion_del_servicio'],
            'precio': float(service['Precio']),
            'duracion': service['Duracion']
        })
    
    return render_template('catalogo.html', services=servicios_formateados)


@app.route('/agendar_turno', methods=['POST'])
def agendar_turno():
    """Endpoint para agendar un turno"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Debes iniciar sesión'}), 401
    
    try:
        data = request.get_json()
        servicios = data.get('servicios', [])
        fecha = data.get('fecha')
        hora = data.get('hora')
        
        if not all([servicios, fecha, hora]):
            return jsonify({'success': False, 'message': 'Faltan datos requeridos'}), 400
        
        fecha_obj = datetime.strptime(fecha, "%Y-%m-%d").date()
        hora_obj = datetime.strptime(hora, "%H:%M").time()
        fecha_hora_completa = datetime.combine(fecha_obj, hora_obj)
        
        if fecha_hora_completa < datetime.now():
            return jsonify({'success': False, 'message': 'No puedes agendar turnos en el pasado'}), 400
        
        cur = get_cursor(dictionary=True)
        cur.execute("""
            SELECT * FROM turnos 
            WHERE fecha = %s AND hora = %s 
            AND Estado_del_turno NOT IN ('cancelado')
        """, (fecha, hora))
        
        if cur.fetchone():
            cur.close()
            return jsonify({'success': False, 'message': 'Este horario ya está ocupado'}), 400
        
        ids_servicios = [s['id'] for s in servicios if 'id' in s]
        servicios_nombres = [s.get('nombre', s.get('Tipo_de_servicio', '')) for s in servicios]
        servicios_str = ', '.join(servicios_nombres)
        
        if ids_servicios:
            placeholders = ','.join(['%s'] * len(ids_servicios))
            cur.execute(f"SELECT SUM(Precio) as total FROM servicios WHERE id_Servicios IN ({placeholders})", ids_servicios)
            resultado = cur.fetchone()
            total = float(resultado['total']) if resultado['total'] else 0
        else:
            total = sum(float(s.get('precio', s.get('Precio', 0))) for s in servicios)
        
        id_servicio_principal = ids_servicios[0] if ids_servicios else None
        
        cur.execute("""
            INSERT INTO turnos (id_Usuario, id_Servicio, Servicios, fecha, hora, Total, Estado_del_turno, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (session['user_id'], id_servicio_principal, servicios_str, fecha, hora, total, 'pendiente', datetime.now()))
        
        mysql.connection.commit()
        cur.close()
        
        return jsonify({'success': True, 'message': 'Turno agendado exitosamente'}), 200
        
    except Exception as e:
        print(f"Error al agendar turno: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': f'Error al agendar turno: {str(e)}'}), 500


@app.route('/mis_turnos')
def mis_turnos():
    """Muestra los turnos del usuario actual"""
    if 'user_id' not in session:
        flash('Debes iniciar sesión para ver tus turnos', 'error')
        return redirect(url_for('login'))
    
    try:
        cur = get_cursor(dictionary=True)
        cur.execute("""
            SELECT t.*, u.username, u.email
            FROM turnos t
            JOIN usuarios u ON t.id_Usuario = u.id_Usuario
            WHERE t.id_Usuario = %s
            ORDER BY t.fecha DESC, t.hora DESC
        """, (session['user_id'],))
        turnos = cur.fetchall()
        cur.close()
        
        turnos_formateados = []
        for turno in turnos:
            turno_formateado = dict(turno)
            
            if turno_formateado.get('fecha'):
                if isinstance(turno_formateado['fecha'], datetime):
                    turno_formateado['fecha'] = turno_formateado['fecha'].strftime('%Y-%m-%d')
                elif hasattr(turno_formateado['fecha'], 'strftime'):
                    turno_formateado['fecha'] = turno_formateado['fecha'].strftime('%Y-%m-%d')
                else:
                    turno_formateado['fecha'] = str(turno_formateado['fecha'])
            
            if turno_formateado.get('hora'):
                if isinstance(turno_formateado['hora'], datetime):
                    turno_formateado['hora'] = turno_formateado['hora'].strftime('%H:%M')
                elif hasattr(turno_formateado['hora'], 'strftime'):
                    turno_formateado['hora'] = turno_formateado['hora'].strftime('%H:%M')
                else:
                    if hasattr(turno_formateado['hora'], 'seconds'):
                        total_seconds = turno_formateado['hora'].seconds
                        hours = total_seconds // 3600
                        minutes = (total_seconds % 3600) // 60
                        turno_formateado['hora'] = f"{hours:02d}:{minutes:02d}"
                    else:
                        turno_formateado['hora'] = str(turno_formateado['hora'])
            
            turnos_formateados.append(turno_formateado)
        
        return render_template('mis_turnos.html', turnos=turnos_formateados)
        
    except Exception as e:
        print(f"Error en mis_turnos: {e}")
        import traceback
        traceback.print_exc()
        flash('Error al cargar los turnos', 'error')
        return redirect(url_for('catalogo'))


@app.route('/cancelar_turno/<int:turno_id>', methods=['POST'])
def cancelar_turno(turno_id):
    """Cancela un turno"""
    if 'user_id' not in session:
        flash('No autorizado', 'error')
        return redirect(url_for('login'))
    
    cur = get_cursor(dictionary=True)
    cur.execute("SELECT id_Usuario FROM turnos WHERE id_Turnos = %s", (turno_id,))
    turno = cur.fetchone()
    
    if not turno:
        cur.close()
        flash('Turno no encontrado', 'error')
        if session.get('is_admin'):
            return redirect(url_for('admin'))
        else:
            return redirect(url_for('mis_turnos'))
    
    if turno['id_Usuario'] != session['user_id'] and not session.get('is_admin'):
        cur.close()
        flash('No tienes permisos para cancelar este turno', 'error')
        return redirect(url_for('mis_turnos'))
    
    cur.execute("UPDATE turnos SET Estado_del_turno = 'cancelado' WHERE id_Turnos = %s", (turno_id,))
    mysql.connection.commit()
    cur.close()
    
    flash('Turno cancelado exitosamente', 'success')
    
    # Redirigir según el tipo de usuario
    if session.get('is_admin'):
        return redirect(url_for('/admin'))
    else:
        return redirect(url_for('/mis_turnos'))




# -----------------------------
# Rutas de administrador
# -----------------------------

@app.route('/admin')
def admin():
    """Panel de administración"""
    if 'user_id' not in session or not session.get('is_admin'):
        flash('Acceso denegado. Solo administradores pueden acceder.', 'error')
        return redirect(url_for('index'))
    
    try:
        cur = get_cursor(dictionary=True)
        
        # Obtener todos los turnos
        cur.execute("""
            SELECT t.*, u.username, u.email
            FROM turnos t
            JOIN usuarios u ON t.id_Usuario = u.id_Usuario
            ORDER BY t.fecha DESC, t.hora DESC
        """)
        turnos_raw = cur.fetchall()
        
        # Formatear turnos
        turnos = []
        for turno in turnos_raw:
            turno_formateado = dict(turno)
            
            if turno_formateado.get('fecha'):
                if isinstance(turno_formateado['fecha'], datetime):
                    turno_formateado['fecha_str'] = turno_formateado['fecha'].strftime('%d/%m/%Y')
                elif hasattr(turno_formateado['fecha'], 'strftime'):
                    turno_formateado['fecha_str'] = turno_formateado['fecha'].strftime('%d/%m/%Y')
                else:
                    turno_formateado['fecha_str'] = str(turno_formateado['fecha'])
            else:
                turno_formateado['fecha_str'] = 'N/A'
            
            if turno_formateado.get('hora'):
                if isinstance(turno_formateado['hora'], datetime):
                    turno_formateado['hora_str'] = turno_formateado['hora'].strftime('%H:%M')
                elif hasattr(turno_formateado['hora'], 'strftime'):
                    turno_formateado['hora_str'] = turno_formateado['hora'].strftime('%H:%M')
                else:
                    if hasattr(turno_formateado['hora'], 'seconds'):
                        total_seconds = turno_formateado['hora'].seconds
                        hours = total_seconds // 3600
                        minutes = (total_seconds % 3600) // 60
                        turno_formateado['hora_str'] = f"{hours:02d}:{minutes:02d}"
                    else:
                        turno_formateado['hora_str'] = str(turno_formateado['hora'])
            else:
                turno_formateado['hora_str'] = 'N/A'
            
            turnos.append(turno_formateado)
        
        # Obtener todos los servicios
        cur.execute("SELECT * FROM servicios ORDER BY id_Servicios")
        servicios = cur.fetchall()
        
        # Obtener todos los usuarios
        cur.execute("SELECT id_Usuario, username, email, is_admin, created_at FROM usuarios ORDER BY created_at DESC")
        usuarios = cur.fetchall()
        
        cur.close()
        
        return render_template('admin.html', turnos=turnos, servicios=servicios, usuarios=usuarios)
        
    except Exception as e:
        print(f"Error en admin: {e}")
        import traceback
        traceback.print_exc()
        flash('Error al cargar el panel de administración', 'error')
        return redirect(url_for('index'))


@app.route('/admin/servicios/agregar', methods=['GET', 'POST'])
def admin_agregar_servicio():
    """Agregar un nuevo servicio"""
    if 'user_id' not in session or not session.get('is_admin'):
        flash('Acceso denegado', 'error')
        return redirect(url_for('index'))
        
    if request.method == 'POST':
        tipo_servicio = request.form['tipo_servicio']
        descripcion = request.form['descripcion']
        try:
            duracion = int(request.form['duracion'])
            precio = float(request.form['precio'])
        except ValueError:
            flash('Duración o precio inválido', 'error')
            return render_template('admin_agregar_servicio.html')
            
        cur = get_cursor()
        cur.execute("""
            INSERT INTO servicios (Tipo_de_servicio, Descripcion_del_servicio, Duracion, Precio, created_at)
            VALUES (%s, %s, %s, %s, %s)
        """, (tipo_servicio, descripcion, duracion, precio, datetime.now()))
        mysql.connection.commit()
        cur.close()
        
        flash('Servicio agregado exitosamente', 'success')
        return redirect(url_for('admin'))
        
    return render_template('admin_agregar_servicio.html')


@app.route('/admin/servicios/editar/<int:servicio_id>', methods=['GET', 'POST'])
def admin_editar_servicio(servicio_id):
    """Editar un servicio existente"""
    if 'user_id' not in session or not session.get('is_admin'):
        flash('Acceso denegado', 'error')
        return redirect(url_for('index'))
    
    cur = get_cursor(dictionary=True)
    
    if request.method == 'POST':
        tipo_servicio = request.form['tipo_servicio']
        descripcion = request.form['descripcion']
        try:
            duracion = int(request.form['duracion'])
            precio = float(request.form['precio'])
        except ValueError:
            flash('Duración o precio inválido', 'error')
            return redirect(url_for('admin_editar_servicio', servicio_id=servicio_id))
            
        cur.execute("""
            UPDATE servicios 
            SET Tipo_de_servicio = %s, Descripcion_del_servicio = %s, Duracion = %s, Precio = %s
            WHERE id_Servicios = %s
        """, (tipo_servicio, descripcion, duracion, precio, servicio_id))
        mysql.connection.commit()
        cur.close()
        flash('Servicio actualizado exitosamente', 'success')
        return redirect(url_for('admin'))
    
    cur.execute("SELECT * FROM servicios WHERE id_Servicios = %s", (servicio_id,))
    servicio = cur.fetchone()
    cur.close()
    
    if not servicio:
        flash('Servicio no encontrado', 'error')
        return redirect(url_for('admin'))
    
    return render_template('admin_editar_servicio.html', servicio=servicio)


@app.route('/admin/servicios/eliminar/<int:servicio_id>', methods=['POST'])
def admin_eliminar_servicio(servicio_id):
    """Eliminar un servicio"""
    if 'user_id' not in session or not session.get('is_admin'):
        return jsonify({'success': False, 'message': 'Acceso denegado'}), 403
    
    cur = get_cursor()
    cur.execute("DELETE FROM servicios WHERE id_Servicios = %s", (servicio_id,))
    mysql.connection.commit()
    cur.close()
    
    flash('Servicio eliminado exitosamente', 'success')
    return redirect(url_for('admin'))


@app.route('/admin/turnos/confirmar/<int:turno_id>', methods=['POST'])
def admin_confirmar_turno(turno_id):
    """Confirmar un turno"""
    if 'user_id' not in session or not session.get('is_admin'):
        return jsonify({'success': False, 'message': 'Acceso denegado'}), 403
        
    cur = get_cursor()
    cur.execute("UPDATE turnos SET Estado_del_turno = 'confirmado' WHERE id_Turnos = %s", (turno_id,))
    mysql.connection.commit()
    cur.close()
    
    flash('Turno confirmado exitosamente', 'success')
    return redirect(url_for('admin'))


@app.route('/admin/turnos/completar/<int:turno_id>', methods=['POST'])
def admin_completar_turno(turno_id):
    """Marcar un turno como completado"""
    if 'user_id' not in session or not session.get('is_admin'):
        return jsonify({'success': False, 'message': 'Acceso denegado'}), 403
        
    cur = get_cursor()
    cur.execute("UPDATE turnos SET Estado_del_turno = 'completado' WHERE id_Turnos = %s", (turno_id,))
    mysql.connection.commit()
    cur.close()
    
    flash('Turno marcado como completado', 'success')
    return redirect(url_for('admin'))


if __name__ == '__main__':
    app.run(debug=True)