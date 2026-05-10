import os
import logging
from datetime import datetime, timezone, date, timedelta
from garminconnect import Garmin
from dotenv import load_dotenv

load_dotenv()

log = logging.getLogger(__name__)


def get_client():
    """Log in to Garmin Connect once and return an authenticated client."""
    email = os.getenv("GARMIN_EMAIL")
    password = os.getenv("GARMIN_PASSWORD")
    client = Garmin(email, password)
    client.login()
    return client


def _safe(label, fn, *args, **kwargs):
    """Run a Garmin API call and log (rather than raise) on failure."""
    try:
        return fn(*args, **kwargs)
    except Exception as e:
        log.warning("Garmin %s failed: %s", label, e)
        return None


def _normalize_start_date(raw):
    """Convert Garmin's "YYYY-MM-DD HH:MM:SS" (UTC) into ISO 8601 with Z."""
    if not raw:
        return ""
    iso = raw.replace(" ", "T")
    if not iso.endswith("Z"):
        iso += "Z"
    return iso


def _activity_dt(raw):
    """Parse a Garmin startTimeGMT string into a UTC-aware datetime, or None."""
    if not raw:
        return None
    try:
        return datetime.fromisoformat(raw.replace(" ", "T")).replace(tzinfo=timezone.utc)
    except ValueError:
        return None


def fetch_activities(client, weeks=None):
    """Fetch running activities from Garmin Connect.

    If weeks is None, returns all historical runs. Otherwise stops at the cutoff.
    """
    if weeks is not None:
        cutoff_dt = datetime.now(timezone.utc) - timedelta(weeks=weeks)
    else:
        cutoff_dt = None

    runs = []
    start = 0
    limit = 100

    while True:
        batch = client.get_activities(start, limit)
        if not batch:
            break

        for activity in batch:
            activity_dt = _activity_dt(activity.get("startTimeGMT"))
            if activity_dt is None:
                continue

            # Garmin returns activities newest-first, so we can stop early.
            if cutoff_dt and activity_dt < cutoff_dt:
                return runs

            if activity.get("activityType", {}).get("typeKey") != "running":
                continue

            runs.append({
                "id": activity.get("activityId"),
                "name": activity.get("activityName", "Run"),
                "type": "Run",
                "start_date": _normalize_start_date(activity.get("startTimeGMT")),
                "distance": activity.get("distance", 0),
                "moving_time": int(activity.get("movingDuration") or activity.get("duration", 0)),
                "elevation_gain": activity.get("elevationGain"),
                "calories": activity.get("calories"),
                "average_heartrate": activity.get("averageHR"),
                "max_heartrate": activity.get("maxHR"),
                "average_pace": activity.get("averageSpeed"),  # m/s
                "average_cadence": activity.get("averageRunningCadenceInStepsPerMinute"),
                "training_load": activity.get("activityTrainingLoad"),
                "aerobic_te": activity.get("aerobicTrainingEffect"),
                "anaerobic_te": activity.get("anaerobicTrainingEffect"),
            })

        start += limit

    return runs


def _extract_hrv(payload):
    """Pull last-night HRV average from the HRV API response."""
    if not payload:
        return None
    summary = payload.get("hrvSummary") or {}
    return summary.get("lastNightAvg")


def _extract_sleep(payload):
    """Pull sleep duration (hours) and overall sleep score from the sleep API."""
    if not payload:
        return None, None
    dto = payload.get("dailySleepDTO") or {}
    seconds = dto.get("sleepTimeSeconds")
    hours = round(seconds / 3600, 2) if seconds else None
    score = ((dto.get("sleepScores") or {}).get("overall") or {}).get("value")
    return hours, score


def fetch_health_for_date(client, day):
    """Fetch a single day's health snapshot.

    Combines HRV, sleep, and the daily stats summary (which already contains
    body battery, stress, and resting HR) into one dict. Returns None for any
    metric Garmin doesn't have for that day.
    """
    day_str = day.isoformat() if isinstance(day, date) else day

    hrv = _safe("hrv", client.get_hrv_data, day_str)
    sleep = _safe("sleep", client.get_sleep_data, day_str)
    stats = _safe("stats", client.get_stats, day_str) or {}
    readiness = _safe("training_readiness", client.get_training_readiness, day_str)

    sleep_hours, sleep_score = _extract_sleep(sleep)

    # Training readiness API returns a list (one entry per device); take the first.
    readiness_entry = readiness[0] if isinstance(readiness, list) and readiness else {}

    return {
        "date": day_str,
        "hrv": _extract_hrv(hrv),
        "resting_hr": stats.get("restingHeartRate"),
        "sleep_duration": sleep_hours,
        "sleep_quality": sleep_score,
        "stress_avg": stats.get("averageStressLevel"),
        "stress_max": stats.get("maxStressLevel"),
        "body_battery_high": stats.get("bodyBatteryHighestValue"),
        "body_battery_low": stats.get("bodyBatteryLowestValue"),
        "body_battery_current": stats.get("bodyBatteryMostRecentValue"),
        "steps": stats.get("totalSteps"),
        "training_readiness": readiness_entry.get("score"),
        "training_readiness_level": readiness_entry.get("level"),
        "recovery_time_hours": readiness_entry.get("recoveryTime"),
    }


def fetch_health_range(client, days=30):
    """Fetch health snapshots for the last N days, keyed by YYYY-MM-DD."""
    today = date.today()
    health_by_date = {}

    for offset in range(days):
        day = today - timedelta(days=offset)
        snapshot = fetch_health_for_date(client, day)
        # Only keep snapshots that have at least one real metric.
        if any(v is not None for k, v in snapshot.items() if k != "date"):
            health_by_date[day.isoformat()] = snapshot

    return health_by_date


def get_health_metrics():
    """Convenience wrapper: today's health snapshot."""
    client = get_client()
    return fetch_health_for_date(client, date.today())
