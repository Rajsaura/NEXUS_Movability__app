from app.services.bike_service import BikeService
from app.services.routing.routing_provider import DistanceEstimateProvider
from app.schemas.provenance import SourceTypeEnum, ConfidenceEnum, ProvenanceMetric

def test_bike_calculation():
    route_info = {
        "distance_km": 45.0,
        "duration_minutes": 50.0,
        "geometry": None,
        "provenance_distance": ProvenanceMetric(value=45.0, unit="km", source_type=SourceTypeEnum.LIVE_ROUTING, confidence=ConfidenceEnum.HIGH),
        "provenance_duration": ProvenanceMetric(value=50.0, unit="minutes", source_type=SourceTypeEnum.LIVE_ROUTING, confidence=ConfidenceEnum.HIGH)
    }
    
    # 45 km / 45 km/L = 1.0 L * 100.0 INR/L = 100.0 INR
    option = BikeService.calculate_bike_option(route_info, mileage_kmpl=45.0, petrol_price=100.0)
    
    assert option.mode == "BIKE"
    assert option.is_supported is True
    assert option.total_distance_km == 45.0
    assert option.total_time_minutes == 50.0
    assert option.total_cost_inr == 100.0
    assert option.estimated_co2_kg == 2.31  # 1.0 L * 2.310 kg CO2/L = 2.31 kg
    assert option.provenance.fare.source_type == SourceTypeEnum.CALCULATED_FROM_USER_INPUT
    assert option.provenance.ui_co2_label == "Estimated CO2 based on documented assumptions"

def test_bike_custom_mileage_and_price():
    route_info = {
        "distance_km": 30.0,
        "duration_minutes": 40.0,
        "geometry": None,
        "provenance_distance": ProvenanceMetric(value=30.0, unit="km", source_type=SourceTypeEnum.LIVE_ROUTING, confidence=ConfidenceEnum.HIGH),
        "provenance_duration": ProvenanceMetric(value=40.0, unit="minutes", source_type=SourceTypeEnum.LIVE_ROUTING, confidence=ConfidenceEnum.HIGH)
    }
    
    # 30 km / 60 km/L = 0.5 L * 102.0 INR/L = 51.0 INR
    option = BikeService.calculate_bike_option(route_info, mileage_kmpl=60.0, petrol_price=102.0)
    assert option.total_cost_inr == 51.0
    assert option.estimated_co2_kg == round(0.5 * 2.310, 3)

def test_bike_fallback_distance_provider_on_osrm_failure():
    # VIT Chennai (12.8406, 80.1534) to Chennai Central (13.0827, 80.2757)
    fallback = DistanceEstimateProvider.get_fallback_route(12.8406, 80.1534, 13.0827, 80.2757)
    
    assert fallback["geometry"] is None  # Never fabricate fake road polyline
    assert fallback["distance_km"] > 0
    assert fallback["duration_minutes"] > 0
    assert fallback["provenance_distance"].source_type == SourceTypeEnum.ESTIMATED_WITH_ASSUMPTIONS
    assert fallback["provenance_distance"].confidence == ConfidenceEnum.LOW
    assert fallback["provenance_duration"].source_type == SourceTypeEnum.ESTIMATED_WITH_ASSUMPTIONS
    assert fallback["provenance_duration"].confidence == ConfidenceEnum.LOW
    
    option = BikeService.calculate_bike_option(fallback, mileage_kmpl=45.0, petrol_price=100.75)
    assert option.mode == "BIKE"
    assert option.provenance.distance.source_type == SourceTypeEnum.ESTIMATED_WITH_ASSUMPTIONS
    assert option.provenance.distance.confidence == ConfidenceEnum.LOW
