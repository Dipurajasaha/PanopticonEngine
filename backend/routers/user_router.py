from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List

import schemas.api_schemas as api_schemas
import services.user_service as user_service
import services.audit_service as audit_service
from database import get_db
from routers.auth_router import RoleChecker
import models.db_models as db_models

#############################################################################
# -- User Router Setup --
#############################################################################
router = APIRouter(prefix="/users", tags=["User"])

allow_admin = RoleChecker(["Admin"])

#############################################################################
# -- Public Endpoint --
#############################################################################
# -- Register a new account --
@router.post("/", response_model=api_schemas.UserResponse)
def create_user(user: api_schemas.UserCreate, db: Session = Depends(get_db)):
    existing_user = user_service.get_user_by_email(db, email=user.email)
    if existing_user: 
        raise HTTPException(status_code=400, detail="Email already register")
    
    user.role = "Viewer"
    return user_service.create_user(db=db, user=user)


#############################################################################
# -- Admin Endpoints --
#############################################################################
@router.post("/admin", response_model=api_schemas.UserResponse)
def admin_create_user(
    user: api_schemas.UserCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: db_models.User = Depends(allow_admin)
):
    existing_user = user_service.get_user_by_email(db, email=user.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already register")

    created_user = user_service.create_user(db=db, user=user)

    background_tasks.add_task(
        audit_service.log_action,
        db,
        current_user.id,
        "CREATE_USER",
        "UserManagement",
        f"Admin created user id={created_user.id}, email={created_user.email}",
    )
    return created_user

# -- List all users --
@router.get("/", response_model=List[api_schemas.UserResponse])
def get_all_users(
        db   : Session = Depends(get_db),
        _    : db_models.User = Depends(allow_admin)
):
    return db.query(db_models.User).all()



# -- Update role for a user --
@router.patch("/{user_id}/role", response_model=api_schemas.UserResponse)
def update_user_role(
    user_id: int,
    payload: api_schemas.UserRoleUpdate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: db_models.User = Depends(allow_admin)
):
    updated_user = user_service.update_user_role(db=db, user_id=user_id, role=payload.role)
    if not updated_user:
        raise HTTPException(status_code=404, detail="User not found")

    background_tasks.add_task(
        audit_service.log_action,
        db,
        current_user.id,
        "UPDATE_ROLE",
        "UserManagement",
        f"Admin updated role for user id={user_id} to {updated_user.role}",
    )
    return updated_user



# -- Delete a user account --
@router.delete("/{user_id}")
def delete_user(
    user_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: db_models.User = Depends(allow_admin)
):
    if current_user.id == user_id:
        raise HTTPException(status_code=400, detail="Admin cannot delete own account")

    deleted = user_service.delete_user(db=db, user_id=user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="User not found")

    background_tasks.add_task(
        audit_service.log_action,
        db,
        current_user.id,
        "DELETE_USER",
        "UserManagement",
        f"Admin deleted user id={user_id}",
    )
    return {"message": "User deleted successfully"}