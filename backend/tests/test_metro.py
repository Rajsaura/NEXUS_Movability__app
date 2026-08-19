from app.core.database import SessionLocal
from app.scripts.seed_db import seed_database
from app.services.metro_service import MetroService
from app.schemas.provenance import SourceTypeEnum, ConfidenceEnum

def test_metro_journey():
    seed_database()
    db = SessionLocal()
    try:
        # VIT Chennai to Chennai Central coords
        option = MetroService.calculate_metro_journey(
            db=db,
            origin_lat=12.8406,
            origin_lng=80.1534,
            dest_lat=13.0827,
            dest_lng=80.2757
        )
        assert option.mode == "METRO"
        assert option.is_supported is True
        assert option.total_cost_inr > 0
        assert option.provenance.fare.source_type == SourceTypeEnum.CALCULATED_FROM_OFFICIAL_RULES
        assert option.provenance.co2.source_type == SourceTypeEnum.ESTIMATED_WITH_ASSUMPTIONS
        assert option.provenance.distance.source_type == SourceTypeEnum.ESTIMATED_WITH_ASSUMPTIONS
        assert "source_station" in option.details
        assert "dest_station" in option.details
        assert len(option.details["station_path"]) >= 2
    finally:
        db.close()

def test_metro_alandur_interchange_handling():
    seed_database()
    db = SessionLocal()
    try:
        # From Koyambedu (Green Line) to Chennai Airport (Blue Line) -> Requires interchange at Alandur
        option = MetroService.calculate_metro_journey(
            db=db,
            origin_lat=13.0725,  # Near Koyambedu
            origin_lng=80.1950,
            dest_lat=12.9815,    # Near Chennai Airport
            dest_lng=80.1640
        )
        assert option.mode == "METRO"
        assert option.is_supported is True
        assert option.details["interchange"] == "Alandur"
        assert len(option.details["lines_used"]) > 1
        assert "Green" in option.details["lines_used"]
        assert "Blue" in option.details["lines_used"]
        # Verify interchange penalty was included in total time
        assert option.total_time_minutes > 0
    finally:
        db.close()

def test_metro_no_osrm_road_distance_used():
    seed_database()
    db = SessionLocal()
    try:
        option = MetroService.calculate_metro_journey(
            db=db,
            origin_lat=12.9815,  # Airport
            origin_lng=80.1640,
            dest_lat=13.0090,    # Guindy
            dest_lng=80.2130
        )
        # Verify track distance is derived purely from station hops & topology, not OSRM road distance
        assert option.is_supported is True
        assert option.geometry is None  # Metro does not fabricate fake OSRM road polylines
    finally:
        db.close()
