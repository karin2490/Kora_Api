from sqlalchemy import String, Integer, Column, Text
from sqlalchemy.orm import relationship
from conf.database import Base

class Ejes(Base):
    __tablename__ = "ejes"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    codigo = Column(String(10), nullable=False, unique=True)
    nombre = Column(String(50), nullable=False)
    descripcion = Column(Text, nullable=True)
    
    # Relaciones
    programas = relationship("Programas", back_populates="eje")