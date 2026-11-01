import pytest
from app.climate.projection_engine import ProjectionEngine

def test_linear_projection_net_zero_year():
    baseline_emissions = 2450000.0
    baseline_year = 2024
    annual_reduction = 153125.0
    target_year = 2040

    res = ProjectionEngine.calculate_linear_projection(
        baseline_emissions=baseline_emissions,
        baseline_year=baseline_year,
        annual_reduction_rate_kg=annual_reduction,
        target_year=target_year
    )

    assert res["model_type"] == "LINEAR"
    assert res["projected_net_zero_year"] == 2040
    assert res["achieves_target_by_deadline"] is True
    # At 2040, emissions should reach 0.0
    emissions_2040 = next(t["emissions_kgco2e"] for t in res["trajectory"] if t["year"] == 2040)
    assert emissions_2040 == 0.0

def test_linear_projection_insufficient_reduction():
    baseline_emissions = 2450000.0
    baseline_year = 2024
    annual_reduction = 50000.0 # Only 50k kg/year reduction
    target_year = 2040

    res = ProjectionEngine.calculate_linear_projection(
        baseline_emissions=baseline_emissions,
        baseline_year=baseline_year,
        annual_reduction_rate_kg=annual_reduction,
        target_year=target_year
    )

    assert res["achieves_target_by_deadline"] is False
    assert res["projected_net_zero_year"] > 2040

def test_compound_projection():
    baseline_emissions = 100000.0
    baseline_year = 2024
    annual_rate_pct = 20.0 # 20% annual reduction

    res = ProjectionEngine.calculate_compound_projection(
        baseline_emissions=baseline_emissions,
        baseline_year=baseline_year,
        annual_percentage_rate=annual_rate_pct,
        target_year=2040
    )

    assert res["model_type"] == "COMPOUND"
    # Year 1 (2025): 100000 * 0.8 = 80000
    emissions_2025 = next(t["emissions_kgco2e"] for t in res["trajectory"] if t["year"] == 2025)
    assert round(emissions_2025, 2) == 80000.0

