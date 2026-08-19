from app.core.database import SessionLocal
from app.scripts.seed_db import seed_database
from app.services.bus_service import BusService
from app.schemas.provenance import SourceTypeEnum, ConfidenceEnum

def test_bus_supported_corridor():
    seed_database()
    db = SessionLocal()
    try:
        # VIT Vandalur (12.8785, 80.0825) to Chennai Central (13.0827, 80.2757) along Route 70G
        option = BusService.calculate_bus_option(
            db=db,
            origin_lat=12.8785,
            origin_lng=80.0825,
            dest_lat=13.0827,
            dest_lng=80.2757
        )
        assert option.mode == "MTC_BUS"
        assert option.is_supported is True
        assert option.details["route_number"] == "70G"
        assert option.details["service_category"] == "Ordinary"
        assert option.details["boarding_stage"] == "Vandalur"
        assert option.details["alighting_stage"] == "Chennai Central"
        assert option.details["stages_travelled"] == 13
        assert option.total_cost_inr == 23.0  # Gazetted 2018 Ordinary rule for >=13 stages
        assert option.provenance.fare.source_type == SourceTypeEnum.CALCULATED_FROM_OFFICIAL_RULES
        assert option.provenance.fare.confidence == ConfidenceEnum.MEDIUM
        assert option.provenance.co2.source_type == SourceTypeEnum.ESTIMATED_WITH_ASSUMPTIONS
        assert option.provenance.distance.source_type == SourceTypeEnum.ESTIMATED_WITH_ASSUMPTIONS
    finally:
        db.close()

def test_bus_unsupported_corridor():
    seed_database()
    db = SessionLocal()
    try:
        # Remote location outside supported corridors
        option = BusService.calculate_bus_option(
            db=db,
            origin_lat=12.0000,
            origin_lng=79.0000,
            dest_lat=12.1000,
            dest_lng=79.1000
        )
        assert option.mode == "MTC_BUS"
        assert option.is_supported is False
        assert "outside supported MTC corridors" in option.unsupported_reason
        assert option.provenance.fare.source_type == SourceTypeEnum.UNAVAILABLE
        assert option.provenance.distance.source_type == SourceTypeEnum.UNAVAILABLE
    finally:
        db.close()
