from fastapi import FastAPI
from app.api.routes import router as api_router

app = FastAPI()

# Include the API routes
app.include_router(api_router, prefix="/api/v1")