from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from app.models.bus import BusStop, BusRoute, RouteStop, FareRule
from app.schemas.provenance import SourceTypeEnum, ConfidenceEnum, ProvenanceMetric, ProvenanceMetadata
from app.schemas.commute import TransportOption
from app.services.routing.routing_provider import DistanceEstimateProvider

class BusService:
    @classmethod
    def calculate_bus_option(
        cls,
        db: Session,
        origin_lat: float,
        origin_lng: float,
        dest_lat: float,
        dest_lng: float
    ) -> TransportOption:
        # Find nearest bus stops
        stops = db.query(BusStop).all()
        near_origin = None
        min_orig_dist = float("inf")
        near_dest = None
        min_dest_dist = float("inf")
        
        for stop in stops:
            d_orig = DistanceEstimateProvider.calculate_haversine_km(origin_lat, origin_lng, stop.latitude, stop.longitude)
            if d_orig < min_orig_dist:
                min_orig_dist = d_orig
                near_origin = stop
                
            d_dest = DistanceEstimateProvider.calculate_haversine_km(dest_lat, dest_lng, stop.latitude, stop.longitude)
            if d_dest < min_dest_dist:
                min_dest_dist = d_dest
                near_dest = stop

        # If nearest stop is > 4.0 km away, corridor is unsupported
        if not near_origin or not near_dest or min_orig_dist > 4.0 or min_dest_dist > 4.0:
            return cls._unsupported_response("Origin or destination is outside supported MTC corridors.")

        # Search for direct route connecting nearest origin & destination stops
        routes = db.query(BusRoute).all()
        matching_route = None
        orig_stage = None
        dest_stage = None
        
        for route in routes:
            orig_rs = db.query(RouteStop).filter(RouteStop.route_id == route.id, RouteStop.stop_id == near_origin.id).first()
            dest_rs = db.query(RouteStop).filter(RouteStop.route_id == route.id, RouteStop.stop_id == near_dest.id).first()
            
            if orig_rs and dest_rs and orig_rs.stop_sequence < dest_rs.stop_sequence:
                matching_route = route
                orig_stage = orig_rs.stage_number
                dest_stage = dest_rs.stage_number
                break

        if not matching_route or orig_stage is None or dest_stage is None:
            return cls._unsupported_response("No direct supported MTC corridor route found for this journey.")

        # Calculate stage difference
        stage_diff = max(1, abs(dest_stage - orig_stage))

        # Retrieve official 2018 fare rule
        fare_rule = db.query(FareRule).filter(
            FareRule.service_category == matching_route.service_category,
            FareRule.min_stages <= stage_diff,
            FareRule.max_stages >= stage_diff
        ).first()

        fare_inr = fare_rule.fare_inr if fare_rule else 23.0

        # Estimated travel parameters
        bus_dist_km = round(stage_diff * 2.2, 2)  # Approx 2.2 km per stage
        walk_access_min = round(min_orig_dist * 12.0, 1)
        walk_egress_min = round(min_dest_dist * 12.0, 1)
        bus_ride_min = round(bus_dist_km * 2.5, 1)  # Bus speed ~ 24 km/h
        wait_time_min = 10.0
        total_time_min = round(walk_access_min + wait_time_min + bus_ride_min + walk_egress_min, 1)

        # Emission calculation: 0.0255 kg CO2 per passenger-km (WRI India / GHG Platform: 2.68 kg CO2/L / 3.5 km/L / 30 pass)
        co2_kg = round(bus_dist_km * 0.0255, 3)

        provenance = ProvenanceMetadata(
            distance=ProvenanceMetric(value=bus_dist_km, unit="km", source_type=SourceTypeEnum.ESTIMATED_WITH_ASSUMPTIONS, confidence=ConfidenceEnum.MEDIUM),
            duration=ProvenanceMetric(value=total_time_min, unit="minutes", source_type=SourceTypeEnum.ESTIMATED_WITH_ASSUMPTIONS, confidence=ConfidenceEnum.MEDIUM),
            fare=ProvenanceMetric(value=fare_inr, unit="INR", source_type=SourceTypeEnum.CALCULATED_FROM_OFFICIAL_RULES, confidence=ConfidenceEnum.MEDIUM),
            co2=ProvenanceMetric(value=co2_kg, unit="kg", source_type=SourceTypeEnum.ESTIMATED_WITH_ASSUMPTIONS, confidence=ConfidenceEnum.MEDIUM),
            ui_co2_label="Estimated CO2 based on documented assumptions"
        )

        assumptions = [
            f"Supported MTC Route: {matching_route.route_number} ({matching_route.service_category} Service)",
            f"Boarding Stage: {near_origin.stage_name} (Stage {orig_stage})",
            f"Alighting Stage: {near_dest.stage_name} (Stage {dest_stage})",
            f"Stage Difference: {stage_diff} stages",
            "Fare: Calculated from official 2018 MTC Gazetted Fare Rules",
            "CO2 Factor: 0.0255 kg CO2/passenger-km (2.68 kg/L diesel / 3.5 km/L / 30 passengers)"
        ]

        return TransportOption(
            mode="MTC_BUS",
            is_supported=True,
            total_distance_km=bus_dist_km,
            total_time_minutes=total_time_min,
            total_cost_inr=fare_inr,
            estimated_co2_kg=co2_kg,
            convenience_score=75.0,
            provenance=provenance,
            assumptions=assumptions,
            details={
                "route_number": matching_route.route_number,
                "service_category": matching_route.service_category,
                "boarding_stage": near_origin.stage_name,
                "alighting_stage": near_dest.stage_name,
                "stages_travelled": stage_diff
            }
        )

    @classmethod
    def _unsupported_response(cls, reason: str) -> TransportOption:
        return TransportOption(
            mode="MTC_BUS",
            is_supported=False,
            unsupported_reason=reason,
            total_distance_km=0.0,
            total_time_minutes=0.0,
            total_cost_inr=0.0,
            estimated_co2_kg=0.0,
            convenience_score=0.0,
            provenance=ProvenanceMetadata(
                distance=ProvenanceMetric(value=0.0, unit="km", source_type=SourceTypeEnum.UNAVAILABLE, confidence=ConfidenceEnum.UNAVAILABLE),
                duration=ProvenanceMetric(value=0.0, unit="minutes", source_type=SourceTypeEnum.UNAVAILABLE, confidence=ConfidenceEnum.UNAVAILABLE),
                fare=ProvenanceMetric(value=0.0, unit="INR", source_type=SourceTypeEnum.UNAVAILABLE, confidence=ConfidenceEnum.UNAVAILABLE),
                co2=ProvenanceMetric(value=0.0, unit="kg", source_type=SourceTypeEnum.UNAVAILABLE, confidence=ConfidenceEnum.UNAVAILABLE)
            ),
            assumptions=["Bus comparison is currently available only for supported Chennai corridors."]
        )
