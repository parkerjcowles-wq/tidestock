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
    st.info("Scenario Simulator — coming in Task 10")
with tab4:
    st.info("Inventory & Reorder — coming in Task 9")
with tab5:
    st.info("AI Planning Brief — coming in Task 16")
