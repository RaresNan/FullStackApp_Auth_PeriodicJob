import os
from datetime import datetime, timedelta
# S-au adăugat status și OAuth2PasswordBearer
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, Integer, String, text
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from pydantic import BaseModel
from passlib.context import CryptContext
# S-a adăugat JWTError
from jose import jwt, JWTError

# --- 1. CONFIGURĂRI INIȚIALE ---
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
SECRET_KEY = os.getenv("SECRET_KEY", "cheie_super_secreta_pentru_jwt_local")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 24

# Setăm schema de securitate pentru Swagger (activăm butonul verde 'Authorize')
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

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

# Middleware pentru validarea token-ului JWT (Paznicul nostru)
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token invalid sau expirat",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Decodificăm token-ul
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub") # "sub" conține ID-ul pus la login
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
        
    # Căutăm userul în baza de date
    user = db.query(User).filter(User.id == int(user_id)).first()
    if user is None:
        raise credentials_exception
        
    return user

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
    existing_user = db.query(User).filter(User.email == user_req.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email-ul exista deja in sistem.")
    
    hashed_pw = get_password_hash(user_req.password)
    new_user = User(email=user_req.email, hashed_password=hashed_pw)
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return {"mesaj": "Utilizator creat cu succes", "id": new_user.id, "email": new_user.email}

@app.post("/auth/login")
def login(user_req: RegisterRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == user_req.email).first()
    
    if not user or not verify_password(user_req.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Email sau parola gresita")
        
    access_token = create_access_token(data={"sub": str(user.id)})
    
    return {"access_token": access_token, "token_type": "bearer"}

# --- RUTE NOI (ZIUA 4) ---

@app.get("/me")
def get_me(current_user: User = Depends(get_current_user)):
    # Returnăm doar datele sigure, NICIODATĂ parola (nici măcar hash-ul)
    return {
        "id": current_user.id,
        "email": current_user.email
    }

@app.post("/auth/logout")
def logout():
    # Logout-ul bazat pe JWT se realizează efectiv pe frontend prin ștergerea token-ului
    return {"mesaj": "Logout efectuat cu succes. Frontend-ul trebuie sa stearga token-ul din localStorage."}