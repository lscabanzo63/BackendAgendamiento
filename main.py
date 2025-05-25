# main.py
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from auth import (verify_password, get_password_hash, create_access_token,  decode_access_token, ACCESS_TOKEN_EXPIRE_MINUTES)
import models, schemas
from database import SessionLocal, engine

# Crear todas las tablas (en desarrollo)
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Configuración de OAuth2: se utilizará el endpoint /login
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# Dependencia para obtener la sesión de la BD
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

### Endpoint 1: Autenticación del paciente (/login) ###
@app.post("/login", response_model=schemas.Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    paciente = db.query(models.Paciente).filter(models.Paciente.correo == form_data.username).first()
    if not paciente:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Credenciales incorrectas",
                            headers={"WWW-Authenticate": "Bearer"})
    if not verify_password(form_data.password, paciente.contrasena):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Credenciales incorrectas",
                            headers={"WWW-Authenticate": "Bearer"})
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": paciente.correo}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}

# Función para obtener el paciente actual a partir del token
def get_current_patient(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        token_data = decode_access_token(token)
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Token inválido",
                            headers={"WWW-Authenticate": "Bearer"})
    paciente = db.query(models.Paciente).filter(models.Paciente.correo == token_data.correo).first()
    if not paciente:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Paciente no encontrado")
    return paciente

### Endpoint 2: Registro de un paciente (/register) ###
@app.post("/register", response_model=schemas.PacienteResponse)
async def register(paciente_in: schemas.PacienteCreate, db: Session = Depends(get_db)):
    # Verificar si el correo ya existe
    paciente_existente = db.query(models.Paciente).filter(models.Paciente.correo == paciente_in.correo).first()
    if paciente_existente:
        raise HTTPException(status_code=400, detail="El correo ya está registrado")
    paciente = models.Paciente(
        nombres=paciente_in.nombres,
        apellidos=paciente_in.apellidos,
        correo=paciente_in.correo,
        contrasena=get_password_hash(paciente_in.contrasena)
    )
    db.add(paciente)
    db.commit()
    db.refresh(paciente)
    return paciente

### Endpoint 3: Listar las citas disponibles (/citas/disponibles) ###
@app.get("/citas/disponibles", response_model=list[schemas.CitaResponse])
async def listar_citas_disponibles(db: Session = Depends(get_db)):
    # Se listan las citas que aún no han sido agendadas (agendada == False)
    citas = db.query(models.Citas).filter(models.Citas.agendada == False).all()
    return citas

### Endpoint 4: Agendar una cita disponible (/citas/book) ###
@app.post("/citas/book")
async def agendar_cita(booking: schemas.CitaBooking,
                current_patient: models.Paciente = Depends(get_current_patient),
                db: Session = Depends(get_db)):
    # Verificar que la cita existe y está disponible
    cita = db.query(models.Citas).filter(models.Citas.id_cita == booking.id_cita,
                                        models.Citas.agendada == False).first()
    if not cita:
        raise HTTPException(status_code=404, detail="Cita no encontrada o ya ha sido agendada")
    # Registrar la cita en la tabla citas_agendadas
    nueva_cita_agendada = models.CitasAgendadas(
        id_paciente=current_patient.id_paciente,
        id_cita=cita.id_cita
    )
    db.add(nueva_cita_agendada)
    # Actualizar el estado de la cita a agendada
    cita.agendada = True
    db.commit()
    return {"msg": "Cita agendada correctamente"}

### Endpoint 5: Listar las citas agendadas según el usuario (/citas/agendadas) ###
@app.get("/citas/agendadas", response_model=list[schemas.CitaResponse])
async def listar_citas_agendadas(current_patient: models.Paciente = Depends(get_current_patient),
                                db: Session = Depends(get_db)):
    # Se realiza un join entre las tablas citas y citas_agendadas filtrado por el paciente actual
    citas_agendadas = (db.query(models.Citas)
                        .join(models.CitasAgendadas, models.Citas.id_cita == models.CitasAgendadas.id_cita)
                        .filter(models.CitasAgendadas.id_paciente == current_patient.id_paciente)
                        .all())
    return citas_agendadas
