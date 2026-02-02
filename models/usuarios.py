from sqlalchemy import String, Integer, Column, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from conf.database import Base
from datetime import datetime

class Usuarios(Base):
    __tablename__ = "usuarios"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(50), nullable=False, unique=True)
    email = Column(String(100), nullable=False, unique=True)
    password_hash = Column(String(255), nullable=False)
    nombre = Column(String(100), nullable=True)
    apellido = Column(String(100), nullable=True)
    rol_id = Column(Integer, ForeignKey("roles.id"), nullable=False)
    activo = Column(Boolean, default=True)
    fecha_creacion = Column(DateTime, default=datetime.now)
    fecha_actualizacion = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relaciones
    rol = relationship("Roles", back_populates="usuarios")