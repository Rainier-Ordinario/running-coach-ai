import os
import json
import logging
from datetime import datetime, timezone

from garmin import get_client, fetch_activities, fetch_health_range, fetch_profile
from paths import DATA_DIR, ACTIVITIES_PATH

log = logging.getLogger(__name__)

# Pull a month of daily health data so the recovery advisor has trend context.
HEALTH_LOOKBACK_DAYS = 30


def sync():
    """Pull activities + recent health data from Garmin and write to disk."""
    os.makedirs(DATA_DIR, exist_ok=True)

    # One login covers both calls.
    client = get_client()

    activities = fetch_activities(client)
    log.info("Fetched %d running activities", len(activities))

    health_data = fetch_health_range(client, days=HEALTH_LOOKBACK_DAYS)
    log.info("Fetched health data for %d days", len(health_data))

    # Profile rarely changes but the call is cheap; cache it alongside the rest.
    try:
        profile = fetch_profile(client)
    except Exception as e:
        log.warning("Profile fetch failed: %s", e)
        profile = None

    # Attach matching health snapshot onto each activity for quick lookup.
    for activity in activities:
        day = activity.get("start_date", "")[:10]
        if day in health_data:
            activity["health_metrics"] = health_data[day]

    output = {
        "synced_at": datetime.now(timezone.utc).isoformat(),
        "activities": activities,
        "health_data": health_data,
        "profile": profile,
    }

    with open(ACTIVITIES_PATH, "w") as f:
        json.dump(output, f)

    return len(activities), output["synced_at"]
