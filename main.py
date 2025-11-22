from fastapi import FastAPI
from app.routes import router as api_router

app = FastAPI(title="Small FastAPI Backend", version="0.1.0")

app.include_router(api_router, prefix="/api/v1")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
