import os
import json
from datetime import datetime
from strava import fetch_activities


def sync():
    """Fetch activities from Strava and save to local JSON file"""
    data_dir = "backend/data"
    os.makedirs(data_dir, exist_ok=True)

    # Get all activities from Strava
    activities = fetch_activities()

    # Create output with timestamp and activities
    output = {
        "synced_at": datetime.utcnow().isoformat(),
        "activities": activities,
    }

    # Save to file
    output_path = os.path.join(data_dir, "activities.json")
    with open(output_path, "w") as f:
        json.dump(output, f)

    print(f"Synced {len(activities)} activities")
    return len(activities), output["synced_at"]
