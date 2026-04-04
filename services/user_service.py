from sqlalchemy.orm import Session

import models.db_models as db_models
import schemas.api_schemas as api_schemas
import services.auth_service as auth_service

def get_user_by_email(db: Session, email: str):
    # -- fetches a user by their email address --
    return db.query(db_models.User).filter(db_models.User.email == email).first()


def create_user(db: Session, user: api_schemas.UserCreate):
    hashed_password = auth_service.hash_password(user.password)


    # -- creates a new user in database --
    db_user = db_models.User(
        email = user.email,
        hashed_password = hashed_password,
        role = user.role
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user