from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.scripts.seed_db import seed_database
from app.api.commute import router as commute_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Smart Commute Chennai API - Multi-mode journey comparison and recommendation engine."
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup_event():
    seed_database()

app.include_router(commute_router, prefix=settings.API_V1_STR)

@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "petrol_price_per_litre": settings.PETROL_PRICE_PER_LITRE,
        "default_bike_mileage_kmpl": settings.DEFAULT_BIKE_MILEAGE_KMPL
    }
