from sqlalchemy import String, Integer, Column, DateTime, Boolean, Text, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from conf.database import Base
from datetime import datetime

class Etapas(Base):
    __tablename__ = "etapas"
    __table_args__ = (
        UniqueConstraint('programa_id', 'numero_etapa', name='UQ_etapas_programa_numero'),
    )
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    programa_id = Column(Integer, ForeignKey("programas.id", ondelete="CASCADE"), nullable=False)
    numero_etapa = Column(Integer, nullable=False)
    nombre = Column(String(100), nullable=False)
    prerrequisitos = Column(Text, nullable=True)
    contenido = Column(Text, nullable=True)
    objetivos = Column(Text, nullable=True)
    evaluacion = Column(Text, nullable=True)
    orden_secuencial = Column(Integer, nullable=True)
    activa = Column(Boolean, default=True)
    fecha_creacion = Column(DateTime, default=datetime.now)
    fecha_actualizacion = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relaciones
    programa = relationship("Programas", back_populates="etapas")
    actividades = relationship("Actividades", back_populates="etapa", cascade="all, delete-orphan")
    
    # Prerrequisitos
    etapas_requeridas = relationship(
        "PrerrequisitosEtapa",
        foreign_keys="PrerrequisitosEtapa.etapa_id",
        back_populates="etapa",
        cascade="all, delete-orphan"
    )
    es_prerrequisito_de = relationship(
        "PrerrequisitosEtapa",
        foreign_keys="PrerrequisitosEtapa.prerrequisito_etapa_id",
        back_populates="prerrequisito"
    )