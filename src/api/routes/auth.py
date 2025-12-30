# src/api/routes/auth.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta
import os

SECRET_KEY = os.environ.get("SECRET_KEY", "your-secret-key")
ALGORITHM = "HS256"

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
USERS = {}  # In-memory store for testing

class AuthData(BaseModel):
    username: str
    password: str

# -------- Password Hashing --------
def hash_password(password: str) -> str:
    # Encode and truncate safely to 72 bytes
    encoded = password.encode("utf-8")[:72]
    return pwd_context.hash(encoded)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    encoded = plain_password.encode("utf-8")[:72]
    return pwd_context.verify(encoded, hashed_password)

# -------- Routes --------
@router.post("/register")
async def register(data: AuthData):
    if data.username in USERS:
        raise HTTPException(status_code=400, detail="User exists")
    USERS[data.username] = hash_password(data.password)
    return {"message": "User registered successfully"}

@router.post("/login")
async def login(data: AuthData):
    hashed = USERS.get(data.username)
    if not hashed or not verify_password(data.password, hashed):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = jwt.encode(
        {"sub": data.username, "exp": datetime.utcnow() + timedelta(hours=12)},
        SECRET_KEY,
        algorithm=ALGORITHM
    )
    return {"access_token": token}