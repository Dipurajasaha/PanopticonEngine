from fastapi import FastAPI

from database import engine, Base, SessionLocal
import models.db_models
import services.user_service as user_service

from routers import user_router, finance_router, auth_router, analytics_router

#############################################################################
# -- Database Initialization --
#############################################################################
# -- Create tables from ORM models --
Base.metadata.create_all(bind=engine)


#############################################################################
# -- Seed Initialization --
#############################################################################
# -- Seed default users at startup --
def initialize_db():
    db = SessionLocal()
    try: 
        user_service.seed_default_users(db)
    finally:
        db.close()

initialize_db()


#############################################################################
# -- FastAPI Application Setup --
#############################################################################
app = FastAPI(
    title="Panopticon Engine API",
    description="Finance Intelligence Backend Platform",
    version="1.0.0"
)

app.include_router(auth_router.router) 
app.include_router(user_router.router)
app.include_router(finance_router.router)
app.include_router(analytics_router.router)


#############################################################################
# -- System Endpoint --
#############################################################################
@app.get("/health",tags=["System"])
def health_check():
    # -- Returns backend availability status --
    return {"status": "success", "message":"FastAPI server is running cleanly..."}