from datetime import datetime, timezone, timedelta, date

# Fields the design wants per health snapshot, mapped to internal names.
HEALTH_FIELD_MAP = {
    "hrv": "hrv",
    "sleep": "sleep_duration",
    "sleep_q": "sleep_quality",
    "bb": "body_battery_high",
    "bb_now": "body_battery_current",
    "rhr": "resting_hr",
    "recovery_h": "recovery_time_hours",
    "readiness": "training_readiness",
    "level": "training_readiness_level",
}

RACE_KEYWORDS = ("marathon", "race", "10k", "half")
RACE_DISTANCE_THRESHOLD_M = 35_000  # full-marathon-ish runs auto-tag as RACE


def _pace_str(distance_m, time_seconds):
    """Build a min:sec/km pace string from raw meters + seconds."""
    distance_km = (distance_m or 0) / 1000
    if distance_km <= 0 or not time_seconds:
        return None
    pace_min = (time_seconds / 60) / distance_km
    minutes = int(pace_min)
    seconds = int(round((pace_min - minutes) * 60))
    if seconds == 60:
        minutes += 1
        seconds = 0
    return f"{minutes}:{seconds:02d}"


def _parse_start_date(iso):
    """Parse a stored ISO start_date into a UTC-aware datetime."""
    try:
        return datetime.fromisoformat(iso.replace("Z", "+00:00"))
    except (ValueError, AttributeError):
        return None


def _tag_for(activity):
    """Auto-tag long runs / named races so the UI can highlight them."""
    name = (activity.get("name") or "").lower()
    if any(k in name for k in RACE_KEYWORDS):
        return "RACE"
    if (activity.get("distance") or 0) >= RACE_DISTANCE_THRESHOLD_M:
        return "RACE"
    return None


def _shape_activity(activity):
    """Convert a stored activity into the field names the dashboard expects."""
    distance_m = activity.get("distance") or 0
    return {
        "date": (activity.get("start_date") or "")[:10],
        "name": activity.get("name", "Run"),
        "km": round(distance_m / 1000, 2),
        "sec": int(activity.get("moving_time") or 0),
        "hr": int(activity["average_heartrate"]) if activity.get("average_heartrate") else None,
        "elev": int(round(activity["elevation_gain"])) if activity.get("elevation_gain") else 0,
        "load": round(activity.get("training_load") or 0, 1),
        "te_aero": round(activity.get("aerobic_te") or 0, 1),
        "te_anaero": round(activity.get("anaerobic_te") or 0, 1),
        "tag": _tag_for(activity),
    }


def _shape_health(snapshot):
    """Convert a stored health snapshot into compact dashboard keys."""
    out = {"date": snapshot.get("date")}
    for short, long in HEALTH_FIELD_MAP.items():
        out[short] = snapshot.get(long)
    return out


def _most_recent_health(health_data):
    """Most recent day with at least one populated metric, in design-friendly shape."""
    for day in sorted(health_data.keys(), reverse=True):
        snapshot = health_data[day]
        if any(v is not None for k, v in snapshot.items() if k != "date"):
            return _shape_health(snapshot)
    return None


def _weekly_mileage(runs, weeks=14):
    """Bucket runs into ISO weeks (Mon–Sun) for the last N weeks."""
    today = datetime.now(timezone.utc).date()
    # Anchor each bucket on the Monday that starts the week.
    monday_of_today = today - timedelta(days=today.weekday())
    buckets = []
    for offset in range(weeks - 1, -1, -1):
        week_start = monday_of_today - timedelta(weeks=offset)
        buckets.append({"wk": week_start.isoformat(), "km": 0.0})

    earliest_monday = monday_of_today - timedelta(weeks=weeks - 1)
    for r in runs:
        dt = _parse_start_date(r.get("start_date", ""))
        if not dt:
            continue
        run_date = dt.date()
        if run_date < earliest_monday or run_date > today:
            continue
        run_monday = run_date - timedelta(days=run_date.weekday())
        idx = (run_monday - earliest_monday).days // 7
        if 0 <= idx < weeks:
            buckets[idx]["km"] += (r.get("distance") or 0) / 1000

    for b in buckets:
        b["km"] = round(b["km"], 1)
    return buckets


def build_dashboard(activities, health_data):
    """Build the JSON payload for the dashboard view."""
    runs = [a for a in activities if a.get("type") == "Run"]
    runs.sort(key=lambda r: r.get("start_date", ""), reverse=True)

    today = datetime.now(timezone.utc)
    today_str = today.date().isoformat()
    cutoff_7 = today - timedelta(days=7)
    year = today.year

    last_7 = [r for r in runs if (dt := _parse_start_date(r.get("start_date", ""))) and dt >= cutoff_7]
    ytd = [r for r in runs if (dt := _parse_start_date(r.get("start_date", ""))) and dt.year == year]

    last_7_distance_m = sum(r.get("distance", 0) or 0 for r in last_7)
    last_7_time_s = sum(r.get("moving_time", 0) or 0 for r in last_7)
    ytd_distance_m = sum(r.get("distance", 0) or 0 for r in ytd)

    # Health snapshots, newest day first, in design-friendly shape.
    health_list = [
        _shape_health(health_data[day])
        for day in sorted(health_data.keys(), reverse=True)
    ]

    return {
        "today": today_str,
        "totals": {
            "all_time_runs": len(runs),
            "ytd_runs": len(ytd),
            "ytd_distance_km": round(ytd_distance_m / 1000, 1),
            "last7_runs": len(last_7),
            "last7_distance_km": round(last_7_distance_m / 1000, 1),
            "last7_avg_pace": _pace_str(last_7_distance_m, last_7_time_s),
        },
        "current_health": _most_recent_health(health_data),
        "health": health_list,
        "activities": [_shape_activity(a) for a in runs[:80]],
        "weekly_mileage": _weekly_mileage(runs, weeks=14),
    }
