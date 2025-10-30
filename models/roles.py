from sqlalchemy import String, Integer, Column, DateTime, Boolean
from sqlalchemy.orm import relationship
from conf.database import Base
from datetime import datetime

class Roles(Base):
    __tablename__ = "roles"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nombre = Column(String(50), nullable=False, unique=True)
    descripcion = Column(String(200), nullable=True)
    activo = Column(Boolean, default=True)
    fecha_creacion = Column(DateTime, default=datetime.now)
    
    # Relaciones
    usuarios = relationship("Usuarios", back_populates="rol")