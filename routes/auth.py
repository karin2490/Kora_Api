from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional
from pydantic import BaseModel, EmailStr, field_validator
from conf.database import get_db
from models.usuarios import Usuarios
from models.roles import Roles
import re
import secrets
import string
import os
import bcrypt
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuración de seguridad
SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

# Validar que SECRET_KEY esté configurado
if not SECRET_KEY:
    raise ValueError("JWT_SECRET_KEY no está configurado en las variables de entorno")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

router = APIRouter(
    prefix="/auth",
    tags=["autenticación"]
)

# Schemas Pydantic
class Token(BaseModel):
    access_token: str
    token_type: str
    usuario: dict

class UsuarioResponse(BaseModel):
    id: int
    username: str
    email: str
    nombre: str | None
    apellido: str | None
    rol: str
    activo: bool

class UsuarioCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    nombre: str | None = None
    apellido: str | None = None
    rol_id: int
    
    @field_validator('password')
    @classmethod
    def validar_password(cls, v):
        if len(v) < 8:
            raise ValueError('La contraseña debe tener al menos 8 caracteres')
        if not re.search(r'[A-Z]', v):
            raise ValueError('La contraseña debe contener al menos una letra mayúscula')
        if not re.search(r'[a-z]', v):
            raise ValueError('La contraseña debe contener al menos una letra minúscula')
        if not re.search(r'\d', v):
            raise ValueError('La contraseña debe contener al menos un número')
        if not re.search(r'[.?#*]', v):
            raise ValueError('La contraseña debe contener al menos un carácter especial: . ? # *')
        return v

class SolicitudResetPassword(BaseModel):
    email: EmailStr

class ResetPassword(BaseModel):
    email: EmailStr
    nueva_password: str
    
    @field_validator('nueva_password')
    @classmethod
    def validar_password(cls, v):
        if len(v) < 8:
            raise ValueError('La contraseña debe tener al menos 8 caracteres')
        if not re.search(r'[A-Z]', v):
            raise ValueError('La contraseña debe contener al menos una letra mayúscula')
        if not re.search(r'[a-z]', v):
            raise ValueError('La contraseña debe contener al menos una letra minúscula')
        if not re.search(r'\d', v):
            raise ValueError('La contraseña debe contener al menos un número')
        if not re.search(r'[.?#*]', v):
            raise ValueError('La contraseña debe contener al menos un carácter especial: . ? # *')
        return v

# Funciones auxiliares
def verificar_password(password_plano: str, password_hash: str) -> bool:
    """Verificar contraseña usando bcrypt directamente"""
    return bcrypt.checkpw(password_plano.encode('utf-8'), password_hash.encode('utf-8'))

def hashear_password(password: str) -> str:
    """Hashear contraseña usando bcrypt directamente"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def crear_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def obtener_usuario_por_username(db: Session, username: str):
    return db.query(Usuarios).filter(Usuarios.username == username).first()

def generar_password_temporal():
    """Genera una contraseña temporal que cumple con todos los requisitos"""
    # Asegurar que tiene al menos: 1 mayúscula, 1 minúscula, 1 número, 1 especial
    mayuscula = secrets.choice(string.ascii_uppercase)
    minuscula = secrets.choice(string.ascii_lowercase)
    numero = secrets.choice(string.digits)
    especial = secrets.choice('.?#*')
    
    # Completar con caracteres aleatorios hasta 12 caracteres
    otros_caracteres = ''.join(secrets.choice(string.ascii_letters + string.digits + '.?#*') for _ in range(8))
    
    # Mezclar todos los caracteres
    password = mayuscula + minuscula + numero + especial + otros_caracteres
    password_list = list(password)
    secrets.SystemRandom().shuffle(password_list)
    
    return ''.join(password_list)

# Endpoints
@router.post("/register", status_code=status.HTTP_201_CREATED)
def registrar_usuario(usuario: UsuarioCreate, db: Session = Depends(get_db)):
    # Verificar si el username ya existe
    existe_username = db.query(Usuarios).filter(Usuarios.username == usuario.username).first()
    if existe_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El nombre de usuario ya está registrado"
        )
    
    # Verificar si el email ya existe
    existe_email = db.query(Usuarios).filter(Usuarios.email == usuario.email).first()
    if existe_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El email ya está registrado"
        )
    
    # Verificar que el rol existe
    rol = db.query(Roles).filter(Roles.id == usuario.rol_id).first()
    if not rol:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Rol no válido"
        )
    
    # Crear usuario
    password_hash = hashear_password(usuario.password)
    db_usuario = Usuarios(
        username=usuario.username,
        email=usuario.email,
        password_hash=password_hash,
        nombre=usuario.nombre,
        apellido=usuario.apellido,
        rol_id=usuario.rol_id
    )
    
    db.add(db_usuario)
    db.commit()
    db.refresh(db_usuario)
    
    return {
        "id": db_usuario.id,
        "username": db_usuario.username,
        "email": db_usuario.email,
        "mensaje": "Usuario registrado exitosamente"
    }

@router.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    # Buscar usuario
    usuario = obtener_usuario_por_username(db, form_data.username)
    
    if not usuario or not verificar_password(form_data.password, usuario.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not usuario.activo:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario inactivo"
        )
    
    # Crear token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = crear_access_token(
        data={"sub": usuario.username}, 
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "usuario": {
            "id": usuario.id,
            "username": usuario.username,
            "email": usuario.email,
            "nombre": usuario.nombre,
            "apellido": usuario.apellido,
            "rol": usuario.rol.nombre
        }
    }

@router.get("/me", response_model=UsuarioResponse)
def obtener_usuario_actual(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    usuario = obtener_usuario_por_username(db, username)
    if usuario is None:
        raise credentials_exception
    
    return {
        "id": usuario.id,
        "username": usuario.username,
        "email": usuario.email,
        "nombre": usuario.nombre,
        "apellido": usuario.apellido,
        "rol": usuario.rol.nombre,
        "activo": usuario.activo
    }

@router.post("/forgot-password")
def solicitar_reset_password(
    solicitud: SolicitudResetPassword,
    db: Session = Depends(get_db)
):
    """
    Genera una contraseña temporal para el usuario.
    En producción, esto enviaría un email. 
    Por ahora, devuelve la contraseña temporal directamente.
    """
    # Buscar usuario por email
    usuario = db.query(Usuarios).filter(Usuarios.email == solicitud.email).first()
    
    if not usuario:
        # Por seguridad, no revelamos si el email existe o no
        return {
            "mensaje": "Si el email existe, recibirás instrucciones para resetear tu contraseña",
            "nota": "En desarrollo: Si el email no existe, no se hace nada"
        }
    
    if not usuario.activo:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario inactivo"
        )
    
    # Generar contraseña temporal
    password_temporal = generar_password_temporal()
    
    # Actualizar la contraseña del usuario
    usuario.password_hash = hashear_password(password_temporal)
    usuario.fecha_actualizacion = datetime.now()
    db.commit()
    
    # En producción, aquí se enviaría un email con la contraseña temporal
    # Por ahora, la devolvemos directamente (SOLO PARA DESARROLLO)
    return {
        "mensaje": "Contraseña temporal generada exitosamente",
        "email": usuario.email,
        "password_temporal": password_temporal,
        "nota": "⚠️ SOLO DESARROLLO: En producción esto se enviaría por email y no se mostraría aquí",
        "instrucciones": "Usa esta contraseña temporal para iniciar sesión y luego cámbiala"
    }

@router.post("/reset-password")
def resetear_password(
    reset: ResetPassword,
    db: Session = Depends(get_db)
):
    """
    Permite al usuario establecer una nueva contraseña
    """
    # Buscar usuario por email
    usuario = db.query(Usuarios).filter(Usuarios.email == reset.email).first()
    
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    if not usuario.activo:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario inactivo"
        )
    
    # Actualizar la contraseña
    usuario.password_hash = hashear_password(reset.nueva_password)
    usuario.fecha_actualizacion = datetime.now()
    db.commit()
    
    return {
        "mensaje": "Contraseña actualizada exitosamente",
        "email": usuario.email
    }

@router.put("/change-password")
def cambiar_password(
    password_actual: str,
    password_nueva: str,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """
    Permite al usuario cambiar su contraseña cuando está autenticado
    """
    # Verificar token y obtener usuario
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    usuario = obtener_usuario_por_username(db, username)
    if usuario is None:
        raise credentials_exception
    
    # Verificar contraseña actual
    if not verificar_password(password_actual, usuario.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Contraseña actual incorrecta"
        )
    
    # Validar nueva contraseña
    if len(password_nueva) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La contraseña debe tener al menos 8 caracteres"
        )
    if not re.search(r'[A-Z]', password_nueva):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La contraseña debe contener al menos una letra mayúscula"
        )
    if not re.search(r'[a-z]', password_nueva):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La contraseña debe contener al menos una letra minúscula"
        )
    if not re.search(r'\d', password_nueva):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La contraseña debe contener al menos un número"
        )
    if not re.search(r'[.?#*]', password_nueva):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La contraseña debe contener al menos un carácter especial: . ? # *"
        )
    
    # Actualizar contraseña
    usuario.password_hash = hashear_password(password_nueva)
    usuario.fecha_actualizacion = datetime.now()
    db.commit()
    
    return {
        "mensaje": "Contraseña actualizada exitosamente"
    }