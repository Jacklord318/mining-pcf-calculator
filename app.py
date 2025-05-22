import streamlit as st
import numpy as np

# GWP and Emission Factors
GWP_FACTORS = {'CO2': 1.0, 'CH4': 25.0, 'N2O': 298.0}
EMISSION_FACTORS = {
    'diesel': {'CO2': 2.68, 'CH4': 0.0001, 'N2O': 0.0001},
    'electricity': {'CO2': 0.5, 'CH4': 0.00001, 'N2O': 0.00001},
    'explosives': {'CO2': 0.25, 'CH4': 0.001, 'N2O': 0.005}
}

def calculate_emissions(activity_data):
    stage_emissions = {}
    total_CO2e = 0.0
    for input_type, quantity in activity_data.items():
        if input_type not in EMISSION_FACTORS:
            continue
        emissions = EMISSION_FACTORS[input_type]
        for gas, factor in emissions.items():
            gas_emission = quantity * factor
            CO2e = gas_emission * GWP_FACTORS[gas]
            stage_emissions[gas] = stage_emissions.get(gas, 0) + gas_emission
            total_CO2e += CO2e
    return total_CO2e, stage_emissions

def calculate_product_carbon_footprint(data):
    total_footprint = 0.0
    stage_results = {}
    for stage, inputs in data.items():
        stage_CO2e, stage_gases = calculate_emissions(inputs)
        stage_results[stage] = {'CO2e': stage_CO2e, 'details': stage_gases}
        total_footprint += stage_CO2e
    return total_footprint, stage_results

def monte_carlo_simulation(base_inputs, num_simulations=1000, variation=0.1):
    results = []
    for _ in range(num_simulations):
        noisy_inputs = {
            stage: {k: np.random.normal(v, v * variation) for k, v in inputs.items()}
            for stage, inputs in base_inputs.items()
        }
        total, _ = calculate_product_carbon_footprint(noisy_inputs)
        results.append(total)
    return results

def main():
    st.set_page_config(page_title="Mining PCF Calculator", page_icon="⛏️")
    st.title("⛏️ Mining Carbon Footprint Calculator")
    st.write("Estimate product-level GHG emissions using LCA data.")

    st.subheader("📥 Input Activity Data (per ton of ore)")
    diesel_ext = st.number_input("Diesel (gallons) - Extraction", 0.0, 1000.0, 8.0 * 3.78541, help="Typical range: 1–100 gallons per ton of ore")
    explosives = st.number_input("Explosives (kg) - Extraction", 0.0, 10.0, 2.0)
    electricity_proc = st.number_input("Electricity (kWh) - Processing", 0.0, 500.0, 150.0)
    diesel_trans = st.number_input("Diesel (gallons) - Transport", 0.0, 30.0, 4.0) * 3.78541
    electricity_waste = st.number_input("Electricity (kWh) - Waste Management", 0.0, 100.0, 20.0)

    lifecycle_data = {
        'extraction': {'diesel': diesel_ext, 'explosives': explosives},
        'processing': {'electricity': electricity_proc},
        'transport': {'diesel': diesel_trans},
        'waste_management': {'electricity': electricity_waste}
    }

    if st.button("Calculate Carbon Footprint"):
        total, breakdown = calculate_product_carbon_footprint(lifecycle_data)
        st.subheader("📊 Carbon Footprint Breakdown:")
        for stage, result in breakdown.items():
            st.markdown(f"**🔹 {stage.capitalize()}: {result['CO2e']:.2f} kg CO₂e**")
            for gas, amount in result['details'].items():
                st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp;- {gas}: {amount:.4f} kg")
        st.success(f"🎯 **Total Product Carbon Footprint: {total:.2f} kg CO₂e / ton of ore**")

    if st.checkbox("Enable Monte Carlo Simulation (uncertainty ±10%)"):
        num_simulations = st.slider("Number of Simulations", 100, 2000, 1000)
        results = monte_carlo_simulation(lifecycle_data, num_simulations)
        st.subheader("📉 Uncertainty Analysis:")
        st.write(f"Mean: {np.mean(results):.2f} kg CO₂e")
        st.write(f"5th–95th percentile: {np.percentile(results, 5):.2f}–{np.percentile(results, 95):.2f} kg CO₂e")
        st.line_chart(results)

if __name__ == "__main__":
    main()
