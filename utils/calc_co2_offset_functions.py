
# SOLAR
def calc_solar_energy_offset(avg_sun_duration_hours: float) -> float:
    """
    Calculates co2 emission offset for a solar panel per day based on Swiss energy mix
    and current weather.

    Solar power energy production:
        Formula Solar power: Average hours of sunlight × solar panel watts x 75% = daily watt-hours.
        Source: https://www.dynamicslr.com/a-guide-on-how-to-calculate-solar-panels-output/

    Solar Panel:
        Size: 1.767 x 1.041
        Power: 375-395 Wp -> 385 Wp
        Souce: https://www.meyerburger.com/de/solarmodul

    Swiss Energy Mix Emission:
        Swiss CO2 emission from Energy:
            2021: 33.4 million tones -> 33'400'000'000 kg of carbon dioxide

        Swiss Primary Energy Consumption:
            2021: 1.07 Exajoules -> ~297'222'222'222 kWh

        Swiss CO2 emission per kWh:
            33'400'000'000 / 297'222'222'222 = 0.11237383 CO2/Kg per kWh

        Source: https://www.bp.com/en/global/corporate/energy-economics/statistical-review-of-world-energy/downloads.html

    Returns:
        CO2 offset per day in CO2/KG
    """
    CH_EMISSION_KWH = 0.11237383
    SOLAR_PANEL_POWER = 385
    PERFORMANCE_RATIO = 0.21  # losses due to shading, dirt, dust and other environmental conditions

    solar_power = avg_sun_duration_hours * SOLAR_PANEL_POWER * PERFORMANCE_RATIO / 1000

    offset_solar_power = round(solar_power * CH_EMISSION_KWH, 5)

    return offset_solar_power


# TREES
def calc_trees_offset(num_trees: int) -> float:
    """
    Calculates the co2 emission that is offset by a given number (num_trees) of trees.

    Trees:
        Offset: 10 kg/year -> 0.02739726 kg/day for one tree on average
        Source: https://www.plant-for-the-planet.org/wp-content/uploads/2020/12/faktenblatt_baeume_co2.pdf

    Returns:
        CO2 offset per day in CO2/KG
    """
    TREE_OFFSET_DAILY = 0.02739726

    offset_tree = round(num_trees * TREE_OFFSET_DAILY, 5)

    return offset_tree


# HYDRO
def calc_hydro_offset(flow_rate: float) -> float:
    """
    Calculates the daily co2 emission that is offset by a water wheel with a
    defined water flow in m3/s based on Swiss energy mix.

    Water wheel power:
        Formula: Power = Net head * effective flow rate * water acceleration
        Source: https://en.wikipedia.org/wiki/Water_wheel

    Water wheel assumption:
        Net head: 1 Meter
        Width of the water wheel: 1 Meter

    Aare width:
        40 meters

    Swiss Energy Mix Emission:
        Swiss CO2 emission from Energy:
            2021: 33.4 million tones -> 33'400'000'000 kg of carbon dioxide

        Swiss Primary Energy Consumption:
            2021: 1.07 Exajoules -> ~297'222'222'222 kWh

        Swiss CO2 emission per kWh:
            33'400'000'000 / 297'222'222'222 = 0.11237383 CO2/Kg per kWh

        Source:
        https://www.bp.com/en/global/corporate/energy-economics/statistical-review-of-world-energy/downloads.html


    Returns:
        Hydro power in watts.
    """
    NET_HEAD = 1
    WATER_ACCELERATION = 9.81
    PERFORMANCE_RATIO = 0.21 # Same as solar panel as information can not be estimated
    CH_EMISSION_KWH = 0.11237383

    effective_flow_rate_waterwheel = flow_rate / 40

    # Calculate hydro power in watts
    hydro_power = NET_HEAD * effective_flow_rate_waterwheel * WATER_ACCELERATION

    # Adjust hydro power based on efficiency rating
    adjusted_hydro_power = hydro_power * PERFORMANCE_RATIO

    hydro_kwh_day = adjusted_hydro_power * 24 / 1000

    offset_hydro_power = round(hydro_kwh_day * CH_EMISSION_KWH, 5)

    return offset_hydro_power











