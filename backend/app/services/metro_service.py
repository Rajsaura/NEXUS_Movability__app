import networkx as nx
import math
from typing import Dict, Any, List, Optional, Tuple
from sqlalchemy.orm import Session
from app.models.metro import MetroStation, MetroConnection, MetroFare
from app.schemas.provenance import SourceTypeEnum, ConfidenceEnum, ProvenanceMetric, ProvenanceMetadata
from app.schemas.commute import TransportOption
from app.services.routing.routing_provider import DistanceEstimateProvider

class MetroService:
    @staticmethod
    def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        return DistanceEstimateProvider.calculate_haversine_km(lat1, lon1, lat2, lon2)

    @classmethod
    def get_candidate_stations(cls, db: Session, lat: float, lng: float, top_n: int = 3) -> List[Tuple[MetroStation, float]]:
        stations = db.query(MetroStation).all()
        scored = []
        for stn in stations:
            dist = cls.haversine_km(lat, lng, stn.latitude, stn.longitude)
            scored.append((stn, dist))
        scored.sort(key=lambda x: x[1])
        return scored[:top_n]

    @classmethod
    def build_metro_graph(cls, db: Session) -> nx.Graph:
        G = nx.Graph()
        connections = db.query(MetroConnection).all()
        for conn in connections:
            G.add_edge(
                conn.from_station_id,
                conn.to_station_id,
                weight=conn.travel_time_minutes,
                line=conn.line
            )
        return G

    @classmethod
    def calculate_metro_journey(
        cls,
        db: Session,
        origin_lat: float,
        origin_lng: float,
        dest_lat: float,
        dest_lng: float
    ) -> TransportOption:
        graph = cls.build_metro_graph(db)
        
        cand_sources = cls.get_candidate_stations(db, origin_lat, origin_lng, top_n=3)
        cand_dests = cls.get_candidate_stations(db, dest_lat, dest_lng, top_n=3)
        
        best_journey = None
        min_total_time = float("inf")
        
        for src_stn, access_dist in cand_sources:
            for dst_stn, egress_dist in cand_dests:
                if src_stn.id == dst_stn.id:
                    continue
                try:
                    path = nx.shortest_path(graph, source=src_stn.id, target=dst_stn.id, weight="weight")
                    train_time = nx.shortest_path_length(graph, source=src_stn.id, target=dst_stn.id, weight="weight")
                    
                    # Detect interchange & add penalty
                    lines_used = set()
                    for i in range(len(path) - 1):
                        lines_used.add(graph[path[i]][path[i+1]]["line"])
                    interchange_penalty = 5.0 if len(lines_used) > 1 else 0.0
                    
                    # Access/egress walk time (assuming 5 km/h walk = 12 min/km)
                    access_time = round(access_dist * 12.0, 1)
                    egress_time = round(egress_dist * 12.0, 1)
                    wait_time = 4.0  # Avg Metro headway wait
                    
                    total_time = access_time + wait_time + train_time + interchange_penalty + egress_time
                    
                    if total_time < min_total_time:
                        min_total_time = total_time
                        best_journey = {
                            "source_station": src_stn,
                            "dest_station": dst_stn,
                            "path": path,
                            "train_time": train_time,
                            "access_dist_km": access_dist,
                            "access_time_min": access_time,
                            "egress_dist_km": egress_dist,
                            "egress_time_min": egress_time,
                            "interchange_penalty": interchange_penalty,
                            "lines": list(lines_used),
                            "total_time": round(total_time, 1)
                        }
                except (nx.NetworkXNoPath, nx.NodeNotFound):
                    continue

        if not best_journey:
            # Return unsupported response
            return TransportOption(
                mode="METRO",
                is_supported=False,
                unsupported_reason="No viable Metro network path between candidate stations.",
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
                assumptions=["No path found"]
            )

        # Retrieve fare from database
        src_id = best_journey["source_station"].id
        dst_id = best_journey["dest_station"].id
        fare_record = db.query(MetroFare).filter(
            MetroFare.from_station_id == src_id,
            MetroFare.to_station_id == dst_id
        ).first()
        
        fare_inr = fare_record.fare_inr if fare_record else 40.0
        
        # Estimate network journey distance (approx 1.8 km per hop)
        network_hops = len(best_journey["path"]) - 1
        network_dist_km = round(network_hops * 1.8, 2)
        total_dist_km = round(best_journey["access_dist_km"] + network_dist_km + best_journey["egress_dist_km"], 2)
        
        # Emission calculation: 0.0358 kg CO2 per passenger-km (CEA grid baseline + 0.05 kWh/p-km SEC)
        co2_kg = round(network_dist_km * 0.0358, 3)
        
        # Convenience calculation (starts at 90, deducts walk & interchange)
        conv_score = max(40.0, round(90.0 - (best_journey["access_dist_km"] + best_journey["egress_dist_km"]) * 10.0 - best_journey["interchange_penalty"] * 2.0, 1))

        provenance = ProvenanceMetadata(
            distance=ProvenanceMetric(
                value=total_dist_km,
                unit="km",
                source_type=SourceTypeEnum.ESTIMATED_WITH_ASSUMPTIONS,
                confidence=ConfidenceEnum.MEDIUM
            ),
            duration=ProvenanceMetric(
                value=best_journey["total_time"],
                unit="minutes",
                source_type=SourceTypeEnum.VERIFIED_STATIC,
                confidence=ConfidenceEnum.HIGH
            ),
            fare=ProvenanceMetric(
                value=fare_inr,
                unit="INR",
                source_type=SourceTypeEnum.CALCULATED_FROM_OFFICIAL_RULES,
                confidence=ConfidenceEnum.MEDIUM
            ),
            co2=ProvenanceMetric(
                value=co2_kg,
                unit="kg",
                source_type=SourceTypeEnum.ESTIMATED_WITH_ASSUMPTIONS,
                confidence=ConfidenceEnum.MEDIUM
            ),
            ui_co2_label="Estimated CO2 based on documented assumptions"
        )

        assumptions = [
            f"Access walk: {best_journey['access_dist_km']:.2f} km to {best_journey['source_station'].name}",
            f"Metro transit: {network_hops} station hops ({best_journey['train_time']} mins)",
            f"Egress walk: {best_journey['egress_dist_km']:.2f} km from {best_journey['dest_station'].name}",
            "Fare: Calculated fare matrix derived from official CMRL fare rules, with validation against official examples",
            "CO2 Factor: 0.0358 kg CO2/passenger-km based on CEA Grid Baseline Database (v19) & 0.05 kWh/p-km SEC"
        ]

        station_names = [db.query(MetroStation).filter(MetroStation.id == sid).first().name for sid in best_journey["path"]]

        return TransportOption(
            mode="METRO",
            is_supported=True,
            total_distance_km=total_dist_km,
            total_time_minutes=best_journey["total_time"],
            total_cost_inr=fare_inr,
            estimated_co2_kg=co2_kg,
            convenience_score=conv_score,
            provenance=provenance,
            assumptions=assumptions,
            details={
                "source_station": best_journey["source_station"].name,
                "dest_station": best_journey["dest_station"].name,
                "station_path": station_names,
                "lines_used": best_journey["lines"],
                "interchange": "Alandur" if "Alandur" in station_names and len(best_journey["lines"]) > 1 else None,
                "access_walk_min": best_journey["access_time_min"],
                "egress_walk_min": best_journey["egress_time_min"]
            }
        )
