from pydantic import BaseModel
from enum import Enum
from typing import Any, Optional

class SourceTypeEnum(str, Enum):
    OFFICIAL_DIRECT = "OFFICIAL_DIRECT"
    VERIFIED_STATIC = "VERIFIED_STATIC"
    LIVE_ROUTING = "LIVE_ROUTING"
    CALCULATED_FROM_OFFICIAL_RULES = "CALCULATED_FROM_OFFICIAL_RULES"
    CALCULATED_FROM_USER_INPUT = "CALCULATED_FROM_USER_INPUT"
    ESTIMATED_WITH_ASSUMPTIONS = "ESTIMATED_WITH_ASSUMPTIONS"
    UNAVAILABLE = "UNAVAILABLE"

class ConfidenceEnum(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    UNAVAILABLE = "UNAVAILABLE"

class ProvenanceMetric(BaseModel):
    value: Optional[Any] = None
    unit: str
    source_type: SourceTypeEnum
    confidence: ConfidenceEnum

class ProvenanceMetadata(BaseModel):
    distance: ProvenanceMetric
    duration: ProvenanceMetric
    fare: ProvenanceMetric
    co2: ProvenanceMetric
    ui_co2_label: str = "Estimated CO2 based on documented assumptions"
