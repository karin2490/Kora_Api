from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from conf.database import get_db
from models.etapas import Etapas
from pydantic import BaseModel
from datetime import datetime

class EtapaBase(BaseModel):
    programa_id: int
    numero_etapa: int
    nombre: str
    prerrequisitos: str | None = None
    contenido: str | None = None
    objetivos: str | None = None
    evaluacion: str | None = None
    orden_secuencial: int | None = None
    activa: bool = True

class EtapaCreate(EtapaBase):
    pass

class EtapaUpdate(BaseModel):
    nombre: str | None = None
    prerrequisitos: str | None = None
    contenido: str | None = None
    objetivos: str | None = None
    evaluacion: str | None = None
    orden_secuencial: int | None = None
    activa: bool | None = None

router = APIRouter(
    prefix="/stages",
    tags=["etapas"]
)

@router.get("/")
def get_etapas(
    programa_id: int | None = None,
    solo_activas: bool = True,
    db: Session = Depends(get_db)
):
    query = db.query(Etapas).options(joinedload(Etapas.programa))
    
    if solo_activas:
        query = query.filter(Etapas.activa == True)
    if programa_id:
        query = query.filter(Etapas.programa_id == programa_id)
    
    return query.order_by(Etapas.orden_secuencial).all()

@router.get("/{etapa_id}")
def get_etapa(etapa_id: int, db: Session = Depends(get_db)):
    etapa = db.query(Etapas)\
        .options(joinedload(Etapas.programa))\
        .filter(Etapas.id == etapa_id).first()
    
    if not etapa:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Etapa no encontrada"
        )
    return etapa

@router.get("/programa/{programa_id}")
def get_etapas_por_programa(
    programa_id: int,
    db: Session = Depends(get_db)
):
    etapas = db.query(Etapas)\
        .filter(Etapas.programa_id == programa_id)\
        .order_by(Etapas.numero_etapa)\
        .all()
    return etapas

@router.post("/", status_code=status.HTTP_201_CREATED)
def create_etapa(etapa: EtapaCreate, db: Session = Depends(get_db)):
    # Verificar que no existe otra etapa con el mismo número en el programa
    existe = db.query(Etapas).filter(
        Etapas.programa_id == etapa.programa_id,
        Etapas.numero_etapa == etapa.numero_etapa
    ).first()
    
    if existe:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe una etapa con ese número en este programa"
        )
    
    db_etapa = Etapas(**etapa.dict())
    db.add(db_etapa)
    db.commit()
    db.refresh(db_etapa)
    return db_etapa

@router.put("/{etapa_id}")
def update_etapa(
    etapa_id: int,
    etapa: EtapaUpdate,
    db: Session = Depends(get_db)
):
    db_etapa = db.query(Etapas).filter(Etapas.id == etapa_id).first()
    if not db_etapa:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Etapa no encontrada"
        )
    
    for key, value in etapa.dict(exclude_unset=True).items():
        setattr(db_etapa, key, value)
    
    db_etapa.fecha_actualizacion = datetime.now()
    db.commit()
    db.refresh(db_etapa)
    return db_etapa

@router.delete("/{etapa_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_etapa(etapa_id: int, db: Session = Depends(get_db)):
    etapa = db.query(Etapas).filter(Etapas.id == etapa_id).first()
    if not etapa:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Etapa no encontrada"
        )
    
    db.delete(etapa)
    db.commit()