import logging
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

import schemas.api_schemas as api_schemas
import services.analytics_service as analytics_service
import services.cache_service as cache_service
from database import get_db
from routers.auth_router import RoleChecker
import models.db_models as db_models

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/analytics", tags=["Dashboard Analytics"])

# -- everyone can view the dashboard --
allow_dashboard = RoleChecker(["Admin", "Analyst", "Viewer"])


@router.get("/version")
def get_analytics_data_version(
    _current_user: db_models.User = Depends(allow_dashboard)
):
    return {"version": cache_service.get_finance_data_version()}

@router.get("/summary", response_model=api_schemas.AnalyticsDashboard)
def get_dashboard_summary(
    db: Session = Depends(get_db),
    _current_user: db_models.User = Depends(allow_dashboard)
):
    cached_data = cache_service.get_dashboard_cache()
    if cached_data is not None:
        logger.info("System Notice: Serving dashboard from Redis Cache")
        return cached_data

    logger.info("System Notice: Cache miss...Calculating dashboard from SQLite...")
    dashboard_data = analytics_service.get_global_analytics(db=db)

    if hasattr(dashboard_data, "model_dump"):
        cache_data_to_save = dashboard_data.model_dump()
    elif hasattr(dashboard_data, 'dict'):
        cache_data_to_save = dashboard_data.dict()
    else:
        cache_data_to_save = dashboard_data

    cache_service.set_dashboard_cache(cache_data_to_save)

    return dashboard_data