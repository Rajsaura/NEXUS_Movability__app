from app.services.recommendation_service import RecommendationService
from app.schemas.commute import TransportOption
from app.schemas.provenance import ProvenanceMetadata, ProvenanceMetric, SourceTypeEnum, ConfidenceEnum

def dummy_provenance():
    return ProvenanceMetadata(
        distance=ProvenanceMetric(value=10.0, unit="km", source_type=SourceTypeEnum.LIVE_ROUTING, confidence=ConfidenceEnum.HIGH),
        duration=ProvenanceMetric(value=30.0, unit="minutes", source_type=SourceTypeEnum.LIVE_ROUTING, confidence=ConfidenceEnum.HIGH),
        fare=ProvenanceMetric(value=50.0, unit="INR", source_type=SourceTypeEnum.CALCULATED_FROM_OFFICIAL_RULES, confidence=ConfidenceEnum.MEDIUM),
        co2=ProvenanceMetric(value=0.5, unit="kg", source_type=SourceTypeEnum.ESTIMATED_WITH_ASSUMPTIONS, confidence=ConfidenceEnum.MEDIUM)
    )

def test_recommendation_ranking_and_priorities():
    bike = TransportOption(
        mode="BIKE", is_supported=True, total_distance_km=20.0, total_time_minutes=30.0,
        total_cost_inr=100.0, estimated_co2_kg=2.5, convenience_score=95.0,
        provenance=dummy_provenance(), assumptions=[]
    )
    metro = TransportOption(
        mode="METRO", is_supported=True, total_distance_km=18.0, total_time_minutes=45.0,
        total_cost_inr=40.0, estimated_co2_kg=0.3, convenience_score=80.0,
        provenance=dummy_provenance(), assumptions=[]
    )
    
    # Test Cheapest priority -> Metro should win (40 INR vs 100 INR)
    ranked_cheap, rec_cheap = RecommendationService.rank_options([bike, metro], priority="cheapest")
    assert rec_cheap.mode == "METRO"
    assert ranked_cheap[0].mode == "METRO"
    assert ranked_cheap[0].overall_score >= ranked_cheap[1].overall_score
    assert len(rec_cheap.why_recommended) > 0
    assert any("cheaper" in bullet.lower() or "cost" in bullet.lower() for bullet in rec_cheap.why_recommended)
    
    # Test Fastest priority -> Bike should win (30 min vs 45 min)
    ranked_fast, rec_fast = RecommendationService.rank_options([bike, metro], priority="fastest")
    assert rec_fast.mode == "BIKE"
    assert ranked_fast[0].mode == "BIKE"
    assert any("fastest" in bullet.lower() for bullet in rec_fast.why_recommended)
    
    # Test Greenest priority -> Metro should win (0.3 kg vs 2.5 kg)
    ranked_green, rec_green = RecommendationService.rank_options([bike, metro], priority="greenest")
    assert rec_green.mode == "METRO"
    assert ranked_green[0].mode == "METRO"
    assert any("emission" in bullet.lower() or "lower" in bullet.lower() for bullet in rec_green.why_recommended)

def test_deterministic_scoring_bounds():
    bike = TransportOption(
        mode="BIKE", is_supported=True, total_distance_km=20.0, total_time_minutes=30.0,
        total_cost_inr=100.0, estimated_co2_kg=2.5, convenience_score=95.0,
        provenance=dummy_provenance(), assumptions=[]
    )
    metro = TransportOption(
        mode="METRO", is_supported=True, total_distance_km=18.0, total_time_minutes=45.0,
        total_cost_inr=40.0, estimated_co2_kg=0.3, convenience_score=80.0,
        provenance=dummy_provenance(), assumptions=[]
    )
    
    ranked_1, _ = RecommendationService.rank_options([bike, metro], priority="best_overall")
    ranked_2, _ = RecommendationService.rank_options([bike, metro], priority="best_overall")
    
    # Verify deterministic output
    assert ranked_1[0].overall_score == ranked_2[0].overall_score
    assert ranked_1[1].overall_score == ranked_2[1].overall_score
    assert 0.0 <= ranked_1[0].overall_score <= 100.0
    assert 0.0 <= ranked_1[1].overall_score <= 100.0
