from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from pydantic import BaseModel
import jwt

from database import get_db
import services.user_service as user_service
import services.auth_service as auth_service
import models.db_models as db_models


router = APIRouter(prefix="/auth", tags=["Security"])
security = HTTPBearer()

# -- Request model for login --
class LoginRequest(BaseModel):
    email: str
    password: str

# -- Login endpoint --
@router.post("/login")
def login(credentials: LoginRequest, db: Session = Depends(get_db)):
    user = user_service.get_user_by_email(db, email=credentials.email)

    if not user or not auth_service.verify_password(credentials.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password !!!")
    
    token = auth_service.create_jwt_token(user_id=user.id, role=user.role)
    return {"access_token": token, "token_type": "bearer"}

# -- Dependency to get the current user from the token --
def get_current_user(
        credentials: HTTPAuthorizationCredentials = Depends(security), 
        db: Session=Depends(get_db)
    ):
    token = credentials.credentials
    # -- Decode the JWT token and extract user information -- 
    try:
        payload = jwt.decode(token, auth_service.SECRET_KEY, algorithms=[auth_service.ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token structure...")
    # -- Handle token expiration --
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired... Please login again...")
    # -- Handle any other JWT decoding errors --
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Could not validate credentials...")
    
    # -- Fetch the user from the database using the extracted user ID --
    user = db.query(db_models.User).filter(db_models.User.id == int(user_id)).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found...")
    return user