from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import jwt
import hashlib
from datetime import datetime, timedelta

SECRET_KEY = "your-secret-key"
router = APIRouter()


USERS = {}

class AuthData(BaseModel):
    username: str
    password: str

@router.post("/register")
async def register(data: AuthData):
    if data.username in USERS:
        raise HTTPException(status_code=400, detail="User exists")
    USERS[data.username] = hashlib.sha256(data.password.encode()).hexdigest()
    return {"message": "User registered"}

@router.post("/login")
async def login(data: AuthData):
    hashed = hashlib.sha256(data.password.encode()).hexdigest()
    if USERS.get(data.username) != hashed:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = jwt.encode(
        {"user": data.username, "exp": datetime.utcnow() + timedelta(hours=12)},
        SECRET_KEY,
        algorithm="HS256"
    )
    return {"access_token": token}
