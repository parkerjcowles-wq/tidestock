import streamlit as st
import pandas as pd
from dotenv import load_dotenv
load_dotenv()

import config


def _trunc(s: str, n: int) -> str:
    if len(s) <= n:
        return s
    cut = s[:n].rsplit(" ", 1)[0].rstrip(" —-")
    return cut + "…" if cut else s[:n] + "…"
import datetime
from signals.noaa import fetch_tide_predictions, fetch_water_temp, get_tide_quality
from signals.weather import fetch_weather, fetch_7day_forecast, compute_weather_demand_mult
from signals.moon import get_week_moon_data, get_moon_phase, get_fishing_score
from signals.reddit_signals import (
    fetch_reddit_signals, fetch_location_reddit_posts,
    get_overall_social_velocity,
    compute_social_fishing_boost, get_sku_demand_signals,
)
from charts.tides import build_tide_chart
from charts.pressure import build_pressure_chart
from charts.moon_calendar import build_moon_strip_html
from charts.inventory_gauges import build_gauge
from charts.days_of_supply import build_dos_chart
from charts.revenue_at_risk import build_revenue_at_risk_chart
from charts.scenario import build_scenario_comparison
from charts.reddit_feed import build_reddit_feed_html, build_catch_intel_cards
from charts.web_report_feed import build_web_report_feed
from signals.web_reports import fetch_web_fishing_reports
from assets.sku_styles import source_badge_html, dos_progress_bar_html, SKU_STYLES
from inventory.model import safety_stock, reorder_point, economic_order_quantity, days_of_supply, SERVICE_LEVEL_Z, stockout_probability
from inventory.data import load_inventory, get_avg_daily_demand, get_std_daily_demand, get_lead_time
from inventory.recommendations import (
    urgency_score, confidence_label, reason_card, why_not_reorder,
    fallback_buyer_brief, gross_margin, revenue_at_risk, newsvendor_order_qty,
)
from inventory.forecast import compute_demand_index, compute_scenario_demand_by_category

st.set_page_config(page_title="TideStock", page_icon="📦", layout="wide")

# ── CSS ──────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
[data-testid="stAppViewContainer"] { background: #111113; }
[data-testid="stSidebar"]          { background: #0e0e10; border-right: 1px solid #2a2a2e; }
[data-testid="stHeader"]           { background: transparent; }
[data-testid="stTabsContent"]      { padding-top: 14px; }

button[data-baseweb="tab"] {
    font-size: 12px !important;
    padding: 8px 14px !important;
    color: #8b8b8f !important;
    letter-spacing: 0.02em !important;
}
button[data-baseweb="tab"][aria-selected="true"] {
    border-bottom: 2px solid #f1f1f3 !important;
    color: #f1f1f3 !important;
}

.kpi-card {
    background: #1c1c1e;
    border: 1px solid #2a2a2e;
    border-radius: 8px;
    padding: 14px 16px;
    margin-bottom: 10px;
}
.kpi-label {
    font-size: 11px;
    color: #8b8b8f;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    margin-bottom: 4px;
}
.kpi-value {
    font-size: 22px;
    font-weight: 700;
    color: #f1f1f3;
    line-height: 1.2;
}
.kpi-sub {
    font-size: 11px;
    color: #8b8b8f;
    margin-top: 2px;
}

.signal-cell {
    background: #1c1c1e;
    border: 1px solid #2a2a2e;
    border-radius: 8px;
    padding: 10px 12px;
    text-align: center;
}
.signal-cell-label {
    font-size: 10px;
    color: #8b8b8f;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: 4px;
}
.signal-cell-value {
    font-size: 14px;
    font-weight: 600;
    color: #f1f1f3;
}

.section-header {
    font-size: 11px;
    font-weight: 700;
    color: #8b8b8f;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin: 20px 0 10px;
    padding-bottom: 6px;
    border-bottom: 1px solid #2a2a2e;
}
.section-header::before {
    content: "◈ ";
    color: #3a3a3e;
}

.badge {
    display: inline-block;
    padding: 2px 8px;
    border-radius: 4px;
    font-size: 11px;
    font-weight: 600;
    font-family: monospace;
    letter-spacing: 0.02em;
}
.badge-critical  { background: #3a0f0f; color: #f87171; }
.badge-reorder   { background: #2c1206; color: #fb923c; }
.badge-watch     { background: #211600; color: #fbbf24; }
.badge-healthy   { background: #061410; color: #4ade80; }
.badge-neutral   { background: #1c1c1e; color: #8b8b8f; border: 1px solid #2a2a2e; }

.card {
    background: #1c1c1e;
    border: 1px solid #2a2a2e;
    border-radius: 8px;
    padding: 14px 16px;
    margin-bottom: 10px;
}
.card-critical  { border-left: 3px solid #f87171 !important; }
.card-reorder   { border-left: 3px solid #fb923c !important; }
.card-watch     { border-left: 3px solid #fbbf24 !important; }
.card-healthy   { border-left: 3px solid #4ade80 !important; }

.detail-panel {
    background: #1c1c1e;
    border: 1px solid #2a2a2e;
    border-radius: 8px;
    padding: 16px 20px;
    margin-top: 10px;
}

.metric-mini {
    background: #111113;
    border-radius: 6px;
    padding: 8px 10px;
}
.metric-mini-label { font-size: 10px; color: #8b8b8f; margin-bottom: 2px; }
.metric-mini-value { font-size: 13px; font-weight: 700; color: #f1f1f3; }

.whatif-active {
    background: #111e30;
    border: 1px solid #1e3a5f;
    border-radius: 6px;
    padding: 8px 12px;
    font-size: 12px;
    color: #93c5fd;
    margin-bottom: 8px;
}

.activity-peak     { background: #0a2810; color: #bbf7d0; padding: 3px 8px; border-radius: 4px; font-size: 11px; font-weight: 600; }
.activity-good     { background: #0f2f14; color: #86efac; padding: 3px 8px; border-radius: 4px; font-size: 11px; font-weight: 600; }
.activity-fair     { background: #211600; color: #fde68a; padding: 3px 8px; border-radius: 4px; font-size: 11px; font-weight: 600; }
.activity-low      { background: #2d1200; color: #fdba74; padding: 3px 8px; border-radius: 4px; font-size: 11px; font-weight: 600; }
.activity-inactive { background: #1c1c1e; color: #6b7280; padding: 3px 8px; border-radius: 4px; font-size: 11px; font-weight: 600; }

.source-row { display: flex; align-items: center; gap: 8px; margin-bottom: 12px; flex-wrap: wrap; }

[data-testid="stMetricValue"] { font-size: 1.4rem !important; color: #f1f1f3 !important; }
[data-testid="stMetricLabel"] { color: #8b8b8f !important; font-size: 11px !important; }

[data-testid="baseButton-primary"] {
    background: #1c1c1e !important;
    border: 1px solid #3a3a3e !important;
    border-radius: 6px !important;
    color: #f1f1f3 !important;
    font-size: 12px !important;
}
[data-testid="baseButton-secondary"] {
    background: #1c1c1e !important;
    border: 1px solid #2a2a2e !important;
    border-radius: 6px !important;
    color: #8b8b8f !important;
    font-size: 12px !important;
}

.js-plotly-plot .plotly .modebar { background: transparent !important; }
</style>
""", unsafe_allow_html=True)

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="padding:14px 0 4px;display:flex;align-items:center;justify-content:space-between">
    <div style="display:flex;align-items:center;gap:10px">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <circle cx="12" cy="6" r="3" stroke="#38bdf8" stroke-width="1.5"/>
            <line x1="12" y1="9" x2="12" y2="22" stroke="#38bdf8" stroke-width="1.5" stroke-linecap="round"/>
            <path d="M6 14c0 0 2 2 6 2s6-2 6-2" stroke="#38bdf8" stroke-width="1.5" stroke-linecap="round"/>
            <line x1="5" y1="22" x2="19" y2="22" stroke="#38bdf8" stroke-width="1.5" stroke-linecap="round"/>
        </svg>
        <span style="font-size:22px;font-weight:700;color:#f1f1f3;letter-spacing:-0.02em">TideStock</span>
        <span style="font-size:12px;color:#8b8b8f">Inventory Command Center · Newburyport, MA</span>
    </div>
    <span style="display:inline-flex;align-items:center;gap:5px;background:#061410;border:1px solid #166534;border-radius:20px;padding:3px 10px;font-size:11px;font-weight:600;color:#4ade80">
        <span style="width:6px;height:6px;background:#4ade80;border-radius:50%;display:inline-block"></span>
        Live
    </span>
</div>
<div style="height:1px;background:#2a2a2e;margin-bottom:12px"></div>
""", unsafe_allow_html=True)

# ── Cached data loaders ───────────────────────────────────────────────────────
@st.cache_data(ttl=3600)
def load_conditions():
    try:
        tide_df = fetch_tide_predictions(config.NOAA_STATION_ID, days=7)
    except Exception:
        tide_df = pd.DataFrame(columns=["time", "height"])
    try:
        water_temp = fetch_water_temp(config.NOAA_STATION_ID)
    except Exception:
        water_temp = 55.0
    try:
        weather = fetch_weather(config.SHOP_LAT, config.SHOP_LON)
    except Exception:
        weather = {
            "pressure_series": pd.DataFrame(columns=["time", "pressure"]),
            "current_temp_f": 65.0, "current_wind_mph": 0.0, "pressure_trend": "stable",
        }
    try:
        forecast = fetch_7day_forecast(config.SHOP_LAT, config.SHOP_LON)
    except Exception:
        forecast = []
    week_moon     = get_week_moon_data()
    today_phase   = get_moon_phase(datetime.date.today())
    tide_quality  = get_tide_quality(tide_df)
    fishing_score = get_fishing_score(today_phase, weather["pressure_trend"])
    weather_mult  = compute_weather_demand_mult(forecast)
    return {
        "tide_df": tide_df, "water_temp": water_temp, "weather": weather,
        "week_moon": week_moon, "today_phase": today_phase,
        "tide_quality": tide_quality, "fishing_score": fishing_score,
        "forecast": forecast, "weather_mult": weather_mult,
        "loaded_at": datetime.datetime.now().strftime("%I:%M %p"),
    }


@st.cache_data(ttl=1800)
def load_social_signals():
    try:
        posts = fetch_reddit_signals(limit=20)
    except Exception:
        posts = []
    try:
        local_posts = fetch_location_reddit_posts(config.REDDIT_LOCATION_QUERY, limit=12)
    except Exception:
        local_posts = []
    return {
        "posts":         posts,
        "local_posts":   local_posts,
        "velocity":      get_overall_social_velocity(posts),
        "fishing_boost": compute_social_fishing_boost(posts),
        "sku_signals":   get_sku_demand_signals(posts),
        "loaded_at":     datetime.datetime.now().strftime("%I:%M %p"),
    }


@st.cache_data(ttl=3600)
def load_web_reports():
    try:
        return fetch_web_fishing_reports(days=14)
    except Exception:
        return []


def build_all_recs(demand_mult: float, delay_days: int, service_pct: float,
                   fishing_score: int, species_now: dict,
                   sku_signals: dict = None, weather_mult: float = 1.0) -> list:
    z         = SERVICE_LEVEL_Z[service_pct]
    inventory = load_inventory()
    month_now = datetime.date.today().month
    striper_active = species_now.get("Striped Bass", "Inactive") in ("Peak", "Good")

    season_map = {1: "off", 2: "off", 3: "shoulder", 4: "shoulder", 5: "peak",
                  6: "peak", 7: "shoulder", 8: "shoulder", 9: "peak", 10: "peak",
                  11: "shoulder", 12: "off"}
    season_level = season_map.get(month_now, "shoulder")

    recs = []
    for sku_key, sku in inventory.items():
        is_seasonal   = sku.get("is_seasonal", False)
        is_perishable = sku.get("is_perishable", False)
        shelf_life    = sku.get("shelf_life_days")
        species_tags  = sku.get("species_tags", [])
        category      = sku.get("category", sku_key)

        eff_mult = demand_mult * weather_mult if is_seasonal else demand_mult
        daily  = get_avg_daily_demand(sku) * eff_mult
        std    = get_std_daily_demand(sku) * eff_mult
        lt     = get_lead_time(sku, config.DEFAULT_LEAD_TIME_DAYS) + delay_days
        ss     = safety_stock(std, lt, z)
        rop    = reorder_point(daily, lt, ss)
        eoq    = economic_order_quantity(
            sku["avg_weekly_demand"] * 52 * eff_mult,
            sku["order_cost"], sku["holding_cost"],
        )
        dos    = days_of_supply(sku["on_hand"], daily)
        margin = gross_margin(sku.get("unit_cost", 0), sku.get("retail_price", 1))
        rev_risk = revenue_at_risk(sku["on_hand"], rop, sku.get("retail_price", 0))

        cat_boost = (sku_signals or {}).get(category, 0)
        score = urgency_score(
            sku["on_hand"], rop, dos, lt, fishing_score, striper_active, sku_key, margin,
            is_seasonal=is_seasonal, is_perishable=is_perishable, shelf_life_days=shelf_life,
            social_sku_boost=cat_boost,
        )
        conf = confidence_label(
            sku["on_hand"], rop, dos, lt, fishing_score, striper_active, sku_key,
            is_seasonal=is_seasonal,
        )
        reasons = reason_card(
            sku_key, sku["on_hand"], rop, dos, lt, fishing_score, striper_active,
            margin, species_now, species_tags=species_tags, is_seasonal=is_seasonal,
        )

        if dos < lt or sku["on_hand"] < rop * 0.5:
            status = "Critical"
        elif sku["on_hand"] < rop or dos < lt * 1.5:
            status = "Reorder Soon"
        elif dos < lt * 2 or sku["on_hand"] < rop * 1.2:
            status = "Watch"
        else:
            status = "Healthy"

        stockout_prob = stockout_probability(sku["on_hand"], daily, std, lt)

        pack = sku.get("reorder_pack_size", 1)
        if is_perishable and shelf_life and daily > 0:
            nv_raw = newsvendor_order_qty(
                daily, std, shelf_life,
                sku.get("unit_cost", 0), sku.get("retail_price", 1),
            )
            order_qty = max(pack, round(nv_raw / pack) * pack) if pack > 0 else max(1, round(nv_raw))
            order_model = "newsvendor"
        else:
            raw_qty = (max(eoq, (rop - sku["on_hand"]) + eoq) if sku["on_hand"] < rop else eoq)
            order_qty = max(pack, round(raw_qty / pack) * pack) if pack > 0 else max(1, round(raw_qty))
            order_model = "eoq"

        recs.append({
            "sku_key":      sku_key,
            "product_name": sku.get("product_name", sku_key),
            "label":        sku.get("product_name", sku_key),
            "category":     category,
            "category_label": config.SKU_CATEGORIES.get(category, category),
            "brand":        sku.get("brand", "—"),
            "supplier":     sku.get("supplier", "—"),
            "species_tags": species_tags,
            "status":       status,
            "urgency":      score,
            "confidence":   conf,
            "reasons":      reasons,
            "on_hand":      sku["on_hand"],
            "unit":         sku["unit"],
            "dos":          dos,
            "lead_time":    lt,
            "rop":          rop,
            "eoq":          eoq,
            "order_qty":    order_qty,
            "order_model":  order_model,
            "stockout_prob": stockout_prob,
            "margin":       margin,
            "rev_risk":     rev_risk,
            "avg_weekly_demand": sku["avg_weekly_demand"],
            "is_perishable": is_perishable,
            "shelf_life":   shelf_life,
            "season_level": season_level,
        })

    STATUS_PRIORITY = {"Critical": 0, "Reorder Soon": 1, "Watch": 2, "Healthy": 3}
    recs.sort(key=lambda r: (STATUS_PRIORITY.get(r["status"], 4), -r["urgency"]))
    return recs


# ── Load data ─────────────────────────────────────────────────────────────────
cond         = load_conditions()
social       = load_social_signals()
web_reports  = load_web_reports()

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div style="font-size:13px;font-weight:600;color:#f1f1f3;margin-bottom:10px">What-If Controls</div>', unsafe_allow_html=True)
    demand_mult_raw = st.slider("Demand Surge", 0.8, 2.0, 1.0, 0.05,
                                help="Simulate tourist season, viral bait moment, or general surge")
    delay_days_raw = st.slider("Supplier Delay (extra days)", 0, 7, 0,
                               help="Add extra days to all supplier lead times")
    bad_weather_raw = st.checkbox("Bad Weather (−20%)", value=False,
                                  help="Cold front or storm — suppresses demand across seasonal SKUs")
    service_pct_raw = st.selectbox("Service Level", [0.85, 0.90, 0.95, 0.99],
                                   index=2, format_func=lambda x: f"{int(x*100)}%")

    demand_mult_final = demand_mult_raw * (0.80 if bad_weather_raw else 1.0)
    st.session_state["demand_mult"]         = demand_mult_final
    st.session_state["delay_days"]          = delay_days_raw
    st.session_state["service_pct_sidebar"] = service_pct_raw

    overrides = []
    if abs(demand_mult_raw - 1.0) > 0.05:
        overrides.append(f"Demand {demand_mult_raw:.2f}×")
    if delay_days_raw > 0:
        overrides.append(f"+{delay_days_raw}d lead time")
    if bad_weather_raw:
        overrides.append("Bad weather −20%")
    if overrides:
        st.markdown(
            f'<div class="whatif-active">Active: {" · ".join(overrides)}</div>',
            unsafe_allow_html=True,
        )

    st.markdown("---")

    # 7-day weather forecast strip
    _fc = cond.get("forecast", [])
    if _fc:
        st.markdown(
            '<div style="font-size:11px;font-weight:600;color:#8b8b8f;'
            'text-transform:uppercase;letter-spacing:0.05em;margin-bottom:8px">'
            '7-Day Forecast</div>',
            unsafe_allow_html=True,
        )
        day_cells = ""
        for _d in _fc:
            _hl = "border:1px solid #3a3a3e;" if _d.get("is_weekend") else ""
            day_cells += (
                f'<div style="text-align:center;flex:1;padding:4px 2px;'
                f'border-radius:6px;{_hl}">'
                f'<div style="font-size:9px;color:#6b7280;margin-bottom:2px">{_d["dow"]}</div>'
                f'<div style="font-size:15px;line-height:1">{_d["emoji"]}</div>'
                f'<div style="font-size:10px;font-weight:700;color:#f1f1f3;margin-top:2px">'
                f'{_d["temp_max"]:.0f}°</div>'
                f'<div style="font-size:9px;color:#60a5fa">{int(_d["precip_pct"])}%</div>'
                f'</div>'
            )
        st.markdown(
            f'<div style="display:flex;gap:2px;background:#1c1c1e;border-radius:8px;'
            f'padding:8px 6px;border:1px solid #2a2a2e">{day_cells}</div>',
            unsafe_allow_html=True,
        )
        _wpct = (cond["weather_mult"] - 1.0) * 100
        _wcolor = "#4ade80" if _wpct >= 0 else "#f87171"
        _wsign  = "+" if _wpct >= 0 else ""
        st.markdown(
            f'<div style="text-align:center;margin-top:5px;font-size:11px;color:{_wcolor}">'
            f'Weather impact: {_wsign}{_wpct:.0f}% demand</div>',
            unsafe_allow_html=True,
        )
        st.markdown("")

    st.markdown('<div style="font-size:11px;color:#8b8b8f;line-height:1.6">'
                '25 SKUs · Newburyport, MA<br>'
                'Environmental: live NOAA/Open-Meteo<br>'
                'Social: live Reddit API<br>'
                'AI Brief: Groq · LLaMA 3'
                '</div>', unsafe_allow_html=True)

# ── Resolve sidebar state ─────────────────────────────────────────────────────
demand_mult  = st.session_state.get("demand_mult", 1.0)
delay_days   = st.session_state.get("delay_days", 0)
service_pct  = st.session_state.get("service_pct_sidebar", config.DEFAULT_SERVICE_LEVEL)

month_now    = datetime.date.today().month
month_name   = datetime.date.today().strftime("%B")
species_now  = config.SPECIES_CALENDAR.get(month_now, {})

# Fishing score = environmental base + social boost (capped at 100)
fishing_score = min(cond["fishing_score"] + social["fishing_boost"], 100)

all_recs = build_all_recs(
    demand_mult, delay_days, service_pct,
    fishing_score, species_now, sku_signals=social["sku_signals"],
    weather_mult=cond["weather_mult"],
)

STATUS_BADGE_CLASS = {
    "Critical":    "badge-critical",
    "Reorder Soon": "badge-reorder",
    "Watch":       "badge-watch",
    "Healthy":     "badge-healthy",
}
CARD_CLASS = {
    "Critical":    "card-critical",
    "Reorder Soon": "card-reorder",
    "Watch":       "card-watch",
    "Healthy":     "card-healthy",
}

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Command Center", "Inventory", "Demand Signals", "Scenario Simulator", "AI Brief"
])

# ════════════════════════════════════════════════════════════════════════════════
# Tab 1 — Command Center
# ════════════════════════════════════════════════════════════════════════════════
with tab1:
    n_critical    = sum(1 for r in all_recs if r["status"] == "Critical")
    n_reorder     = sum(1 for r in all_recs if r["status"] == "Reorder Soon")
    total_rev_risk = sum(r["rev_risk"] for r in all_recs if r["status"] in ("Critical", "Reorder Soon"))
    valid_dos     = [r["dos"] for r in all_recs if r["dos"] < 999]
    avg_dos       = sum(valid_dos) / len(valid_dos) if valid_dos else 0

    st.markdown(
        f'<div style="font-size:10px;color:#6b7280;margin-bottom:6px">'
        f'Env data: {cond["loaded_at"]} · Social data: {social.get("loaded_at", "—")} · '
        f'{datetime.date.today().strftime("%b %d, %Y")}</div>',
        unsafe_allow_html=True,
    )

    avg_lt = sum(r["lead_time"] for r in all_recs) / max(1, len(all_recs))

    hc1, hc2 = st.columns(2)
    with hc1:
        crit_color = "#f87171" if n_critical > 0 else "#4ade80"
        crit_glow  = "box-shadow:0 0 22px rgba(248,113,113,0.22);" if n_critical > 0 else ""
        st.markdown(
            f'<div class="kpi-card" style="border-color:{"#f87171" if n_critical else "#2a2a2e"};{crit_glow};padding:20px 16px">'
            f'<div class="kpi-label">Critical — Order Today</div>'
            f'<div class="kpi-value" style="font-size:38px;color:{crit_color}">{n_critical}</div>'
            f'<div class="kpi-sub">{"SKUs below reorder point" if n_critical else "All SKUs above reorder point"}</div>'
            f'</div>', unsafe_allow_html=True)
    with hc2:
        risk_color = "#f87171" if total_rev_risk > 200 else "#fb923c" if total_rev_risk > 0 else "#4ade80"
        st.markdown(
            f'<div class="kpi-card" style="padding:20px 16px">'
            f'<div class="kpi-label">Revenue at Risk</div>'
            f'<div class="kpi-value" style="font-size:38px;color:{risk_color}">${total_rev_risk:,.0f}</div>'
            f'<div class="kpi-sub">critical + reorder SKUs</div>'
            f'</div>', unsafe_allow_html=True)

    sc1, sc2, sc3 = st.columns(3)
    with sc1:
        st.markdown(
            f'<div class="kpi-card"><div class="kpi-label">Total SKUs</div>'
            f'<div class="kpi-value">{len(all_recs)}</div>'
            f'<div class="kpi-sub">across 7 categories</div></div>', unsafe_allow_html=True)
    with sc2:
        ro_color = "#fb923c" if n_reorder > 0 else "#f1f1f3"
        ro_glow  = "box-shadow:0 0 18px rgba(251,146,60,0.18);" if n_reorder > 0 else ""
        st.markdown(
            f'<div class="kpi-card" style="{ro_glow}"><div class="kpi-label">Reorder Soon</div>'
            f'<div class="kpi-value" style="color:{ro_color}">{n_reorder}</div>'
            f'<div class="kpi-sub">this week</div></div>', unsafe_allow_html=True)
    with sc3:
        dos_color = "#f87171" if avg_dos < 7 else "#fbbf24" if avg_dos < 14 else "#f1f1f3"
        st.markdown(
            f'<div class="kpi-card"><div class="kpi-label">Avg Days of Supply</div>'
            f'<div class="kpi-value" style="color:{dos_color}">{avg_dos:.0f}d</div>'
            f'<div class="kpi-sub">vs. {avg_lt:.0f}d avg lead time</div></div>', unsafe_allow_html=True)

    st.markdown(
        '<div style="font-size:10px;color:#6b7280;margin:4px 0 16px;line-height:1.6">'
        'ROP = daily demand × lead time + safety stock (z = 1.64 at 95% service level) · '
        'EOQ = √(2DS/H) · DoS = on-hand ÷ daily demand · '
        'Rev at Risk = (ROP − on-hand) × retail price for at-risk SKUs</div>',
        unsafe_allow_html=True,
    )

    # Signal snapshot
    st.markdown('<div class="section-header">Signal Snapshot</div>', unsafe_allow_html=True)
    sc1, sc2, sc3, sc4, sc5, sc6 = st.columns(6)
    moon_label = cond["today_phase"].replace("_", " ").title()
    moon_val_map = {"New": "🌑", "Full": "🌕", "Waxing Crescent": "🌒", "Waxing Gibbous": "🌔",
                    "First Quarter": "🌓", "Waning Gibbous": "🌖", "Last Quarter": "🌗", "Waning Crescent": "🌘"}
    moon_sym     = moon_val_map.get(moon_label, "🌙")
    tide_color   = {"prime": "#4ade80", "moderate": "#fbbf24", "poor": "#f87171"}.get(cond["tide_quality"], "#8b8b8f")
    pressure_color = {"rising": "#4ade80", "stable": "#fbbf24", "falling": "#f87171"}.get(cond["weather"]["pressure_trend"], "#8b8b8f")
    social_vel   = social["velocity"]
    social_color = {"trending": "#f87171", "elevated": "#fbbf24", "baseline": "#8b8b8f"}.get(social_vel, "#8b8b8f")
    score_color  = "#4ade80" if fishing_score >= 80 else "#fbbf24" if fishing_score >= 60 else "#8b8b8f"
    temp_color   = "#4ade80" if 55 <= cond["water_temp"] <= 68 else "#fbbf24" if cond["water_temp"] < 50 else "#8b8b8f"
    boost_label  = f"+{social['fishing_boost']} social" if social["fishing_boost"] > 0 else ""

    for col, lbl, val, vcolor, sub in [
        (sc1, "Moon Phase",    f"{moon_sym} {moon_label}",                        "#f1f1f3",    ""),
        (sc2, "Tide Quality",  cond["tide_quality"].capitalize(),                  tide_color,   ""),
        (sc3, "Water Temp",    f"{cond['water_temp']:.1f}°F",                     temp_color,   ""),
        (sc4, "Pressure",      cond["weather"]["pressure_trend"].capitalize(),     pressure_color, ""),
        (sc5, "Social Signal", social_vel.capitalize(),                            social_color, "post velocity"),
        (sc6, "Fishing Score", f"{fishing_score}/100",                             score_color,  boost_label),
    ]:
        with col:
            sub_html = (
                f'<div style="font-size:10px;color:#4ade80;margin-top:2px">{sub}</div>'
                if sub else ""
            )
            st.markdown(
                f'<div class="signal-cell">'
                f'<div class="signal-cell-label">{lbl}</div>'
                f'<div class="signal-cell-value" style="color:{vcolor}">{val}</div>'
                f'{sub_html}'
                f'</div>',
                unsafe_allow_html=True,
            )

    # Live Catch Reports
    _catch_html = build_catch_intel_cards(social["posts"])
    if _catch_html:
        st.markdown('<div class="section-header">Live Catch Reports</div>', unsafe_allow_html=True)
        st.markdown(_catch_html, unsafe_allow_html=True)

    # Inventory table
    st.markdown('<div class="section-header">Inventory Status</div>', unsafe_allow_html=True)
    st.markdown(
        '<div style="font-size:10px;color:#6b7280;margin:-8px 0 8px">'
        'Demo seed data — modeled after a real bait shop workflow. Not connected to live POS data.</div>',
        unsafe_allow_html=True,
    )

    _STATUS_SHORT = {"Critical": "Critical", "Reorder Soon": "Reorder", "Watch": "Watch", "Healthy": "Healthy"}
    table_rows = []
    for r in all_recs:
        dos_display = f"{r['dos']:.0f}d" if r["dos"] < 999 else "—"
        table_rows.append({
            "Product":         r["product_name"],
            "Category":        r["category_label"],
            "On Hand":         f"{r['on_hand']} {r['unit']}",
            "DoS":             dos_display,
            "Status":          _STATUS_SHORT.get(r["status"], r["status"]),
            "Stockout Risk":   r["stockout_prob"] * 100,
            "Rev at Risk":     f"${r['rev_risk']:,.0f}" if r["rev_risk"] > 0 else "—",
            "Urgency":         r["urgency"],
        })
    table_df = pd.DataFrame(table_rows)

    event = st.dataframe(
        table_df,
        on_select="rerun",
        selection_mode="single-row",
        use_container_width=True,
        hide_index=True,
        column_config={
            "Product":       st.column_config.TextColumn("Product",       width="medium"),
            "Category":      st.column_config.TextColumn("Category",      width="small"),
            "On Hand":       st.column_config.TextColumn("On Hand",       width="small"),
            "DoS":           st.column_config.TextColumn("DoS",           width="small"),
            "Status":        st.column_config.TextColumn("Status",        width="small"),
            "Stockout Risk": st.column_config.ProgressColumn("Stockout Risk", min_value=0, max_value=100, format="%.0f%%", width="medium"),
            "Rev at Risk":   st.column_config.TextColumn("Rev at Risk",   width="small"),
            "Urgency":       st.column_config.ProgressColumn("Urgency",   min_value=0, max_value=100, format="%d", width="medium"),
        },
    )

    selected_rows = event.selection.rows
    selected_idx = selected_rows[0] if selected_rows else 0
    if True:
        r = all_recs[selected_idx]
        sbadge = STATUS_BADGE_CLASS.get(r["status"], "badge-neutral")
        cc = {"High": "#4ade80", "Medium": "#fbbf24", "Low": "#8b8b8f"}[r["confidence"]]
        dos_bar = dos_progress_bar_html(r["dos"], r["lead_time"], r["status"])
        sku_style = SKU_STYLES.get(r["category"], {})
        accent = sku_style.get("accent", "#8b8b8f")
        sp = r["stockout_prob"]
        sp_color = "#f87171" if sp >= 0.6 else "#fbbf24" if sp >= 0.3 else "#4ade80"
        nv_badge = '<span style="font-size:9px;color:#a78bfa;margin-left:4px">NV</span>' if r["order_model"] == "newsvendor" else ""
        st.markdown(
            f'<div class="detail-panel" style="border-left:3px solid {accent}">'
            f'<div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:12px">'
            f'<div>'
            f'<div style="font-size:15px;font-weight:700;color:#f1f1f3;margin-bottom:2px">{r["product_name"]}</div>'
            f'<div style="font-size:11px;color:#8b8b8f">{r["brand"]} · {r["supplier"]}</div>'
            f'</div>'
            f'<div style="display:flex;gap:6px;align-items:center">'
            f'<span class="badge {sbadge}">{r["status"]}</span>'
            f'<span style="font-size:11px;font-weight:600;color:{cc}">{r["confidence"]} confidence</span>'
            f'</div>'
            f'</div>'
            f'{dos_bar}'
            f'<div style="display:grid;grid-template-columns:repeat(6,1fr);gap:8px;margin:12px 0">'
            f'<div class="metric-mini"><div class="metric-mini-label">On Hand</div><div class="metric-mini-value">{r["on_hand"]} {r["unit"]}</div></div>'
            f'<div class="metric-mini"><div class="metric-mini-label">Reorder Pt</div><div class="metric-mini-value">{r["rop"]:.0f} {r["unit"]}</div></div>'
            f'<div class="metric-mini"><div class="metric-mini-label">Stockout Risk</div><div class="metric-mini-value" style="color:{sp_color}">{sp:.0%}</div></div>'
            f'<div class="metric-mini"><div class="metric-mini-label">Gross Margin</div><div class="metric-mini-value">{r["margin"]:.0%}</div></div>'
            f'<div class="metric-mini"><div class="metric-mini-label">Rev at Risk</div><div class="metric-mini-value" style="color:#fb923c">${r["rev_risk"]:.0f}</div></div>'
            f'<div class="metric-mini"><div class="metric-mini-label">Order Qty</div><div class="metric-mini-value" style="color:#7dd3fc">{r["order_qty"]:.0f} {r["unit"]}{nv_badge}</div></div>'
            f'</div>'
            f'<div style="font-size:12px;color:#8b8b8f;border-top:1px solid #2a2a2e;padding-top:10px;line-height:1.7">'
            f'<span style="color:#6b6b6f">Business:</span> {r["reasons"]["business"]}<br>'
            f'<span style="color:#6b6b6f">Calculation:</span> {r["reasons"]["calc"]}<br>'
            f'<span style="color:#6b6b6f">Demand signal:</span> {r["reasons"]["demand"]}'
            f'</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

    st.markdown('<div class="section-header" style="margin-top:24px">Buyer Action Summary</div>', unsafe_allow_html=True)
    _brief = fallback_buyer_brief(all_recs, species_now, fishing_score)
    st.markdown(
        f'<div class="card" style="border-left:3px solid #7dd3fc;font-size:13px;line-height:1.8;color:#c8c8cc">{_brief}</div>',
        unsafe_allow_html=True,
    )

# ════════════════════════════════════════════════════════════════════════════════
# Tab 2 — Inventory
# ════════════════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown(
        f'<div class="source-row">'
        f'<span style="font-size:10px;color:#8b8b8f">25 SKUs · Newburyport, MA · '
        f'Service level {int(service_pct * 100)}% · '
        f'{"Demand ×" + f"{demand_mult:.2f}" if abs(demand_mult - 1.0) > 0.05 else "Baseline demand"}'
        f'</span></div>',
        unsafe_allow_html=True,
    )

    st.markdown('<div class="section-header">Stock Gauges — Top SKUs by Urgency</div>', unsafe_allow_html=True)
    top9 = all_recs[:9]
    inventory = load_inventory()
    gauge_cols = st.columns(3)
    for i, rec in enumerate(top9):
        sku = inventory[rec["sku_key"]]
        max_val = max(sku["on_hand"] * 1.5, rec["rop"] * 2.5, 1)
        with gauge_cols[i % 3]:
            st.plotly_chart(
                build_gauge(_trunc(rec["product_name"], 34), sku["on_hand"], max_val, sku["unit"], rop=rec["rop"]),
                use_container_width=True,
            )

    st.markdown('<div class="section-header">Days of Supply — All SKUs</div>', unsafe_allow_html=True)
    dos_data = [{"label": r["product_name"], "dos": min(r["dos"], 60), "urgency": r["status"]} for r in all_recs]
    _avg_lt_days = round(sum(r["lead_time"] for r in all_recs) / max(1, len(all_recs)))
    st.plotly_chart(build_dos_chart(dos_data, lead_time_days=_avg_lt_days), use_container_width=True)

    st.markdown('<div class="section-header">Revenue at Risk</div>', unsafe_allow_html=True)
    st.plotly_chart(
        build_revenue_at_risk_chart([{"product_name": r["product_name"], "rev_risk": r["rev_risk"], "status": r["status"]} for r in all_recs]),
        use_container_width=True,
    )

    flagged = [r for r in all_recs if r["urgency"] >= 30]
    if flagged:
        st.markdown('<div class="section-header">Reorder Actions</div>', unsafe_allow_html=True)
        for rec in flagged:
            sbadge = STATUS_BADGE_CLASS.get(rec["status"], "badge-neutral")
            card_cls = CARD_CLASS.get(rec["status"], "")
            dos_bar = dos_progress_bar_html(rec["dos"], rec["lead_time"], rec["status"])
            sku_style = SKU_STYLES.get(rec["category"], {})
            accent = sku_style.get("accent", "#8b8b8f")
            cc = {"High": "#4ade80", "Medium": "#fbbf24", "Low": "#8b8b8f"}[rec["confidence"]]
            perishable_note = ' · <span style="color:#fb923c;font-size:10px">Perishable</span>' if rec["is_perishable"] else ""
            sku_accent = sku_style.get("accent", "#8b8b8f")
            _cat_codes = {
                "soft_plastics": "SOFT", "hard_baits": "HARD", "bait": "BAIT",
                "terminal_tackle": "TERM", "bucktails_jigs": "JIGS",
                "line_leaders": "LINE", "accessories": "ACCS",
            }
            _cat_code = _cat_codes.get(rec["category"], rec["category"][:4].upper())
            cat_tag = (
                f'<span style="background:rgba(0,0,0,0.3);border:1px solid {sku_accent}33;'
                f'color:{sku_accent};padding:1px 6px;border-radius:3px;font-size:9px;'
                f'font-weight:700;font-family:monospace;letter-spacing:0.05em;margin-right:6px">'
                f'{_cat_code}</span>'
            )
            st.markdown(f"""
<div class="card {card_cls}">
  <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:10px">
    <div>
      <div style="font-size:14px;font-weight:700;color:#f1f1f3">{cat_tag}{rec['product_name']}</div>
      <div style="font-size:11px;color:#8b8b8f">{rec['brand']} · {rec['supplier']}{perishable_note}</div>
    </div>
    <div style="display:flex;gap:6px;align-items:center;flex-wrap:wrap;justify-content:flex-end">
      <span class="badge {sbadge}">{rec['status']}</span>
      <span class="badge badge-neutral">Urgency {rec['urgency']}/100</span>
      <span style="color:{cc};font-size:11px;font-weight:600">{rec['confidence']}</span>
    </div>
  </div>
  {dos_bar}
  <div style="display:grid;grid-template-columns:repeat(6,1fr);gap:8px;margin:10px 0">
    <div class="metric-mini"><div class="metric-mini-label">On Hand</div><div class="metric-mini-value">{rec['on_hand']} {rec['unit']}</div></div>
    <div class="metric-mini"><div class="metric-mini-label">Reorder Pt</div><div class="metric-mini-value">{rec['rop']:.0f} {rec['unit']}</div></div>
    <div class="metric-mini"><div class="metric-mini-label">Stockout Risk</div><div class="metric-mini-value" style="color:{'#f87171' if rec['stockout_prob'] >= 0.6 else '#fbbf24' if rec['stockout_prob'] >= 0.3 else '#4ade80'}">{rec['stockout_prob']:.0%}</div></div>
    <div class="metric-mini"><div class="metric-mini-label">Gross Margin</div><div class="metric-mini-value">{rec['margin']:.0%}</div></div>
    <div class="metric-mini"><div class="metric-mini-label">Rev at Risk</div><div class="metric-mini-value" style="color:#fb923c">${rec['rev_risk']:.0f}</div></div>
    <div class="metric-mini"><div class="metric-mini-label">Order Qty</div><div class="metric-mini-value" style="color:#7dd3fc">{rec['order_qty']:.0f} {rec['unit']}{"<span style='font-size:9px;color:#a78bfa;margin-left:4px'>NV</span>" if rec['order_model'] == 'newsvendor' else ""}</div></div>
  </div>
  <div style="font-size:12px;color:#8b8b8f;border-top:1px solid #2a2a2e;padding-top:8px;line-height:1.7">
    <span style="color:#6b6b6f">Business:</span> {rec['reasons']['business']}<br>
    <span style="color:#6b6b6f">Calculation:</span> {rec['reasons']['calc']}<br>
    <span style="color:#6b6b6f">Demand signal:</span> {rec['reasons']['demand']}
  </div>
</div>""", unsafe_allow_html=True)

    healthy = [r for r in all_recs if r["urgency"] < 20]
    if healthy:
        st.markdown('<div class="section-header">No Action Needed</div>', unsafe_allow_html=True)
        for rec in healthy:
            why = why_not_reorder(rec["product_name"], rec["dos"], rec["lead_time"], rec["rop"], rec["on_hand"])
            st.markdown(
                f'<div style="padding:7px 12px;background:#061410;border-radius:6px;'
                f'font-size:12px;color:#4ade80;margin-bottom:5px">✓ {why}</div>',
                unsafe_allow_html=True,
            )

# ════════════════════════════════════════════════════════════════════════════════
# Tab 3 — Demand Signals
# ════════════════════════════════════════════════════════════════════════════════
with tab3:
    from signals.trends import fetch_trends_data, get_trending_keywords_from_df
    from signals.tournament import fetch_tournaments
    from charts.fishing_forecast import build_fishing_forecast_chart

    @st.cache_data(ttl=1800)
    def load_trends_tournaments():
        try:
            trend_df = fetch_trends_data(config.FISHING_KEYWORDS)
        except Exception:
            trend_df = None
        trend_kws = get_trending_keywords_from_df(trend_df, config.FISHING_KEYWORDS)
        try:
            tournaments = fetch_tournaments(config.SHOP_REGION)
        except Exception:
            tournaments = []
        return trend_kws, trend_df, tournaments, datetime.datetime.now().strftime("%I:%M %p")

    # Reuse top-level social signals; load trends/tournaments separately
    posts            = social["posts"]
    velocity         = social["velocity"]
    trend_kws, trend_df, tournaments, social_loaded_at = load_trends_tournaments()

    s1, s2 = st.columns([6, 1])
    with s1:
        velocity_color = {"trending": "#f87171", "elevated": "#fbbf24", "baseline": "#8b8b8f"}[velocity]
        st.markdown(
            f'<div class="source-row">'
            f'{source_badge_html("noaa", "Tides")} '
            f'{source_badge_html("meteo", "Pressure")} '
            f'{source_badge_html("reddit", "Public API")} '
            f'{source_badge_html("exa", "Tournaments")} '
            f'<span style="font-size:10px;color:#8b8b8f">· Env: {cond["loaded_at"]} · Social: {social["loaded_at"]}</span> '
            f'<span class="badge badge-neutral" style="color:{velocity_color}">Social: {velocity}</span>'
            f'</div>',
            unsafe_allow_html=True,
        )
    with s2:
        if st.button("Refresh", key="refresh_signals"):
            load_conditions.clear()
            load_social_signals.clear()
            load_trends_tournaments.clear()
            st.rerun()

    alerts = [k for k in trend_kws if k["velocity"] in ("trending", "elevated")]
    st.session_state["trend_alerts"] = [
        f'{a["keyword"]} +{a["pct_change"]}% ({a["velocity"]})' for a in alerts
    ]
    if alerts:
        st.markdown('<div class="section-header">Trend Alerts</div>', unsafe_allow_html=True)
        chips = " ".join(
            f'<span class="badge badge-critical">▲ {a["keyword"].title()} +{a["pct_change"]}%</span>'
            if a["velocity"] == "trending" else
            f'<span class="badge badge-watch">↑ {a["keyword"].title()} +{a["pct_change"]}%</span>'
            for a in alerts
        )
        st.markdown(chips, unsafe_allow_html=True)

    # Environmental
    st.markdown('<div class="section-header">Environmental — ' + month_name + '</div>', unsafe_allow_html=True)
    env1, env2 = st.columns(2)
    with env1:
        st.plotly_chart(build_tide_chart(cond["tide_df"]), use_container_width=True)
    with env2:
        st.plotly_chart(build_pressure_chart(cond["weather"]["pressure_series"], cond["weather"]["pressure_trend"]), use_container_width=True)

    st.markdown('<div class="section-header">Moon Phase — 7-Day</div>', unsafe_allow_html=True)
    st.markdown(build_moon_strip_html(cond["week_moon"]), unsafe_allow_html=True)

    # Species
    st.markdown('<div class="section-header">Species Activity</div>', unsafe_allow_html=True)
    SPECIES_ICONS = {"Striped Bass": "🎣", "Flounder": "🐟", "Largemouth Bass": "🎣"}
    ACTIVITY_BG = {
        "Peak":     "rgba(34,197,94,0.09)",
        "Good":     "rgba(134,239,172,0.06)",
        "Fair":     "rgba(251,191,36,0.06)",
        "Low":      "rgba(249,115,22,0.06)",
        "Inactive": "rgba(107,114,128,0.04)",
    }
    sp_cols = st.columns(len(species_now))
    for col, (sp, level) in zip(sp_cols, species_now.items()):
        css_class = f"activity-{level.lower()}"
        icon = SPECIES_ICONS.get(sp, "🐠")
        bg   = ACTIVITY_BG.get(level, "rgba(107,114,128,0.04)")
        with col:
            st.markdown(
                f'<div class="card" style="text-align:center;padding:16px 10px;background:{bg}">'
                f'<div style="font-size:26px;margin-bottom:8px">{icon}</div>'
                f'<div style="font-size:11px;color:#8b8b8f;margin-bottom:8px">{sp}</div>'
                f'<span class="{css_class}">{level}</span></div>',
                unsafe_allow_html=True,
            )

    # Web fishing reports (Exa) — full width above Reddit
    st.markdown('<div class="section-header">Fishing Reports — Web, Bait Shops & Forums</div>', unsafe_allow_html=True)
    st.markdown(
        '<div style="font-size:10px;color:#6b7280;margin:-8px 0 10px">'
        'OnTheWater · The Fisherman · StripersOnline · local bait shop reports · last 14 days</div>',
        unsafe_allow_html=True,
    )
    wr_cols = st.columns(2)
    half = max(1, (len(web_reports) + 1) // 2)
    with wr_cols[0]:
        st.markdown(build_web_report_feed(web_reports[:half], max_items=half), unsafe_allow_html=True)
    with wr_cols[1]:
        st.markdown(build_web_report_feed(web_reports[half:], max_items=half), unsafe_allow_html=True)

    # Social
    social_left, social_right = st.columns([1, 1])
    with social_left:
        local_posts = social.get("local_posts", [])
        if local_posts:
            st.markdown(
                '<div class="section-header">Plum Island / Newburyport — Local Reports</div>',
                unsafe_allow_html=True,
            )
            st.markdown(build_reddit_feed_html(local_posts, max_posts=4), unsafe_allow_html=True)
            st.markdown('<div class="section-header" style="margin-top:18px">Regional Fishing Feed</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="section-header">Regional Fishing Feed</div>', unsafe_allow_html=True)
        if posts:
            st.markdown(build_reddit_feed_html(posts), unsafe_allow_html=True)
        else:
            st.markdown('<div class="card" style="color:#8b8b8f;text-align:center;padding:20px">'
                        'No Reddit posts loaded — public API may be temporarily throttled.</div>',
                        unsafe_allow_html=True)

    with social_right:
        st.markdown('<div class="section-header">7-Day Fishing Quality Forecast</div>', unsafe_allow_html=True)
        st.plotly_chart(
            build_fishing_forecast_chart(cond["week_moon"], cond["forecast"]),
            use_container_width=True,
        )

        st.markdown('<div class="section-header">Tournament Calendar</div>', unsafe_allow_html=True)
        if tournaments:
            from html import escape
            for t in tournaments:
                safe_title = escape(t["title"])[:70]
                raw_url = t.get("url", "")
                safe_url = escape(raw_url) if raw_url.startswith(("https://", "http://")) else "#"
                days = t.get("days_until", "")
                days_badge = f'<span class="badge badge-watch">{days}d away</span>' if days else ""
                st.markdown(
                    f'<div class="card" style="padding:10px 14px">'
                    f'<div style="display:flex;justify-content:space-between;align-items:center">'
                    f'<span style="color:#fbbf24;font-size:13px">{safe_title}</span>'
                    f'{days_badge}</div>'
                    f'<a href="{safe_url}" style="color:#8b8b8f;font-size:11px">Source →</a></div>',
                    unsafe_allow_html=True,
                )
        else:
            st.markdown('<div class="card" style="color:#8b8b8f;font-size:12px">'
                        'No upcoming tournaments found for this region.</div>', unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════════
# Tab 4 — Scenario Simulator
# ════════════════════════════════════════════════════════════════════════════════
with tab4:
    st.markdown('<div class="section-header">Mode A — Signal Weight Sliders</div>', unsafe_allow_html=True)
    st.caption("Adjust how much each environmental/social signal contributes to demand. Updates in real time. All sliders at 1.0 = neutral baseline — not current live conditions.")

    col_sliders, col_chart = st.columns([1, 2])
    with col_sliders:
        weights = {
            "moon":       st.slider("Moon Phase",      0.0, 1.0, 1.0, 0.1, key="w_moon"),
            "tide":       st.slider("Tide Quality",    0.0, 1.0, 1.0, 0.1, key="w_tide"),
            "social":     st.slider("Social Velocity", 0.0, 1.0, 1.0, 0.1, key="w_social"),
            "pressure":   st.slider("Pressure",        0.0, 1.0, 1.0, 0.1, key="w_pressure"),
            "tournament": st.slider("Tournament",      0.0, 1.0, 1.0, 0.1, key="w_tournament"),
            "season":     st.slider("Season",          0.0, 1.0, 1.0, 0.1, key="w_season"),
        }
        weekend_boost = st.checkbox("Weekend Boost (+25%)", value=False)

    season_map_s = {1: "off", 2: "off", 3: "shoulder", 4: "shoulder", 5: "peak",
                    6: "peak", 7: "shoulder", 8: "shoulder", 9: "peak", 10: "peak",
                    11: "shoulder", 12: "off"}
    boost = 1.25 if weekend_boost else 1.0

    # Build per-category base demands (sum weekly demand across SKUs in each category)
    cat_base = {}
    for r in all_recs:
        cat_base[r["category"]] = cat_base.get(r["category"], 0) + r["avg_weekly_demand"]

    weighted_cat = {
        cat: compute_demand_index(
            base_demand=base * boost,
            moon_phase=cond["today_phase"],
            tide_quality=cond["tide_quality"],
            social_velocity="baseline",
            pressure_trend=cond["weather"]["pressure_trend"],
            tournament_proximity="none",
            season_level=season_map_s.get(month_now, "shoulder"),
            weights=weights,
        )
        for cat, base in cat_base.items()
    }

    with col_chart:
        total_base = sum(cat_base.values())
        total_weighted = sum(weighted_cat.values())
        avg_mult = total_weighted / total_base if total_base else 1.0
        direction = "above" if avg_mult > 1.1 else "below" if avg_mult < 0.9 else "near"
        mult_color = "#4ade80" if avg_mult > 1.05 else "#f87171" if avg_mult < 0.95 else "#fbbf24"
        st.markdown(
            f'<div style="display:flex;gap:10px;align-items:center;margin-bottom:8px">'
            f'<span class="badge badge-neutral" style="color:{mult_color};font-size:13px">'
            f'Demand Index {avg_mult:.2f}× baseline — {direction} normal</span>'
            f'</div>',
            unsafe_allow_html=True,
        )
        sku_labels = {k: v for k, v in config.SKU_CATEGORIES.items()}
        st.plotly_chart(
            build_scenario_comparison(cat_base, weighted_cat, sku_labels, subtitle="Signal Weights"),
            use_container_width=True,
        )

    st.markdown("---")
    st.markdown('<div class="section-header">Mode B — Preset Scenarios</div>', unsafe_allow_html=True)

    SCENARIO_LABELS = {
        "tournament_weekend": "Tournament This Weekend",
        "viral_bait_moment":  "Viral Bait Moment",
        "cold_front":         "Cold Front Incoming",
        "striper_run_peak":   "Striper Run Peak",
        "tourist_season":     "Tourist Season",
        "supplier_delay":     "Supplier Delay",
    }
    SCENARIO_DESCRIPTIONS = {
        "tournament_weekend": "Local tournament drives finesse tackle and soft plastic demand up sharply.",
        "viral_bait_moment":  "A bait goes viral — soft plastic demand 3× baseline.",
        "cold_front":         "Cold front suppresses activity — bait and soft plastics drop 30–40%.",
        "striper_run_peak":   "Striper migration peak — paddle tails and bucktails in high demand.",
        "tourist_season":     "Summer tourists — accessories and hard baits spike 40–60%.",
        "supplier_delay":     "Key supplier running 3+ days late — models urgency under extended lead times.",
    }

    active_scenario = st.radio(
        "Select a scenario", list(SCENARIO_LABELS.keys()),
        format_func=lambda k: SCENARIO_LABELS[k], index=None,
    )

    if active_scenario:
        # Compute scenario demands by category
        sku_items = [(r["sku_key"], r["avg_weekly_demand"], r["category"]) for r in all_recs]
        scenario_sku_demands = compute_scenario_demand_by_category(sku_items, active_scenario)

        # Aggregate to category level for chart
        cat_scenario = {}
        for r in all_recs:
            cat_scenario[r["category"]] = (
                cat_scenario.get(r["category"], 0) + scenario_sku_demands.get(r["sku_key"], r["avg_weekly_demand"])
            )

        total_scen = sum(cat_scenario.values())
        overall_pct = (total_scen - total_base) / total_base * 100 if total_base else 0
        pct_color = "#4ade80" if overall_pct > 0 else "#f87171"
        pct_sign  = "+" if overall_pct > 0 else ""
        st.markdown(
            f'<div class="whatif-active">'
            f'<b>{SCENARIO_LABELS[active_scenario]}</b> · '
            f'<span style="color:{pct_color}">{pct_sign}{overall_pct:.0f}% total demand shift</span>'
            f' · {SCENARIO_DESCRIPTIONS[active_scenario]}'
            f'</div>',
            unsafe_allow_html=True,
        )
        st.plotly_chart(
            build_scenario_comparison(cat_base, cat_scenario, sku_labels, subtitle=SCENARIO_LABELS[active_scenario]),
            use_container_width=True,
        )

        # SKU status changes table
        st.markdown('<div class="section-header">SKU Status Under This Scenario</div>', unsafe_allow_html=True)
        status_rows = []
        for r in all_recs:
            scen_demand = scenario_sku_demands.get(r["sku_key"], r["avg_weekly_demand"])
            scen_dos = days_of_supply(r["on_hand"], scen_demand / 7) if scen_demand > 0 else 999
            lt = r["lead_time"]
            if scen_dos < lt or r["on_hand"] < r["rop"] * 0.5:
                scen_status = "Critical"
            elif r["on_hand"] < r["rop"] or scen_dos < lt * 1.5:
                scen_status = "Reorder Soon"
            elif scen_dos < lt * 2 or r["on_hand"] < r["rop"] * 1.2:
                scen_status = "Watch"
            else:
                scen_status = "Healthy"
            changed = scen_status != r["status"]
            delta = scen_demand - r["avg_weekly_demand"]
            status_rows.append({
                "Product":        r["product_name"],
                "Category":       r["category_label"],
                "Baseline Status": r["status"],
                "Scenario Status": scen_status,
                "Demand Delta":   f"+{delta:.0f}" if delta >= 0 else f"{delta:.0f}",
                "Changed":        "Yes" if changed else "",
            })
        status_df = pd.DataFrame(status_rows)
        st.dataframe(status_df, use_container_width=True, hide_index=True)

        st.session_state["active_scenario"]       = active_scenario
        st.session_state["active_scenario_label"] = SCENARIO_LABELS[active_scenario]
    else:
        st.session_state.pop("active_scenario", None)

# ════════════════════════════════════════════════════════════════════════════════
# Tab 5 — AI Brief (Dave)
# ════════════════════════════════════════════════════════════════════════════════
with tab5:
    from ai.brief import build_brief_prompt, generate_brief_streaming, build_ask_dave_prompt
    import re as _re

    def _dave_md(text: str) -> str:
        """Convert the AI's markdown output to HTML for rendering inside a styled div."""
        import html as _html
        lines = text.split("\n")
        out = []
        for line in lines:
            # Section headers: ## 📦 Reorder Now
            if line.startswith("## "):
                content = line[3:].strip()
                out.append(
                    f'<div style="font-size:13px;font-weight:700;color:#f1f1f3;'
                    f'margin:18px 0 8px;padding-bottom:5px;border-bottom:1px solid #2a2a3e">'
                    f'{content}</div>'
                )
            # Bullet lines: • **Product** — reason
            elif line.startswith("• ") or line.startswith("- "):
                content = line[2:].strip()
                # Bold: **text**
                content = _re.sub(r'\*\*(.+?)\*\*', r'<strong style="color:#f1f1f3">\1</strong>', content)
                out.append(
                    f'<div style="display:flex;gap:8px;margin-bottom:6px;padding-left:4px">'
                    f'<span style="color:#38bdf8;flex-shrink:0;margin-top:1px">•</span>'
                    f'<span>{content}</span></div>'
                )
            elif line.strip() == "" or line.strip() == "---":
                out.append('<div style="height:6px"></div>')
            else:
                content = _re.sub(r'\*\*(.+?)\*\*', r'<strong style="color:#f1f1f3">\1</strong>', line)
                out.append(f'<div style="margin-bottom:4px">{content}</div>')
        return "".join(out)

    social_velocity = social["velocity"]
    trend_alerts    = st.session_state.get("trend_alerts", [])
    active_scenario = st.session_state.get("active_scenario_label", None)

    # ── Build inventory context ───────────────────────────────────────────────
    inv_summary = {}
    for cat_key, cat_label in config.SKU_CATEGORIES.items():
        cat_recs = [r for r in all_recs if r["category"] == cat_key]
        if not cat_recs:
            continue
        critical_count = sum(1 for r in cat_recs if r["status"] == "Critical")
        valid = [r["dos"] for r in cat_recs if r["dos"] < 999]
        avg_dos_cat = sum(valid) / len(valid) if valid else 0
        worst_urgency = max((r["urgency"] for r in cat_recs), default=0)
        urgency_label = "Order Today" if worst_urgency >= 55 else "This Week" if worst_urgency >= 30 else "Monitor"
        inv_summary[cat_label] = {"dos": avg_dos_cat, "urgency": urgency_label, "critical_skus": critical_count}

    critical_skus = [r for r in all_recs if r["status"] in ("Critical", "Reorder Soon")]

    conditions_ctx = {
        "date":           datetime.date.today().isoformat(),
        "moon_phase":     cond["today_phase"],
        "tide_quality":   cond["tide_quality"],
        "pressure_trend": cond["weather"]["pressure_trend"],
        "water_temp":     cond["water_temp"],
        "fishing_score":  cond["fishing_score"],
        "species":        species_now,
    }

    # ── Dave avatar & header ─────────────────────────────────────────────────
    dave_svg = """
<svg width="72" height="72" viewBox="0 0 72 72" fill="none" xmlns="http://www.w3.org/2000/svg">
  <circle cx="36" cy="36" r="35" fill="#1c1c1e" stroke="#3a3a3e" stroke-width="1.5"/>
  <!-- Hat brim -->
  <ellipse cx="36" cy="26" rx="22" ry="5.5" fill="#78350f"/>
  <!-- Hat crown -->
  <rect x="20" y="13" width="32" height="14" rx="4" fill="#92400e"/>
  <!-- Hat band -->
  <rect x="20" y="24" width="32" height="4" fill="#451a03"/>
  <!-- Hat highlight -->
  <rect x="22" y="15" width="10" height="3" rx="1.5" fill="#b45309" opacity="0.5"/>
  <!-- Skin -->
  <ellipse cx="36" cy="46" rx="16" ry="14" fill="#d97706" opacity="0.25"/>
  <!-- Eyes -->
  <circle cx="30" cy="42" r="3" fill="#f1f1f3"/>
  <circle cx="42" cy="42" r="3" fill="#f1f1f3"/>
  <circle cx="30.8" cy="42" r="1.8" fill="#1c1c1e"/>
  <circle cx="42.8" cy="42" r="1.8" fill="#1c1c1e"/>
  <circle cx="31.3" cy="41.4" r="0.6" fill="white"/>
  <circle cx="43.3" cy="41.4" r="0.6" fill="white"/>
  <!-- Smile -->
  <path d="M 29 51 Q 36 57 43 51" stroke="#f1f1f3" stroke-width="2" fill="none" stroke-linecap="round"/>
  <!-- Rod -->
  <line x1="52" y1="8" x2="68" y2="30" stroke="#92400e" stroke-width="2.2" stroke-linecap="round"/>
  <line x1="68" y1="30" x2="70" y2="48" stroke="#94a3b8" stroke-width="1" stroke-dasharray="2,2"/>
  <circle cx="70" cy="49" r="1.5" fill="#60a5fa" opacity="0.7"/>
</svg>"""

    brief_time = st.session_state.get("dave_brief_time", "")
    time_label = f"Generated at {brief_time}" if brief_time else "Generating now…"
    moon_label = cond["today_phase"].replace("_", " ").title()
    score_color = "#4ade80" if fishing_score >= 80 else "#fbbf24" if fishing_score >= 60 else "#f87171"

    st.markdown(f"""
<div style="background:linear-gradient(135deg,#1a1a2e 0%,#1c1c1e 60%,#0f2018 100%);
    border:1px solid #2a2a4e;border-radius:14px;padding:20px 24px;margin-bottom:18px">
  <div style="display:flex;align-items:center;gap:20px">
    <div style="flex-shrink:0">{dave_svg}</div>
    <div style="flex:1">
      <div style="font-size:22px;font-weight:800;color:#f1f1f3;letter-spacing:-0.02em">Dave's Morning Intel</div>
      <div style="font-size:12px;color:#8b8b8f;margin-top:2px">Dave's Bait &amp; Tackle · Newburyport, MA · Plum Island</div>
      <div style="display:flex;gap:8px;flex-wrap:wrap;margin-top:10px">
        <span class="badge badge-neutral" style="color:#93c5fd">{moon_label}</span>
        <span class="badge badge-neutral" style="color:#7dd3fc">{cond['water_temp']:.0f}°F water</span>
        <span class="badge badge-neutral" style="color:#a78bfa">{cond['weather']['pressure_trend'].capitalize()} pressure</span>
        <span class="badge badge-neutral" style="color:{score_color}">Fishing {fishing_score}/100</span>
        <span class="badge badge-neutral" style="color:#fbbf24">Social: {social_velocity.capitalize()}</span>
      </div>
    </div>
    <div style="flex-shrink:0;text-align:right">
      <div style="font-size:10px;color:#6b7280">{time_label}</div>
      <div style="font-size:10px;color:#6b7280;margin-top:2px">Powered by Groq · LLaMA 3</div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

    # ── Auto-generate brief ───────────────────────────────────────────────────
    brief_placeholder = st.empty()

    def _render_brief(text: str) -> str:
        return (
            f'<div style="background:#111318;border:1px solid #2a2a3e;border-radius:10px;'
            f'padding:22px 26px;line-height:1.85;font-size:13.5px;color:#c8c8cc">'
            f'{text}'
            f'</div>'
        )

    _dave_posts = [
        p for p in social["posts"]
        if p["sentiment"] == "catching" and p["bait_mentions"]
    ][:4]
    _dave_reports = web_reports[:3]

    if "dave_brief" not in st.session_state:
        prompt = build_brief_prompt(
            conditions=conditions_ctx,
            inventory_summary=inv_summary,
            social_velocity=social_velocity,
            trend_alerts=trend_alerts,
            tournaments=[],
            active_scenario=active_scenario,
            service_level=service_pct,
            critical_skus=critical_skus,
            social_posts=_dave_posts,
            web_reports=_dave_reports,
        )
        full_brief = ""
        for chunk in generate_brief_streaming(prompt):
            full_brief += chunk
            brief_placeholder.markdown(_render_brief(full_brief), unsafe_allow_html=True)
        st.session_state["dave_brief"] = full_brief
        st.session_state["dave_brief_time"] = datetime.datetime.now().strftime("%I:%M %p")
        st.session_state["dave_intel_posts"] = _dave_posts
        st.session_state["dave_intel_reports"] = _dave_reports
        st.rerun()
    else:
        brief_placeholder.markdown(_render_brief(_dave_md(st.session_state["dave_brief"])), unsafe_allow_html=True)

    _intel_posts = st.session_state.get("dave_intel_posts", [])
    _intel_reports = st.session_state.get("dave_intel_reports", [])

    if _intel_posts or _intel_reports:
        cards_html = []

        for p in _intel_posts:
            bait_pills = "".join(
                f'<span style="background:#1a2a1a;color:#4ade80;border:1px solid #2a4a2a;'
                f'border-radius:4px;padding:1px 6px;font-size:10px;font-family:monospace">'
                f'{b}</span>'
                for b in p.get("bait_mentions", [])
            )
            cards_html.append(
                f'<div style="display:flex;align-items:flex-start;gap:10px;padding:10px 14px;'
                f'background:#1a1a1e;border:1px solid #2a2a2e;border-radius:8px;margin-bottom:8px">'
                f'<span style="background:#431407;color:#fb923c;border:1px solid #7c2d12;'
                f'border-radius:4px;padding:2px 7px;font-size:10px;font-weight:700;font-family:monospace;'
                f'flex-shrink:0">r/{p.get("subreddit","")}</span>'
                f'<div style="flex:1;min-width:0">'
                f'<div style="font-size:12px;color:#c8c8cc;line-height:1.4">"{p.get("title","")}"</div>'
                f'<div style="display:flex;gap:4px;flex-wrap:wrap;margin-top:5px">{bait_pills}</div>'
                f'</div>'
                f'<div style="font-size:10px;color:#6b7280;flex-shrink:0;padding-top:2px">{p.get("time_ago","")}</div>'
                f'</div>'
            )

        for r in _intel_reports:
            src_color = r.get("source_color", "#6b7280")
            cards_html.append(
                f'<div style="display:flex;align-items:flex-start;gap:10px;padding:10px 14px;'
                f'background:#1a1a1e;border:1px solid #2a2a2e;border-radius:8px;margin-bottom:8px">'
                f'<span style="background:#1a1a2a;color:{src_color};border:1px solid #2a2a3e;'
                f'border-radius:4px;padding:2px 7px;font-size:10px;font-weight:700;font-family:monospace;'
                f'flex-shrink:0">{r.get("source_label","")}</span>'
                f'<div style="flex:1;min-width:0">'
                f'<div style="font-size:12px;color:#c8c8cc;line-height:1.4">"{r.get("title","")}"</div>'
                f'</div>'
                f'<div style="font-size:10px;color:#6b7280;flex-shrink:0;padding-top:2px">{r.get("time_ago","")}</div>'
                f'</div>'
            )

        st.markdown(
            f'<div style="margin-top:14px;margin-bottom:4px">'
            f'<div style="font-size:11px;font-weight:700;color:#8b8b8f;letter-spacing:0.06em;'
            f'text-transform:uppercase;margin-bottom:10px">◈ Intel Sources — what Dave read this morning</div>'
            f'{"".join(cards_html)}'
            f'</div>',
            unsafe_allow_html=True,
        )

    col_dl, col_ref = st.columns([4, 1])
    with col_ref:
        if st.button("↺ Refresh Dave", key="refresh_dave", use_container_width=True):
            for k in ("dave_brief", "dave_brief_time", "dave_last_q", "dave_last_a",
                      "dave_intel_posts", "dave_intel_reports"):
                st.session_state.pop(k, None)
            st.rerun()
    with col_dl:
        if st.session_state.get("dave_brief"):
            st.download_button(
                "Download Brief", st.session_state["dave_brief"],
                file_name=f"dave-brief-{datetime.date.today()}.txt",
                mime="text/plain", key="dl_brief",
            )

    # ── Ask Dave ─────────────────────────────────────────────────────────────
    st.markdown(
        '<div style="height:1px;background:#2a2a2e;margin:22px 0 16px"></div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        f'<div style="display:flex;align-items:center;gap:10px;margin-bottom:10px">'
        f'<div style="width:28px;height:28px;border-radius:50%;background:#92400e;'
        f'display:flex;align-items:center;justify-content:center;font-size:12px;font-weight:700;color:#fff">D</div>'
        f'<span style="font-size:14px;font-weight:600;color:#f1f1f3">Ask Dave</span>'
        f'<span style="font-size:11px;color:#6b7280">— conditions, inventory, bait advice</span>'
        f'</div>',
        unsafe_allow_html=True,
    )
    user_q = st.text_input(
        "Ask Dave anything",
        key="dave_question",
        placeholder="E.g., Should I stock up on bloodworms this week?",
        label_visibility="collapsed",
    )
    if user_q and user_q != st.session_state.get("dave_last_q"):
        q_prompt = build_ask_dave_prompt(user_q, conditions_ctx, social_velocity, species_now)
        dave_answer = ""
        ans_placeholder = st.empty()
        for chunk in generate_brief_streaming(q_prompt):
            dave_answer += chunk
            ans_placeholder.markdown(
                f'<div style="background:#1c1c1e;border:1px solid #2a2a2e;border-left:3px solid #92400e;'
                f'border-radius:8px;padding:14px 18px;font-size:13px;color:#c8c8cc;line-height:1.7">'
                f'<span style="font-size:11px;font-weight:600;color:#b45309">Dave says:</span><br>{dave_answer}'
                f'</div>',
                unsafe_allow_html=True,
            )
        st.session_state["dave_last_q"] = user_q
        st.session_state["dave_last_a"] = dave_answer
    elif st.session_state.get("dave_last_a") and not user_q:
        pass
    elif st.session_state.get("dave_last_a"):
        rendered_a = _dave_md(st.session_state["dave_last_a"])
        st.markdown(
            f'<div style="background:#1c1c1e;border:1px solid #2a2a2e;border-left:3px solid #92400e;'
            f'border-radius:8px;padding:14px 18px;font-size:13px;color:#c8c8cc;line-height:1.7">'
            f'<span style="font-size:11px;font-weight:600;color:#b45309">Dave says:</span><br>{rendered_a}'
            f'</div>',
            unsafe_allow_html=True,
        )
