import os
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from .database import get_db
from .models import Teacher

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
bearer = HTTPBearer(auto_error=False)
ALGORITHM = "HS256"

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(password: str, password_hash: str) -> bool:
    return pwd_context.verify(password, password_hash)

def create_token(teacher: Teacher) -> str:
    secret = os.getenv("JWT_SECRET", "")
    if len(secret) < 32:
        raise RuntimeError("Set JWT_SECRET to a random secret of at least 32 characters.")
    expiry = int(os.getenv("JWT_EXPIRE_MINUTES", "720"))
    payload = {"sub": str(teacher.id), "admin": teacher.is_admin,
               "exp": datetime.now(timezone.utc) + timedelta(minutes=expiry)}
    return jwt.encode(payload, secret, algorithm=ALGORITHM)

def current_teacher(credentials: HTTPAuthorizationCredentials = Depends(bearer),
                    db: Session = Depends(get_db)) -> Teacher:
    if not credentials:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Login required")
    try:
        payload = jwt.decode(credentials.credentials, os.getenv("JWT_SECRET", ""), algorithms=[ALGORITHM])
        teacher_id = int(payload.get("sub", "0"))
    except (JWTError, ValueError):
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    teacher = db.get(Teacher, teacher_id)
    if not teacher:
        raise HTTPException(status_code=401, detail="Account not found")
    return teacher

def admin_teacher(teacher: Teacher = Depends(current_teacher)) -> Teacher:
    if not teacher.is_admin:
        raise HTTPException(status_code=403, detail="Administrator access required")
    return teacher
