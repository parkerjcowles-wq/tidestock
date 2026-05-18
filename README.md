# 🎣 TideStock — Bait Shop Demand Intelligence

> AI-powered demand planning for independent bait & tackle shops.

**[→ Live Demo](YOUR_STREAMLIT_URL_HERE)**

TideStock combines environmental signals, social velocity data, and AI to help bait shop buyers make smarter inventory decisions — before demand hits.

## What It Does

| Tab | What you get |
|---|---|
| 🌊 Conditions | NOAA tide predictions, moon phase fishing scores, pressure trends, species activity |
| 📡 Social Intel | Reddit fishing community buzz, Google Trends spikes, tournament calendar |
| 🎛️ Scenario Sim | Adjust signal weights in real time, toggle preset scenarios, compare baseline vs. scenario demand |
| 📦 Inventory | Plotly gauges, days-of-supply chart, safety stock / reorder point / EOQ per SKU |
| 🤖 AI Brief | Claude-powered Monday morning planning memo — synthesizes all signals |

## Tech Stack

Python · Streamlit · Plotly · NOAA CO-OPS API · Open-Meteo · ephem · PRAW · pytrends · Exa · Anthropic Claude

## Local Setup

```bash
git clone https://github.com/parkerjcowles/tidestock
cd tidestock
pip install -r requirements.txt
cp .env.example .env   # fill in API keys
streamlit run app.py
```

## API Keys Required

Set these in `.env` for local dev, or in Streamlit Cloud Secrets for deployment:

```
ANTHROPIC_API_KEY=...
REDDIT_CLIENT_ID=...
REDDIT_CLIENT_SECRET=...
REDDIT_USER_AGENT=TideStock/1.0
EXA_API_KEY=...
```

Reddit credentials: create a free app at [reddit.com/prefs/apps](https://www.reddit.com/prefs/apps) (script type).
