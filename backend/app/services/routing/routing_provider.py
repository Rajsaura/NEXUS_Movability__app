import httpx
import math
from typing import Dict, Any, Tuple, Optional
from app.core.config import settings
from app.schemas.provenance import SourceTypeEnum, ConfidenceEnum, ProvenanceMetric

class DistanceEstimateProvider:
    """Straight-line fallback provider when live routing service is unavailable."""
    @staticmethod
    def calculate_haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        R = 6371.0
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return R * c

    @classmethod
    def get_fallback_route(cls, origin_lat: float, origin_lng: float, dest_lat: float, dest_lng: float) -> Dict[str, Any]:
        direct_dist = cls.calculate_haversine_km(origin_lat, origin_lng, dest_lat, dest_lng)
        road_dist_est = round(direct_dist * 1.3, 2)  # 1.3 urban detour factor
        
        # Estimate duration assuming 35 km/h avg speed
        duration_min = round((road_dist_est / 35.0) * 60, 1)
        
        return {
            "distance_km": road_dist_est,
            "duration_minutes": duration_min,
            "geometry": None,  # Explicitly do NOT fabricate fake route polylines
            "provenance_distance": ProvenanceMetric(
                value=road_dist_est,
                unit="km",
                source_type=SourceTypeEnum.ESTIMATED_WITH_ASSUMPTIONS,
                confidence=ConfidenceEnum.LOW
            ),
            "provenance_duration": ProvenanceMetric(
                value=duration_min,
                unit="minutes",
                source_type=SourceTypeEnum.ESTIMATED_WITH_ASSUMPTIONS,
                confidence=ConfidenceEnum.LOW
            )
        }

class RoutingProvider:
    """Pluggable OSRM client with LRU memory caching and DistanceEstimateProvider fallback."""
    _cache: Dict[str, Dict[str, Any]] = {}

    @classmethod
    async def get_road_route(cls, origin_lat: float, origin_lng: float, dest_lat: float, dest_lng: float) -> Dict[str, Any]:
        cache_key = f"{origin_lat:.4f},{origin_lng:.4f};{dest_lat:.4f},{dest_lng:.4f}"
        if cache_key in cls._cache:
            return cls._cache[cache_key]

        url = f"{settings.OSRM_BASE_URL}/route/v1/driving/{origin_lng},{origin_lat};{dest_lng},{dest_lat}?overview=full&geometries=geojson"
        
        try:
            async with httpx.AsyncClient(timeout=3.0) as client:
                res = await client.get(url, headers={"User-Agent": "SmartCommuteChennai/1.0"})
                if res.status_code == 200:
                    data = res.json()
                    if data.get("routes"):
                        route = data["routes"][0]
                        dist_km = round(route["distance"] / 1000.0, 2)
                        dur_min = round(route["duration"] / 60.0, 1)
                        geom = route.get("geometry")

                        result = {
                            "distance_km": dist_km,
                            "duration_minutes": dur_min,
                            "geometry": geom,
                            "provenance_distance": ProvenanceMetric(
                                value=dist_km,
                                unit="km",
                                source_type=SourceTypeEnum.LIVE_ROUTING,
                                confidence=ConfidenceEnum.HIGH
                            ),
                            "provenance_duration": ProvenanceMetric(
                                value=dur_min,
                                unit="minutes",
                                source_type=SourceTypeEnum.LIVE_ROUTING,
                                confidence=ConfidenceEnum.HIGH
                            )
                        }
                        cls._cache[cache_key] = result
                        return result
        except Exception as e:
            print(f"OSRM request failed/timed out: {e}. Falling back to DistanceEstimateProvider.")

        # Fallback to DistanceEstimateProvider if OSRM is unreachable
        return DistanceEstimateProvider.get_fallback_route(origin_lat, origin_lng, dest_lat, dest_lng)

    @classmethod
    async def geocode(cls, query: str) -> Tuple[Optional[float], Optional[float], str]:
        url = f"{settings.NOMINATIM_BASE_URL}/search?q={query}+Chennai&format=json&limit=1"
        try:
            async with httpx.AsyncClient(timeout=3.0) as client:
                res = await client.get(url, headers={"User-Agent": "SmartCommuteChennai/1.0"})
                if res.status_code == 200 and res.json():
                    item = res.json()[0]
                    return float(item["lat"]), float(item["lon"]), item.get("display_name", query)
        except Exception as e:
            print(f"Geocoding failed for {query}: {e}")
        return None, None, query
