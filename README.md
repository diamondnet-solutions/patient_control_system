# Sistema de Gestión Dental

## Descripción
El Sistema de Gestión de PACIENTES  es una aplicación de escritorio desarrollada en Python que permite administrar eficientemente un consultorio dental. La aplicación facilita el registro y control de pacientes, citas, tratamientos y pagos, además de generar reportes útiles para el análisis de la operación del consultorio.

## Características principales
- **Gestión de Citas**: Creación, modificación y cancelación de citas.
- **Expedientes de Pacientes**: Registro completo de información personal y médica.
- **Historial Clínico**: Seguimiento detallado de las visitas y tratamientos por paciente.
- **Control de Tratamientos**: Catálogo de servicios con precios y seguimiento.
- **Sistema de Pagos**: Registro y control de pagos realizados por los pacientes.
- **Reportes Mensuales**:
  - Ingresos generados
  - Horas trabajadas
  - Análisis de ocupación (horas sin citas)
- **Comunicación con Pacientes**: Envío automático de correos para confirmación y recordatorios de citas.

## Tecnologías utilizadas
- **Python**: Lenguaje de programación principal
- **CustomTkinter**: Interfaz gráfica de usuario de madera Moderna
- **SQLite**: Base de datos local
- **Pillow**: Procesamiento de imágenes para expedientes
- **Matplotlib/Pandas**: Generación de reportes y análisis de datos
- **tkcalendar**: Widgets de calendario para la programación de citas

## Estructura del proyecto
```
patient_control_system/
│
├── main.py                 # Punto de entrada de la aplicación
├── requirements.txt        # Dependencias del proyecto
│
├── ui/                     # Interfaz gráfica con Tkinter
│   ├── main_window.py      # Ventana principal de la aplicación
│   ├── appointments.py     # Gestión de citas
│   ├── patients.py         # Gestión de pacientes
│   ├── treatments.py       # Gestión de tratamientos
│   └── reports.py          # Visualización de informes
│
├── core/                   # Lógica del negocio
│   ├── appointment_manager.py
│   ├── patient_manager.py
│   ├── treatment_manager.py
│   └── report_generator.py
│
├── db/                     # Capa de acceso a datos
│   └── database.py         # Gestión de la base de datos SQLite
│
├── utils/                  # Utilidades
│   ├── email_handler.py    # Envío y gestión de correos
│   └── image_utils.py      # Procesamiento de imágenes con Pillow
│
└── data/                   # Almacenamiento de datos locales
    ├── images/             # Imágenes de pacientes
    └── backups/            # Respaldos de la base de datos
```

## Requisitos del sistema
- Python 3.8 o superior
- Espacio en disco para la base de datos y archivos de imágenes
- Conexión a Internet para el envío de correos electrónicos

## Instalación

### 1. Clonar el repositorio
```bash
git clone https://github.com/tuusuario/sistema-gestion-dental.git
cd sistema-gestion-dental
```

### 2. Crear un entorno virtual (recomendado)
```bash
python -m venv venv

# Activar el entorno virtual
# En Windows:
.venv\Scripts\activate
# En macOS/Linux:
source venv/bin/activate
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4. Configuración inicial
- Crear archivo de configuración para el servidor de correo:
  - Copia el archivo `config.example.json` a `config.json`
  - Agrega los datos de tu servidor SMTP para el envío de correos

### 5. Iniciar la aplicación
```bash
python main.py
```

## Guía de uso

### Primer inicio
Al iniciar la aplicación por primera vez, se creará automáticamente la base de datos con la estructura necesaria. Por defecto, se creará un usuario administrador con las siguientes credenciales:
- **Usuario**: admin
- **Contraseña**: admin

Se recomienda cambiar estas credenciales inmediatamente después del primer inicio.

### Gestión de pacientes
1. Haz clic en la pestaña "Pacientes"
2. Usa el botón "Nuevo paciente" para registrar un nuevo expediente
3. Completa los datos del formulario y guarda
4. Puedes buscar, editar o eliminar pacientes desde esta misma pantalla

### Programación de citas
1. Selecciona la pestaña "Citas"
2. Utiliza el calendario para seleccionar una fecha
3. Haz clic en la hora deseada para añadir una nueva cita
4. Selecciona al paciente y el tratamiento
5. Configura la duración y las notificaciones si es necesario
6. Guarda la cita

### Tratamientos y pagos
1. Accede a la pestaña "Tratamientos"
2. Puedes crear nuevos tratamientos con sus precios
3. Al finalizar una cita, registra los tratamientos realizados
4. Registra los pagos recibidos y genera recibos si es necesario

### Reportes
1. Ve a la sección "Reportes"
2. Selecciona el tipo de informe y el período
3. Visualiza las estadísticas y gráficos
4. Exporta los informes a formato PDF o Excel si es necesario

## Respaldo y recuperación
La aplicación realiza automáticamente respaldos diarios de la base de datos. Para realizar un respaldo manual:
1. Ve a "Configuración" > "Respaldo de datos"
2. Haz clic en "Realizar respaldo ahora"
3. Selecciona la ubicación donde deseas guardar el archivo

Para restaurar una copia de seguridad:
1. Ve a "Configuración" > "Respaldo de datos"
2. Haz clic en "Restaurar base de datos"
3. Selecciona el archivo de respaldo que deseas restaurar

## Configuración del servidor de correo
Para habilitar el envío de correos electrónicos:
1. Ve a "Configuración" > "Servidor de correo"
2. Configura la dirección del servidor SMTP, puerto, usuario y contraseña
3. Realiza una prueba de conexión para verificar la configuración

## Solución de problemas comunes
- **Error de conexión a la base de datos**: Verifica que el archivo de la base de datos no esté bloqueado por otra aplicación.
- **Fallos al enviar correos**: Comprueba la configuración del servidor SMTP y tu conexión a Internet.
- **Imágenes no visibles**: Asegúrate de que el directorio de datos tenga permisos de escritura.

## Contribución
Si deseas contribuir al proyecto, por favor:
1. Haz un fork del repositorio
2. Crea una rama para tu funcionalidad (`git checkout -b feature/nueva-funcionalidad`)
3. Haz commit de tus cambios (`git commit -m 'Añadir nueva funcionalidad'`)
4. Envía tus cambios (`git push origin feature/nueva-funcionalidad`)
5. Abre un Pull Request

## Licencia
Este proyecto está licenciado bajo la Licencia MIT - consulta el archivo LICENSE para más detalles.

## Contacto
Para soporte técnico o consultas, contacta a: [tu@email.com]
