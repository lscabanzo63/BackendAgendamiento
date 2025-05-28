# database.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Actualiza el string de conexión con las credenciales reales (usuario, contraseña, host y base de datos)
SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:password@localhost:3306/agendamiento_citas"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    echo=True  # Esto imprime las consultas SQL en consola; desactívalo en producción
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
