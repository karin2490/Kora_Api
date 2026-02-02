from sqlalchemy import String, Integer, Column, DateTime, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from conf.database import Base
from datetime import datetime

class ActividadesUsuarios(Base):
    __tablename__ = "actividades_usuarios"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    actividad_id = Column(Integer, ForeignKey("actividades.id"), nullable=False)
    estado = Column(String(20), nullable=False, default='pending')  # pending, in_progress, completed, abandoned
    fecha_inicio = Column(DateTime, nullable=True)
    fecha_completado = Column(DateTime, nullable=True)
    progreso_porcentaje = Column(Numeric(5, 2), default=0.00)
    tiempo_dedicado = Column(Integer, nullable=True)  # En minutos
    intentos = Column(Integer, default=0)
    fecha_creacion = Column(DateTime, default=datetime.now)
    fecha_actualizacion = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # Relaciones
    usuario = relationship("Usuarios", backref="actividades_usuario")
    actividad = relationship("Actividades", backref="usuarios_actividad")
