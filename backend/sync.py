import os
import json
from datetime import datetime
from strava import fetch_activities


def sync():
    data_dir = "backend/data"
    os.makedirs(data_dir, exist_ok=True)

    activities = fetch_activities()

    output = {
        "synced_at": datetime.utcnow().isoformat(),
        "activities": activities,
    }

    output_path = os.path.join(data_dir, "activities.json")
    with open(output_path, "w") as f:
        json.dump(output, f)

    print(f"Synced {len(activities)} activities")
    return len(activities), output["synced_at"]
