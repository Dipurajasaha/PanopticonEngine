from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from pydantic import BaseModel
import jwt

from database import get_db
import services.user_service as user_service
import services.auth_service as auth_service
import services.audit_service as audit_service
import models.db_models as db_models


router = APIRouter(prefix="/auth", tags=["Security"])
security = HTTPBearer()

#############################################################################
# -- Request Schema --
#############################################################################
class LoginRequest(BaseModel):
    email: str
    password: str

#############################################################################
# -- Authentication Endpoint --
#############################################################################
@router.post("/login")
def login(
    credentials: LoginRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    user = user_service.get_user_by_email(db, email=credentials.email)

    if not user or not auth_service.verify_password(credentials.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password !!!")

    background_tasks.add_task(
        audit_service.log_action,
        db,
        user.id,
        "LOGIN",
        "System",
        "User authenticated successfully",
    )

    token = auth_service.create_jwt_token(user_id=user.id, role=user.role)
    return {"access_token": token, "token_type": "bearer"}

#############################################################################
# -- Authentication Dependency --
#############################################################################
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

#############################################################################
# -- RBAC Dependency --
#############################################################################
class RoleChecker:
    def __init__(self, allowed_roles: list):
        # Normalize allowed roles to prevent case/whitespace mismatches.
        self.allowed_roles = [str(role).strip().lower() for role in allowed_roles]

    def __call__(self, current_user: db_models.User = Depends(get_current_user)):
        normalized_role = str(current_user.role).strip().lower()
        if normalized_role not in self.allowed_roles:
            raise HTTPException(
                status_code=403, 
                detail=f"Operation not permitted. Your role '{current_user.role}' is blocked. Allowed roles: {self.allowed_roles}"
            )
        return current_user