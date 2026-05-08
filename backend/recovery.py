import os
import json
from anthropic import Anthropic
from formatter import format_activities
from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv()


def get_recovery_recommendation(activities, health_data):
    """Get rest vs train recommendation based on recent health trends and training"""
    # Initialize client with API key from environment
    client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    # Format recent activities with their health metrics
    activities_summary = format_activities(activities)

    # Calculate recent health trends (last 7 days average)
    recent_health = calculate_health_trends(activities, health_data)

    # Build health summary
    health_summary = f"""
Recent Health Trends (Last 7 Days):
- Average HRV: {recent_health.get('avg_hrv', 'N/A')} ms
- Average Sleep: {recent_health.get('avg_sleep', 'N/A')} hours
- Average Sleep Quality: {recent_health.get('avg_sleep_quality', 'N/A')}%
- Average Stress: {recent_health.get('avg_stress', 'N/A')}/100
- Average Body Battery: {recent_health.get('avg_body_battery', 'N/A')}%

Today's Status:
- Today's HRV: {recent_health.get('today_hrv', 'N/A')} ms
- Today's Sleep Quality: {recent_health.get('today_sleep_quality', 'N/A')}%
- Today's Stress: {recent_health.get('today_stress', 'N/A')}/100
- Today's Body Battery: {recent_health.get('today_body_battery', 'N/A')}%

Recent Training:
{activities_summary}
"""

    # System prompt for recovery advisor
    system_prompt = (
        "You are an expert sports physiologist and recovery specialist. "
        "Based on the athlete's health metrics trends and recent training data, provide a clear recommendation: REST or TRAIN. "
        "Consider HRV trends, sleep quality, stress levels, body battery status, and training volume. "
        "If recommending rest, explain why and suggest recovery activities (stretching, foam rolling, etc). "
        "If recommending training, specify intensity (easy, moderate, hard) and duration. "
        "Be direct and specific."
    )

    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=1024,
        system=system_prompt,
        messages=[{"role": "user", "content": health_summary}],
    )

    return response.content[0].text


def calculate_health_trends(activities, health_data):
    """Calculate recent health trends from the past 7 days"""
    trends = {
        'avg_hrv': None,
        'avg_sleep': None,
        'avg_sleep_quality': None,
        'avg_stress': None,
        'avg_body_battery': None,
        'today_hrv': None,
        'today_sleep_quality': None,
        'today_stress': None,
        'today_body_battery': None,
    }

    today = datetime.now().date()
    seven_days_ago = today - timedelta(days=7)

    hrv_values = []
    sleep_values = []
    sleep_quality_values = []
    stress_values = []
    battery_values = []

    for date_str, metrics in health_data.items():
        try:
            date_obj = datetime.fromisoformat(date_str).date()

            # Collect 7-day averages
            if seven_days_ago <= date_obj <= today:
                if metrics.get('hrv'):
                    hrv_values.append(metrics['hrv'])
                if metrics.get('sleep_duration'):
                    sleep_values.append(metrics['sleep_duration'])
                if metrics.get('sleep_quality'):
                    sleep_quality_values.append(metrics['sleep_quality'])
                if metrics.get('stress'):
                    stress_values.append(metrics['stress'])
                if metrics.get('body_battery'):
                    battery_values.append(metrics['body_battery'])

            # Get today's specific metrics
            if date_obj == today:
                trends['today_hrv'] = metrics.get('hrv')
                trends['today_sleep_quality'] = metrics.get('sleep_quality')
                trends['today_stress'] = metrics.get('stress')
                trends['today_body_battery'] = metrics.get('body_battery')
        except:
            continue

    # Calculate averages
    if hrv_values:
        trends['avg_hrv'] = round(sum(hrv_values) / len(hrv_values), 1)
    if sleep_values:
        trends['avg_sleep'] = round(sum(sleep_values) / len(sleep_values), 1)
    if sleep_quality_values:
        trends['avg_sleep_quality'] = round(sum(sleep_quality_values) / len(sleep_quality_values), 1)
    if stress_values:
        trends['avg_stress'] = round(sum(stress_values) / len(stress_values), 1)
    if battery_values:
        trends['avg_body_battery'] = round(sum(battery_values) / len(battery_values), 1)

    return trends
