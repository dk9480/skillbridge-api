# # # import jwt
# # # from datetime import datetime, timedelta
# # # from passlib.context import CryptContext
# # # import os
# # # from dotenv import load_dotenv

# # # load_dotenv()

# # # SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key")
# # # ALGORITHM = "HS256"
# # # ACCESS_TOKEN_EXPIRE_HOURS = 24
# # # MONITORING_TOKEN_EXPIRE_HOURS = 1

# # # pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# # # def hash_password(password: str) -> str:
# # #     """Hash a password using bcrypt"""
# # #     return pwd_context.hash(password)

# # # def verify_password(plain_password: str, hashed_password: str) -> bool:
# # #     """Verify a password against its hash"""
# # #     return pwd_context.verify(plain_password, hashed_password)

# # # # def create_access_token(user_id: int, role: str, institution_id: int = None) -> str:
# # # def create_access_token(user_id: int, role: str, institution_id: int = None) -> str:
# # #     """Create a JWT token for normal users (24 hour expiry)"""
# # #     expire = datetime.utcnow() + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
# # #     payload = {
# # #         "user_id": user_id,
# # #         "role": role,
# # #         "institution_id": institution_id,
# # #         "iat": datetime.utcnow(),
# # #         "exp": expire,
# # #         "type": "access"
# # #     }
# # #     token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
# # #     return token

# # # def create_monitoring_token(user_id: int, role: str) -> str:
# # #     """Create a short-lived token for monitoring officer (1 hour expiry)"""
# # #     expire = datetime.utcnow() + timedelta(hours=MONITORING_TOKEN_EXPIRE_HOURS)
# # #     payload = {
# # #         "user_id": user_id,
# # #         "role": role,
# # #         "iat": datetime.utcnow(),
# # #         "exp": expire,
# # #         "type": "monitoring"
# # #     }
# # #     token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
# # #     return token

# # # def verify_token(token: str):
# # #     """Verify and decode a JWT token"""
# # #     try:
# # #         payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
# # #         return payload
# # #     except jwt.PyJWTError:
# # #         return None



# # import jwt
# # from datetime import datetime, timedelta
# # from passlib.context import CryptContext
# # import os
# # from dotenv import load_dotenv

# # load_dotenv()

# # SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key")
# # ALGORITHM = "HS256"
# # ACCESS_TOKEN_EXPIRE_HOURS = 24
# # MONITORING_TOKEN_EXPIRE_HOURS = 1

# # pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# # def hash_password(password: str) -> str:
# #     """Hash a password using bcrypt"""
# #     # bcrypt has 72 byte limit, truncate if needed
# #     password_bytes = password.encode('utf-8')
# #     if len(password_bytes) > 72:
# #         password_bytes = password_bytes[:72]
# #     return pwd_context.hash(password_bytes.decode('utf-8'))

# # def verify_password(plain_password: str, hashed_password: str) -> bool:
# #     """Verify a password against its hash"""
# #     # Truncate plain password to 72 bytes for verification
# #     password_bytes = plain_password.encode('utf-8')
# #     if len(password_bytes) > 72:
# #         password_bytes = password_bytes[:72]
# #     return pwd_context.verify(password_bytes.decode('utf-8'), hashed_password)

# # def create_access_token(user_id: int, role: str, institution_id: int = None) -> str:
# #     """Create a JWT token for normal users (24 hour expiry)"""
# #     expire = datetime.utcnow() + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
# #     payload = {
# #         "user_id": user_id,
# #         "role": role,
# #         "institution_id": institution_id,
# #         "iat": datetime.utcnow(),
# #         "exp": expire,
# #         "type": "access"
# #     }
# #     token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
# #     return token

# # def create_monitoring_token(user_id: int, role: str) -> str:
# #     """Create a short-lived token for monitoring officer (1 hour expiry)"""
# #     expire = datetime.utcnow() + timedelta(hours=MONITORING_TOKEN_EXPIRE_HOURS)
# #     payload = {
# #         "user_id": user_id,
# #         "role": role,
# #         "iat": datetime.utcnow(),
# #         "exp": expire,
# #         "type": "monitoring"
# #     }
# #     token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
# #     return token

# # def verify_token(token: str):
# #     """Verify and decode a JWT token"""
# #     try:
# #         payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
# #         return payload
# #     except jwt.PyJWTError:
# #         return None





# import jwt
# from datetime import datetime, timedelta
# from werkzeug.security import generate_password_hash, check_password_hash
# import os
# from dotenv import load_dotenv

# load_dotenv()

# SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key")
# ALGORITHM = "HS256"
# ACCESS_TOKEN_EXPIRE_HOURS = 24
# MONITORING_TOKEN_EXPIRE_HOURS = 1

# def hash_password(password: str) -> str:
#     """Hash a password using werkzeug"""
#     return generate_password_hash(password)

# def verify_password(plain_password: str, hashed_password: str) -> bool:
#     """Verify a password against its hash"""
#     return check_password_hash(hashed_password, plain_password)

# def create_access_token(user_id: int, role: str, institution_id: int = None) -> str:
#     """Create a JWT token for normal users (24 hour expiry)"""
#     expire = datetime.utcnow() + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
#     payload = {
#         "user_id": user_id,
#         "role": role,
#         "institution_id": institution_id,
#         "iat": datetime.utcnow(),
#         "exp": expire,
#         "type": "access"
#     }
#     token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
#     return token

# def create_monitoring_token(user_id: int, role: str) -> str:
#     """Create a short-lived token for monitoring officer (1 hour expiry)"""
#     expire = datetime.utcnow() + timedelta(hours=MONITORING_TOKEN_EXPIRE_HOURS)
#     payload = {
#         "user_id": user_id,
#         "role": role,
#         "iat": datetime.utcnow(),
#         "exp": expire,
#         "type": "monitoring"
#     }
#     token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
#     return token

# def verify_token(token: str):
#     """Verify and decode a JWT token"""
#     try:
#         payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#         return payload
#     except jwt.PyJWTError:
#         return None


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
