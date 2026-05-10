from datetime import datetime

# Cap context size — recent runs are what matter for coaching.
MAX_RUNS = 80


def _parse_date(start_date):
    """Parse stored ISO start_date back into a date string."""
    iso = start_date.replace("Z", "+00:00")
    return datetime.fromisoformat(iso).strftime("%Y-%m-%d")


def _format_pace(distance_m, moving_seconds):
    """Build a min:sec/km pace string from raw distance + duration."""
    distance_km = distance_m / 1000
    if distance_km <= 0:
        return "—"
    pace_min = (moving_seconds / 60) / distance_km
    minutes = int(pace_min)
    seconds = int((pace_min - minutes) * 60)
    return f"{minutes}:{seconds:02d}"


def _format_health(metrics):
    """Compact one-line summary of attached health metrics."""
    if not metrics:
        return ""
    parts = []
    if metrics.get("hrv") is not None:
        parts.append(f"HRV {metrics['hrv']}ms")
    if metrics.get("sleep_duration") is not None:
        parts.append(f"sleep {metrics['sleep_duration']}h")
    if metrics.get("sleep_quality") is not None:
        parts.append(f"sleep score {metrics['sleep_quality']}")
    if metrics.get("body_battery_high") is not None:
        parts.append(f"BB {metrics['body_battery_high']}")
    if metrics.get("training_readiness") is not None:
        parts.append(f"readiness {metrics['training_readiness']}")
    return f" | {', '.join(parts)}" if parts else ""


def format_activities(activities):
    """Format the most recent runs into a compact summary for the AI coach."""
    runs = [a for a in activities if a.get("type") == "Run"]
    runs.sort(key=lambda x: x.get("start_date", ""), reverse=True)
    runs = runs[:MAX_RUNS]

    lines = []
    for run in runs:
        date_str = _parse_date(run["start_date"])
        name = run.get("name", "Run")
        distance_km = run.get("distance", 0) / 1000
        pace_str = _format_pace(run.get("distance", 0), run.get("moving_time", 1))

        avg_hr = run.get("average_heartrate")
        hr_str = f"HR {int(avg_hr)}bpm" if avg_hr else "HR N/A"

        health_str = _format_health(run.get("health_metrics"))

        lines.append(
            f"[{date_str}] {name} — {distance_km:.2f}km @ {pace_str}/km | {hr_str}{health_str}"
        )

    return "\n".join(lines)
