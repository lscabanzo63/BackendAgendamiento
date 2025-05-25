# models.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class Paciente(Base):
    __tablename__ = "paciente"
    id_paciente = Column(Integer, primary_key=True, index=True)
    nombres = Column(String(255), nullable=False)
    apellidos = Column(String(255), nullable=False)
    correo = Column(String(255), unique=True, index=True, nullable=False)
    contrasena = Column(String(255), nullable=False)
    # Relación opcional: un paciente puede tener varias citas agendadas
    citas_agendadas = relationship("CitasAgendadas", back_populates="paciente")

class Doctores(Base):
    __tablename__ = "doctores"
    id_doctor = Column(Integer, primary_key=True, index=True)
    nombres = Column(String(255), nullable=False)
    apellidos = Column(String(255), nullable=False)
    correo = Column(String(255), unique=True, index=True, nullable=False)
    contrasena = Column(String(255), nullable=False)

class Especializaciones(Base):
    __tablename__ = "especializaciones"
    id_especializacion = Column(Integer, primary_key=True, index=True)
    nombre_especializacion = Column(String(100), nullable=False)

class EspecializacionesDoctores(Base):
    __tablename__ = "especializaciones_doctores"
    id_especializacion_doc = Column(Integer, primary_key=True, index=True)
    id_doctor = Column(Integer, ForeignKey("doctores.id_doctor"), nullable=False)
    id_especializacion = Column(Integer, ForeignKey("especializaciones.id_especializacion"), nullable=False)

class Sedes(Base):
    __tablename__ = "sedes"
    id_sede = Column(Integer, primary_key=True, index=True)
    nombre_sede = Column(String(100), nullable=False)

class Citas(Base):
    __tablename__ = "citas"
    id_cita = Column(Integer, primary_key=True, index=True)
    id_sede = Column(Integer, ForeignKey("sedes.id_sede"), nullable=False)
    fecha_inicio = Column(DateTime, nullable=False)
    fecha_fin = Column(DateTime, nullable=False)
    id_especializacion_doc = Column(Integer, ForeignKey("especializaciones_doctores.id_especializacion_doc"), nullable=False)
    agendada = Column(Boolean, nullable=False, default=False)

class CitasAgendadas(Base):
    __tablename__ = "citas_agendadas"
    id_cita_agendada = Column(Integer, primary_key=True, index=True)
    id_paciente = Column(Integer, ForeignKey("paciente.id_paciente"), nullable=False)
    id_cita = Column(Integer, ForeignKey("citas.id_cita"), nullable=False)
    # Relaciones para facilitar consultas
    paciente = relationship("Paciente", back_populates="citas_agendadas")
