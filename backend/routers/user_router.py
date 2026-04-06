from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

import schemas.api_schemas as api_schemas
import services.user_service as user_service
from database import get_db
from routers.auth_router import RoleChecker
import models.db_models as db_models

# -- User Router --
router = APIRouter(prefix="/users", tags=["User"])

allow_admin = RoleChecker(["Admin"])

# -- Public route: Anyone can register an account --
@router.post("/", response_model=api_schemas.UserResponse)
def create_user(user: api_schemas.UserCreate, db: Session = Depends(get_db)):
    existing_user = user_service.get_user_by_email(db, email=user.email)
    if existing_user: 
        raise HTTPException(status_code=400, detail="Email already register")
    
    return user_service.create_user(db=db, user=user)

# -- Admin route: only Admins can manage all users in the system --
@router.get("/", response_model=List[api_schemas.UserResponse])
def get_all_users(
        db   : Session = Depends(get_db),
        _    : db_models.User = Depends(allow_admin)
):
    return db.query(db_models.User).all()