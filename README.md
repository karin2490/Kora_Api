# 🎓 Kora API - Educational Management System

![FastAPI](https://img.shields.io/badge/FastAPI-0.109.0-009688?style=flat-square&logo=fastapi)
![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat-square&logo=python)
![SQL Server](https://img.shields.io/badge/SQL%20Server-2019+-CC2927?style=flat-square&logo=microsoft-sql-server)

REST API developed with FastAPI to manage educational programs, subjects, stages, and activities for the Kora learning platform.

## 📋 Prerequisites

- **Python 3.11+**
- **SQL Server 2019+** (local or remote)
- **Git** (optional)
- **ODBC Driver 17 for SQL Server**

## 🚀 Installation and Setup

### 1. Clone the Repository

```bash
git clone https://github.com/karin2490/Kora_Api
cd Kora_Api
```

### 2. Create Virtual Environment

**Windows (Command Prompt):**
```bash
python -m venv env
env\Scripts\activate
```

**Windows (PowerShell):**
```bash
python -m venv env
.\env\Scripts\activate
```

**Windows (Git Bash):**
```bash
python -m venv env
source env/Scripts/activate
```

**macOS/Linux:**
```bash
python -m venv env
source env/bin/activate
```

### 3. Install Dependencies

With virtual environment activated (you should see `(env)` in your terminal):

```bash
pip install -r requirements.txt
```

Or manually:
```bash
pip install fastapi uvicorn pyodbc sqlalchemy python-dotenv python-jose passlib bcrypt
```

### 4. Setup Database

Execute the provided `CreateDB.sql` script in SQL Server Management Studio or your preferred tool to create tables and initial data.

**Initial data includes:**
- Roles: `student`, `teacher`, `admin`
- Sample subjects and programs
- Activity types

### 5. Configure Environment Variables

Create a `.env` file in the root directory:

```env
# Database Configuration
DB_SERVER=localhost
DB_NAME=Kora
DB_USER=sa
DB_PASSWORD=your_password
DB_DRIVER=ODBC Driver 17 for SQL Server

# JWT Configuration
JWT_SECRET_KEY=your-secret-key-here-change-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### 6. Verify Database Connection

```bash
python test_db.py
```

If successful, you'll see: ✅ Successful connection to SQL Server

### 7. Run the API

**Development mode (with auto-reload):**
```bash
uvicorn main:app --reload
```

**Production mode:**
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

**Additional options:**
- `--host 0.0.0.0` - Allow access from other machines on network
- `--port 8000` - Specify port (default is 8000)
- `--reload` - Auto-restart when detecting changes
- `--log-level debug` - Show detailed debug information

## 📚 API Access

Once the server is running, you can access:

- **API Base:** http://127.0.0.1:8000
- **Interactive Documentation (Swagger UI):** http://127.0.0.1:8000/docs
- **Alternative Documentation (ReDoc):** http://127.0.0.1:8000/redoc

## 🔧 Project Structure

```
Kora_Api/
├── env/                          # Virtual environment (don't commit)
├── conf/
│   └── database.py               # Database configuration
├── models/
│   ├── __init__.py               # Model exports
│   ├── actividades.py            # Activities model
│   ├── actividades_usuarios.py   # User activities model
│   ├── ejes.py                   # Axes model
│   ├── ejercicios.py             # Exercises model
│   ├── etapas.py                 # Stages model
│   ├── materias.py               # Subjects model
│   ├── programas.py              # Programs model
│   ├── roles.py                  # Roles model
│   ├── tipos_actividades.py      # Activity types model
│   └── usuarios.py               # Users model
├── routes/
│   ├── activity.py               # Activity endpoints
│   ├── activity_type.py          # Activity type endpoints
│   ├── auth.py                   # Authentication endpoints
│   ├── axis.py                   # Axis endpoints
│   ├── exercise.py               # Exercise endpoints
│   ├── program.py                # Program endpoints
│   ├── stage.py                  # Stage endpoints
│   ├── subject.py                # Subject endpoints
│   └── user_activities.py        # User activities endpoints
├── .env                          # Environment variables (don't commit)
├── .gitignore                    # Files ignored by Git
├── CreateDB.sql                  # Database schema
├── main.py                       # Application entry point
├── migrate_db_simple.py          # Database migration script
├── test_db.py                    # Database connection test
├── requirements.txt              # Project dependencies
└── README.md                     # This file
```

## 📝 Available Endpoints

### Authentication (`/auth`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/token` | Login and get JWT token |
| GET | `/auth/me` | Get current user info |

### Subjects (`/subjects`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/subjects` | List all subjects |
| GET | `/subjects/{id}` | Get specific subject |
| POST | `/subjects` | Create new subject |
| PUT | `/subjects/{id}` | Update subject |
| DELETE | `/subjects/{id}` | Delete subject |

**Query parameters:**
- `solo_activas` (bool): Filter active subjects only

### Programs (`/programs`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/programs` | List all programs |
| GET | `/programs/{id}` | Get specific program |
| POST | `/programs` | Create new program |
| PUT | `/programs/{id}` | Update program |
| DELETE | `/programs/{id}` | Delete program |

**Query parameters:**
- `materia_id` (int): Filter by subject
- `eje_id` (int): Filter by axis
- `solo_activos` (bool): Filter active programs only

### Activities (`/activities`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/activities` | List all activities |
| GET | `/activities/{id}` | Get specific activity |
| POST | `/activities` | Create new activity |
| PUT | `/activities/{id}` | Update activity |
| DELETE | `/activities/{id}` | Delete activity |

**Query parameters:**
- `etapa_id` (int): Filter by stage
- `tipo_id` (int): Filter by type
- `solo_activas` (bool): Filter active activities only

### User Activities (`/users/me/activities`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/users/me/activities` | Get all user activities |
| GET | `/users/me/activities/hoy` | Get today's activities (pending/in progress) |
| POST | `/users/me/activities` | Assign activity to user |
| PUT | `/users/me/activities/{id}` | Update activity progress |

**Activity states:**
- `pending`: Not started
- `in_progress`: Currently working on
- `completed`: Finished
- `abandoned`: Discontinued

### Axes (`/axes`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/axes` | List all axes |
| GET | `/axes/{id}` | Get specific axis |
| POST | `/axes` | Create new axis |
| PUT | `/axes/{id}` | Update axis |
| DELETE | `/axes/{id}` | Delete axis |

### Stages (`/stages`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/stages` | List all stages |
| GET | `/stages/{id}` | Get specific stage |
| POST | `/stages` | Create new stage |
| PUT | `/stages/{id}` | Update stage |
| DELETE | `/stages/{id}` | Delete stage |

### Activity Types (`/activity-types`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/activity-types` | List all activity types |
| GET | `/activity-types/{id}` | Get specific activity type |
| POST | `/activity-types` | Create new activity type |
| PUT | `/activity-types/{id}` | Update activity type |
| DELETE | `/activity-types/{id}` | Delete activity type |

### Exercises (`/exercises`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/exercises` | List all exercises |
| GET | `/exercises/{id}` | Get specific exercise |
| POST | `/exercises` | Create new exercise |
| PUT | `/exercises/{id}` | Update exercise |
| DELETE | `/exercises/{id}` | Delete exercise |

## 🔐 Authentication

The API uses JWT (JSON Web Tokens) for authentication.

### Login Flow

1. POST credentials to `/auth/token`
2. Receive JWT token in response
3. Include token in Authorization header: `Bearer <token>`
4. Token expires after 30 minutes (configurable)

### Example Login

```bash
curl -X POST "http://localhost:8000/auth/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=estudiante1&password=1234"
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "usuario": {
    "id": 1,
    "username": "estudiante1",
    "email": "estudiante1@kora.com",
    "rol": "student",
    "nombre": "Juan",
    "apellido": null
  }
}
```

### Protected Endpoints

All endpoints except `/auth/token` require authentication. Include the token:

```bash
curl -X GET "http://localhost:8000/subjects" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

## 🗄️ Database Schema

### Main Tables

- **roles**: User roles (student, teacher, admin)
- **usuarios**: User information and credentials
- **materias**: Subject areas
- **ejes**: Thematic axes (subdivisions of subjects)
- **programas**: Educational programs
- **etapas**: Program stages
- **tipos_actividades**: Activity type catalog
- **actividades**: Activity catalog
- **ejercicios**: Exercise details
- **actividades_usuarios**: User activity tracking and progress

### Key Relationships

- Users belong to one Role
- Programs belong to a Subject and optionally an Axis
- Stages belong to a Program
- Activities belong to a Stage and Activity Type
- User Activities track student progress on Activities

## 🐛 Common Issues and Solutions

### Error: "Table 'x' is already defined"

**Cause:** Duplicate or misnamed model
**Solution:** Verify each model has a unique class name

### Error: "Cannot import name 'router'"

**Cause:** Missing or misconfigured route file
**Solution:** Verify file exists and has `router = APIRouter()` defined

### Error: "Connection refused"

**Cause:** SQL Server not running or incorrect credentials
**Solution:** Verify SQL Server is active and credentials in `.env` are correct

### Error: "pyodbc.InterfaceError"

**Cause:** ODBC Driver not installed
**Solution:** Install [ODBC Driver 17 for SQL Server](https://docs.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server)

### PowerShell Script Execution Error

If PowerShell doesn't allow script execution:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Port 8000 in Use

```bash
# Use a different port
uvicorn main:app --reload --port 8001
```

## 🔒 Security Best Practices

- ✅ Never commit `.env` file to version control
- ✅ Change `JWT_SECRET_KEY` to a secure key in production
- ✅ Use different environment variables for development and production
- ✅ Configure CORS appropriately for production
- ✅ Use HTTPS in production
- ✅ Implement rate limiting for production
- ✅ Hash all passwords (already implemented with bcrypt)

## 🚀 Deployment

### Production Checklist

- [ ] Set strong `JWT_SECRET_KEY`
- [ ] Update CORS origins in `main.py`
- [ ] Use production database credentials
- [ ] Enable HTTPS
- [ ] Set up monitoring and logging
- [ ] Configure firewall rules
- [ ] Set up automatic backups

### Running with Gunicorn (Recommended for Production)

```bash
pip install gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## 📦 Dependencies

Main dependencies (see `requirements.txt` for complete list):

- **FastAPI**: Modern web framework
- **Uvicorn**: ASGI server
- **SQLAlchemy**: ORM for database
- **PyODBC**: SQL Server connector
- **Python-Jose**: JWT handling
- **Passlib & Bcrypt**: Password hashing
- **Python-Dotenv**: Environment variables

## 🤝 Contributing

1. Fork the project
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add: amazing feature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Coding Standards

- Use English for all code (variables, functions, comments)
- Use Spanish for user-facing text and database content
- Follow PEP 8 style guide
- Add docstrings to all functions
- Write meaningful commit messages

## 📄 License

This project is an educational application. See LICENSE file for details.

## 👥 Authors

Developed as an educational project for the Kora preschool learning system.

## 📞 Support

If you encounter issues or have questions:

1. Check the "Common Issues" section
2. Verify you have the correct Python and SQL Server versions
3. Check database connection and credentials
4. Review API documentation at `/docs`
5. Open an issue in the repository

---

**Last Updated**: February 2026
**Version**: 2.0.0
**API Status**: Production Ready
