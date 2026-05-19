# 🎣 TideStock — Bait Shop Demand Intelligence

> AI-assisted inventory intelligence dashboard for a coastal bait and tackle shop.

**[→ Live Demo](YOUR_STREAMLIT_URL_HERE)**

---

## Why This Exists

I worked at Crossroads Bait & Tackle for four years. Every spring we'd sell out of paddle tails the week stripers showed up, and every winter we'd sit on overstock we'd never move. The buying decisions were made on gut feel — experienced gut feel, but gut feel.

TideStock is what I'd have wanted: a Monday morning dashboard that combines environmental signals, social velocity, and inventory math to surface reorder decisions before demand hits the counter. The same forward-looking approach Amazon and Pepsi use internally, applied to a domain I actually know.

---

## What It Does

| Tab | What you get |
|---|---|
| 🌊 Conditions | Live NOAA tide predictions, moon phase fishing scores, barometric pressure trends, water temperature, species activity by month |
| 📡 Social Intel | Reddit fishing community signal feed, Google Trends spikes for bait keywords, tournament calendar via Exa |
| 🎛️ Scenario Sim | Adjust signal weights in real time, toggle preset scenarios (tournament weekend, viral bait, cold front, striper run), before/after demand comparison |
| 📦 Inventory | Plotly gauges, days-of-supply chart, per-SKU reorder table with Status labels, explainability bullets explaining why each SKU is flagged |
| 🤖 AI Brief | Groq-powered Monday morning S&OP memo — synthesizes all signals into buyer-ready planning language |

---

## Demand Signal Engine

The core of TideStock is a weighted signal index that makes explicit what experienced bait shop buyers do intuitively:

```
demand_index = base_demand × Σ(signal_multiplier[i] × weight[i]) / Σ(weight[i])
```

| Signal | Low | Medium | High |
|---|---|---|---|
| Moon phase | Crescent 1.0× | Quarter 1.2× | New/Full 1.8× |
| Tide quality | Poor 0.8× | Moderate 1.2× | Prime 1.6× |
| Social velocity | Baseline 1.0× | Elevated 1.4× | Trending 2.0× |
| Barometric pressure | Falling 0.8× | Stable 1.0× | Rising 1.3× |
| Tournament proximity | None 1.0× | Same week 1.5× | Within 3 days 2.2× |
| Species season | Off 0.7× | Shoulder 1.2× | Peak 1.7× |

---

## Inventory Logic

Safety stock, reorder point, EOQ, and days of supply are computed from per-SKU seed data seeded from real bait shop experience:

- **Safety Stock** = Z × σ_demand × √lead_time
- **Reorder Point** = avg_daily_demand × lead_time + safety_stock
- **EOQ** = √(2 × annual_demand × order_cost / holding_cost)
- **Days of Supply** = on_hand / avg_daily_demand

Status labels — Critical / Reorder Soon / Watch / Healthy — are computed per SKU with explainability bullets explaining the signal drivers.

---

## Tech Stack

Python · Streamlit · Plotly · NOAA CO-OPS API · NDBC Buoy · Open-Meteo · ephem · PRAW · pytrends · Exa · Groq (LLaMA 3.3 70B)

---

## Local Setup

```bash
git clone https://github.com/parkerjcowles-wq/tidestock
cd tidestock
pip install -r requirements.txt
cp .env.example .env   # fill in API keys
streamlit run app.py
```

The app runs without any API keys — environmental data uses graceful fallbacks, the AI brief tab requires `GROQ_API_KEY`.

---

## API Keys

Set in `.env` for local dev or Streamlit Cloud Secrets for deployment:

```
GROQ_API_KEY=...          # free at console.groq.com
REDDIT_CLIENT_ID=...      # free script app at reddit.com/prefs/apps
REDDIT_CLIENT_SECRET=...
REDDIT_USER_AGENT=TideStock/1.0
EXA_API_KEY=...           # free tier at exa.ai
```

---

## Running Tests

```bash
pip install -r requirements-dev.txt
pytest tests/ -v
```

---

## Screenshots

*Coming soon — deploy to Streamlit Cloud and replace this section with screenshots of each tab.*

---

## AI Development

See [`docs/ai-development-log.md`](docs/ai-development-log.md) for a full breakdown of how AI was used in this project — what it generated, what I validated, and where domain knowledge drove the decisions.

---

## Resume Summary

> Built AI-powered bait shop demand intelligence dashboard — integrates NOAA tide predictions, moon phase, Reddit social velocity (PRAW), and Google Trends signals into interactive Plotly scenario simulations and Groq-powered weekly planning briefs with per-SKU reorder explainability; deployed on Streamlit Cloud.

**Interview story:** I worked at a bait shop for four years. We'd sell out of paddle tails right when striper season peaked and over-order all winter. I built a demand planning system that combines environmental data with social signal velocity to predict demand before it happens — the same forward-looking approach Amazon and Pepsi use internally, applied to a domain I actually know.

---

## What This Demonstrates

- **AI-assisted product development** — Claude and Groq used as collaborators, not black boxes; all recommendations are computed deterministically first, then explained by AI
- **Inventory modeling** — safety stock, reorder point, EOQ, and days of supply applied to a real business domain with per-SKU lead times and demand variability
- **Explainable decision support** — every reorder recommendation includes a business reason, calculation reason, and demand signal reason; confidence scores make uncertainty visible
- **Streamlit dashboard development** — multi-tab layout, sidebar what-if controls, Plotly interactive charts, custom CSS card components, real-time recalculation on slider changes
- **Testable Python business logic** — all supply chain math and signal weighting lives outside `app.py` in importable modules with a full pytest suite
- **Practical use of forecasting signals** — NOAA tides, moon phase, barometric pressure, Reddit social velocity, and Google Trends combined into a single weighted demand index
- **Human-in-the-loop AI design** — AI explains what the math already decided; domain knowledge (4 years in a bait shop) informed every multiplier value and SKU assumption

## Future Improvements

- Connect live POS data to replace seed inventory
- Add historical demand tracking to improve signal multiplier calibration
- SMS/email reorder alerts when SKU crosses reorder point
- Expand to multi-location inventory comparison
