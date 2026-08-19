import json
import os
import math
from sqlalchemy.orm import Session
from app.core.database import SessionLocal, Base, engine
from app.models.metro import MetroStation, MetroConnection, MetroFare
from app.models.bus import BusStop, BusRoute, RouteStop, FareRule

SEEDS_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "seeds")

def haversine_km(lat1, lon1, lat2, lon2):
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def calculate_cmrl_fare(distance_km: float) -> float:
    if distance_km <= 2.0:
        return 10.0
    elif distance_km <= 5.0:
        return 20.0
    elif distance_km <= 12.0:
        return 30.0
    elif distance_km <= 21.0:
        return 40.0
    else:
        return 50.0

def seed_database():
    Base.metadata.create_all(bind=engine)
    db: Session = SessionLocal()
    try:
        # Seed Metro Stations
        with open(os.path.join(SEEDS_DIR, "metro_stations.json"), "r") as f:
            stations_data = json.load(f)
            for item in stations_data:
                existing = db.query(MetroStation).filter(MetroStation.id == item["id"]).first()
                if not existing:
                    stn = MetroStation(**item)
                    db.add(stn)
        db.commit()

        # Seed Metro Connections
        with open(os.path.join(SEEDS_DIR, "metro_connections.json"), "r") as f:
            connections_data = json.load(f)
            for item in connections_data:
                # Calculate track distance estimation for secondary display
                from_stn = db.query(MetroStation).filter(MetroStation.id == item["from_station_id"]).first()
                to_stn = db.query(MetroStation).filter(MetroStation.id == item["to_station_id"]).first()
                dist = haversine_km(from_stn.latitude, from_stn.longitude, to_stn.latitude, to_stn.longitude) * 1.2 if from_stn and to_stn else None
                
                existing = db.query(MetroConnection).filter(
                    MetroConnection.from_station_id == item["from_station_id"],
                    MetroConnection.to_station_id == item["to_station_id"]
                ).first()
                if not existing:
                    conn = MetroConnection(
                        from_station_id=item["from_station_id"],
                        to_station_id=item["to_station_id"],
                        travel_time_minutes=item["travel_time_minutes"],
                        estimated_distance_km=round(dist, 2) if dist else None,
                        line=item["line"]
                    )
                    db.add(conn)
        db.commit()

        # Generate & Seed Metro Fares (CALCULATED_FROM_OFFICIAL_RULES)
        all_stations = db.query(MetroStation).all()
        for s1 in all_stations:
            for s2 in all_stations:
                if s1.id != s2.id:
                    existing = db.query(MetroFare).filter(
                        MetroFare.from_station_id == s1.id,
                        MetroFare.to_station_id == s2.id
                    ).first()
                    if not existing:
                        direct_dist = haversine_km(s1.latitude, s1.longitude, s2.latitude, s2.longitude) * 1.3
                        fare = calculate_cmrl_fare(direct_dist)
                        mf = MetroFare(
                            from_station_id=s1.id,
                            to_station_id=s2.id,
                            fare_inr=fare,
                            fare_source_type="CALCULATED_FROM_OFFICIAL_RULES"
                        )
                        db.add(mf)
        db.commit()

        # Seed Bus Stops
        with open(os.path.join(SEEDS_DIR, "bus_stops.json"), "r") as f:
            bus_stops_data = json.load(f)
            for item in bus_stops_data:
                existing = db.query(BusStop).filter(BusStop.id == item["id"]).first()
                if not existing:
                    db.add(BusStop(**item))

        # Seed Bus Routes
        with open(os.path.join(SEEDS_DIR, "bus_routes.json"), "r") as f:
            bus_routes_data = json.load(f)
            for item in bus_routes_data:
                existing = db.query(BusRoute).filter(BusRoute.id == item["id"]).first()
                if not existing:
                    db.add(BusRoute(**item))

        # Seed Route Stops
        with open(os.path.join(SEEDS_DIR, "route_stops.json"), "r") as f:
            route_stops_data = json.load(f)
            for item in route_stops_data:
                existing = db.query(RouteStop).filter(
                    RouteStop.route_id == item["route_id"],
                    RouteStop.stop_id == item["stop_id"]
                ).first()
                if not existing:
                    db.add(RouteStop(**item))

        # Seed Fare Rules
        with open(os.path.join(SEEDS_DIR, "fare_rules.json"), "r") as f:
            fare_rules_data = json.load(f)
            for item in fare_rules_data:
                existing = db.query(FareRule).filter(
                    FareRule.service_category == item["service_category"],
                    FareRule.min_stages == item["min_stages"],
                    FareRule.max_stages == item["max_stages"]
                ).first()
                if not existing:
                    db.add(FareRule(**item))

        db.commit()
        print("Database successfully seeded with verified provenance records!")
    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
        raise e
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
