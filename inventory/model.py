import math

# One-sided z-scores for common inventory service levels
SERVICE_LEVEL_Z = {0.85: 1.04, 0.90: 1.28, 0.95: 1.645, 0.99: 2.326}

def safety_stock(std_demand: float, lead_time_days: int, z: float) -> float:
    return z * std_demand * math.sqrt(lead_time_days)

def reorder_point(avg_demand_per_day: float, lead_time_days: int, ss: float) -> float:
    return avg_demand_per_day * lead_time_days + ss

def economic_order_quantity(annual_demand: float, order_cost: float, holding_cost_per_unit: float) -> float:
    if holding_cost_per_unit <= 0:
        raise ValueError(f"holding_cost_per_unit must be positive, got {holding_cost_per_unit}")
    if annual_demand < 0 or order_cost < 0:
        raise ValueError("annual_demand and order_cost must be non-negative")
    return math.sqrt((2 * annual_demand * order_cost) / holding_cost_per_unit)

def days_of_supply(on_hand: float, avg_daily_demand: float) -> float:
    if avg_daily_demand <= 0:
        return float("inf")
    return on_hand / avg_daily_demand
