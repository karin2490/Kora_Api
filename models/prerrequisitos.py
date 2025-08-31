from sqlalchemy import Integer, Column, Boolean, ForeignKey, UniqueConstraint, CheckConstraint
from sqlalchemy.orm import relationship
from conf.database import Base

class PrerrequisitosPrograma(Base):
    __tablename__ = "prerrequisitos_programas"
    __table_args__ = (
        UniqueConstraint('programa_id', 'prerrequisito_programa_id', name='UQ_prerrequisitos_programas'),
        CheckConstraint('programa_id != prerrequisito_programa_id', name='CK_prereq_prog_no_circular'),
    )
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    programa_id = Column(Integer, ForeignKey("programas.id", ondelete="CASCADE"), nullable=False)
    prerrequisito_programa_id = Column(Integer, ForeignKey("programas.id"), nullable=False)
    obligatorio = Column(Boolean, default=True)
    
    # Relaciones
    programa = relationship("Programas", foreign_keys=[programa_id], back_populates="programas_requeridos")
    prerrequisito = relationship("Programas", foreign_keys=[prerrequisito_programa_id], back_populates="es_prerrequisito_de")


class PrerrequisitosEtapa(Base):
    __tablename__ = "prerrequisitos_etapas"
    __table_args__ = (
        UniqueConstraint('etapa_id', 'prerrequisito_etapa_id', name='UQ_prerrequisitos_etapas'),
        CheckConstraint('etapa_id != prerrequisito_etapa_id', name='CK_prereq_etapa_no_circular'),
    )
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    etapa_id = Column(Integer, ForeignKey("etapas.id", ondelete="CASCADE"), nullable=False)
    prerrequisito_etapa_id = Column(Integer, ForeignKey("etapas.id"), nullable=False)
    obligatorio = Column(Boolean, default=True)
    
    # Relaciones
    etapa = relationship("Etapas", foreign_keys=[etapa_id], back_populates="etapas_requeridas")
    prerrequisito = relationship("Etapas", foreign_keys=[prerrequisito_etapa_id], back_populates="es_prerrequisito_de")