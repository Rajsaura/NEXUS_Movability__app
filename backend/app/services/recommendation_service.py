from typing import List, Dict, Any, Tuple
from app.schemas.commute import TransportOption, RecommendedOption

class RecommendationService:
    WEIGHTS = {
        "best_overall": {"time": 0.35, "cost": 0.30, "co2": 0.25, "convenience": 0.10},
        "fastest":      {"time": 0.70, "cost": 0.10, "co2": 0.10, "convenience": 0.10},
        "cheapest":     {"cost": 0.70, "time": 0.10, "co2": 0.10, "convenience": 0.10},
        "greenest":     {"co2": 0.70,  "time": 0.10, "cost": 0.10, "convenience": 0.10}
    }

    @classmethod
    def rank_options(
        cls,
        options: List[TransportOption],
        priority: str = "best_overall"
    ) -> Tuple[List[TransportOption], RecommendedOption]:
        valid_options = [opt for opt in options if opt.is_supported and opt.total_distance_km > 0]
        
        if not valid_options:
            raise ValueError("No supported transport options available to score.")

        weights = cls.WEIGHTS.get(priority, cls.WEIGHTS["best_overall"])

        # Find best values in group (min for time, cost, co2; max for convenience)
        best_time = min(opt.total_time_minutes for opt in valid_options)
        best_cost = min(opt.total_cost_inr for opt in valid_options)
        best_co2 = min(opt.estimated_co2_kg for opt in valid_options)

        # Normalize and score each option
        for opt in valid_options:
            time_score = (best_time / max(opt.total_time_minutes, 0.1)) * 100.0
            cost_score = (best_cost / max(opt.total_cost_inr, 0.1)) * 100.0 if best_cost > 0 and opt.total_cost_inr > 0 else 100.0
            co2_score = (best_co2 / max(opt.estimated_co2_kg, 0.001)) * 100.0
            conv_score = opt.convenience_score

            overall = (
                time_score * weights["time"] +
                cost_score * weights["cost"] +
                co2_score * weights["co2"] +
                conv_score * weights["convenience"]
            )
            opt.overall_score = round(min(100.0, max(0.0, overall)), 1)

        # Sort options descending by overall score
        valid_options.sort(key=lambda x: x.overall_score, reverse=True)
        top_option = valid_options[0]

        # Generate rule-based deterministic explanations
        why_bullets = cls._generate_explanations(top_option, valid_options, priority)

        recommended = RecommendedOption(
            mode=top_option.mode,
            overall_score=top_option.overall_score,
            total_time_minutes=top_option.total_time_minutes,
            total_cost_inr=top_option.total_cost_inr,
            estimated_co2_kg=top_option.estimated_co2_kg,
            why_recommended=why_bullets
        )

        return valid_options, recommended

    @classmethod
    def _generate_explanations(
        cls,
        top: TransportOption,
        all_options: List[TransportOption],
        priority: str
    ) -> List[str]:
        bullets = []
        others = [opt for opt in all_options if opt.mode != top.mode]
        
        if not others:
            bullets.append("Only available transport choice for this journey.")
            return bullets

        # Cost bullet
        cheapest_other = min(others, key=lambda x: x.total_cost_inr)
        if top.total_cost_inr < cheapest_other.total_cost_inr:
            savings = round(cheapest_other.total_cost_inr - top.total_cost_inr, 0)
            bullets.append(f"₹{savings:.0f} cheaper than {cheapest_other.mode.title()}")
        elif top.total_cost_inr == cheapest_other.total_cost_inr:
            bullets.append("Lowest available travel cost")

        # CO2 bullet
        greenest_other = min(others, key=lambda x: x.estimated_co2_kg)
        if top.estimated_co2_kg < greenest_other.estimated_co2_kg:
            reduction_pct = round(((greenest_other.estimated_co2_kg - top.estimated_co2_kg) / greenest_other.estimated_co2_kg) * 100, 0)
            bullets.append(f"{reduction_pct:.0f}% lower estimated emissions than {greenest_other.mode.title()}")

        # Time bullet
        fastest_other = min(all_options, key=lambda x: x.total_time_minutes)
        if top.mode == fastest_other.mode:
            bullets.append("Fastest travel choice")
        else:
            time_diff = round(top.total_time_minutes - fastest_other.total_time_minutes)
            bullets.append(f"Only {time_diff} minutes slower than the fastest option ({fastest_other.mode.title()})")

        # Priority bullet
        bullets.append(f"Highest weighted score for your selected preference ({priority.replace('_', ' ').title()})")

        return bullets
