from fastapi import FastAPI
from database import engine, Base
import models.db_models


Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="Panopticon Engine API",
    description="Finance Intelligence Backend Platform",
    version="1.0.0"
)

@app.get("/health",tags=["System"])
def health_check():
    return {"status": "success", "message":"FastAPI server is running cleanly..."}