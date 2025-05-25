# schemas.py
from pydantic import BaseModel
from datetime import datetime

### Esquemas para Paciente ###
class PacienteBase(BaseModel):
    nombres: str
    apellidos: str
    correo: str

class PacienteCreate(PacienteBase):
    contrasena: str  # Se recibirá en texto plano y luego se hasheará

class PacienteResponse(PacienteBase):
    id_paciente: int
    class Config:
        orm_mode = True

### Esquemas para Autenticación ###
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    correo: str | None = None

### Esquemas para Citas ###
class CitaResponse(BaseModel):
    id_cita: int
    fecha_inicio: datetime
    fecha_fin: datetime
    agendada: bool
    class Config:
        orm_mode = True

class CitaBooking(BaseModel):
    id_cita: int
