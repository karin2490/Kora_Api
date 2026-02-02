# Kora API - Sistema de Gestión Educativa

API REST desarrollada con FastAPI para gestionar programas educativos, materias, etapas y ejercicios.

## 📋 Requisitos Previos

- Python 3.11 o superior
- SQL Server (local o remoto)
- Git (opcional)

## 🚀 Instalación y Configuración

### 1. Clonar el repositorio (o descargar los archivos)

git clone https://github.com/karin2490/Kora_Api
cd Kora_Api

### 2. Crear entorno virtual

## En Windows (Command prompt):

python -m venv env

env/Scripts/activate

## En Windows (Powershell):

python -m venv env

./env/Scripts/activate

## En Windows (Git Bash):

python -m venv env

source env/Scripts/activate

## En macOS/Linux:

python -m venv env

source env/bin/activate

### 3. Instalar dependencias

Con el entorno virtual activado (deberías ver (env) en tu terminal):
pip install fastapi uvicorn pyodbc sqlalchemy python-dotenv

### 4. Crear base de datos

Ejecuta el script SQL proporcionado CreateDB.sql en SQL Server Management Studio o tu herramienta preferida para crear las tablas y datos iniciales.

### 5. Verificar la conexiòn a la base de datos

python test_db.py

Si la conexión es exitosa, verás: ✅ Conexión exitosa a SQL Server

### 6. Ejecutar la API

Modo desarrollo (con recarga automática):
uvicorn main:app --reload

Modo producción:
uvicorn main:app --host 0.0.0.0 --port 8000

Opciones adicionales:
--host 0.0.0.0 - Permite acceso desde otras máquinas en la red
--port 8000 - Especifica el puerto (por defecto es 8000)
--reload - Reinicia automáticamente al detectar cambios
--log-level debug - Muestra información detallada de debug

📚 Acceso a la API
Una vez que el servidor esté ejecutándose, puedes acceder a:

API Base: http://127.0.0.1:8000
Documentación Interactiva (Swagger UI): http://127.0.0.1:8000/docs
Documentación Alternativa (ReDoc): http://127.0.0.1:8000/redoc

🔧 Estructura del Proyecto
Kora_Api/
├── env/ # Entorno virtual (no subir a Git)
├── conf/
│ └── database.py # Configuración de base de datos
├── models/
│ ├── **init**.py # Exportación de modelos
│ ├── materias.py # Modelo de materias
│ ├── programas.py # Modelo de programas
│ ├── ejes.py # Modelo de ejes
│ ├── etapas.py # Modelo de etapas
│ ├── actividades.py # Modelo de actividades
│ ├── ejercicios.py # Modelo de ejercicios
│ ├── tipos_actividades.py # Modelo de tipos de actividades
│ └── prerrequisitos.py # Modelos de prerrequisitos
├── routes/
│ ├── materia.py # Endpoints de materias
│ ├── programa.py # Endpoints de programas
│ ├── eje.py # Endpoints de ejes
│ ├── etapa.py # Endpoints de etapas
│ ├── actividad.py # Endpoints de actividades
│ ├── ejercicio.py # Endpoints de ejercicios
│ └── tipo_actividad.py # Endpoints de tipos de actividades
├── .env # Variables de entorno (no subir a Git)
├── .gitignore # Archivos ignorados por Git
├── main.py # Punto de entrada de la aplicación
├── test_db.py # Script para probar conexión
├── requirements.txt # Dependencias del proyecto
└── README.md # Este archivo

📝 Endpoints Disponibles
Materias

GET /materias - Listar todas las materias
GET /materias/{id} - Obtener una materia específica
POST /materias - Crear nueva materia
PUT /materias/{id} - Actualizar materia
DELETE /materias/{id} - Eliminar materia

Programas

GET /programas - Listar todos los programas
GET /programas/{id} - Obtener un programa específico
GET /programas/materia/{materia_id} - Programas por materia
POST /programas - Crear nuevo programa
PUT /programas/{id} - Actualizar programa
DELETE /programas/{id} - Eliminar programa

Ejes

GET /ejes - Listar todos los ejes
GET /ejes/{id} - Obtener un eje específico
GET /ejes/codigo/{codigo} - Obtener eje por código
POST /ejes - Crear nuevo eje
PUT /ejes/{id} - Actualizar eje
DELETE /ejes/{id} - Eliminar eje

(Y así sucesivamente para los demás endpoints...)
🐛 Solución de Problemas Comunes
Error: "Table 'x' is already defined"

Causa: Modelo duplicado o mal nombrado
Solución: Verificar que cada modelo tenga un nombre de clase único

Error: "Cannot import name 'router'"

Causa: Archivo de ruta faltante o mal configurado
Solución: Verificar que el archivo existe y tiene router = APIRouter() definido

Error: "Connection refused"

Causa: SQL Server no está ejecutándose o credenciales incorrectas
Solución: Verificar que SQL Server esté activo y las credenciales en .env sean correctas

Error en Windows con PowerShell
Si PowerShell no permite ejecutar scripts:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

Puerto 8000 en uso:

# Usar un puerto diferente

uvicorn main:app --reload --port 8001

🔒 Seguridad

Nunca subas el archivo .env a control de versiones
Cambia la SECRET_KEY por una clave segura en producción
Usa variables de entorno diferentes para desarrollo y producción
Configura CORS apropiadamente para producción

📦 Generar archivo de requirements
Para crear un archivo con todas las dependencias:
pip install -r requirements.txt

🤝 Contribuir

Fork el proyecto
Crea una rama para tu feature (git checkout -b feature/AmazingFeature)
Commit tus cambios (git commit -m 'Add some AmazingFeature')
Push a la rama (git push origin feature/AmazingFeature)

Nota: Este proyecto está en desarrollo activo. Para reportar bugs o sugerir mejoras, por favor abre un issue en el repositorio.
