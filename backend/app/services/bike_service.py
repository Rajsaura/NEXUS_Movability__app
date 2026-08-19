from typing import Dict, Any
from app.core.config import settings
from app.schemas.provenance import SourceTypeEnum, ConfidenceEnum, ProvenanceMetric, ProvenanceMetadata
from app.schemas.commute import TransportOption

class BikeService:
    @staticmethod
    def calculate_bike_option(
        route_info: Dict[str, Any],
        mileage_kmpl: float = settings.DEFAULT_BIKE_MILEAGE_KMPL,
        petrol_price: float = settings.PETROL_PRICE_PER_LITRE
    ) -> TransportOption:
        dist_km = route_info["distance_km"]
        dur_min = route_info["duration_minutes"]
        
        # Fuel calculation
        fuel_litres = dist_km / mileage_kmpl
        cost_inr = round(fuel_litres * petrol_price, 2)
        
        # IPCC dynamic CO2 calculation (2.310 kg CO2 / Litre petrol)
        co2_kg = round(fuel_litres * 2.310, 3)
        
        prov_dist = route_info.get("provenance_distance", ProvenanceMetric(
            value=dist_km, unit="km", source_type=SourceTypeEnum.LIVE_ROUTING, confidence=ConfidenceEnum.HIGH
        ))
        prov_dur = route_info.get("provenance_duration", ProvenanceMetric(
            value=dur_min, unit="minutes", source_type=SourceTypeEnum.LIVE_ROUTING, confidence=ConfidenceEnum.HIGH
        ))
        
        provenance = ProvenanceMetadata(
            distance=prov_dist,
            duration=prov_dur,
            fare=ProvenanceMetric(
                value=cost_inr,
                unit="INR",
                source_type=SourceTypeEnum.CALCULATED_FROM_USER_INPUT,
                confidence=ConfidenceEnum.MEDIUM
            ),
            co2=ProvenanceMetric(
                value=co2_kg,
                unit="kg",
                source_type=SourceTypeEnum.CALCULATED_FROM_USER_INPUT,
                confidence=ConfidenceEnum.MEDIUM
            ),
            ui_co2_label="Estimated CO2 based on documented assumptions"
        )
        
        assumptions = [
            f"User bike mileage: {mileage_kmpl} km/L",
            f"Petrol price used for estimate: ₹{petrol_price:.2f}/L (configurable)",
            "Dynamic IPCC carbon factor: 2.310 kg CO2 per Litre of petrol",
            "Door-to-door direct road journey (Convenience score: 95/100)"
        ]
        
        return TransportOption(
            mode="BIKE",
            is_supported=True,
            total_distance_km=dist_km,
            total_time_minutes=dur_min,
            total_cost_inr=cost_inr,
            estimated_co2_kg=co2_kg,
            convenience_score=95.0,
            provenance=provenance,
            assumptions=assumptions,
            geometry=route_info.get("geometry"),
            details={
                "mileage_kmpl": mileage_kmpl,
                "petrol_price": petrol_price,
                "fuel_used_litres": round(fuel_litres, 2)
            }
        )
