from sqlalchemy import String, Integer, Column, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.orm import relationship
from conf.database import Base
from datetime import datetime

class Actividades(Base):
    __tablename__ = "actividades"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    etapa_id = Column(Integer, ForeignKey("etapas.id", ondelete="CASCADE"), nullable=False)
    tipo_actividad_id = Column(Integer, ForeignKey("tipos_actividades.id"), nullable=False)
    nombre = Column(String(100), nullable=False)
    descripcion = Column(Text, nullable=True)
    instrucciones = Column(Text, nullable=True)
    tiempo_estimado = Column(Integer, nullable=True)  # en minutos
    orden_secuencial = Column(Integer, nullable=True)
    activa = Column(Boolean, default=True)
    fecha_creacion = Column(DateTime, default=datetime.now)
    fecha_actualizacion = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relaciones
    etapa = relationship("Etapas", back_populates="actividades")
    tipo_actividad = relationship("TiposActividades", back_populates="actividades")
    ejercicios = relationship("Ejercicios", back_populates="actividad", cascade="all, delete-orphan")