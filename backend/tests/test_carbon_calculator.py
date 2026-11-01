import pytest
from app.climate.carbon_calculator import CarbonCalculator

def test_electricity_emissions():
    grid_kwh = 1000.0
    factor = 0.82
    emissions = CarbonCalculator.calculate_electricity_emissions(grid_kwh, factor)
    assert emissions == 820.0

def test_diesel_emissions():
    litres = 100.0
    factor = 2.68
    emissions = CarbonCalculator.calculate_diesel_emissions(litres, factor)
    assert emissions == 268.0

def test_transport_emissions():
    passenger_km = 500.0
    factor = 0.175 # Private car
    emissions = CarbonCalculator.calculate_transport_emissions(passenger_km, factor)
    assert emissions == 87.5

def test_waste_emissions_net_accounting():
    # 100 kg to landfill (1.25), 50 kg composted (0.08), 50 kg recycled (-0.65)
    landfill_kg = 100.0
    compost_kg = 50.0
    recycle_kg = 50.0
    # (100*1.25) + (50*0.08) - (50*0.65) = 125 + 4 - 32.5 = 96.5
    emissions = CarbonCalculator.calculate_waste_emissions(landfill_kg, compost_kg, recycle_kg)
    assert emissions == 96.5

