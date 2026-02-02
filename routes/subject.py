from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from conf.database import get_db
from models.materias import Materias
from pydantic import BaseModel
from datetime import datetime

# Schemas Pydantic para validación
class MateriaBase(BaseModel):
    nombre: str
    descripcion: str | None = None
    activa: bool = True

class MateriaCreate(MateriaBase):
    pass

class MateriaUpdate(BaseModel):
    nombre: str | None = None
    descripcion: str | None = None
    activa: bool | None = None

router = APIRouter(
    prefix="/subjects",
    tags=["materias"]
)


@router.get("/")
def get_materias(
    skip: int = 0, 
    limit: int = 100,
    solo_activas: bool = True,
    db: Session = Depends(get_db)
):
    query = db.query(Materias)
    if solo_activas:
        query = query.filter(Materias.activa == True)
    return query.order_by(Materias.id).offset(skip).limit(limit).all()

@router.get("/{materia_id}")
def get_materia(materia_id: int, db: Session = Depends(get_db)):
    materia = db.query(Materias).filter(Materias.id == materia_id).first()
    if not materia:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Materia no encontrada"
        )
    return materia

@router.post("/", status_code=status.HTTP_201_CREATED)
def create_materia(materia: MateriaCreate, db: Session = Depends(get_db)):
    # Verificar si ya existe
    existe = db.query(Materias).filter(Materias.nombre == materia.nombre).first()
    if existe:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe una materia con ese nombre"
        )
    
    db_materia = Materias(**materia.dict())
    db.add(db_materia)
    db.commit()
    db.refresh(db_materia)
    return db_materia

@router.put("/{materia_id}")
def update_materia(
    materia_id: int, 
    materia: MateriaUpdate, 
    db: Session = Depends(get_db)
):
    db_materia = db.query(Materias).filter(Materias.id == materia_id).first()
    if not db_materia:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Materia no encontrada"
        )
    
    for key, value in materia.dict(exclude_unset=True).items():
        setattr(db_materia, key, value)
    
    db_materia.fecha_actualizacion = datetime.now()
    db.commit()
    db.refresh(db_materia)
    return db_materia

@router.delete("/{materia_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_materia(materia_id: int, db: Session = Depends(get_db)):
    materia = db.query(Materias).filter(Materias.id == materia_id).first()
    if not materia:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Materia no encontrada"
        )
    
    db.delete(materia)
    db.commit()
