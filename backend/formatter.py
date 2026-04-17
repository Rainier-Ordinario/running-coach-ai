from datetime import datetime


def format_activities(activities):
    runs = [a for a in activities if a.get("type") == "Run"]
    runs.sort(key=lambda x: x.get("start_date", ""), reverse=True)
    runs = runs[:80]

    lines = []
    for run in runs:
        date_str = datetime.fromisoformat(run["start_date"].replace("Z", "+00:00")).strftime(
            "%Y-%m-%d"
        )
        name = run.get("name", "Run")
        distance_km = run.get("distance", 0) / 1000
        moving_time_seconds = run.get("moving_time", 1)
        moving_time_minutes = moving_time_seconds / 60
        pace = moving_time_minutes / distance_km if distance_km > 0 else 0
        pace_minutes = int(pace)
        pace_seconds = int((pace - pace_minutes) * 60)
        pace_str = f"{pace_minutes}:{pace_seconds:02d}"

        avg_hr = run.get("average_heartrate")
        hr_str = f"HR: {int(avg_hr)}bpm" if avg_hr else "HR: N/A"

        line = f"[{date_str}] {name} — {distance_km:.2f}km @ {pace_str}/km | {hr_str}"
        lines.append(line)

    return "\n".join(lines)
