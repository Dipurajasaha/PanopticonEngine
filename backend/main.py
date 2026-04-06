from fastapi import FastAPI

from database import engine, Base, SessionLocal
import models.db_models
import services.user_service as user_service

from routers import user_router, finance_router, auth_router, analytics_router

###########################################################################
# -- Create database tables based on SQLAlchemy models --
###########################################################################
Base.metadata.create_all(bind=engine)


##########################################################################
# -- run the SEED SCRIPT --
##########################################################################
def initialize_db():
    db = SessionLocal()
    try: 
        user_service.seed_default_users(db)
    finally:
        db.close()

initialize_db()


###########################################################################
# -- Initialize FastAPI app and include routers --
###########################################################################
app = FastAPI(
    title="Panopticon Engine API",
    description="Finance Intelligence Backend Platform",
    version="1.0.0"
)

app.include_router(auth_router.router) 
app.include_router(user_router.router)
app.include_router(finance_router.router)
app.include_router(analytics_router.router)


# -- Health Check Endpoint --
@app.get("/health",tags=["System"])
def health_check():
    return {"status": "success", "message":"FastAPI server is running cleanly..."}