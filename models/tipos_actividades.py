from sqlalchemy import String, Integer, Column, Text
from sqlalchemy.orm import relationship
from conf.database import Base

class TiposActividades(Base):
    __tablename__ = "tipos_actividades"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nombre = Column(String(100), nullable=False, unique=True)
    descripcion = Column(Text, nullable=True)
    
    # Relaciones
    actividades = relationship("Actividades", back_populates="tipo_actividad")