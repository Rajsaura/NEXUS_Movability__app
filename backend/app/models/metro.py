from sqlalchemy import Column, String, Float, Boolean, Integer, ForeignKey
from app.core.database import Base

class MetroStation(Base):
    __tablename__ = "metro_stations"

    id = Column(String(50), primary_key=True)
    name = Column(String(100), nullable=False)
    line = Column(String(20), nullable=False)  # Blue / Green / Interchange
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    is_interchange = Column(Boolean, default=False)

class MetroConnection(Base):
    __tablename__ = "metro_connections"

    id = Column(Integer, primary_key=True, autoincrement=True)
    from_station_id = Column(String(50), ForeignKey("metro_stations.id"), nullable=False)
    to_station_id = Column(String(50), ForeignKey("metro_stations.id"), nullable=False)
    travel_time_minutes = Column(Float, nullable=False)
    estimated_distance_km = Column(Float, nullable=True)
    line = Column(String(20), nullable=False)

class MetroFare(Base):
    __tablename__ = "metro_fares"

    from_station_id = Column(String(50), ForeignKey("metro_stations.id"), primary_key=True)
    to_station_id = Column(String(50), ForeignKey("metro_stations.id"), primary_key=True)
    fare_inr = Column(Float, nullable=False)
    fare_source_type = Column(String(50), default="CALCULATED_FROM_OFFICIAL_RULES")
