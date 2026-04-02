from sqlalchemy.orm import Session
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

def get_user_records(db: Session, owner_id: int, skip: int = 0, limit: int = 100):
    # -- fetches all non-deleted finance records for a user with pagination --
    return db.query(db_models.FinanceRecord).filter(
        db_models.FinanceRecord.owner_id == owner_id,
        db_models.FinanceRecord.is_deleted == False
    ).offset(skip).limit(limit).all()


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
