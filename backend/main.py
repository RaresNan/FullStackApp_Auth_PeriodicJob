import os
from datetime import datetime, timedelta
from fastapi import FastAPI, Depends, HTTPException
from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, Integer, String, text
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from pydantic import BaseModel
from passlib.context import CryptContext
from jose import jwt

# --- 1. CONFIGURĂRI INIȚIALE ---
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
SECRET_KEY = os.getenv("SECRET_KEY", "cheie_super_secreta_pentru_jwt_local")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 24

# --- 2. BAZA DE DATE ---
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)

# Creează tabelele (dacă nu există)
Base.metadata.create_all(bind=engine)

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- 3. SECURITATE (Parole și JWT) ---
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# --- 4. SCHEME PYDANTIC ---
class RegisterRequest(BaseModel):
    email: str
    password: str

# --- 5. RUTELE APLICAȚIEI ---

@app.get("/")
def read_root():
    return {"status": "ok", "mesaj": "Backend funcțional"}

@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        return {"status": "ok", "db": "connected"}
    except Exception:
        raise HTTPException(status_code=500, detail="Eroare conexiune BD")

@app.post("/auth/register")
def register(user_req: RegisterRequest, db: Session = Depends(get_db)):
    # Verificăm dacă email-ul există
    existing_user = db.query(User).filter(User.email == user_req.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email-ul exista deja in sistem.")
    
    # Hash-uim parola și salvăm userul
    hashed_pw = get_password_hash(user_req.password)
    new_user = User(email=user_req.email, hashed_password=hashed_pw)
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return {"mesaj": "Utilizator creat cu succes", "id": new_user.id, "email": new_user.email}

@app.post("/auth/login")
def login(user_req: RegisterRequest, db: Session = Depends(get_db)):
    # Căutăm userul
    user = db.query(User).filter(User.email == user_req.email).first()
    
    # Verificăm existența și parola
    if not user or not verify_password(user_req.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Email sau parola gresita")
        
    # Generăm tokenul JWT
    access_token = create_access_token(data={"sub": str(user.id)})
    
    return {"access_token": access_token, "token_type": "bearer"}