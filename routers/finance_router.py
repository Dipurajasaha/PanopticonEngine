from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

import schemas.api_schemas as api_schemas
import services.finance_service as finance_service
from database import get_db
from routers.auth_router import RoleChecker
import models.db_models as db_models

router = APIRouter(prefix="/records", tags=["Finance Records"])

# -- defined specific role access --
allow_admin = RoleChecker(["Admin"])
allow_view_records = RoleChecker(["Admin","Analyst"])


# -- only Admin can create record -- 
@router.post("/", response_model=api_schemas.RecordResponse)
def create_record(
    record          :api_schemas.RecordCreate, 
    db              :Session = Depends(get_db),
    current_user    :db_models.User = Depends(allow_admin)
):
    return finance_service.create_finance_record(db=db, record=record, owner_id=current_user.id)


# -- Admin and Analyst can view record --
@router.get("/", response_model=List[api_schemas.RecordResponse])
def read_records(
    skip            :int = 0, 
    limit           :int = 100, 
    db              :Session = Depends(get_db), 
    current_user    :db_models.User = Depends(allow_view_records)
):
    return finance_service.get_user_records(db=db, owner_id=current_user.id, skip=skip, limit=limit)


# -- only Admin can delete record --
@router.delete("/{record_id}")
def delete_record(
    record_id       :int, 
    db              :Session = Depends(get_db),
    current_user    :db_models.User = Depends(allow_admin)
):
    success = finance_service.soft_delete_record(db=db, record_id=record_id, owner_id=current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Record not found or already deleted")
    return {"message": "Record successfully deleted..."}
