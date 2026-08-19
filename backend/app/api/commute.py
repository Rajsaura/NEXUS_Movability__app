from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.config import settings
from app.schemas.commute import CommuteRequest, CommuteResponse
from app.services.routing.routing_provider import RoutingProvider
from app.services.bike_service import BikeService
from app.services.metro_service import MetroService
from app.services.bus_service import BusService
from app.services.recommendation_service import RecommendationService

router = APIRouter(prefix="/commute", tags=["commute"])

@router.post("/compare", response_model=CommuteResponse)
async def compare_commute_options(
    req: CommuteRequest,
    db: Session = Depends(get_db)
):
    # Geocode origin if lat/lng missing
    orig_lat, orig_lng = req.origin.lat, req.origin.lng
    if orig_lat is None or orig_lng is None:
        orig_lat, orig_lng, _ = await RoutingProvider.geocode(req.origin.text)
        if orig_lat is None or orig_lng is None:
            raise HTTPException(status_code=400, detail=f"Could not geocode origin location: '{req.origin.text}'")

    # Geocode destination if lat/lng missing
    dest_lat, dest_lng = req.destination.lat, req.destination.lng
    if dest_lat is None or dest_lng is None:
        dest_lat, dest_lng, _ = await RoutingProvider.geocode(req.destination.text)
        if dest_lat is None or dest_lng is None:
            raise HTTPException(status_code=400, detail=f"Could not geocode destination location: '{req.destination.text}'")

    # 1. Compute Bike option
    bike_route = await RoutingProvider.get_road_route(orig_lat, orig_lng, dest_lat, dest_lng)
    bike_option = BikeService.calculate_bike_option(
        route_info=bike_route,
        mileage_kmpl=req.bike_mileage_kmpl,
        petrol_price=settings.PETROL_PRICE_PER_LITRE
    )

    # 2. Compute Metro option
    metro_option = MetroService.calculate_metro_journey(
        db=db,
        origin_lat=orig_lat,
        origin_lng=orig_lng,
        dest_lat=dest_lat,
        dest_lng=dest_lng
    )

    # 3. Compute Bus option
    bus_option = BusService.calculate_bus_option(
        db=db,
        origin_lat=orig_lat,
        origin_lng=orig_lng,
        dest_lat=dest_lat,
        dest_lng=dest_lng
    )

    options_list = [bike_option, metro_option, bus_option]

    # 4. Score and Rank options
    ranked_options, recommended = RecommendationService.rank_options(
        options=options_list,
        priority=req.priority
    )

    # Re-append unsupported options for full transparency
    unsupported = [opt for opt in options_list if not opt.is_supported]
    all_final_options = ranked_options + unsupported

    return CommuteResponse(
        query={
            "origin": {"text": req.origin.text, "lat": orig_lat, "lng": orig_lng},
            "destination": {"text": req.destination.text, "lat": dest_lat, "lng": dest_lng},
            "priority": req.priority,
            "bike_mileage_kmpl": req.bike_mileage_kmpl
        },
        recommended_option=recommended,
        options=all_final_options,
        assumptions=[
            f"Petrol price used for estimate: ₹{settings.PETROL_PRICE_PER_LITRE:.2f}/L (configurable)",
            "Estimated CO2 based on documented assumptions (IPCC / CPCB / CEA Grid Baseline)",
            "Metro fare derived from official CMRL distance slab rules"
        ],
        configured_parameters={
            "petrol_price_per_litre": settings.PETROL_PRICE_PER_LITRE,
            "default_bike_mileage": settings.DEFAULT_BIKE_MILEAGE_KMPL
        }
    )
