from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

import schemas.api_schemas as api_schemas
import services.analytics_service as analytics_service
from database import get_db
from routers.auth_router import RoleChecker
import models.db_models as db_models

router = APIRouter(prefix="/analytics", tags=["Dashboard Analytics"])

# -- everyone can view the dashboard --
allow_dashboard = RoleChecker(["Admin","Analyst","Viewer"])

@router.get("/summary", response_model=api_schemas.AnalyticsDashboard)
def get_dashboard_summary(
    db          : Session= Depends(get_db),
    current_user: db_models.User = Depends(allow_dashboard)
):
    return analytics_service.get_global_analytics(db=db)