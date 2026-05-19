import os
import groq
import config


def build_brief_prompt(
    conditions: dict,
    inventory_summary: dict,
    social_velocity: str,
    trend_alerts: list,
    tournaments: list,
    active_scenario: str = None,
    service_level: float = 0.95,
) -> str:
    scenario_line = f"\nACTIVE SCENARIO: {active_scenario}" if active_scenario else ""
    tournament_line = (
        "Upcoming tournaments: " + ", ".join(t["title"][:50] for t in tournaments[:2])
        if tournaments else "No tournaments in near-term calendar."
    )
    trend_line = ", ".join(trend_alerts) if trend_alerts else "No significant trend spikes."
    inv_lines = "\n".join(
        f"  {label}: {summary['dos']:.0f} days of supply ({summary['urgency']})"
        for label, summary in inventory_summary.items()
    )
    return f"""You are a senior buyer at a New England bait shop preparing the Monday morning planning brief.
Write a concise S&OP-style memo (200–250 words) using ONLY the data below.
Use planning language: recommend, signal, risk, action required.
Format with these sections: Conditions Outlook | Hot SKUs This Week | Reorder Actions | Risk Watch

LOCATION: {config.SHOP_REGION}
DATE: {conditions.get('date', 'today')}

ENVIRONMENTAL CONDITIONS:
  Moon phase: {conditions.get('moon_phase', 'unknown').replace('_', ' ')}
  Tide quality: {conditions.get('tide_quality', 'moderate')}
  Barometric pressure: {conditions.get('pressure_trend', 'stable')}
  Water temperature: {conditions.get('water_temp', 55):.1f}°F
  Fishing score: {conditions.get('fishing_score', 70)}/100

SPECIES ACTIVITY: {', '.join(f"{sp}: {lvl}" for sp, lvl in conditions.get('species', {}).items())}

SOCIAL SIGNALS:
  Overall velocity: {social_velocity}
  Google Trends alerts: {trend_line}
  {tournament_line}

INVENTORY STATUS (days of supply):
{inv_lines}

TARGET SERVICE LEVEL: {int(service_level * 100)}%
{scenario_line}

Write the planning brief now:"""


def generate_brief_streaming(prompt: str):
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        yield (
            "**Demo Mode — AI brief unavailable** (no `GROQ_API_KEY` configured).\n\n"
            "Add your free Groq API key to Streamlit secrets to enable the AI-generated S&OP memo. "
            "The **Buyer's Brief** in the Inventory tab provides a deterministic summary that works without any API key."
        )
        return
    client = groq.Groq(api_key=api_key)
    stream = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        max_tokens=512,
        messages=[{"role": "user", "content": prompt}],
        stream=True,
    )
    for chunk in stream:
        text = chunk.choices[0].delta.content
        if text:
            yield text
