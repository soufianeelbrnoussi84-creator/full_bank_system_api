from pwdlib import PasswordHash
from datetime import datetime, timedelta
from jose import jwt, JWTError
from dotenv import load_dotenv
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException
import os
from models import UserRole,Accounts
from sqlmodel import Session,select
from database import get_session


password_hash = PasswordHash.recommended() 

def hash_password(h_password: str):
    return password_hash.hash(h_password)

def verify_password(plain_password: str, hashed_password: str):
    return password_hash.verify(plain_password, hashed_password)

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("SECRET_KEY is not set")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: Session = Depends(get_session)
    ):
    try:
        paylaod = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = paylaod.get("sub")
        
        if email is None : 
            raise HTTPException(status_code=401, detail="Invalid token")
        
        user = session.exec(select(Accounts).where(Accounts.email == email)).first()
        
        if user is None:
            raise HTTPException(status_code=404, detail="user not found")
        
        return user
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    
def get_current_admin(
    current_user: Accounts = Depends(get_current_user)
    ):
    if current_user.role != UserRole.admin:
        raise HTTPException(
            status_code=403, 
            detail="Admin privileges required"
            )
        
    return current_user
        
    