from sqlalchemy import String, Integer, Column, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.orm import relationship
from conf.database import Base
from datetime import datetime

class Programas(Base):
    __tablename__ = "programas"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    materia_id = Column(Integer, ForeignKey("materias.id", ondelete="CASCADE"), nullable=False)
    eje_id = Column(Integer, ForeignKey("ejes.id", ondelete="SET NULL"), nullable=True)
    nombre = Column(String(100), nullable=False)
    nombre_comercial = Column(String(100), nullable=True)
    grado_inicio = Column(String(10), nullable=True)
    grado_fin = Column(String(10), nullable=True)
    descripcion_breve = Column(Text, nullable=True)
    prerrequisitos = Column(Text, nullable=True)
    activo = Column(Boolean, default=True)
    orden_secuencial = Column(Integer, nullable=True)
    fecha_creacion = Column(DateTime, default=datetime.now)
    fecha_actualizacion = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relaciones
    materia = relationship("Materias", back_populates="programas")
    eje = relationship("Ejes", back_populates="programas")
    etapas = relationship("Etapas", back_populates="programa", cascade="all, delete-orphan")
    
    # Prerrequisitos (muchos a muchos consigo mismo)
    programas_requeridos = relationship(
        "PrerrequisitosPrograma",
        foreign_keys="PrerrequisitosPrograma.programa_id",
        back_populates="programa",
        cascade="all, delete-orphan"
    )
    es_prerrequisito_de = relationship(
        "PrerrequisitosPrograma",
        foreign_keys="PrerrequisitosPrograma.prerrequisito_programa_id",
        back_populates="prerrequisito"
    )