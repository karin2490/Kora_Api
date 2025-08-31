from sqlalchemy import String, Integer, Column, DateTime, Boolean, Text, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from conf.database import Base
from datetime import datetime

class Ejercicios(Base):
    __tablename__ = "ejercicios"
    __table_args__ = (
        CheckConstraint(
            "tipo_respuesta IN ('opcion_multiple', 'texto_libre', 'verdadero_falso', 'ordenamiento', 'clasificacion')",
            name="CK_ejercicios_tipo_respuesta"
        ),
    )
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    actividad_id = Column(Integer, ForeignKey("actividades.id", ondelete="CASCADE"), nullable=False)
    nombre = Column(String(100), nullable=False)
    enunciado = Column(Text, nullable=True)
    tipo_respuesta = Column(String(50), default='opcion_multiple')
    contenido_ejercicio = Column(Text, nullable=True)  # JSON content
    puntuacion_maxima = Column(Integer, default=100)
    tiempo_limite = Column(Integer, nullable=True)  # en segundos
    orden_secuencial = Column(Integer, nullable=True)
    activo = Column(Boolean, default=True)
    fecha_creacion = Column(DateTime, default=datetime.now)
    fecha_actualizacion = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relaciones
    actividad = relationship("Actividades", back_populates="ejercicios")