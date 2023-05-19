
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
    PERFORMANCE_RATIO = 0.75  # losses due to shading, dirt, dust and other environmental conditions

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

#
# # HYDRO
# def calc_hydro_offset(flow_rate: float) -> float:
#     """
#     Calculates the daily co2 emission that is offset by a water wheel with a
#     defined water flow in m3/s based on Swiss energy mix.
#
#     Waterwheel:
#         Volume flow rate (Q): flow rate (v) x Effective cross-sectional area of the incoming water (A)
#         Source : https://en.wikipedia.org/wiki/Volumetric_flow_rate
#
#         Sample water wheel:
#             Name: Wyssebacher Sagi
#             Source: https://www.wyssebachersagi.ch/technik/wasserrad/
#
#             flow_rate (v): v = sqrt(2 * g * H)
#                 g: water acceleration of gravity (m/s2) -> 9.81 m/s2
#                 H: fall hight of water wheel. -> 2.75 m
#                 Calculation: sqrt(2 * 9.81 * 2.75) = ~7.34 m/s
#
#             Effective cross-sectional area of incoming water:
#             A = pi * r^2 -> A = pi * (5.5/2)^2 -> 23.75 m2
#
#             Q = A * v -> 23.75 * 7.34 = ~ 174.325 m3/s
#
#
#     Hydro Power:
#         Formula: P = flow_rate * ρ * g * H * η
#             P: Power in kVA
#             Volume flow rate: m3/s
#             p: water density (kg/m3) -> 1000 kg/m3
#             g: water acceleration of gravity (m/s2) -> 9.81 m/s2
#             H: waterfall height -> 5.5 / 2 = 2.75 m
#             η: global efficiency ratio -> 0.7
#
#         Source: https://greener4life.com/Hydroelectric-Power-Calculator
#
#         Watts to kWh:
#             Formula: E(kWh) = (P * t) / 1000
#             Source: https://www.inchcalculator.com/watts-to-kwh-calculator/
#
#     Swiss Energy Mix Emission:
#         Swiss CO2 emission from Energy:
#             2021: 33.4 million tones -> 33'400'000'000 kg of carbon dioxide
#
#         Swiss Primary Energy Consumption:
#             2021: 1.07 Exajoules -> ~297'222'222'222 kWh
#
#         Swiss CO2 emission per kWh:
#             33'400'000'000 / 297'222'222'222 = 0.11237383 CO2/Kg per kWh
#
#         Source: https://www.bp.com/en/global/corporate/energy-economics/statistical-review-of-world-energy/downloads.html
#
#     Returns:
#         CO2 offset per day in CO2/KG
#     """
#     CH_EMISSION_KWH = 0.11237383
#     WATER_DENSITY = 1000
#     WATER_ACCELERATION = 9.81
#     WATERFALL_HEIGHT = 0.1
#     PERFORMANCE_RATIO = 0.7
#     FLOW_RATE_WATERWHEEL = 174.325
#     EFFICIENCY_FACTOR = 0.5  # only 1/2 of wheel submerged
#
#     effective_flow_rate = min(flow_rate, FLOW_RATE_WATERWHEEL * EFFICIENCY_FACTOR)
#
#     hydro_power = effective_flow_rate * WATER_DENSITY * WATER_ACCELERATION * WATERFALL_HEIGHT * PERFORMANCE_RATIO
#     hydro_kwh_day = hydro_power * 24 / 1000
#
#     offset_hydro_power = round(hydro_kwh_day * CH_EMISSION_KWH, 5)
#
#     return offset_hydro_power


def calc_hydro_offset(flow_rate: float) -> float:
    """
    Calculates the hydro power of a water wheel in watts.

    Args:
        net_head (float): Net head distance in meters.
        flow_rate (float): Flow rate in liters per second.
        efficiency (float): Efficiency rating in percentage.

    Returns:
        Hydro power in watts.
    """
    NET_HEAD = 1
    WATER_ACCELERATION = 9.81
    PERFORMANCE_RATIO = 0.7
    CH_EMISSION_KWH = 0.11237383

    effective_flow_rate_waterwheel = flow_rate / 40

    # Calculate hydro power in watts
    hydro_power = NET_HEAD * effective_flow_rate_waterwheel * WATER_ACCELERATION

    # Adjust hydro power based on efficiency rating
    adjusted_hydro_power = hydro_power * PERFORMANCE_RATIO

    hydro_kwh_day = adjusted_hydro_power * 24 / 1000

    offset_hydro_power = round(hydro_kwh_day * CH_EMISSION_KWH, 5)

    return offset_hydro_power











