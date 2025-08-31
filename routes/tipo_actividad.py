from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from conf.database import get_db
from models.tipos_actividades import TiposActividades
from pydantic import BaseModel

class TipoActividadBase(BaseModel):
    nombre: str
    descripcion: str | None = None

class TipoActividadCreate(TipoActividadBase):
    pass

router = APIRouter(
    prefix="/tipos-actividades",
    tags=["tipos de actividades"]
)

@router.get("/")
def get_tipos_actividades(db: Session = Depends(get_db)):
    return db.query(TiposActividades).all()

@router.get("/{tipo_id}")
def get_tipo_actividad(tipo_id: int, db: Session = Depends(get_db)):
    tipo = db.query(TiposActividades).filter(TiposActividades.id == tipo_id).first()
    if not tipo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tipo de actividad no encontrado"
        )
    return tipo

@router.post("/", status_code=status.HTTP_201_CREATED)
def create_tipo_actividad(tipo: TipoActividadCreate, db: Session = Depends(get_db)):
    # Verificar nombre único
    existe = db.query(TiposActividades).filter(TiposActividades.nombre == tipo.nombre).first()
    if existe:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe un tipo de actividad con ese nombre"
        )
    
    db_tipo = TiposActividades(**tipo.dict())
    db.add(db_tipo)
    db.commit()
    db.refresh(db_tipo)
    return db_tipo

@router.delete("/{tipo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_tipo_actividad(tipo_id: int, db: Session = Depends(get_db)):
    tipo = db.query(TiposActividades).filter(TiposActividades.id == tipo_id).first()
    if not tipo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tipo de actividad no encontrado"
        )
    
    db.delete(tipo)
    db.commit()