from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    PROJECT_NAME: str = "Smart Commute Chennai"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api"
    
    # Application Parameters
    PETROL_PRICE_PER_LITRE: float = 100.75
    DEFAULT_BIKE_MILEAGE_KMPL: float = 45.0
    
    # Routing Endpoints
    OSRM_BASE_URL: str = "https://router.project-osrm.org"
    NOMINATIM_BASE_URL: str = "https://nominatim.openstreetmap.org"
    ROUTING_API_KEY: str = ""
    
    # Database Configuration
    DATABASE_URL: str = "sqlite:///./smart_commute.db"
    
    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
