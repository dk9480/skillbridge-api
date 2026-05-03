import jwt
from datetime import datetime, timedelta
import bcrypt
import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 24
MONITORING_TOKEN_EXPIRE_HOURS = 1

def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def create_access_token(user_id: int, role: str, institution_id: int = None) -> str:
    """Create a JWT token for normal users (24 hour expiry)"""
    expire = datetime.utcnow() + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    payload = {
        "user_id": user_id,
        "role": role,
        "institution_id": institution_id,
        "iat": datetime.utcnow(),
        "exp": expire,
        "type": "access"
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token

def create_monitoring_token(user_id: int, role: str) -> str:
    """Create a short-lived token for monitoring officer (1 hour expiry)"""
    expire = datetime.utcnow() + timedelta(hours=MONITORING_TOKEN_EXPIRE_HOURS)
    payload = {
        "user_id": user_id,
        "role": role,
        "iat": datetime.utcnow(),
        "exp": expire,
        "type": "monitoring"
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token

def verify_token(token: str):
    """Verify and decode a JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.PyJWTError:
        return None
