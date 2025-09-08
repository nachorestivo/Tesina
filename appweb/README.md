# Nail Studio - Sistema de Turnos para Uñas

Un sistema completo de gestión de turnos para salones de uñas desarrollado con Flask.

## Características

- ✅ **Autenticación de usuarios**: Registro e inicio de sesión
- ✅ **Catálogo de servicios**: Visualización de todos los servicios disponibles
- ✅ **Reserva de turnos**: Sistema de reserva con fecha y hora
- ✅ **Gestión de turnos**: Ver, cancelar y gestionar turnos
- ✅ **Panel de administrador**: Gestión completa para administradores
- ✅ **Diseño responsive**: Interfaz moderna y adaptable a dispositivos móviles
- ✅ **Base de datos SQLite**: Almacenamiento persistente de datos

## Instalación

1. **Clonar el repositorio**:
```bash
git clone <url-del-repositorio>
cd nail-studio
```

2. **Crear entorno virtual**:
```bash
python -m venv venv
```

3. **Activar entorno virtual**:
```bash
# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

4. **Instalar dependencias**:
```bash
pip install -r requirements.txt
```

5. **Ejecutar la aplicación**:
```bash
python app.py
```

6. **Abrir en el navegador**:
```
http://localhost:5000
```

## Uso

### Para Clientes

1. **Registrarse**: Crear una cuenta nueva en la página de registro
2. **Iniciar sesión**: Acceder con usuario y contraseña
3. **Ver catálogo**: Explorar los servicios disponibles
4. **Reservar turno**: Seleccionar servicio, fecha y hora
5. **Gestionar turnos**: Ver, cancelar o modificar turnos existentes

### Para Administradores

**Credenciales por defecto**:
- Usuario: `admin`
- Contraseña: `admin123`

**Funciones disponibles**:
- Ver estadísticas del sistema
- Gestionar todos los turnos
- Confirmar turnos pendientes
- Agregar nuevos servicios
- Ver usuarios registrados

## Estructura del Proyecto

```
nail-studio/
├── app.py                 # Aplicación principal Flask
├── requirements.txt       # Dependencias de Python
├── README.md             # Este archivo
├── templates/            # Plantillas HTML
│   ├── base.html         # Plantilla base
│   ├── index.html        # Página de inicio
│   ├── login.html        # Página de login
│   ├── register.html     # Página de registro
│   ├── catalog.html      # Catálogo de servicios
│   ├── book_appointment.html  # Reserva de turnos
│   ├── my_appointments.html   # Mis turnos
│   ├── admin.html        # Panel de administrador
│   └── add_service.html  # Agregar servicios
├── static/               # Archivos estáticos
│   ├── css/
│   │   └── style.css     # Estilos CSS
│   ├── js/
│   │   └── script.js     # JavaScript
│   └── images/           # Imágenes (opcional)
└── nail_salon.db        # Base de datos SQLite (se crea automáticamente)
```

## Base de Datos

La aplicación utiliza SQLite con los siguientes modelos:

- **User**: Usuarios del sistema
- **Service**: Servicios disponibles
- **Appointment**: Turnos reservados

## Personalización

### Agregar nuevos servicios

1. Iniciar sesión como administrador
2. Ir a "Agregar Servicio"
3. Completar el formulario con los detalles del servicio

### Modificar estilos

Editar el archivo `static/css/style.css` para personalizar la apariencia.

### Cambiar configuración

Modificar las variables en `app.py`:
- `SECRET_KEY`: Clave secreta para sesiones
- `SQLALCHEMY_DATABASE_URI`: URL de la base de datos

## Tecnologías Utilizadas

- **Backend**: Flask, SQLAlchemy
- **Frontend**: HTML5, CSS3, JavaScript
- **Base de datos**: SQLite
- **Iconos**: Font Awesome
- **Diseño**: CSS Grid, Flexbox

## Contribuir

1. Fork el proyecto
2. Crear una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abrir un Pull Request

## Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## Soporte

Si tienes alguna pregunta o problema, por favor abre un issue en el repositorio.

---

**Desarrollado con ❤️ para salones de uñas** 