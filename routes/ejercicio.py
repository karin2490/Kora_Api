from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from conf.database import get_db
from models.ejercicios import Ejercicios
from pydantic import BaseModel
import json
from datetime import datetime

class EjercicioBase(BaseModel):
    actividad_id: int
    nombre: str
    enunciado: str | None = None
    tipo_respuesta: str = "opcion_multiple"
    contenido_ejercicio: dict | None = None  # Recibe como dict, se guarda como JSON
    puntuacion_maxima: int = 100
    tiempo_limite: int | None = None
    orden_secuencial: int | None = None
    activo: bool = True

class EjercicioCreate(EjercicioBase):
    pass

class EjercicioUpdate(BaseModel):
    nombre: str | None = None
    enunciado: str | None = None
    tipo_respuesta: str | None = None
    contenido_ejercicio: dict | None = None
    puntuacion_maxima: int | None = None
    tiempo_limite: int | None = None
    orden_secuencial: int | None = None
    activo: bool | None = None

router = APIRouter(
    prefix="/ejercicios",
    tags=["ejercicios"]
)

@router.get("/")
def get_ejercicios(
    actividad_id: int | None = None,
    tipo_respuesta: str | None = None,
    solo_activos: bool = True,
    db: Session = Depends(get_db)
):
    # query = db.query(Ejercicios).options(joinedload(Ejercicios.actividad))
    query = db.query(Ejercicios)  # Sin joinedload por ahora
    
    if solo_activos:
        query = query.filter(Ejercicios.activo == True)
    if actividad_id:
        query = query.filter(Ejercicios.actividad_id == actividad_id)
    if tipo_respuesta:
        query = query.filter(Ejercicios.tipo_respuesta == tipo_respuesta)
    
    ejercicios = query.order_by(Ejercicios.orden_secuencial).all()
    
    # Parsear JSON del contenido
    for ejercicio in ejercicios:
        if ejercicio.contenido_ejercicio:
            try:
                ejercicio.contenido_ejercicio = json.loads(ejercicio.contenido_ejercicio)
            except:
                pass
    
    return ejercicios

@router.get("/{ejercicio_id}")
def get_ejercicio(ejercicio_id: int, db: Session = Depends(get_db)):
    ejercicio = db.query(Ejercicios)\
        .options(joinedload(Ejercicios.actividad))\
        .filter(Ejercicios.id == ejercicio_id).first()
    
    if not ejercicio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ejercicio no encontrado"
        )
    
    # Parsear JSON del contenido
    if ejercicio.contenido_ejercicio:
        try:
            ejercicio.contenido_ejercicio = json.loads(ejercicio.contenido_ejercicio)
        except:
            pass
    
    return ejercicio

@router.post("/", status_code=status.HTTP_201_CREATED)
def create_ejercicio(ejercicio: EjercicioCreate, db: Session = Depends(get_db)):
    # Validar tipo_respuesta
    tipos_validos = ['opcion_multiple', 'texto_libre', 'verdadero_falso', 'ordenamiento', 'clasificacion']
    if ejercicio.tipo_respuesta not in tipos_validos:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Tipo de respuesta inválido. Debe ser uno de: {tipos_validos}"
        )
    
    # Convertir dict a JSON string
    ejercicio_dict = ejercicio.dict()
    if ejercicio_dict.get('contenido_ejercicio'):
        ejercicio_dict['contenido_ejercicio'] = json.dumps(ejercicio_dict['contenido_ejercicio'])
    
    db_ejercicio = Ejercicios(**ejercicio_dict)
    db.add(db_ejercicio)
    db.commit()
    db.refresh(db_ejercicio)
    
    # Parsear de vuelta para la respuesta
    if db_ejercicio.contenido_ejercicio:
        db_ejercicio.contenido_ejercicio = json.loads(db_ejercicio.contenido_ejercicio)
    
    return db_ejercicio

@router.put("/{ejercicio_id}")
def update_ejercicio(
    ejercicio_id: int,
    ejercicio: EjercicioUpdate,
    db: Session = Depends(get_db)
):
    db_ejercicio = db.query(Ejercicios).filter(Ejercicios.id == ejercicio_id).first()
    if not db_ejercicio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ejercicio no encontrado"
        )
    
    update_data = ejercicio.dict(exclude_unset=True)
    
    # Convertir contenido a JSON si está presente
    if 'contenido_ejercicio' in update_data and update_data['contenido_ejercicio']:
        update_data['contenido_ejercicio'] = json.dumps(update_data['contenido_ejercicio'])
    
    for key, value in update_data.items():
        setattr(db_ejercicio, key, value)
    
    db_ejercicio.fecha_actualizacion = datetime.now()
    db.commit()
    db.refresh(db_ejercicio)
    
    # Parsear de vuelta para la respuesta
    if db_ejercicio.contenido_ejercicio:
        try:
            db_ejercicio.contenido_ejercicio = json.loads(db_ejercicio.contenido_ejercicio)
        except:
            pass
    
    return db_ejercicio

@router.delete("/{ejercicio_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_ejercicio(ejercicio_id: int, db: Session = Depends(get_db)):
    ejercicio = db.query(Ejercicios).filter(Ejercicios.id == ejercicio_id).first()
    if not ejercicio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ejercicio no encontrado"
        )
    
    db.delete(ejercicio)
    db.commit()