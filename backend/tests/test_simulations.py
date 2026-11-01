import pytest
from app.simulation.solar_simulator import SolarSimulator
from app.simulation.transport_simulator import TransportSimulator
from app.simulation.waste_simulator import WasteSimulator
from app.simulation.water_simulator import WaterSimulator

def test_solar_simulation():
    res = SolarSimulator.simulate(
        additional_capacity_kw=100.0,
        generation_yield_kwh_per_kwp=1400.0,
        grid_emission_factor_kg_per_kwh=0.82,
        displacement_ratio=1.0
    )
    assert res["annual_generation_kwh"] == 140000.0
    assert res["avoided_emissions_kgco2e"] == round(140000.0 * 0.82, 2)
    assert res["avoided_emissions_tonnes_co2e"] == round((140000.0 * 0.82) / 1000.0, 2)

def test_transport_simulation():
    res = TransportSimulator.simulate(
        pct_shift_to_public_transit=50.0,
        pct_shift_to_cycling_walking=0.0,
        avg_commute_km_roundtrip=20.0,
        annual_commuting_days=200,
        private_vehicle_users_count=100,
        car_emission_factor=0.175,
        bus_train_emission_factor=0.040
    )
    # 50 commuters shifted. Annual km each = 20 * 200 = 4,000 km.
    # Total km = 200,000 km.
    # Car emissions = 200,000 * 0.175 = 35,000 kg.
    # Transit emissions = 200,000 * 0.040 = 8,000 kg.
    # Avoided = 27,000 kg.
    assert res["commuters_shifted_to_public_transit"] == 50
    assert res["annual_passenger_km_shifted"] == 200000.0
    assert res["avoided_emissions_kgco2e"] == 27000.0

def test_waste_simulation():
    res = WasteSimulator.simulate(
        baseline_annual_waste_kg=50000.0,
        waste_reduction_pct=10.0,
        target_recycling_pct=50.0,
        target_composting_pct=40.0
    )
    # Reduced waste = 45,000 kg
    assert res["projected_total_kg"] == 45000.0
    assert res["landfill_diversion_rate"] == 90.0

def test_water_simulation_disclaimer():
    res = WaterSimulator.simulate(
        baseline_annual_litres=1000000.0,
        fixture_efficiency_reduction_pct=20.0,
        rainwater_cistern_expansion_m3=0.0,
        greywater_reuse_litres_per_day=0.0
    )
    assert res["total_freshwater_saved_litres"] == 200000.0
    assert "embodied" in res["methodology_disclaimer"].lower()

