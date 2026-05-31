# TideStock — Bait Shop Inventory Command Center

> AI-assisted inventory command center for bait shop purchasing — SKU-level reorder decisions driven by environmental signals, social velocity, and supply chain math.

**[→ Live Demo](https://tidestock-ncjzm6vw5q7umpahfexwgy.streamlit.app)**

---

## Why This Exists

I worked at Crossroads Bait & Tackle for four years. Every spring we'd sell out of paddle tails the week stripers showed up, and every winter we'd sit on overstock we'd never move. The buying decisions were made on gut feel — experienced gut feel, but gut feel.

TideStock is what I'd have wanted: a Monday morning dashboard that combines environmental signals, social velocity, and inventory math to surface reorder decisions before demand hits the counter. The same forward-looking approach Amazon and Pepsi use internally, applied to a domain I actually know.

---

## What It Does

| Tab | What you get |
|---|---|
| Command Center | Sortable/filterable inventory table across 25 SKUs, KPI strip (Critical count, Revenue at Risk, Avg DoS), environmental signal snapshot, row-select detail panel, deterministic Buyer's Brief |
| Inventory | Plotly gauges for top SKUs by urgency, Days of Supply chart, Revenue at Risk chart, per-SKU reorder cards with explainability bullets |
| Demand Signals | Live NOAA tides, moon phase strip, pressure trend, species activity by month, Exa web fishing reports, Reddit fishing feed, 7-day fishing forecast, tournament calendar |
| Scenario Simulator | Signal weight sliders with real-time demand chart, preset scenario toggles (tournament weekend, viral bait, cold front, striper run), SKU-level status changes table |
| AI Brief | Groq-powered Monday morning S&OP memo — synthesizes all signals into buyer-ready planning language, streamable output, "Ask Dave" Q&A, Intel Sources provenance |

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

Status labels — Critical / Reorder Soon / Watch / Healthy — are computed per SKU across 25 realistic products (7 categories) with explainability bullets covering business context, calculation basis, and demand signal. Perishable SKUs (bloodworms, sandworms, minnows) carry additional urgency logic for overstock spoilage risk.

---

## Tech Stack

Python · Streamlit · Plotly · NOAA CO-OPS API · NDBC Buoy · Open-Meteo · ephem · Reddit Public JSON API · pytrends · Exa · Groq (LLaMA 3.3 70B)

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
EXA_API_KEY=...           # free tier at exa.ai
```

Reddit data is fetched from the public JSON API — no credentials required.

---

## Running Tests

```bash
pip install -r requirements-dev.txt
pytest tests/ -v
```

---

## Screenshots

*To capture from the running app before final push (save under `docs/screenshots/`, reference with relative links):*

- [ ] Command Center — KPI strip + sortable inventory table
- [ ] Inventory — gauges, Days of Supply, Revenue at Risk
- [ ] Demand Signals — tides, barometric pressure, web fishing reports
- [ ] Scenario Simulator — signal weight sliders + scenario presets
- [ ] AI Brief — Dave's Morning Intel + Ask Dave

---

## AI Development

See [`docs/ai-development-log.md`](docs/ai-development-log.md) for a full breakdown of how AI was used in this project — what it generated, what I validated, and where domain knowledge drove the decisions.

---

## Resume Summary

> Built AI-powered bait shop demand intelligence dashboard — integrates NOAA tide predictions, moon phase, barometric pressure, Reddit social velocity, Exa web reports, and species calendars into interactive Plotly scenario simulations and Groq-powered weekly planning briefs with per-SKU reorder explainability; deployed on Streamlit Cloud.

**Interview story:** I worked at a bait shop for four years. We'd sell out of paddle tails right when striper season peaked and over-order all winter. I built a demand planning system that combines environmental data with social signal velocity to predict demand before it happens — the same forward-looking approach Amazon and Pepsi use internally, applied to a domain I actually know.

---

## What This Demonstrates

- **AI-assisted product development** — Claude assisted development (architecture, code generation, review); Groq/LLaMA powers the in-app planning briefs at runtime. All recommendations are computed deterministically first, then explained by AI
- **Inventory modeling** — safety stock, reorder point, EOQ, and days of supply applied to a real business domain with per-SKU lead times and demand variability
- **Explainable decision support** — every reorder recommendation includes a business reason, calculation reason, and demand signal reason; confidence scores make uncertainty visible
- **Streamlit dashboard development** — multi-tab layout, sidebar what-if controls, Plotly interactive charts, custom CSS card components, real-time recalculation on slider changes
- **Testable Python business logic** — all supply chain math and signal weighting lives outside `app.py` in importable modules with a full pytest suite
- **Practical use of forecasting signals** — NOAA tides, moon phase, barometric pressure, Reddit social velocity, Exa web reports, and species calendars combined into a single weighted demand index
- **Human-in-the-loop AI design** — AI explains what the math already decided; domain knowledge (4 years in a bait shop) informed every multiplier value and SKU assumption

## Future Improvements

- Connect live POS data to replace seed inventory
- Add historical demand tracking to improve signal multiplier calibration
- SMS/email reorder alerts when SKU crosses reorder point
- Expand to multi-location inventory comparison
