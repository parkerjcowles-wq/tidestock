# AI Development Log

This document describes how AI was used in building TideStock — what it did, what I validated, and where human judgment drove the decisions.

## How I Used AI in This Project

### Project Scaffolding
I described the domain problem — a bait shop that consistently over- and under-orders because demand is environmental, not just historical — and used AI to help design the five-tab app structure and file architecture. I made the call to prioritize a public Streamlit Cloud URL over a local-only tool, which shaped every other decision.

### Supply Chain Formula Validation
The inventory math (safety stock, reorder point, EOQ, days of supply) follows standard supply chain formulas. AI generated the initial implementations; I validated them against my OSCM coursework at Virginia Tech and my four years of real inventory experience at Crossroads Bait & Tackle. The signal weighting formula — a weighted average of six environmental and social multipliers — is an original design that I defined based on domain knowledge. AI implemented it; I defined the multipliers.

### Signal Multiplier Design
I set all multiplier values based on real fishing experience:
- New/full moon = 1.8× (tides are extreme, fish are active)
- Tournament proximity = 2.2× (single biggest demand spike in the business)
- Social trending = 2.0× (viral baits sell out faster than anything)

AI suggested the structure; I tuned every number.

### Code Review and Bug Detection
AI caught a bug where `safety_stock()` was being called with four arguments but the function signature only accepted three, causing silent incorrect calculations. I reviewed the fix before merging.

### Test Generation
AI generated the initial test suite covering NOAA API error handling, moon phase calculations, and inventory formula edge cases. I reviewed each test for correctness and added edge cases AI missed — specifically the case where a NOAA station returns HTTP 200 with an error body (a known API quirk that would have silently failed in production).

### Data Sourcing
All API integrations (NOAA CO-OPS, Open-Meteo, PRAW, pytrends, Exa) were chosen by me based on what data a real bait shop buyer would care about. AI wrote the fetcher code; I identified the correct NOAA station ID for Newburyport (8440466) and the NDBC buoy fallback (44013) for water temperature from prior fishing research.

### AI Planning Brief
The Groq/LLaMA prompt was co-designed: I specified the S&OP memo format, the signal inputs, and the planning language ("recommend," "risk," "action required"). The AI generates the text; the underlying data it reasons over is all computed deterministically by the signal weighting engine.

### Debugging
Several deployment issues were debugged collaboratively: Python 3.14 wheel compatibility (fixed via runtime.txt), NOAA station ID returning 400 errors (wrong station), and graceful fallback logic when APIs are unavailable.

### What I Validated Myself
- All multiplier values reflect real fishing patterns, not AI guesses
- NOAA station selection (verified against tidesandcurrents.noaa.gov)
- Inventory seed data (seeded from four years of Crossroads Bait & Tackle experience)
- Species seasonality calendar (regional New England fishing calendar)
- The claim that social velocity predicts demand before it hits the counter — this is the core thesis, and it's from direct observation working in a shop during viral bait moments

## Summary
AI acted as a fast collaborator and code generator. Domain knowledge, formula validation, data source selection, and product decisions were mine. The combination is what makes this project credible as a supply chain portfolio piece.
