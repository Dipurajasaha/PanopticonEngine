from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

import schemas.api_schemas as api_schemas
import services.analytics_service as analytics_service
from database import get_db
from routers.auth_router import get_current_user
import models.db_models as db_models

router = APIRouter(prefix="/analytics", tags=["Dashboard Analytics"])

@router.get("/summary", response_model=api_schemas.AnalyticsDashboard)
def get_dashboard_summary(
    db          : Session= Depends(get_db),
    current_user: db_models.User = Depends(get_current_user)
):
    return analytics_service.get_user_analytics(db=db, owner_id=current_user.id)