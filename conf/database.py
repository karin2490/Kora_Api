from sqlalchemy import create_engine, text 
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv
from pathlib import Path

# Cargar variables de entorno
# Subir un nivel desde conf/ para llegar a la raíz
env_path = Path(__file__).parent.parent / '.env'
load_dotenv()

# Configuración de la base de datos
DB_SERVER = os.getenv("DB_SERVER")
DB_DATABASE = os.getenv("DB_DATABASE") 
DB_USERNAME = os.getenv("DB_USERNAME")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_DRIVER = os.getenv("DB_DRIVER")

# Verificar que las variables se cargaron
if not all([DB_SERVER, DB_DATABASE, DB_USERNAME, DB_PASSWORD, DB_DRIVER]):
    print("❌ Error: No se pudieron cargar todas las variables de entorno")
    print(f"DB_SERVER: {DB_SERVER}")
    print(f"DB_DATABASE: {DB_DATABASE}")
    print(f"DB_USERNAME: {DB_USERNAME}")
    print(f"DB_PASSWORD: {'***' if DB_PASSWORD else None}")
    print(f"DB_DRIVER: {DB_DRIVER}")
    raise ValueError("Faltan variables de entorno. Verifica tu archivo .env")

# String de conexión para SQL Server
DATABASE_URL = f"mssql+pyodbc://{DB_USERNAME}:{DB_PASSWORD}@{DB_SERVER}/{DB_DATABASE}?driver={DB_DRIVER.replace(' ', '+')}"

print(f"Conectando a: {DATABASE_URL}")  # Para debug

# Crear el engine de SQLAlchemy
engine = create_engine(
    DATABASE_URL,
    echo=True,  # Para ver las queries SQL en consola (debug)
    pool_pre_ping=True,  # Verificar conexiones antes de usarlas
)

# Crear SessionLocal
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para los modelos
Base = declarative_base()

# Dependency para obtener la sesión de BD
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Función para probar la conexión
def test_connection():
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            print("✅ Conexión exitosa a SQL Server")
            return True
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return False