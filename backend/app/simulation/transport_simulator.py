from typing import Dict, Any

class TransportSimulator:
    @staticmethod
    def simulate(
        pct_shift_to_public_transit: float = 20.0,
        pct_shift_to_cycling_walking: float = 10.0,
        avg_commute_km_roundtrip: float = 18.0,
        annual_commuting_days: int = 220,
        private_vehicle_users_count: int = 450,
        car_emission_factor: float = 0.175,
        bus_train_emission_factor: float = 0.041
    ) -> Dict[str, Any]:
        """
        Simulates mode shift from private cars/motorcycles to public transit or active mobility.
        """
        shift_public_count = int(private_vehicle_users_count * (pct_shift_to_public_transit / 100.0))
        shift_active_count = int(private_vehicle_users_count * (pct_shift_to_cycling_walking / 100.0))

        annual_km_per_person = avg_commute_km_roundtrip * annual_commuting_days

        # Baseline emissions for shifting commuters
        baseline_emissions_public_shift = shift_public_count * annual_km_per_person * car_emission_factor
        baseline_emissions_active_shift = shift_active_count * annual_km_per_person * car_emission_factor
        total_baseline_affected = baseline_emissions_public_shift + baseline_emissions_active_shift

        # Proposed emissions
        proposed_emissions_public_shift = shift_public_count * annual_km_per_person * bus_train_emission_factor
        proposed_emissions_active_shift = 0.0 # Active mobility zero direct emission
        total_proposed = proposed_emissions_public_shift + proposed_emissions_active_shift

        avoided_emissions = total_baseline_affected - total_proposed

        return {
            "intervention": "TRANSPORT_MODAL_SHIFT",
            "commuters_shifted_to_public_transit": shift_public_count,
            "commuters_shifted_to_active_mobility": shift_active_count,
            "annual_passenger_km_shifted": round((shift_public_count + shift_active_count) * annual_km_per_person, 2),
            "baseline_affected_emissions_kgco2e": round(total_baseline_affected, 2),
            "projected_emissions_kgco2e": round(total_proposed, 2),
            "avoided_emissions_kgco2e": round(avoided_emissions, 2),
            "avoided_emissions_tonnes_co2e": round(avoided_emissions / 1000.0, 2),
            "assumptions": {
                "avg_roundtrip_km": avg_commute_km_roundtrip,
                "annual_commute_days": annual_commuting_days,
                "private_car_factor": car_emission_factor,
                "public_transit_factor": bus_train_emission_factor
            }
        }

transport_simulator = TransportSimulator()

