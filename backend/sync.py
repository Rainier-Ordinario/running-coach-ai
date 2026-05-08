import os
import json
from datetime import datetime
from garmin import fetch_activities, fetch_daily_health_data


def sync():
    """Fetch activities and health data from Garmin and save to local JSON file"""
    data_dir = "backend/data"
    os.makedirs(data_dir, exist_ok=True)

    # Get all activities from Garmin
    activities = fetch_activities()

    # Collect activity dates for health data fetch
    activity_dates = [a.get("start_date", "") for a in activities if a.get("start_date")]

    # Fetch daily health metrics for those dates
    print(f"Fetching health data for {len(activity_dates)} days...")
    health_data = fetch_daily_health_data(activity_dates)

    # Add health data to activities
    for activity in activities:
        activity_date = activity.get("start_date", "").split("T")[0]
        if activity_date in health_data:
            activity["health_metrics"] = health_data[activity_date]

    # Create output with timestamp, activities, and health data
    output = {
        "synced_at": datetime.utcnow().isoformat(),
        "activities": activities,
        "health_data": health_data,
    }

    # Save to file
    output_path = os.path.join(data_dir, "activities.json")
    with open(output_path, "w") as f:
        json.dump(output, f)

    print(f"Synced {len(activities)} activities with health data")
    return len(activities), output["synced_at"]
