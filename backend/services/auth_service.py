from datetime import datetime, timedelta
from typing import Optional
from passlib.context import CryptContext
from dotenv import load_dotenv
import os
import jwt

#############################################################################
# -- Environment Configuration --
#############################################################################
load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))


#############################################################################
# -- Password and Token Utilities --
#############################################################################
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


if not SECRET_KEY:
    raise ValueError("no  SECRET_KEY set for JWT generation... check .env file...")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

#############################################################################
# -- Password Helpers --
#############################################################################
def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


#############################################################################
# -- Token Helper --
#############################################################################
def create_jwt_token(user_id: int, role: str) -> str:
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
        "sub": str(user_id),
        "role": role,
        "exp": expire
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)