import fastapi
import sqlite3
import hashlib
from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPBearer, HTTPBasic, HTTPBasicCredentials
from starlette.responses import JSONResponse
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

security = HTTPBasic()
app = fastapi.FastAPI()

security_bearer = HTTPBearer()

origins = [
    "https://8080-gustavodelraz-authfront-9mni84dingg.ws-us106.gitpod.io"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Session:
    def __init__(self):
        self.token = None

@app.middleware("http")
async def add_session(request: Request, call_next):
    request.state.session = Session()
    response = await call_next(request)
    return response

class Contacto(BaseModel):
    email: str
    nombre: str
    telefono: str

def get_connection():
    """Función para obtener una nueva conexión a la base de datos"""
    return sqlite3.connect("sql/contactos.db")

def md5_hash(text):
    """Función para calcular el hash MD5 de una cadena"""
    return hashlib.md5(text.encode()).hexdigest()

@app.get("/")
def authenticate(credentials: HTTPBearer = Depends(security_bearer), session: Session = Depends()):
    """Autenticación con token fijo"""
    token = credentials.credentials
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT token FROM usuarios WHERE token = ?', (token,))
    exists = cursor.fetchone()

    if exists is None:
        raise HTTPException(status_code=401, detail="Not Authenticated")
    else:
        # Almacenar el token en la sesión
        session.token = token
        return {"message": "Hello World"}

@app.post("/token", response_class=JSONResponse)  
def get_token(credentials: HTTPBasicCredentials = Depends(security), session: Session = Depends()):
    username = credentials.username
    password = credentials.password

    conn = get_connection()
    cursor = conn.cursor()

    hashed_password = md5_hash(password)

    cursor.execute('SELECT * FROM usuarios WHERE username = ? AND password = ?', (username, hashed_password))
    user_exists = cursor.fetchone()

    if user_exists:
        token = user_exists[2]  # Suponiendo que el token está en la tercera columna de la tabla usuarios
        # Almacenar el token en la sesión
        session.token = token

        response = JSONResponse(content={"token": token})
        response.set_cookie(key="token", value=token, httponly=True)
        return response
    else:
        # En caso de credenciales incorrectas, eliminar la cookie
        response = JSONResponse(content={"detail": "Not Authenticated"})
        response.delete_cookie("token")
        raise HTTPException(status_code=401, detail="Not Authenticated")

@app.post("/contactos", dependencies=[Depends(authenticate)])
async def create_contact(contact: Contacto):
    """Crea un nuevo contacto."""
    try:
        # Verifica si el email ya existe en la base de datos
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM contactos WHERE email = ?', (contact.email,))
        existing_contact = cursor.fetchone()

        if existing_contact:
            raise HTTPException(status_code=400, detail={"message": "Email already exists"})

        # Inserta el nuevo contacto en la base de datos
        cursor.execute('INSERT INTO contactos (email, nombre, telefono) VALUES (?, ?, ?)',
                       (contact.email, contact.nombre, contact.telefono))
        conn.commit()

        return {"message": "Contact inserted successfully"}

    except Exception as e:
        raise HTTPException(status_code=400, detail={"message": "Error querying data"})

@app.get("/contactos", dependencies=[Depends(authenticate)])
async def get_contacts():
    """Obtiene todos los contactos."""
    try:
        # Consulta todos los contactos de la base de datos y los envía en un JSON
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM contactos')
        response = []
        for row in cursor.fetchall():
            contact = {
                "email": row[0],
                "nombre": row[1],
                "telefono": row[2]
            }
            response.append(contact)

        if response:
            return response
        else:
            raise HTTPException(status_code=202, detail="No records found")

    except Exception as e:
        raise HTTPException(status_code=400, detail={"message": "Error querying data"})

@app.get("/contactos/{email}", dependencies=[Depends(authenticate)])
async def get_contact(email: str):
    """Obtiene un contacto por su email."""
    try:
        # Consulta el contacto por su email
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM contactos WHERE email = ?', (email,))
        row = cursor.fetchone()

        if row:
            contact = {
                "email": row[0],
                "nombre": row[1],
                "telefono": row[2]
            }
            return contact
        else:
            raise HTTPException(status_code=404, detail={"message": "Email does not exist"})

    except Exception as e:
        raise HTTPException(status_code=400, detail={"message": "Error querying data"})

@app.put("/contactos/{email}", dependencies=[Depends(authenticate)])
async def update_contact(email: str, contact: Contacto):
    """Actualiza un contacto."""
    try:
        if contact.nombre is None or contact.telefono is None:
            raise HTTPException(status_code=422, detail="Name and phone are required fields")

        # Verifica si el contacto con el email proporcionado existe
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM contactos WHERE email = ?', (email,))
        existing_contact = cursor.fetchone()

        if not existing_contact:
            raise HTTPException(status_code=404, detail={"message": "Contact ID does not exist"})

        # Actualiza el contacto en la base de datos
        cursor.execute('UPDATE contactos SET nombre = ?, telefono = ? WHERE email = ?',
                       (contact.nombre, contact.telefono, email))
        conn.commit()

        return {"message": "Contact updated successfully"}

    except Exception as e:
        raise HTTPException(status_code=400, detail={"message": "Error querying or updating data"})

@app.delete("/contactos/{email}", dependencies=[Depends(authenticate)])
async def delete_contact(email: str):
    """Elimina un contacto."""
    try:
        # Verifica si el contacto con el email proporcionado existe
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM contactos WHERE email = ?', (email,))
        existing_contact = cursor.fetchone()

        if not existing_contact:
            raise HTTPException(status_code=404, detail={"message": "Contact email does not exist"})

        # Elimina el contacto de la base de datos
        cursor.execute('DELETE FROM contactos WHERE email = ?', (email,))
        conn.commit()

        return {"message": "Contact deleted successfully"}

    except Exception as e:
        raise HTTPException(status_code=400, detail={"message": "Error querying or deleting data"})
