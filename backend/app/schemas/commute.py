from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from app.schemas.provenance import ProvenanceMetadata

class LocationInput(BaseModel):
    text: str
    lat: Optional[float] = None
    lng: Optional[float] = None

class CommuteRequest(BaseModel):
    origin: LocationInput
    destination: LocationInput
    departure_time: Optional[str] = None
    bike_mileage_kmpl: float = Field(default=45.0, ge=10.0, le=120.0)
    priority: str = Field(default="best_overall", description="best_overall | fastest | cheapest | greenest")

class TransportOption(BaseModel):
    mode: str  # BIKE | METRO | MTC_BUS
    is_supported: bool = True
    unsupported_reason: Optional[str] = None
    
    total_distance_km: float
    total_time_minutes: float
    total_cost_inr: float
    estimated_co2_kg: float
    convenience_score: float
    overall_score: float = 0.0
    
    provenance: ProvenanceMetadata
    assumptions: List[str]
    geometry: Optional[Dict[str, Any]] = None
    details: Optional[Dict[str, Any]] = None

class RecommendedOption(BaseModel):
    mode: str
    overall_score: float
    total_time_minutes: float
    total_cost_inr: float
    estimated_co2_kg: float
    why_recommended: List[str]

class CommuteResponse(BaseModel):
    query: Dict[str, Any]
    recommended_option: RecommendedOption
    options: List[TransportOption]
    assumptions: List[str]
    configured_parameters: Dict[str, Any]
