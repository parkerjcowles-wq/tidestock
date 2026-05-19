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
/* Global */
[data-testid="stAppViewContainer"] { background: #0f172a; }
[data-testid="stSidebar"] { background: #0f172a; }
[data-testid="stHeader"] { background: transparent; }
[data-testid="stTabsContent"] { padding-top: 16px; }

/* Tab bar */
button[data-baseweb="tab"] {
    font-size: 13px !important;
    padding: 8px 16px !important;
}
button[data-baseweb="tab"][aria-selected="true"] {
    border-bottom: 2px solid #38bdf8 !important;
    color: #38bdf8 !important;
}

/* Cards */
.metric-card {
    background: #1e293b;
    border-radius: 10px;
    padding: 14px 18px;
    margin-bottom: 8px;
    border: 1px solid #334155;
}

/* Signal chips */
.signal-chip {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 600;
    margin: 3px;
}

/* Species activity */
.activity-peak     { background: #166534; color: #bbf7d0; }
.activity-good     { background: #14532d; color: #86efac; }
.activity-fair     { background: #713f12; color: #fde68a; }
.activity-low      { background: #7c2d12; color: #fdba74; }
.activity-inactive { background: #1f2937; color: #9ca3af; }

/* Plotly charts — remove white bg */
.js-plotly-plot .plotly .modebar { background: transparent !important; }

/* Streamlit metric */
[data-testid="stMetricValue"] { font-size: 1.6rem !important; color: #38bdf8; }
[data-testid="stMetricLabel"] { color: #64748b !important; font-size: 12px !important; }

/* Buttons */
[data-testid="baseButton-primary"] {
    background: linear-gradient(135deg, #0369a1, #0c4a6e) !important;
    border: none !important;
    border-radius: 8px !important;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div style="padding:16px 0 8px">
    <span style="font-size:28px;font-weight:700;color:#f1f5f9">🎣 TideStock</span>
    <span style="font-size:14px;color:#64748b;margin-left:12px">Bait Shop Demand Intelligence</span>
</div>
<div style="height:1px;background:#1e293b;margin-bottom:16px"></div>
""", unsafe_allow_html=True)

# ── Sidebar: What-If Controls ────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ What-If Controls")
    st.caption("Adjust conditions to see how reorder recommendations change instantly.")
    demand_mult_raw = st.slider("📈 Demand Surge", 0.8, 2.0, 1.0, 0.05,
                                help="Simulate tourist season, viral bait moment, or general surge")
    delay_days_raw = st.slider("🚚 Supplier Delay (extra days)", 0, 7, 0,
                               help="Add extra days to all supplier lead times")
    bad_weather_raw = st.checkbox("🌧️ Bad Weather (−20%)", value=False,
                                  help="Cold front or storm — suppresses demand across seasonal SKUs")
    service_pct_raw = st.selectbox("🎯 Service Level", [0.85, 0.90, 0.95, 0.99],
                                   index=2, format_func=lambda x: f"{int(x*100)}%")
    demand_mult_final = demand_mult_raw * (0.80 if bad_weather_raw else 1.0)
    st.session_state["demand_mult"] = demand_mult_final
    st.session_state["delay_days"] = delay_days_raw
    st.session_state["service_pct_sidebar"] = service_pct_raw
    st.markdown("---")
    st.markdown("**🎣 Demo Mode**")
    st.caption("All features work without API keys. AI Brief tab requires GROQ_API_KEY (free at console.groq.com).")

# ── Data loading (cached) ─────────────────────────────────────────────────────
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
        weather = {"pressure_series": pd.DataFrame(columns=["time", "pressure"]), "current_temp_f": 65.0, "current_wind_mph": 0.0, "pressure_trend": "stable"}
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
    st.markdown("### 📡 Social Intelligence")
    st.caption("What's buzzing in fishing communities right now — before it hits your counter.")

    from signals.reddit_signals import fetch_reddit_signals, get_overall_social_velocity
    from signals.trends import fetch_trends_data, get_trending_keywords
    from signals.tournament import fetch_tournaments
    from charts.reddit_feed import build_reddit_feed_html
    from charts.trends_chart import build_trends_chart

    @st.cache_data(ttl=1800)
    def load_social():
        try:
            posts = fetch_reddit_signals(limit=15)
        except Exception:
            posts = []
        try:
            trend_kws = get_trending_keywords(config.FISHING_KEYWORDS)
        except Exception:
            trend_kws = []
        try:
            trend_df = fetch_trends_data(config.FISHING_KEYWORDS)
        except Exception:
            trend_df = None
        try:
            tournaments = fetch_tournaments(config.SHOP_REGION)
        except Exception:
            tournaments = []
        velocity = get_overall_social_velocity(posts)
        return posts, trend_kws, trend_df, tournaments, velocity

    posts, trend_kws, trend_df, tournaments, velocity = load_social()

    # Update session state so Scenario Sim can use live velocity
    st.session_state["social_velocity"] = velocity

    # Trend Alert chips
    alerts = [k for k in trend_kws if k["velocity"] in ("trending", "elevated")]
    if alerts:
        st.markdown("**🚨 Trend Alerts**")
        chips = " ".join(
            f'<span class="signal-chip" style="background:#450a0a;color:#fca5a5">🔴 {a["keyword"].title()} +{a["pct_change"]}%</span>'
            if a["velocity"] == "trending" else
            f'<span class="signal-chip" style="background:#422006;color:#fde68a">🟡 {a["keyword"].title()} +{a["pct_change"]}%</span>'
            for a in alerts
        )
        st.markdown(chips, unsafe_allow_html=True)

    col_left, col_right = st.columns([1, 1])

    with col_left:
        st.markdown(f"**Reddit Fishing Feed** — Overall velocity: `{velocity}`")
        st.markdown(build_reddit_feed_html(posts), unsafe_allow_html=True)

    with col_right:
        st.markdown("**Google Trends (90-day)**")
        if trend_df is not None and not trend_df.empty:
            st.plotly_chart(build_trends_chart(trend_df, config.FISHING_KEYWORDS),
                            use_container_width=True)
        else:
            st.warning("Google Trends data unavailable (rate limited). Try again in a few minutes.")

        # Tournament calendar
        st.markdown("**Upcoming Tournaments**")
        if tournaments:
            for t in tournaments:
                st.markdown(
                    f'<div class="metric-card"><div style="color:#fbbf24;font-size:13px">🏆 {t["title"][:70]}</div>'
                    f'<a href="{t["url"]}" style="color:#64748b;font-size:11px">Source ↗</a></div>',
                    unsafe_allow_html=True,
                )
        else:
            st.caption("No upcoming tournaments found for your region.")
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
        weekend_boost = st.checkbox("📅 Weekend Boost (+25%)", value=False,
                                    help="Weekends typically drive 20–30% higher foot traffic at bait shops.")

    # Load conditions for current signal states
    cond = load_conditions()
    inv = load_inventory()
    base_demands = {k: v["avg_weekly_demand"] for k, v in inv.items()}

    # Compute per-SKU demand with custom weights
    month = datetime.date.today().month
    season_map = {1: "off", 2: "off", 3: "shoulder", 4: "shoulder", 5: "peak",
                  6: "peak", 7: "shoulder", 8: "shoulder", 9: "peak", 10: "peak",
                  11: "shoulder", 12: "off"}

    boost = 1.25 if weekend_boost else 1.0
    weighted_demands = {
        sku: compute_demand_index(
            base_demand=base * boost,
            moon_phase=cond["today_phase"],
            tide_quality=cond["tide_quality"],
            social_velocity="baseline",
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
        "tourist_season":     "🏖️ Tourist Season",
        "supplier_delay":     "🚚 Supplier Delay",
    }
    SCENARIO_DESCRIPTIONS = {
        "tournament_weekend": "Local bass tournament drives finesse tackle and soft plastic demand up sharply.",
        "viral_bait_moment":  "A bait is going viral on Reddit/YouTube — soft plastic demand 3× baseline.",
        "cold_front":         "Cold front suppresses activity — live bait and soft plastics drop 30–40%.",
        "striper_run_peak":   "Striper migration peak — paddle tails and bucktails in high demand.",
        "tourist_season":     "Summer tourists flood in — accessories and hard baits spike 40–60%.",
        "supplier_delay":     "Key supplier running 3+ days late — models urgency under extended lead times.",
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
    st.markdown("### 📦 Inventory & Reorder Command Center")

    from inventory.model import safety_stock, reorder_point, economic_order_quantity, days_of_supply, SERVICE_LEVEL_Z
    from inventory.data import load_inventory, get_avg_daily_demand, get_std_daily_demand, get_lead_time
    from inventory.recommendations import (
        urgency_score, confidence_label, reason_card, why_not_reorder,
        fallback_buyer_brief, gross_margin, revenue_at_risk, SKU_SPECIES_MAP,
    )
    from charts.inventory_gauges import build_gauge
    from charts.days_of_supply import build_dos_chart

    demand_mult = st.session_state.get("demand_mult", 1.0)
    delay_days  = st.session_state.get("delay_days", 0)
    service_pct = st.session_state.get("service_pct_sidebar", 0.95)

    z = SERVICE_LEVEL_Z[service_pct]
    inventory = load_inventory()
    cond4 = load_conditions()
    month_now = datetime.date.today().month
    month_name = datetime.date.today().strftime("%B")
    species_now = config.SPECIES_CALENDAR.get(month_now, {})
    striper_active = species_now.get("Striped Bass", "Inactive") in ("Peak", "Good")
    fishing_score_now = cond4["fishing_score"]

    # ── Seasonal Intelligence ─────────────────────────────────────────────────
    st.markdown("#### 🗓️ Local Demand Context")
    active_species = {sp: lvl for sp, lvl in species_now.items() if lvl in ("Peak", "Good")}
    if active_species:
        sp_str = "  ·  ".join(f"**{sp}** {lvl}" for sp, lvl in active_species.items())
        st.info(f"📍 {month_name} near {config.SHOP_REGION}: {sp_str} season. Seasonal SKUs receive a demand lift in the Command Center below.")
    else:
        st.info(f"📍 {month_name} near {config.SHOP_REGION}: Low species activity. Demand signals are muted across seasonal SKUs.")

    sp_cols = st.columns(len(config.SKU_CATEGORIES))
    for i, (sku_key, label) in enumerate(config.SKU_CATEGORIES.items()):
        species = SKU_SPECIES_MAP.get(sku_key, [])
        with sp_cols[i]:
            active_for_sku = [sp for sp in species if species_now.get(sp) in ("Peak", "Good")]
            badge = "🟢" if active_for_sku else "⚪"
            st.markdown(f"{badge} **{label}**")
            for sp in (species or ["All-season"]):
                lvl = species_now.get(sp, "")
                st.caption(f"{sp}{': ' + lvl if lvl else ''}")

    st.markdown("---")

    # ── Build all recommendations ─────────────────────────────────────────────
    all_recs = []
    dos_data  = []

    for sku_key, label in config.SKU_CATEGORIES.items():
        sku = inventory[sku_key]
        daily  = get_avg_daily_demand(sku) * demand_mult
        std    = get_std_daily_demand(sku)
        lt     = get_lead_time(sku, config.DEFAULT_LEAD_TIME_DAYS) + delay_days
        ss     = safety_stock(std, lt, z)
        rop    = reorder_point(daily, lt, ss)
        eoq    = economic_order_quantity(sku["avg_weekly_demand"] * 52 * demand_mult,
                                         sku["order_cost"], sku["holding_cost"])
        dos    = days_of_supply(sku["on_hand"], daily)
        margin = gross_margin(sku.get("unit_cost", 0), sku.get("retail_price", 1))
        rev_risk = revenue_at_risk(sku["on_hand"], rop, sku.get("retail_price", 0))
        score  = urgency_score(sku["on_hand"], rop, dos, lt, fishing_score_now,
                               striper_active, sku_key, margin)
        conf   = confidence_label(sku["on_hand"], rop, dos, lt, fishing_score_now,
                                  striper_active, sku_key)
        reasons = reason_card(sku_key, sku["on_hand"], rop, dos, lt, fishing_score_now,
                              striper_active, margin, species_now)

        if dos < lt or sku["on_hand"] < rop * 0.5:
            status = "🔴 Critical"
        elif sku["on_hand"] < rop or dos < lt * 1.5:
            status = "🟠 Reorder Soon"
        elif dos < lt * 2 or sku["on_hand"] < rop * 1.2:
            status = "🟡 Watch"
        else:
            status = "🟢 Healthy"

        order_qty = (max(eoq, (rop - sku["on_hand"]) + eoq)
                     if sku["on_hand"] < rop else eoq * 0.5)

        dos_data.append({"label": label, "dos": min(dos, 60), "urgency": status})
        all_recs.append({
            "sku_key": sku_key, "label": label, "status": status, "urgency": score,
            "confidence": conf, "reasons": reasons, "on_hand": sku["on_hand"],
            "unit": sku["unit"], "dos": dos, "lead_time": lt, "rop": rop,
            "eoq": eoq, "order_qty": order_qty, "margin": margin,
            "rev_risk": rev_risk, "supplier": sku.get("supplier", "—"),
        })

    all_recs.sort(key=lambda r: r["urgency"], reverse=True)
    flagged = [r for r in all_recs if r["urgency"] >= 30]
    healthy  = [r for r in all_recs if r["urgency"] < 20]

    # ── Reorder Command Center ────────────────────────────────────────────────
    st.markdown("#### 🎯 Reorder Command Center")
    CONF_COLOR = {"High": "#22c55e", "Medium": "#fbbf24", "Low": "#94a3b8"}

    if not flagged:
        st.success("All SKUs are healthy under current conditions. No reorder actions needed.")
    else:
        for rec in flagged:
            cc = CONF_COLOR[rec["confidence"]]
            st.markdown(f"""
<div class="metric-card" style="border-left:4px solid {cc};margin-bottom:12px">
  <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px">
    <span style="font-size:16px;font-weight:700">{rec['label']}</span>
    <span style="display:flex;gap:8px;align-items:center">
      <span style="background:#1e3a5f;color:#93c5fd;padding:2px 10px;border-radius:12px;font-size:12px">{rec['status']}</span>
      <span style="background:#1e293b;color:#94a3b8;padding:2px 10px;border-radius:12px;font-size:12px">Urgency {rec['urgency']}/100</span>
      <span style="color:{cc};font-size:12px;font-weight:600">{rec['confidence']} confidence</span>
    </span>
  </div>
  <div style="display:grid;grid-template-columns:repeat(5,1fr);gap:10px;margin-bottom:10px">
    <div><div style="font-size:11px;color:#64748b">On Hand</div><div style="font-weight:600">{rec['on_hand']} {rec['unit']}</div></div>
    <div><div style="font-size:11px;color:#64748b">Days of Supply</div><div style="font-weight:600">{rec['dos']:.0f}d</div></div>
    <div><div style="font-size:11px;color:#64748b">Gross Margin</div><div style="font-weight:600">{rec['margin']:.0%}</div></div>
    <div><div style="font-size:11px;color:#64748b">Rev. at Risk</div><div style="font-weight:600;color:#f97316">${rec['rev_risk']:.0f}</div></div>
    <div><div style="font-size:11px;color:#64748b">Suggested Order</div><div style="font-weight:600;color:#38bdf8">{rec['order_qty']:.0f} {rec['unit']}</div></div>
  </div>
  <div style="font-size:12px;color:#94a3b8;border-top:1px solid #334155;padding-top:8px;line-height:1.6">
    <span style="color:#64748b">Business:</span> {rec['reasons']['business']}<br>
    <span style="color:#64748b">Calculation:</span> {rec['reasons']['calc']}<br>
    <span style="color:#64748b">Demand signal:</span> {rec['reasons']['demand']}
  </div>
</div>""", unsafe_allow_html=True)

    st.markdown("---")

    # ── Buyer's Brief ─────────────────────────────────────────────────────────
    st.markdown("#### 🤖 Buyer's Brief")
    brief = fallback_buyer_brief(all_recs, species_now, fishing_score_now)
    st.markdown(
        f'<div class="metric-card" style="border-left:4px solid #38bdf8;font-size:14px;line-height:1.7">{brief}</div>',
        unsafe_allow_html=True,
    )

    st.markdown("---")

    # ── Stock Level Gauges + DoS chart ────────────────────────────────────────
    st.markdown("#### 📊 Stock Levels")
    gauge_cols = st.columns(3)
    for i, (sku_key, label) in enumerate(list(config.SKU_CATEGORIES.items())[:6]):
        sku = inventory[sku_key]
        with gauge_cols[i % 3]:
            st.plotly_chart(build_gauge(label, sku["on_hand"], sku["on_hand"] * 1.5, sku["unit"]),
                            use_container_width=True)
    st.plotly_chart(build_dos_chart(dos_data), use_container_width=True)

    # ── Why Not? ──────────────────────────────────────────────────────────────
    if healthy:
        st.markdown("#### ✅ Why Not Reorder?")
        for rec in healthy:
            why = why_not_reorder(rec["label"], rec["dos"], rec["lead_time"],
                                  rec["rop"], rec["on_hand"])
            st.markdown(
                f'<div style="padding:8px 14px;background:#0a2010;border-radius:8px;'
                f'font-size:13px;color:#86efac;margin-bottom:6px">✓ {why}</div>',
                unsafe_allow_html=True,
            )
with tab5:
    st.markdown("### 🤖 AI Planning Brief")
    st.caption("Claude synthesizes all signals into a Monday morning buyer's memo.")

    from ai.brief import build_brief_prompt, generate_brief_streaming
    from inventory.model import days_of_supply, safety_stock, reorder_point, SERVICE_LEVEL_Z
    from inventory.data import load_inventory, get_avg_daily_demand, get_std_daily_demand, get_lead_time

    cond = load_conditions()
    inv = load_inventory()
    month_now = datetime.date.today().month
    species_activity = config.SPECIES_CALENDAR.get(month_now, {})

    service_pct = st.session_state.get("service_pct", config.DEFAULT_SERVICE_LEVEL)
    z = SERVICE_LEVEL_Z[service_pct]
    inv_summary = {}
    for sku_key, label in config.SKU_CATEGORIES.items():
        sku = inv[sku_key]
        daily = get_avg_daily_demand(sku)
        std = get_std_daily_demand(sku)
        lt = get_lead_time(sku, config.DEFAULT_LEAD_TIME_DAYS)
        ss = safety_stock(std, lt, z)
        rop = reorder_point(daily, lt, ss)
        dos = days_of_supply(sku["on_hand"], daily)
        urgency = "Order Today" if dos < lt else "This Week" if dos < lt * 2 else "Monitor"
        inv_summary[label] = {"dos": dos, "urgency": urgency}

    social_velocity = st.session_state.get("social_velocity", "baseline")
    trend_alerts = st.session_state.get("trend_alerts", [])
    active_scenario = st.session_state.get("active_scenario_label", None)

    # Signal chips
    chip_data = [
        ("🌙", cond["today_phase"].replace("_", " ").title()),
        ("🌡️", f"{cond['water_temp']:.0f}°F"),
        ("🌀", cond["weather"]["pressure_trend"].capitalize()),
        ("📡", f"Social: {social_velocity}"),
    ]
    if active_scenario:
        chip_data.append(("🎛️", active_scenario))

    chips_html = " ".join(
        f'<span class="signal-chip" style="background:#1e3a5f;color:#93c5fd">{icon} {label}</span>'
        for icon, label in chip_data
    )
    st.markdown(chips_html, unsafe_allow_html=True)
    st.markdown("")

    if st.button("Generate Planning Brief", type="primary"):
        conditions_ctx = {
            "date": datetime.date.today().isoformat(),
            "moon_phase": cond["today_phase"],
            "tide_quality": cond["tide_quality"],
            "pressure_trend": cond["weather"]["pressure_trend"],
            "water_temp": cond["water_temp"],
            "fishing_score": cond["fishing_score"],
            "species": species_activity,
        }
        prompt = build_brief_prompt(
            conditions=conditions_ctx,
            inventory_summary=inv_summary,
            social_velocity=social_velocity,
            trend_alerts=trend_alerts,
            tournaments=[],
            active_scenario=active_scenario,
            service_level=service_pct,
        )
        brief_placeholder = st.empty()
        full_brief = ""
        for chunk in generate_brief_streaming(prompt):
            full_brief += chunk
            brief_placeholder.markdown(
                f'<div class="metric-card" style="line-height:1.7;font-size:14px">{full_brief}</div>',
                unsafe_allow_html=True,
            )
        # Download button
        st.download_button("📥 Download Brief", full_brief,
                           file_name=f"tidestock-brief-{datetime.date.today()}.txt",
                           mime="text/plain")
