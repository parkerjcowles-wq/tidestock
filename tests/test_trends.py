from unittest.mock import patch, MagicMock
import pandas as pd
from signals.trends import classify_trend_spike, get_trending_keywords

def test_classify_spike_high():
    assert classify_trend_spike(current=85, baseline=30) == "trending"

def test_classify_spike_moderate():
    assert classify_trend_spike(current=55, baseline=40) == "elevated"

def test_classify_spike_flat():
    assert classify_trend_spike(current=40, baseline=38) == "baseline"

def test_get_trending_keywords_returns_list():
    mock_df = pd.DataFrame(
        {"paddle tail": [20, 25, 80], "ned rig": [30, 28, 32]},
    )
    with patch("signals.trends.TrendReq") as MockTrend:
        instance = MockTrend.return_value
        instance.interest_over_time.return_value = mock_df
        result = get_trending_keywords(["paddle tail", "ned rig"])
    assert isinstance(result, list)
