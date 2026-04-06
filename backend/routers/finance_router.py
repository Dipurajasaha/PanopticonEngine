from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

import schemas.api_schemas as api_schemas
import services.finance_service as finance_service
from database import get_db
from routers.auth_router import RoleChecker
import models.db_models as db_models
import services.audit_service as audit_service
import services.cache_service as cache_service

router = APIRouter(prefix="/records", tags=["Finance Records"])

#############################################################################
# -- Role Access Dependencies --
#############################################################################
allow_admin = RoleChecker(["Admin"])
allow_view_records = RoleChecker(["Admin","Analyst"])
allow_edit_records = RoleChecker(["Admin", "Analyst"])


#############################################################################
# -- Version Endpoint --
#############################################################################
# -- Returns finance data version key --
@router.get("/version")
def get_records_version(
    _current_user: db_models.User = Depends(allow_view_records)
):
    return {"version": cache_service.get_finance_data_version()}


#############################################################################
# -- Record Create Endpoint --
#############################################################################
# -- Creates a new finance record --
@router.post("/", response_model=api_schemas.RecordResponse)
def create_record(
    record            : api_schemas.RecordCreate, 
    background_tasks  : BackgroundTasks,
    db                : Session = Depends(get_db),
    current_user      : db_models.User = Depends(allow_edit_records)
):
    new_record = finance_service.create_finance_record(db=db, record=record, owner_id=current_user.id)

    background_tasks.add_task(
        audit_service.log_action,
        db, current_user.id, "CREATE", "FinanceRecord", f"Created record ID: {new_record.id}"
    )

    cache_service.invalidate_dashboard_cache()
    cache_service.bump_finance_data_version()

    return new_record


#############################################################################
# -- Record Read Endpoint --
#############################################################################
# -- Returns filtered finance records --
@router.get("/", response_model=List[api_schemas.RecordResponse])
def read_records(
    skip            :int = 0, 
    limit           :int = 100, 
    record_type     :Optional[str] = Query(None, description="Filter by 'Income' or 'Expense'"),
    category        :Optional[str] = Query(None, description="Filter by a specific category (e.g. 'Food')"),
    start_date      :Optional[datetime] = Query(None, description="Filter records from this date Onwards"),
    end_date        :Optional[datetime] = Query(None, description="Filter records upto this date"),
    db              :Session = Depends(get_db), 
    current_user    :db_models.User = Depends(allow_view_records)
):
    return finance_service.get_all_records(
        db=db, 
        skip=skip, 
        limit=limit,
        record_type=record_type,
        category=category,
        start_date=start_date,
        end_date=end_date
    )


#############################################################################
# -- Record Delete Endpoint --
#############################################################################
# -- Soft-deletes a finance record --
@router.delete("/{record_id}")
def delete_record(
    record_id         : int, 
    background_tasks  : BackgroundTasks,
    db                : Session = Depends(get_db),
    current_user      : db_models.User = Depends(allow_edit_records)
):
    success = finance_service.soft_delete_record(db=db, record_id=record_id, owner_id=current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Record not found or already deleted")
    
    background_tasks.add_task(
        audit_service.log_action,
        db, current_user.id, "DELETE", "FinanceRecord", f"Soft deleted record ID: {record_id}"
    )
    
    cache_service.invalidate_dashboard_cache()
    cache_service.bump_finance_data_version()

    return {"message": "Record successfully deleted..."}
