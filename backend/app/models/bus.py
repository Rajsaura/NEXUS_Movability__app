from sqlalchemy import Column, String, Float, Integer, ForeignKey
from app.core.database import Base

class BusStop(Base):
    __tablename__ = "bus_stops"

    id = Column(String(50), primary_key=True)
    name = Column(String(100), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    stage_name = Column(String(100), nullable=True)

class BusRoute(Base):
    __tablename__ = "bus_routes"

    id = Column(String(50), primary_key=True)
    route_number = Column(String(20), nullable=False)
    service_category = Column(String(50), nullable=False)  # Ordinary, Express, Deluxe
    origin_stop_id = Column(String(50), ForeignKey("bus_stops.id"))
    destination_stop_id = Column(String(50), ForeignKey("bus_stops.id"))

class RouteStop(Base):
    __tablename__ = "route_stops"

    id = Column(Integer, primary_key=True, autoincrement=True)
    route_id = Column(String(50), ForeignKey("bus_routes.id"), nullable=False)
    stop_id = Column(String(50), ForeignKey("bus_stops.id"), nullable=False)
    stop_sequence = Column(Integer, nullable=False)
    stage_number = Column(Integer, nullable=False)

class FareRule(Base):
    __tablename__ = "fare_rules"

    id = Column(Integer, primary_key=True, autoincrement=True)
    service_category = Column(String(50), nullable=False)
    min_stages = Column(Integer, nullable=False)
    max_stages = Column(Integer, nullable=False)
    fare_inr = Column(Float, nullable=False)
