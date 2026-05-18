import streamlit as st
from dotenv import load_dotenv
load_dotenv()

import config
from signals.noaa import fetch_tide_predictions, fetch_water_temp, get_tide_quality
from signals.weather import fetch_weather
from signals.moon import get_week_moon_data, get_moon_phase, get_fishing_score
from charts.tides import build_tide_chart
from charts.pressure import build_pressure_chart
from charts.moon_calendar import build_moon_strip_html
import datetime

st.set_page_config(page_title="TideStock", page_icon="🎣", layout="wide")

# ── CSS ──────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
[data-testid="stAppViewContainer"] { background: #0f172a; }
.metric-card { background:#1e293b; border-radius:10px; padding:14px 18px; margin-bottom:8px; }
.signal-chip { display:inline-block; padding:3px 10px; border-radius:20px; font-size:12px; font-weight:600; margin:3px; }
.activity-peak   { background:#166534; color:#bbf7d0; }
.activity-good   { background:#14532d; color:#86efac; }
.activity-fair   { background:#713f12; color:#fde68a; }
.activity-low    { background:#7c2d12; color:#fdba74; }
.activity-inactive { background:#1f2937; color:#9ca3af; }
</style>
""", unsafe_allow_html=True)

# ── Data loading (cached) ─────────────────────────────────────────────────────
@st.cache_data(ttl=3600)
def load_conditions():
    tide_df = fetch_tide_predictions(config.NOAA_STATION_ID, days=7)
    water_temp = fetch_water_temp(config.NOAA_STATION_ID)
    weather = fetch_weather(config.SHOP_LAT, config.SHOP_LON)
    week_moon = get_week_moon_data()
    today_phase = get_moon_phase(datetime.date.today())
    tide_quality = get_tide_quality(tide_df)
    fishing_score = get_fishing_score(today_phase, weather["pressure_trend"])
    return {
        "tide_df": tide_df,
        "water_temp": water_temp,
        "weather": weather,
        "week_moon": week_moon,
        "today_phase": today_phase,
        "tide_quality": tide_quality,
        "fishing_score": fishing_score,
    }

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🌊 Conditions", "📡 Social Intel", "🎛️ Scenario Sim", "📦 Inventory", "🤖 AI Brief"
])

# ── Tab 1: Conditions ──────────────────────────────────────────────────────────
with tab1:
    st.markdown("### 🌊 Fishing Conditions This Week")
    st.caption(f"📍 {config.SHOP_REGION}")

    cond = load_conditions()

    # Top KPI row
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("🎣 Fishing Score", f"{cond['fishing_score']}/100")
    col2.metric("🌡️ Water Temp", f"{cond['water_temp']:.1f}°F")
    col3.metric("🌙 Moon Phase", cond["today_phase"].replace("_", " ").title())
    col4.metric("🌀 Pressure", cond["weather"]["pressure_trend"].capitalize())

    # Moon strip
    st.markdown("**7-Day Moon Forecast**")
    st.markdown(build_moon_strip_html(cond["week_moon"]), unsafe_allow_html=True)

    # Tide chart
    st.markdown("**Tide Predictions**")
    st.plotly_chart(build_tide_chart(cond["tide_df"]), use_container_width=True)

    # Pressure chart
    st.markdown("**Barometric Pressure (48h)**")
    pressure_df = cond["weather"]["pressure_series"]
    st.plotly_chart(build_pressure_chart(pressure_df, cond["weather"]["pressure_trend"]), use_container_width=True)

    # Species activity
    st.markdown("**Species Activity**")
    month = datetime.date.today().month
    species = config.SPECIES_CALENDAR.get(month, {})
    cols = st.columns(len(species))
    for col, (sp, level) in zip(cols, species.items()):
        css_class = f"activity-{level.lower()}"
        col.markdown(
            f'<div class="metric-card"><div style="font-size:13px;color:#94a3b8">{sp}</div>'
            f'<span class="signal-chip {css_class}">{level}</span></div>',
            unsafe_allow_html=True,
        )

# Remaining tabs — stubs (built in later tasks)
with tab2:
    st.info("Social Intelligence — coming in Task 12")
with tab3:
    st.markdown("### 🎛️ Scenario Simulator")
    st.caption("Adjust signal weights to see how demand forecasts change in real time.")

    from inventory.forecast import compute_demand_index, compute_scenario_demand
    from inventory.data import load_inventory
    from charts.scenario import build_scenario_comparison

    # ── Mode A: Signal Weighting ─────────────────────────────────────────
    st.markdown("#### Mode A — Signal Weight Sliders")
    st.caption("Drag sliders to control how much each signal influences this week's demand forecast.")

    col_sliders, col_chart = st.columns([1, 2])
    with col_sliders:
        weights = {
            "moon":       st.slider("🌙 Moon Phase",      0.0, 1.0, 1.0, 0.1),
            "tide":       st.slider("🌊 Tide Quality",    0.0, 1.0, 1.0, 0.1),
            "social":     st.slider("📡 Social Velocity", 0.0, 1.0, 1.0, 0.1),
            "pressure":   st.slider("🌀 Pressure",        0.0, 1.0, 1.0, 0.1),
            "tournament": st.slider("🏆 Tournament",      0.0, 1.0, 1.0, 0.1),
            "season":     st.slider("📅 Season",          0.0, 1.0, 1.0, 0.1),
        }

    # Load conditions for current signal states
    cond = load_conditions()
    inv = load_inventory()
    base_demands = {k: v["avg_weekly_demand"] for k, v in inv.items()}

    # Compute per-SKU demand with custom weights
    month = datetime.date.today().month
    season_map = {1: "off", 2: "off", 3: "shoulder", 4: "shoulder", 5: "peak",
                  6: "peak", 7: "shoulder", 8: "shoulder", 9: "peak", 10: "peak",
                  11: "shoulder", 12: "off"}

    weighted_demands = {
        sku: compute_demand_index(
            base_demand=base,
            moon_phase=cond["today_phase"],
            tide_quality=cond["tide_quality"],
            social_velocity="baseline",  # updated in Task 12 after Reddit is live
            pressure_trend=cond["weather"]["pressure_trend"],
            tournament_proximity="none",
            season_level=season_map.get(month, "shoulder"),
            weights=weights,
        )
        for sku, base in base_demands.items()
    }

    with col_chart:
        st.plotly_chart(
            build_scenario_comparison(base_demands, weighted_demands, config.SKU_CATEGORIES),
            use_container_width=True,
        )

    # Demand narrative
    avg_multiplier = sum(weighted_demands.values()) / sum(base_demands.values())
    st.markdown(
        f"**Demand Index:** `{avg_multiplier:.2f}×` baseline — "
        f"{'above' if avg_multiplier > 1.1 else 'below' if avg_multiplier < 0.9 else 'near'} normal"
    )

    # ── Mode B: Scenario Toggles ──────────────────────────────────────────
    st.markdown("---")
    st.markdown("#### Mode B — Preset Scenario Toggles")

    SCENARIO_LABELS = {
        "tournament_weekend": "🏆 Tournament This Weekend",
        "viral_bait_moment":  "🔥 Viral Bait Moment",
        "cold_front":         "🧊 Cold Front Incoming",
        "striper_run_peak":   "🐟 Striper Run Peak",
    }
    SCENARIO_DESCRIPTIONS = {
        "tournament_weekend": "Local bass tournament drives finesse tackle and soft plastic demand up sharply.",
        "viral_bait_moment":  "A bait is going viral on Reddit/YouTube — soft plastic demand 3× baseline.",
        "cold_front":         "Cold front suppresses activity — live bait and soft plastics drop 30–40%.",
        "striper_run_peak":   "Striper migration peak — paddle tails and bucktails in high demand.",
    }

    active_scenario = st.radio("Select a scenario", list(SCENARIO_LABELS.keys()),
                               format_func=lambda k: SCENARIO_LABELS[k], index=None)

    if active_scenario:
        st.caption(SCENARIO_DESCRIPTIONS[active_scenario])
        scenario_demands = compute_scenario_demand(base_demands, active_scenario)
        st.plotly_chart(
            build_scenario_comparison(base_demands, scenario_demands, config.SKU_CATEGORIES),
            use_container_width=True,
        )
        # Delta table
        import pandas as pd
        delta_rows = [
            {
                "Category": config.SKU_CATEGORIES[k],
                "Baseline (units/wk)": f"{base_demands[k]:.0f}",
                "Scenario (units/wk)": f"{scenario_demands.get(k, base_demands[k]):.0f}",
                "Change": f"+{scenario_demands.get(k, base_demands[k]) - base_demands[k]:.0f}"
                          if scenario_demands.get(k, base_demands[k]) >= base_demands[k]
                          else f"{scenario_demands.get(k, base_demands[k]) - base_demands[k]:.0f}",
            }
            for k in base_demands
        ]
        st.dataframe(pd.DataFrame(delta_rows), use_container_width=True, hide_index=True)

        # Store active scenario in session state for AI brief
        st.session_state["active_scenario"] = active_scenario
        st.session_state["active_scenario_label"] = SCENARIO_LABELS[active_scenario]
    else:
        st.session_state.pop("active_scenario", None)
with tab4:
    st.markdown("### 📦 Inventory Status & Reorder Recommendations")

    lead_time = st.slider("Supplier Lead Time (days)", 1, 14, config.DEFAULT_LEAD_TIME_DAYS)
    service_pct = st.selectbox("Target Service Level", [0.85, 0.90, 0.95, 0.99],
                                index=2, format_func=lambda x: f"{int(x*100)}%")

    from inventory.model import safety_stock, reorder_point, economic_order_quantity, days_of_supply, SERVICE_LEVEL_Z
    from inventory.data import load_inventory, get_avg_daily_demand
    from charts.inventory_gauges import build_gauge
    from charts.days_of_supply import build_dos_chart

    z = SERVICE_LEVEL_Z[service_pct]
    inventory = load_inventory()
    dos_data = []
    reorder_rows = []

    for sku_key, label in config.SKU_CATEGORIES.items():
        sku = inventory[sku_key]
        daily_demand = get_avg_daily_demand(sku)
        std_demand = daily_demand * 0.3  # assume 30% demand variability
        ss = safety_stock(daily_demand, std_demand, lead_time, z)
        rop = reorder_point(daily_demand, lead_time, ss)
        eoq = economic_order_quantity(
            sku["avg_weekly_demand"] * 52,
            sku["order_cost"],
            sku["holding_cost"],
        )
        dos = days_of_supply(sku["on_hand"], daily_demand)
        urgency = "Order Today" if dos < lead_time else "This Week" if dos < lead_time * 2 else "Monitor"
        dos_data.append({"label": label, "dos": min(dos, 60), "urgency": urgency})
        reorder_rows.append({
            "Category": label,
            "On Hand": f"{sku['on_hand']} {sku['unit']}",
            "Days of Supply": f"{dos:.0f}d" if dos < 100 else "60d+",
            "Safety Stock": f"{ss:.0f}",
            "Reorder Point": f"{rop:.0f}",
            "EOQ": f"{eoq:.0f}",
            "Urgency": urgency,
        })

    # Gauges row
    st.markdown("**Stock Levels**")
    gauge_cols = st.columns(3)
    for i, (sku_key, label) in enumerate(list(config.SKU_CATEGORIES.items())[:6]):
        sku = inventory[sku_key]
        with gauge_cols[i % 3]:
            max_val = sku["on_hand"] * 1.5
            st.plotly_chart(build_gauge(label, sku["on_hand"], max_val, sku["unit"]),
                            use_container_width=True)

    # Days of supply chart
    st.plotly_chart(build_dos_chart(dos_data), use_container_width=True)

    # Reorder table
    st.markdown("**Reorder Recommendations**")
    import pandas as pd
    df_reorder = pd.DataFrame(reorder_rows)
    st.dataframe(df_reorder, use_container_width=True, hide_index=True)
with tab5:
    st.info("AI Planning Brief — coming in Task 16")
