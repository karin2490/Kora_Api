from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from conf.database import get_db
from models.actividades_usuarios import ActividadesUsuarios
from models.actividades import Actividades
from models.usuarios import Usuarios
from routes.auth import oauth2_scheme
from jose import JWTError, jwt
from pydantic import BaseModel
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()
SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")

class ActividadUsuarioResponse(BaseModel):
    id: int
    usuario_id: int
    actividad_id: int
    estado: str
    fecha_inicio: datetime | None
    fecha_completado: datetime | None
    progreso_porcentaje: float
    tiempo_dedicado: int | None
    intentos: int
    actividad: dict | None

class ActividadUsuarioCreate(BaseModel):
    actividad_id: int
    estado: str = 'pending'

class ActividadUsuarioUpdate(BaseModel):
    estado: str | None = None
    progreso_porcentaje: float | None = None
    tiempo_dedicado: int | None = None

router = APIRouter(
    prefix="/usuarios",
    tags=["actividades-usuarios"]
)

def obtener_usuario_actual(token: str, db: Session):
    """Helper para obtener el usuario del token"""
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

    usuario = db.query(Usuarios).filter(Usuarios.username == username).first()
    if usuario is None:
        raise credentials_exception
    return usuario

@router.get("/me/actividades")
def obtener_mis_actividades(
    estado: str | None = None,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """Obtiene todas las actividades del usuario autenticado"""
    usuario = obtener_usuario_actual(token, db)

    query = db.query(ActividadesUsuarios)\
        .options(joinedload(ActividadesUsuarios.actividad).joinedload(Actividades.tipo_actividad))\
        .filter(ActividadesUsuarios.usuario_id == usuario.id)

    if estado:
        query = query.filter(ActividadesUsuarios.estado == estado)

    actividades_usuario = query.order_by(ActividadesUsuarios.fecha_creacion.desc()).all()

    # Formatear respuesta
    resultado = []
    for act_usuario in actividades_usuario:
        resultado.append({
            "id": act_usuario.id,
            "usuario_id": act_usuario.usuario_id,
            "actividad_id": act_usuario.actividad_id,
            "estado": act_usuario.estado,
            "fecha_inicio": act_usuario.fecha_inicio,
            "fecha_completado": act_usuario.fecha_completado,
            "progreso_porcentaje": float(act_usuario.progreso_porcentaje) if act_usuario.progreso_porcentaje else 0.0,
            "tiempo_dedicado": act_usuario.tiempo_dedicado,
            "intentos": act_usuario.intentos,
            "actividad": {
                "id": act_usuario.actividad.id,
                "nombre": act_usuario.actividad.nombre,
                "descripcion": act_usuario.actividad.descripcion,
                "instrucciones": act_usuario.actividad.instrucciones,
                "tiempo_estimado": act_usuario.actividad.tiempo_estimado,
                "tipo_actividad": {
                    "id": act_usuario.actividad.tipo_actividad.id,
                    "nombre": act_usuario.actividad.tipo_actividad.nombre,
                    "icono": act_usuario.actividad.tipo_actividad.icono
                } if act_usuario.actividad.tipo_actividad else None
            } if act_usuario.actividad else None
        })

    return resultado

@router.get("/me/actividades/hoy")
def obtener_actividades_hoy(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """Obtiene las actividades pendientes o en progreso del usuario (actividades de hoy)"""
    usuario = obtener_usuario_actual(token, db)

    actividades_hoy = db.query(ActividadesUsuarios)\
        .options(joinedload(ActividadesUsuarios.actividad).joinedload(Actividades.tipo_actividad))\
        .filter(
            ActividadesUsuarios.usuario_id == usuario.id,
            ActividadesUsuarios.estado.in_(['pending', 'in_progress'])
        )\
        .order_by(ActividadesUsuarios.fecha_creacion)\
        .limit(5)\
        .all()

    # Formatear respuesta
    resultado = []
    for act_usuario in actividades_hoy:
        resultado.append({
            "id": act_usuario.id,
            "usuario_id": act_usuario.usuario_id,
            "actividad_id": act_usuario.actividad_id,
            "estado": act_usuario.estado,
            "fecha_inicio": act_usuario.fecha_inicio,
            "fecha_completado": act_usuario.fecha_completado,
            "progreso_porcentaje": float(act_usuario.progreso_porcentaje) if act_usuario.progreso_porcentaje else 0.0,
            "tiempo_dedicado": act_usuario.tiempo_dedicado,
            "intentos": act_usuario.intentos,
            "actividad": {
                "id": act_usuario.actividad.id,
                "nombre": act_usuario.actividad.nombre,
                "descripcion": act_usuario.actividad.descripcion,
                "instrucciones": act_usuario.actividad.instrucciones,
                "tiempo_estimado": act_usuario.actividad.tiempo_estimado,
                "tipo_actividad": {
                    "id": act_usuario.actividad.tipo_actividad.id,
                    "nombre": act_usuario.actividad.tipo_actividad.nombre,
                    "icono": act_usuario.actividad.tipo_actividad.icono
                } if act_usuario.actividad.tipo_actividad else None
            } if act_usuario.actividad else None
        })

    return resultado

@router.post("/me/actividades", status_code=status.HTTP_201_CREATED)
def asignar_actividad(
    actividad_data: ActividadUsuarioCreate,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """Asigna una nueva actividad al usuario autenticado"""
    usuario = obtener_usuario_actual(token, db)

    # Verificar que la actividad existe
    actividad = db.query(Actividades).filter(Actividades.id == actividad_data.actividad_id).first()
    if not actividad:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Actividad no encontrada"
        )

    # Verificar si ya existe
    existe = db.query(ActividadesUsuarios).filter(
        ActividadesUsuarios.usuario_id == usuario.id,
        ActividadesUsuarios.actividad_id == actividad_data.actividad_id
    ).first()

    if existe:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Esta actividad ya está asignada al usuario"
        )

    # Crear registro
    nueva_actividad_usuario = ActividadesUsuarios(
        usuario_id=usuario.id,
        actividad_id=actividad_data.actividad_id,
        estado=actividad_data.estado
    )

    db.add(nueva_actividad_usuario)
    db.commit()
    db.refresh(nueva_actividad_usuario)

    return {
        "id": nueva_actividad_usuario.id,
        "mensaje": "Actividad asignada exitosamente"
    }

@router.put("/me/actividades/{actividad_usuario_id}")
def actualizar_mi_actividad(
    actividad_usuario_id: int,
    actividad_data: ActividadUsuarioUpdate,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """Actualiza el estado/progreso de una actividad del usuario"""
    usuario = obtener_usuario_actual(token, db)

    actividad_usuario = db.query(ActividadesUsuarios).filter(
        ActividadesUsuarios.id == actividad_usuario_id,
        ActividadesUsuarios.usuario_id == usuario.id
    ).first()

    if not actividad_usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Actividad no encontrada o no pertenece al usuario"
        )

    # Actualizar campos
    if actividad_data.estado:
        actividad_usuario.estado = actividad_data.estado
        if actividad_data.estado == 'in_progress' and not actividad_usuario.fecha_inicio:
            actividad_usuario.fecha_inicio = datetime.now()
        elif actividad_data.estado == 'completed':
            actividad_usuario.fecha_completado = datetime.now()
            actividad_usuario.progreso_porcentaje = 100.0

    if actividad_data.progreso_porcentaje is not None:
        actividad_usuario.progreso_porcentaje = actividad_data.progreso_porcentaje

    if actividad_data.tiempo_dedicado is not None:
        actividad_usuario.tiempo_dedicado = actividad_data.tiempo_dedicado

    actividad_usuario.fecha_actualizacion = datetime.now()
    db.commit()
    db.refresh(actividad_usuario)

    return {
        "id": actividad_usuario.id,
        "estado": actividad_usuario.estado,
        "progreso_porcentaje": float(actividad_usuario.progreso_porcentaje) if actividad_usuario.progreso_porcentaje else 0.0,
        "mensaje": "Actividad actualizada exitosamente"
    }
