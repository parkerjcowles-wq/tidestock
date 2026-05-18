import math
import pytest
from inventory.model import safety_stock, reorder_point, economic_order_quantity, days_of_supply, SERVICE_LEVEL_Z
from inventory.data import get_avg_daily_demand

def test_safety_stock_95():
    ss = safety_stock(std_demand=2.0, lead_time_days=5, z=SERVICE_LEVEL_Z[0.95])
    assert abs(ss - 7.35) < 0.1  # 1.645 * 2.0 * sqrt(5) ≈ 7.35

def test_safety_stock_zero_std():
    assert safety_stock(0.0, 5, SERVICE_LEVEL_Z[0.95]) == 0.0

def test_reorder_point():
    ss = 7.35
    rop = reorder_point(avg_demand_per_day=5.0, lead_time_days=5, ss=ss)
    assert abs(rop - 32.35) < 0.1  # 5 * 5 + 7.35

def test_eoq():
    eoq = economic_order_quantity(annual_demand=1820, order_cost=12, holding_cost_per_unit=0.50)
    assert abs(eoq - 295.0) < 5.0  # sqrt(2*1820*12/0.5) ≈ 295

def test_days_of_supply():
    assert abs(days_of_supply(on_hand=240, avg_daily_demand=5.0) - 48.0) < 0.1

def test_days_of_supply_zero_demand():
    assert days_of_supply(on_hand=100, avg_daily_demand=0) == float("inf")

def test_eoq_raises_on_zero_holding_cost():
    with pytest.raises(ValueError):
        economic_order_quantity(1820, 12, 0)

def test_get_avg_daily_demand():
    sku = {"avg_weekly_demand": 35}
    assert abs(get_avg_daily_demand(sku) - 5.0) < 0.01
