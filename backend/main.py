from fastapi import FastAPI
from database import engine, Base
import models.db_models

from routers import user_router, finance_router, auth_router, analytics_router

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Panopticon Engine API",
    description="Finance Intelligence Backend Platform",
    version="1.0.0"
)

app.include_router(auth_router.router)
app.include_router(user_router.router)
app.include_router(finance_router.router)
app.include_router(analytics_router.router)



@app.get("/health",tags=["System"])
def health_check():
    return {"status": "success", "message":"FastAPI server is running cleanly..."}