import os
from datetime import datetime, timedelta

from anthropic import Anthropic
from dotenv import load_dotenv

from formatter import format_activities

load_dotenv()

MODEL = "claude-opus-4-7"
TREND_WINDOW_DAYS = 7


def _avg(values):
    """Round-1 average, or None if the list is empty."""
    return round(sum(values) / len(values), 1) if values else None


def calculate_health_trends(health_data):
    """Aggregate the last 7 days of health snapshots and pull today's values."""
    today = datetime.now().date()
    window_start = today - timedelta(days=TREND_WINDOW_DAYS)

    buckets = {
        "hrv": [], "sleep": [], "sleep_quality": [],
        "stress": [], "body_battery": [], "readiness": [],
    }
    today_metrics = {}

    for date_str, metrics in health_data.items():
        try:
            day = datetime.fromisoformat(date_str).date()
        except ValueError:
            continue

        if window_start <= day <= today:
            if metrics.get("hrv") is not None: buckets["hrv"].append(metrics["hrv"])
            if metrics.get("sleep_duration") is not None: buckets["sleep"].append(metrics["sleep_duration"])
            if metrics.get("sleep_quality") is not None: buckets["sleep_quality"].append(metrics["sleep_quality"])
            if metrics.get("stress_avg") is not None: buckets["stress"].append(metrics["stress_avg"])
            if metrics.get("body_battery_high") is not None: buckets["body_battery"].append(metrics["body_battery_high"])
            if metrics.get("training_readiness") is not None: buckets["readiness"].append(metrics["training_readiness"])

        if day == today:
            today_metrics = metrics

    return {
        "avg_hrv": _avg(buckets["hrv"]),
        "avg_sleep": _avg(buckets["sleep"]),
        "avg_sleep_quality": _avg(buckets["sleep_quality"]),
        "avg_stress": _avg(buckets["stress"]),
        "avg_body_battery": _avg(buckets["body_battery"]),
        "avg_readiness": _avg(buckets["readiness"]),
        "today_hrv": today_metrics.get("hrv"),
        "today_sleep": today_metrics.get("sleep_duration"),
        "today_sleep_quality": today_metrics.get("sleep_quality"),
        "today_stress": today_metrics.get("stress_avg"),
        "today_body_battery": today_metrics.get("body_battery_current"),
        "today_readiness": today_metrics.get("training_readiness"),
        "today_readiness_level": today_metrics.get("training_readiness_level"),
        "today_recovery_hours": today_metrics.get("recovery_time_hours"),
    }


def _build_health_summary(trends, activities_summary):
    """Render the trends + recent runs into a single prompt-friendly block."""
    return f"""
Recent Health Trends (Last {TREND_WINDOW_DAYS} Days):
- Average HRV: {trends['avg_hrv']} ms
- Average Sleep Duration: {trends['avg_sleep']} hours
- Average Sleep Score: {trends['avg_sleep_quality']}/100
- Average Stress: {trends['avg_stress']}/100
- Average Body Battery (peak): {trends['avg_body_battery']}/100
- Average Training Readiness: {trends['avg_readiness']}/100

Today's Status:
- HRV: {trends['today_hrv']} ms
- Sleep: {trends['today_sleep']} hours (score {trends['today_sleep_quality']}/100)
- Stress: {trends['today_stress']}/100
- Body Battery: {trends['today_body_battery']}/100
- Training Readiness: {trends['today_readiness']}/100 ({trends['today_readiness_level']})
- Recovery Time Remaining: {trends['today_recovery_hours']} hours

Recent Training:
{activities_summary}
"""


def get_recovery_recommendation(activities, health_data):
    """Ask Claude for a REST-vs-TRAIN recommendation grounded in the data."""
    client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    trends = calculate_health_trends(health_data)
    activities_summary = format_activities(activities)
    user_prompt = _build_health_summary(trends, activities_summary)

    system_prompt = (
        "You are an expert sports physiologist and recovery specialist. "
        "Based on the athlete's health metrics trends and recent training data, "
        "provide a clear recommendation: REST or TRAIN. "
        "Consider HRV trends, sleep quality, stress levels, body battery status, "
        "training readiness, and recent training volume. "
        "If recommending rest, explain why and suggest recovery activities. "
        "If recommending training, specify intensity (easy, moderate, hard) and duration. "
        "Be direct and specific — reference the actual numbers."
    )

    response = client.messages.create(
        model=MODEL,
        max_tokens=1024,
        system=system_prompt,
        messages=[{"role": "user", "content": user_prompt}],
    )
    return response.content[0].text
