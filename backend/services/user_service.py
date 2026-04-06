from sqlalchemy.orm import Session

import models.db_models as db_models
import schemas.api_schemas as api_schemas
import services.auth_service as auth_service


#############################################################################
# -- User Service: Handles all user-related database operations and business logic --
#############################################################################
def _normalize_role(role: str) -> str:
    normalized = str(role).strip().lower()
    role_map = {
        "viewer": "Viewer",
        "analyst": "Analyst",
        "admin": "Admin",
    }
    if normalized not in role_map:
        raise ValueError("Invalid role. Allowed roles are Viewer, Analyst, Admin")
    return role_map[normalized]


##########################################################################
# -- User Management Functions --
##########################################################################
def get_user_by_email(db: Session, email: str):
    # -- fetches a user by their email address --
    return db.query(db_models.User).filter(db_models.User.email == email).first()


def get_user_by_id(db: Session, user_id: int):
    return db.query(db_models.User).filter(db_models.User.id == user_id).first()


############################################################################
# -- User Creation and Seeding Functions --
############################################################################
def create_user(db: Session, user: api_schemas.UserCreate):
    hashed_password = auth_service.hash_password(user.password)

    # -- creates a new user in database --
    db_user = db_models.User(
        email = user.email,
        hashed_password = hashed_password,
        role = _normalize_role(user.role)
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def update_user_role(db: Session, user_id: int, role: str):
    db_user = get_user_by_id(db, user_id)
    if not db_user:
        return None

    db_user.role = _normalize_role(role)
    db.commit()
    db.refresh(db_user)
    return db_user


def delete_user(db: Session, user_id: int):
    db_user = get_user_by_id(db, user_id)
    if not db_user:
        return False

    db.delete(db_user)
    db.commit()
    return True


###########################################################################
# -- Seed function to create default users at startup --
###########################################################################
def seed_default_users(db: Session):
    # -- check if the admin already exists to prevent duplicate errors on restart
    admin_exists = get_user_by_email(db, "admin@panopticon.com")

    if not admin_exists:
        # -- Create Super Admin --
        create_user(db, api_schemas.UserCreate(email="admin@panopticon.com", password="admin123", role="Admin"))
        # -- Create Analyst --
        create_user(db, api_schemas.UserCreate(email="analyst@panopticon.com", password="analyst123", role="Analyst"))
        # -- Create Viewer --
        create_user(db, api_schemas.UserCreate(email="viewer@panopticon.com", password="viewer123", role="Viewer"))
        print("System Notice: Default testing credentials successfully injected into database...")