from sqlalchemy import String, Integer, Column, DateTime, Boolean, Text
from sqlalchemy.orm import relationship
from conf.database import Base
from datetime import datetime

class Materias(Base):
    __tablename__ = "materias"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nombre = Column(String(100), nullable=False, unique=True)
    descripcion = Column(Text, nullable=True)
    activa = Column(Boolean, default=True)
    fecha_creacion = Column(DateTime, default=datetime.now)
    fecha_actualizacion = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relaciones
    programas = relationship("Programas", back_populates="materia", cascade="all, delete-orphan")