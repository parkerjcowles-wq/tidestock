import math

SERVICE_LEVEL_Z = {0.85: 1.04, 0.90: 1.28, 0.95: 1.645, 0.99: 2.326}

def safety_stock(avg_demand_per_day: float, std_demand: float, lead_time_days: int, z: float) -> float:
    return z * std_demand * math.sqrt(lead_time_days)

def reorder_point(avg_demand_per_day: float, lead_time_days: int, ss: float) -> float:
    return avg_demand_per_day * lead_time_days + ss

def economic_order_quantity(annual_demand: float, order_cost: float, holding_cost_per_unit: float) -> float:
    if holding_cost_per_unit <= 0:
        return 0.0
    return math.sqrt((2 * annual_demand * order_cost) / holding_cost_per_unit)

def days_of_supply(on_hand: float, avg_daily_demand: float) -> float:
    if avg_daily_demand <= 0:
        return float("inf")
    return on_hand / avg_daily_demand
