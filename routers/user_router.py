from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import schemas.api_schemas as api_schemas
import services.user_service as user_service
from database import get_db

# -- User Router --
router = APIRouter(prefix="/users", tags=["User"])



@router.post("/", response_model=api_schemas.UserResponse)
def create_user(user: api_schemas.UserCreate, db: Session = Depends(get_db)):
    existing_user = user_service.get_user_by_email(db, email=user.email)
    if existing_user: 
        raise HTTPException(status_code=400, detail="Email already register")
    
    return user_service.create_user(db=db, user=user)