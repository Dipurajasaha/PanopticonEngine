from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional
from datetime import datetime

import models.db_models as db_models
import schemas.api_schemas as api_schemas


def create_finance_record(db: Session, record: api_schemas.RecordCreate, owner_id: int):
    # -- creates a new finance record in database --
    db_record = db_models.FinanceRecord(
        **record.model_dump(),
        owner_id = owner_id
    )
    db.add(db_record)
    db.commit()
    db.refresh(db_record)

    return db_record


def get_user_records(
        db          : Session, 
        owner_id    : int, 
        skip        : int = 0, 
        limit       : int = 100,
        record_type: Optional[str] = None,
        category    : Optional[str] = None,
        start_date  : Optional[datetime] = None,
        end_date    : Optional[datetime] = None
):
    # -- fetches user active records --
    query = db.query(db_models.FinanceRecord).filter(
        db_models.FinanceRecord.owner_id == owner_id,
        db_models.FinanceRecord.is_deleted == False,
        func.lower(db_models.FinanceRecord.record_type).in_(["income", "expense"]),
    )

    # -- dynamically add filters if user provides them --
    if record_type:
        query = query.filter(db_models.FinanceRecord.record_type.ilike(record_type))
    if category:
        query = query.filter(db_models.FinanceRecord.category.ilike(category))
    if start_date:
        query = query.filter(db_models.FinanceRecord.created_at >= start_date)
    if end_date:
        query = query.filter(db_models.FinanceRecord.created_at <= end_date)

    # -- fetches all non-deleted finance records for a user with pagination --
    return query.offset(skip).limit(limit).all()


def get_all_records(
        db          : Session,
        skip        : int = 0,
        limit       : int = 100,
        record_type : Optional[str] = None,
        category    : Optional[str] = None,
        start_date  : Optional[datetime] = None,
        end_date    : Optional[datetime] = None
):
    query = db.query(db_models.FinanceRecord).filter(
        db_models.FinanceRecord.is_deleted == False,
        func.lower(db_models.FinanceRecord.record_type).in_(["income", "expense"]),
    )

    if record_type:
        query = query.filter(db_models.FinanceRecord.record_type.ilike(record_type))
    if category:
        query = query.filter(db_models.FinanceRecord.category.ilike(category))
    if start_date:
        query = query.filter(db_models.FinanceRecord.created_at >= start_date)
    if end_date:
        query = query.filter(db_models.FinanceRecord.created_at <= end_date)

    return query.offset(skip).limit(limit).all()


def soft_delete_record(db: Session, record_id: int, owner_id: int):
    # -- soft deletes a finance record for a user --
    db_record = db.query(db_models.FinanceRecord).filter(
        db_models.FinanceRecord.id == record_id,
        db_models.FinanceRecord.owner_id == owner_id,
        db_models.FinanceRecord.is_deleted == False,
    ).first()

    #-- if record exists and belongs to user, mark as deleted --
    if db_record:
        db_record.is_deleted = True
        db.commit()
        return True
    return False
