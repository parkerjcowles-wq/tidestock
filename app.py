import streamlit as st
import pandas as pd
from dotenv import load_dotenv
load_dotenv()

import config
from signals.noaa import fetch_tide_predictions, fetch_water_temp, get_tide_quality
from signals.weather import fetch_weather
from signals.moon import get_week_moon_data, get_moon_phase, get_fishing_score
from charts.tides import build_tide_chart
from charts.pressure import build_pressure_chart
from charts.moon_calendar import build_moon_strip_html
from assets.sku_styles import source_badge_html, dos_progress_bar_html, SKU_STYLES
import datetime

st.set_page_config(page_title="TideStock", page_icon="🎣", layout="wide")

# ── CSS ──────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* ── Base ── */
[data-testid="stAppViewContainer"] { background: #0f172a; }
[data-testid="stSidebar"]          { background: #0c1322; }
[data-testid="stHeader"]           { background: transparent; }
[data-testid="stTabsContent"]      { padding-top: 16px; }

/* ── Tab bar ── */
button[data-baseweb="tab"] {
    font-size: 13px !important;
    padding: 8px 16px !important;
    color: #64748b !important;
}
button[data-baseweb="tab"][aria-selected="true"] {
    border-bottom: 2px solid #38bdf8 !important;
    color: #f1f5f9 !important;
}

/* ── Cards ── */
.metric-card {
    background: #1e293b;
    border-radius: 10px;
    padding: 14px 18px;
    margin-bottom: 10px;
    border: 1px solid #334155;
    transition: border-color 0.15s ease;
}
.metric-card:hover { border-color: #475569; }

/* ── Reorder risk card ── */
.risk-card {
    background: #1e293b;
    border-radius: 12px;
    padding: 16px 20px;
    margin-bottom: 14px;
    border: 1px solid #334155;
}
.risk-card-critical   { border-left: 4px solid #ef4444 !important; }
.risk-card-reorder    { border-left: 4px solid #f97316 !important; }
.risk-card-watch      { border-left: 4px solid #fbbf24 !important; }

/* ── Signal chips ── */
.signal-chip {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 20px;
    font-size: 11px;
    font-weight: 600;
    margin: 2px 3px;
    letter-spacing: 0.01em;
}

/* ── Source badges ── */
.source-row {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 12px;
    flex-wrap: wrap;
}

/* ── Species activity ── */
.activity-peak     { background: #166534; color: #bbf7d0; }
.activity-good     { background: #14532d; color: #86efac; }
.activity-fair     { background: #713f12; color: #fde68a; }
.activity-low      { background: #7c2d12; color: #fdba74; }
.activity-inactive { background: #1f2937; color: #9ca3af; }

/* ── Status badges ── */
.badge-critical  { background:#450a0a; color:#fca5a5; }
.badge-reorder   { background:#431407; color:#fdba74; }
.badge-watch     { background:#422006; color:#fde68a; }
.badge-healthy   { background:#052e16; color:#86efac; }
.badge-neutral   { background:#1e293b; color:#94a3b8; }

/* ── Section dividers ── */
.section-header {
    font-size: 13px;
    font-weight: 700;
    color: #94a3b8;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin: 18px 0 10px;
    padding-bottom: 6px;
    border-bottom: 1px solid #1e293b;
}

/* ── What-if active state ── */
.whatif-active {
    background: #0c2545;
    border: 1px solid #1e3a5f;
    border-radius: 8px;
    padding: 8px 12px;
    font-size: 12px;
    color: #93c5fd;
    margin-bottom: 8px;
}

/* ── Plotly ── */
.js-plotly-plot .plotly .modebar { background: transparent !important; }

/* ── Streamlit metrics ── */
[data-testid="stMetricValue"] { font-size: 1.5rem !important; color: #38bdf8; }
[data-testid="stMetricLabel"] { color: #64748b !important; font-size: 12px !important; }
[data-testid="stMetricDelta"] { font-size: 11px !important; }

/* ── Buttons ── */
[data-testid="baseButton-primary"] {
    background: linear-gradient(135deg, #0369a1, #0c4a6e) !important;
    border: none !important;
    border-radius: 8px !important;
}
[data-testid="baseButton-secondary"] {
    background: #1e293b !important;
    border: 1px solid #334155 !important;
    border-radius: 8px !important;
    color: #94a3b8 !important;
    font-size: 12px !important;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] [data-testid="stMarkdown"] { color: #94a3b8; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div style="padding:16px 0 6px;display:flex;align-items:baseline;gap:12px">
    <span style="font-size:26px;font-weight:700;color:#f1f5f9;letter-spacing:-0.02em">🎣 TideStock</span>
    <span style="font-size:13px;color:#475569">Bait Shop Demand Intelligence · Newburyport, MA</span>
</div>
<div style="height:1px;background:#1e293b;margin-bottom:14px"></div>
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

    # Active what-if indicator
    overrides = []
    if abs(demand_mult_raw - 1.0) > 0.05:
        overrides.append(f"Demand {demand_mult_raw:.2f}×")
    if delay_days_raw > 0:
        overrides.append(f"+{delay_days_raw}d lead time")
    if bad_weather_raw:
        overrides.append("Bad weather −20%")
    if overrides:
        st.markdown(
            f'<div class="whatif-active">⚡ Active: {" · ".join(overrides)}</div>',
            unsafe_allow_html=True,
        )

    st.markdown("---")
    st.markdown("**🎣 Portfolio / Demo Mode**")
    st.markdown("""
<div style="font-size:12px;color:#64748b;line-height:1.6">
• Seed inventory data powers all recommendations offline<br>
• Environmental data (NOAA, weather, moon) fetches live — graceful fallback if unavailable<br>
• Social Intel reads public Reddit feeds — no credentials needed<br>
• AI Brief requires <code>GROQ_API_KEY</code> — free at <a href="https://console.groq.com" style="color:#38bdf8">console.groq.com</a>
</div>
""", unsafe_allow_html=True)

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
        "loaded_at": datetime.datetime.now().strftime("%I:%M %p"),
    }

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🌊 Conditions", "📡 Social Intel", "🎛️ Scenario Sim", "📦 Inventory", "🤖 AI Brief"
])

# ── Tab 1: Conditions ──────────────────────────────────────────────────────────
with tab1:
    cond = load_conditions()

    # Source badges + refresh
    rcol1, rcol2 = st.columns([6, 1])
    with rcol1:
        st.markdown(
            f'<div class="source-row">'
            f'{source_badge_html("noaa", "Tides")} '
            f'{source_badge_html("ndbc", "Water temp")} '
            f'{source_badge_html("meteo", "Pressure")} '
            f'<span style="font-size:10px;color:#334155">· refreshes hourly · last loaded {cond["loaded_at"]}</span>'
            f'</div>',
            unsafe_allow_html=True,
        )
    with rcol2:
        if st.button("⟳ Refresh", key="refresh_cond", help="Reload environmental data"):
            load_conditions.clear()
            st.rerun()

    # Top KPI row
    col1, col2, col3, col4 = st.columns(4)
    score = cond["fishing_score"]
    score_delta = "Prime" if score >= 80 else "Good" if score >= 60 else "Fair" if score >= 40 else "Poor"
    col1.metric("Fishing Score", f"{score}/100", score_delta)
    col2.metric("Water Temp", f"{cond['water_temp']:.1f}°F")
    col3.metric("Moon Phase", cond["today_phase"].replace("_", " ").title())
    col4.metric("Pressure", cond["weather"]["pressure_trend"].capitalize())

    st.markdown('<div class="section-header">7-Day Moon Forecast</div>', unsafe_allow_html=True)
    st.markdown(build_moon_strip_html(cond["week_moon"]), unsafe_allow_html=True)

    st.markdown('<div class="section-header">Tide Predictions</div>', unsafe_allow_html=True)
    st.plotly_chart(build_tide_chart(cond["tide_df"]), use_container_width=True)

    st.markdown('<div class="section-header">Barometric Pressure (48h)</div>', unsafe_allow_html=True)
    pressure_df = cond["weather"]["pressure_series"]
    st.plotly_chart(build_pressure_chart(pressure_df, cond["weather"]["pressure_trend"]), use_container_width=True)

    st.markdown('<div class="section-header">Species Activity — ' + datetime.date.today().strftime("%B") + '</div>', unsafe_allow_html=True)
    month = datetime.date.today().month
    species = config.SPECIES_CALENDAR.get(month, {})
    cols = st.columns(len(species))
    for col, (sp, level) in zip(cols, species.items()):
        css_class = f"activity-{level.lower()}"
        col.markdown(
            f'<div class="metric-card" style="text-align:center">'
            f'<div style="font-size:12px;color:#64748b;margin-bottom:6px">{sp}</div>'
            f'<span class="signal-chip {css_class}">{level}</span></div>',
            unsafe_allow_html=True,
        )

# Remaining tabs — stubs (built in later tasks)
with tab2:
    from signals.reddit_signals import fetch_reddit_signals, get_overall_social_velocity
    from signals.trends import fetch_trends_data, get_trending_keywords_from_df
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
            trend_df = fetch_trends_data(config.FISHING_KEYWORDS)
        except Exception:
            trend_df = None
        trend_kws = get_trending_keywords_from_df(trend_df, config.FISHING_KEYWORDS)
        try:
            tournaments = fetch_tournaments(config.SHOP_REGION)
        except Exception:
            tournaments = []
        velocity = get_overall_social_velocity(posts)
        return posts, trend_kws, trend_df, tournaments, velocity, datetime.datetime.now().strftime("%I:%M %p")

    posts, trend_kws, trend_df, tournaments, velocity, social_loaded_at = load_social()
    st.session_state["social_velocity"] = velocity

    # Source badges + refresh
    s1, s2 = st.columns([6, 1])
    with s1:
        velocity_color = {"trending": "#fca5a5", "elevated": "#fde68a", "baseline": "#94a3b8"}[velocity]
        st.markdown(
            f'<div class="source-row">'
            f'{source_badge_html("reddit", "Public API")} '
            f'{source_badge_html("trends", "pytrends")} '
            f'{source_badge_html("exa", "Tournaments")} '
            f'<span style="font-size:10px;color:#334155">· last loaded {social_loaded_at}</span> '
            f'<span class="signal-chip" style="background:#1e293b;color:{velocity_color}">Signal: {velocity}</span>'
            f'</div>',
            unsafe_allow_html=True,
        )
    with s2:
        if st.button("⟳ Refresh", key="refresh_social", help="Reload social signals"):
            load_social.clear()
            st.rerun()

    # Trend alert chips
    alerts = [k for k in trend_kws if k["velocity"] in ("trending", "elevated")]
    st.session_state["trend_alerts"] = [
        f'{a["keyword"]} +{a["pct_change"]}% ({a["velocity"]})' for a in alerts
    ]
    if alerts:
        st.markdown('<div class="section-header">Trend Alerts</div>', unsafe_allow_html=True)
        chips = " ".join(
            f'<span class="signal-chip badge-critical">▲ {a["keyword"].title()} +{a["pct_change"]}%</span>'
            if a["velocity"] == "trending" else
            f'<span class="signal-chip badge-watch">↑ {a["keyword"].title()} +{a["pct_change"]}%</span>'
            for a in alerts
        )
        st.markdown(chips, unsafe_allow_html=True)

    col_left, col_right = st.columns([1, 1])

    with col_left:
        st.markdown('<div class="section-header">Reddit Fishing Feed</div>', unsafe_allow_html=True)
        if posts:
            st.markdown(build_reddit_feed_html(posts), unsafe_allow_html=True)
        else:
            st.markdown(
                '<div class="metric-card" style="color:#475569;text-align:center;padding:24px">'
                'No Reddit posts loaded — public API may be temporarily throttled.'
                '</div>',
                unsafe_allow_html=True,
            )

    with col_right:
        st.markdown('<div class="section-header">Google Trends · 90-Day Velocity</div>', unsafe_allow_html=True)
        st.plotly_chart(build_trends_chart(trend_df, config.FISHING_KEYWORDS), use_container_width=True)

        st.markdown('<div class="section-header">Tournament Calendar</div>', unsafe_allow_html=True)
        if tournaments:
            from html import escape
            for t in tournaments:
                safe_title = escape(t["title"])[:70]
                raw_url = t.get("url", "")
                safe_url = escape(raw_url) if raw_url.startswith(("https://", "http://")) else "#"
                days = t.get("days_until", "")
                days_badge = f'<span class="signal-chip badge-watch">{days}d away</span>' if days else ""
                st.markdown(
                    f'<div class="metric-card" style="padding:10px 14px">'
                    f'<div style="display:flex;justify-content:space-between;align-items:center">'
                    f'<span style="color:#fbbf24;font-size:13px">🏆 {safe_title}</span>'
                    f'{days_badge}</div>'
                    f'<a href="{safe_url}" style="color:#475569;font-size:11px">Source ↗</a></div>',
                    unsafe_allow_html=True,
                )
        else:
            st.markdown(
                '<div class="metric-card" style="color:#475569;font-size:13px">'
                'No upcoming tournaments found for this region.</div>',
                unsafe_allow_html=True,
            )
with tab3:

    from inventory.forecast import compute_demand_index, compute_scenario_demand
    from inventory.data import load_inventory
    from charts.scenario import build_scenario_comparison

    st.markdown('<div class="section-header">Mode A — Signal Weight Sliders</div>', unsafe_allow_html=True)
    st.caption("Drag sliders to control how much each signal influences the demand forecast. Updates in real time.")

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
        avg_multiplier = sum(weighted_demands.values()) / sum(base_demands.values())
        direction = "above" if avg_multiplier > 1.1 else "below" if avg_multiplier < 0.9 else "near"
        delta_color = "#22c55e" if avg_multiplier > 1.05 else "#ef4444" if avg_multiplier < 0.95 else "#fbbf24"
        st.markdown(
            f'<div style="display:flex;gap:10px;align-items:center;margin-bottom:8px">'
            f'<span class="signal-chip" style="background:#1e293b;color:{delta_color};font-size:13px">'
            f'Demand Index {avg_multiplier:.2f}× baseline — {direction} normal</span>'
            f'</div>',
            unsafe_allow_html=True,
        )
        st.plotly_chart(
            build_scenario_comparison(base_demands, weighted_demands, config.SKU_CATEGORIES,
                                      subtitle="Signal Weights"),
            use_container_width=True,
        )

    st.markdown("---")
    st.markdown('<div class="section-header">Mode B — Preset Scenario Toggles</div>', unsafe_allow_html=True)

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
        scenario_demands = compute_scenario_demand(base_demands, active_scenario)
        total_base = sum(base_demands.values())
        total_scen = sum(scenario_demands.values())
        overall_pct = (total_scen - total_base) / total_base * 100 if total_base else 0
        pct_color = "#22c55e" if overall_pct > 0 else "#ef4444"
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
            build_scenario_comparison(base_demands, scenario_demands, config.SKU_CATEGORIES,
                                      subtitle=SCENARIO_LABELS[active_scenario]),
            use_container_width=True,
        )
        # Delta table
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

    # Source badge
    st.markdown(
        f'<div class="source-row">{source_badge_html("seed")} '
        f'<span style="font-size:10px;color:#334155">Category-level demo inventory · '
        f'Service level {int(service_pct * 100)}% · '
        f'{"Demand ×" + f"{demand_mult:.2f}" if abs(demand_mult - 1.0) > 0.05 else "Baseline demand"}'
        f'</span></div>',
        unsafe_allow_html=True,
    )

    # ── Seasonal Intelligence ─────────────────────────────────────────────────
    st.markdown('<div class="section-header">Local Demand Context — ' + month_name + '</div>', unsafe_allow_html=True)
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
    st.markdown('<div class="section-header">Reorder Command Center</div>', unsafe_allow_html=True)
    CONF_COLOR = {"High": "#22c55e", "Medium": "#fbbf24", "Low": "#94a3b8"}
    STATUS_BADGE = {
        "🔴 Critical":    "badge-critical",
        "🟠 Reorder Soon": "badge-reorder",
        "🟡 Watch":        "badge-watch",
        "🟢 Healthy":      "badge-healthy",
    }

    if not flagged:
        st.markdown(
            '<div class="metric-card badge-healthy" style="text-align:center;padding:20px;color:#86efac">'
            '✓ All SKUs are healthy under current conditions. No reorder actions needed.</div>',
            unsafe_allow_html=True,
        )
    else:
        for rec in flagged:
            cc       = CONF_COLOR[rec["confidence"]]
            style_k  = rec["sku_key"]
            sku_style = SKU_STYLES.get(style_k, {})
            icon     = sku_style.get("icon", "📦")
            accent   = sku_style.get("accent", "#94a3b8")
            grad     = sku_style.get("gradient", "linear-gradient(135deg,#1e293b,#334155)")
            sbadge   = STATUS_BADGE.get(rec["status"], "badge-neutral")
            dos_bar  = dos_progress_bar_html(rec["dos"], rec["lead_time"], rec["status"])
            supplier_note = f'<span style="color:#475569;font-size:11px">Supplier: {rec["supplier"]}</span>' if rec["supplier"] != "—" else ""
            st.markdown(f"""
<div class="risk-card" style="border-left:4px solid {accent}">
  <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:12px">
    <div style="display:flex;align-items:center;gap:10px">
      <div style="background:{grad};border-radius:8px;width:38px;height:38px;display:flex;align-items:center;justify-content:center;font-size:18px;flex-shrink:0">{icon}</div>
      <div>
        <div style="font-size:15px;font-weight:700;color:#f1f5f9">{rec['label']}</div>
        {supplier_note}
      </div>
    </div>
    <div style="display:flex;gap:6px;align-items:center;flex-wrap:wrap;justify-content:flex-end">
      <span class="signal-chip {sbadge}">{rec['status']}</span>
      <span class="signal-chip badge-neutral">Urgency {rec['urgency']}/100</span>
      <span style="color:{cc};font-size:11px;font-weight:600">{rec['confidence']} confidence</span>
    </div>
  </div>
  {dos_bar}
  <div style="display:grid;grid-template-columns:repeat(5,1fr);gap:8px;margin:10px 0">
    <div style="background:#0f172a;border-radius:6px;padding:8px">
      <div style="font-size:10px;color:#475569;margin-bottom:2px">On Hand</div>
      <div style="font-weight:700;font-size:13px">{rec['on_hand']} {rec['unit']}</div>
    </div>
    <div style="background:#0f172a;border-radius:6px;padding:8px">
      <div style="font-size:10px;color:#475569;margin-bottom:2px">Reorder Point</div>
      <div style="font-weight:700;font-size:13px">{rec['rop']:.0f} {rec['unit']}</div>
    </div>
    <div style="background:#0f172a;border-radius:6px;padding:8px">
      <div style="font-size:10px;color:#475569;margin-bottom:2px">Gross Margin</div>
      <div style="font-weight:700;font-size:13px">{rec['margin']:.0%}</div>
    </div>
    <div style="background:#0f172a;border-radius:6px;padding:8px">
      <div style="font-size:10px;color:#475569;margin-bottom:2px">Rev. at Risk</div>
      <div style="font-weight:700;font-size:13px;color:#f97316">${rec['rev_risk']:.0f}</div>
    </div>
    <div style="background:#0f172a;border-radius:6px;padding:8px">
      <div style="font-size:10px;color:#475569;margin-bottom:2px">Order Qty</div>
      <div style="font-weight:700;font-size:13px;color:#38bdf8">{rec['order_qty']:.0f} {rec['unit']}</div>
    </div>
  </div>
  <div style="font-size:12px;color:#64748b;border-top:1px solid #1e293b;padding-top:8px;line-height:1.7">
    <span style="color:#475569">◆ Business:</span> {rec['reasons']['business']}<br>
    <span style="color:#475569">◆ Calculation:</span> {rec['reasons']['calc']}<br>
    <span style="color:#475569">◆ Demand signal:</span> {rec['reasons']['demand']}
  </div>
</div>""", unsafe_allow_html=True)

    st.markdown("---")

    # ── Buyer's Brief ─────────────────────────────────────────────────────────
    st.markdown('<div class="section-header">Buyer\'s Brief</div>', unsafe_allow_html=True)
    brief = fallback_buyer_brief(all_recs, species_now, fishing_score_now)
    st.markdown(
        f'<div class="metric-card" style="border-left:4px solid #38bdf8;font-size:14px;line-height:1.7">{brief}</div>',
        unsafe_allow_html=True,
    )

    st.markdown("---")

    # ── Stock Level Gauges + DoS chart ────────────────────────────────────────
    st.markdown('<div class="section-header">Stock Levels</div>', unsafe_allow_html=True)
    gauge_cols = st.columns(3)
    for i, (sku_key, label) in enumerate(list(config.SKU_CATEGORIES.items())[:6]):
        sku  = inventory[sku_key]
        rec  = next((r for r in all_recs if r["sku_key"] == sku_key), None)
        rop_val  = rec["rop"] if rec else None
        max_val  = max(sku["on_hand"] * 1.5, (rop_val or 0) * 2.5, 1)
        with gauge_cols[i % 3]:
            st.plotly_chart(
                build_gauge(label, sku["on_hand"], max_val, sku["unit"], rop=rop_val),
                use_container_width=True,
            )
    st.plotly_chart(build_dos_chart(dos_data), use_container_width=True)

    # ── Why Not? ──────────────────────────────────────────────────────────────
    if healthy:
        st.markdown('<div class="section-header">Why Not Reorder?</div>', unsafe_allow_html=True)
        for rec in healthy:
            why = why_not_reorder(rec["label"], rec["dos"], rec["lead_time"],
                                  rec["rop"], rec["on_hand"])
            st.markdown(
                f'<div style="padding:8px 14px;background:#0a2010;border-radius:8px;'
                f'font-size:13px;color:#86efac;margin-bottom:6px">✓ {why}</div>',
                unsafe_allow_html=True,
            )
with tab5:
    st.markdown(
        f'<div class="source-row">{source_badge_html("groq")} '
        f'<span style="font-size:10px;color:#334155">AI synthesizes all signals into a Monday morning buyer\'s memo</span>'
        f'</div>',
        unsafe_allow_html=True,
    )

    from ai.brief import build_brief_prompt, generate_brief_streaming
    from inventory.model import days_of_supply, safety_stock, reorder_point, SERVICE_LEVEL_Z
    from inventory.data import load_inventory, get_avg_daily_demand, get_std_daily_demand, get_lead_time

    cond = load_conditions()
    inv = load_inventory()
    month_now = datetime.date.today().month
    species_activity = config.SPECIES_CALENDAR.get(month_now, {})

    service_pct = st.session_state.get("service_pct_sidebar", config.DEFAULT_SERVICE_LEVEL)
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
