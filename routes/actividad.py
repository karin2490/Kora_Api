from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from conf.database import get_db
from models.actividades import Actividades
from pydantic import BaseModel
from datetime import datetime

class ActividadBase(BaseModel):
    etapa_id: int
    tipo_actividad_id: int
    nombre: str
    descripcion: str | None = None
    instrucciones: str | None = None
    tiempo_estimado: int | None = None
    orden_secuencial: int | None = None
    activa: bool = True

class ActividadCreate(ActividadBase):
    pass

class ActividadUpdate(BaseModel):
    nombre: str | None = None
    descripcion: str | None = None
    instrucciones: str | None = None
    tiempo_estimado: int | None = None
    orden_secuencial: int | None = None
    activa: bool | None = None

router = APIRouter(
    prefix="/actividades",
    tags=["actividades"]
)

@router.get("/")
def get_actividades(
    etapa_id: int | None = None,
    tipo_id: int | None = None,
    solo_activas: bool = True,
    db: Session = Depends(get_db)
):
    query = db.query(Actividades)\
        .options(joinedload(Actividades.etapa))\
        .options(joinedload(Actividades.tipo_actividad))
    
    if solo_activas:
        query = query.filter(Actividades.activa == True)
    if etapa_id:
        query = query.filter(Actividades.etapa_id == etapa_id)
    if tipo_id:
        query = query.filter(Actividades.tipo_actividad_id == tipo_id)
    
    return query.order_by(Actividades.orden_secuencial).all()

@router.get("/{actividad_id}")
def get_actividad(actividad_id: int, db: Session = Depends(get_db)):
    actividad = db.query(Actividades)\
        .options(joinedload(Actividades.etapa))\
        .options(joinedload(Actividades.tipo_actividad))\
        .filter(Actividades.id == actividad_id).first()
    
    if not actividad:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Actividad no encontrada"
        )
    return actividad

@router.post("/", status_code=status.HTTP_201_CREATED)
def create_actividad(actividad: ActividadCreate, db: Session = Depends(get_db)):
    db_actividad = Actividades(**actividad.dict())
    db.add(db_actividad)
    db.commit()
    db.refresh(db_actividad)
    return db_actividad

@router.put("/{actividad_id}")
def update_actividad(
    actividad_id: int,
    actividad: ActividadUpdate,
    db: Session = Depends(get_db)
):
    db_actividad = db.query(Actividades).filter(Actividades.id == actividad_id).first()
    if not db_actividad:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Actividad no encontrada"
        )
    
    for key, value in actividad.dict(exclude_unset=True).items():
        setattr(db_actividad, key, value)
    
    db_actividad.fecha_actualizacion = datetime.now()
    db.commit()
    db.refresh(db_actividad)
    return db_actividad

@router.delete("/{actividad_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_actividad(actividad_id: int, db: Session = Depends(get_db)):
    actividad = db.query(Actividades).filter(Actividades.id == actividad_id).first()
    if not actividad:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Actividad no encontrada"
        )
    
    db.delete(actividad)
    db.commit()