from fastapi import FastAPI

app = FastAPI(
    title="Panopticon Engine API",
    description="Finance Intelligence Backend Platform",
    version="1.0.0"
)

@app.get("/health",tags=["System"])
def health_check():
    return {"status": "success", "message":"FastAPI server is running cleanly..."}