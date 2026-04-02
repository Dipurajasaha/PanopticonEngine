from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import schemas.api_schemas as api_schemas
import services.finance_service as finance_service
from database import get_db

router = APIRouter(prefix="/records", tags=["Finance Records"])

TEMP_USER_ID = 1

@router.post("/", response_model=api_schemas.RecordResponse)
def create_record(record: api_schemas.RecordCreate, db: Session = Depends(get_db)):
    return finance_service.create_finance_record(db=db, record=record, owner_id=TEMP_USER_ID)

@router.get("/", response_model=List[api_schemas.RecordResponse])
def read_records(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return finance_service.get_user_records(db=db, owner_id=TEMP_USER_ID, skip=skip, limit=limit)


@router.delete("/{record_id}")
def delete_record(record_id: int, db: Session = Depends(get_db)):
    success = finance_service.soft_delete_record(db=db, record_id=record_id, owner_id=TEMP_USER_ID)
    if not success:
        raise HTTPException(status_code=404, detail="Record not found or already deleted")
    return {"message": "Record successfully deleted..."}
