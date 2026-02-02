from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from conf.database import get_db
from models.programas import Programas
from models.prerrequisitos import PrerrequisitosPrograma
from pydantic import BaseModel
from datetime import datetime

class ProgramaBase(BaseModel):
    materia_id: int
    eje_id: int | None = None
    nombre: str
    nombre_comercial: str | None = None
    grado_inicio: str | None = None
    grado_fin: str | None = None
    descripcion_breve: str | None = None
    prerrequisitos: str | None = None
    activo: bool = True
    orden_secuencial: int | None = None

class ProgramaCreate(ProgramaBase):
    pass

class ProgramaUpdate(BaseModel):
    nombre: str | None = None
    nombre_comercial: str | None = None
    grado_inicio: str | None = None
    grado_fin: str | None = None
    descripcion_breve: str | None = None
    prerrequisitos: str | None = None
    activo: bool | None = None
    orden_secuencial: int | None = None

router = APIRouter(
    prefix="/programas",
    tags=["programas"]
)

@router.get("/")
def get_programas(
    skip: int = 0,
    limit: int = 100,
    materia_id: int | None = None,
    eje_id: int | None = None,
    solo_activos: bool = True,
    db: Session = Depends(get_db)
):
    query = db.query(Programas)\
        .options(joinedload(Programas.materia))\
        .options(joinedload(Programas.eje))
    
    if solo_activos:
        query = query.filter(Programas.activo == True)
    if materia_id:
        query = query.filter(Programas.materia_id == materia_id)
    if eje_id:
        query = query.filter(Programas.eje_id == eje_id)
    
    return query.order_by(Programas.orden_secuencial).offset(skip).limit(limit).all()

@router.get("/{programa_id}")
def get_programa(programa_id: int, db: Session = Depends(get_db)):
    programa = db.query(Programas)\
        .options(joinedload(Programas.materia))\
        .options(joinedload(Programas.eje))\
        .filter(Programas.id == programa_id).first()
    
    if not programa:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Programa no encontrado"
        )
    return programa

@router.get("/{programa_id}/prerrequisitos")
def get_prerrequisitos_programa(programa_id: int, db: Session = Depends(get_db)):
    prerrequisitos = db.query(PrerrequisitosPrograma)\
        .filter(PrerrequisitosPrograma.programa_id == programa_id)\
        .all()
    return prerrequisitos

@router.post("/", status_code=status.HTTP_201_CREATED)
def create_programa(programa: ProgramaCreate, db: Session = Depends(get_db)):
    db_programa = Programas(**programa.dict())
    db.add(db_programa)
    db.commit()
    db.refresh(db_programa)
    return db_programa

@router.post("/{programa_id}/prerrequisitos/{prerrequisito_id}")
def add_prerrequisito(
    programa_id: int,
    prerrequisito_id: int,
    obligatorio: bool = True,
    db: Session = Depends(get_db)
):
    # Verificar que ambos programas existen
    programa = db.query(Programas).filter(Programas.id == programa_id).first()
    prerrequisito = db.query(Programas).filter(Programas.id == prerrequisito_id).first()
    
    if not programa or not prerrequisito:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Programa no encontrado"
        )
    
    # Verificar que no existe ya
    existe = db.query(PrerrequisitosPrograma).filter(
        PrerrequisitosPrograma.programa_id == programa_id,
        PrerrequisitosPrograma.prerrequisito_programa_id == prerrequisito_id
    ).first()
    
    if existe:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Este prerrequisito ya existe"
        )
    
    nuevo_prereq = PrerrequisitosPrograma(
        programa_id=programa_id,
        prerrequisito_programa_id=prerrequisito_id,
        obligatorio=obligatorio
    )
    
    db.add(nuevo_prereq)
    db.commit()
    return {"message": "Prerrequisito agregado exitosamente"}

@router.put("/{programa_id}")
def update_programa(
    programa_id: int,
    programa: ProgramaUpdate,
    db: Session = Depends(get_db)
):
    db_programa = db.query(Programas).filter(Programas.id == programa_id).first()
    if not db_programa:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Programa no encontrado"
        )
    
    for key, value in programa.dict(exclude_unset=True).items():
        setattr(db_programa, key, value)
    
    db_programa.fecha_actualizacion = datetime.now()
    db.commit()
    db.refresh(db_programa)
    return db_programa

@router.delete("/{programa_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_programa(programa_id: int, db: Session = Depends(get_db)):
    programa = db.query(Programas).filter(Programas.id == programa_id).first()
    if not programa:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Programa no encontrado"
        )
    
    db.delete(programa)
    db.commit()