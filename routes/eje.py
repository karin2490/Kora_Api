from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from conf.database import get_db
from models.ejes import Ejes
from pydantic import BaseModel

class EjeBase(BaseModel):
    codigo: str
    nombre: str
    descripcion: str | None = None

class EjeCreate(EjeBase):
    pass

class EjeUpdate(BaseModel):
    nombre: str | None = None
    descripcion: str | None = None

router = APIRouter(
    prefix="/ejes",
    tags=["ejes"]
)

@router.get("/")
def get_ejes(db: Session = Depends(get_db)):
    return db.query(Ejes).all()

@router.get("/{eje_id}")
def get_eje(eje_id: int, db: Session = Depends(get_db)):
    eje = db.query(Ejes).filter(Ejes.id == eje_id).first()
    if not eje:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Eje no encontrado"
        )
    return eje

@router.get("/codigo/{codigo}")
def get_eje_por_codigo(codigo: str, db: Session = Depends(get_db)):
    eje = db.query(Ejes).filter(Ejes.codigo == codigo).first()
    if not eje:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Eje no encontrado"
        )
    return eje

@router.post("/", status_code=status.HTTP_201_CREATED)
def create_eje(eje: EjeCreate, db: Session = Depends(get_db)):
    # Verificar código único
    existe = db.query(Ejes).filter(Ejes.codigo == eje.codigo).first()
    if existe:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe un eje con ese código"
        )
    
    db_eje = Ejes(**eje.dict())
    db.add(db_eje)
    db.commit()
    db.refresh(db_eje)
    return db_eje

@router.put("/{eje_id}")
def update_eje(eje_id: int, eje: EjeUpdate, db: Session = Depends(get_db)):
    db_eje = db.query(Ejes).filter(Ejes.id == eje_id).first()
    if not db_eje:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Eje no encontrado"
        )
    
    for key, value in eje.dict(exclude_unset=True).items():
        setattr(db_eje, key, value)
    
    db.commit()
    db.refresh(db_eje)
    return db_eje

@router.delete("/{eje_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_eje(eje_id: int, db: Session = Depends(get_db)):
    eje = db.query(Ejes).filter(Ejes.id == eje_id).first()
    if not eje:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Eje no encontrado"
        )
    
    db.delete(eje)
    db.commit()