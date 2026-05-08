import os
import time
from datetime import datetime, timezone, date
from garminconnect import Garmin
from dotenv import load_dotenv

load_dotenv()


def get_health_metrics():
    """Fetch current health metrics including HRV, sleep, stress, and recovery"""
    email = os.getenv("GARMIN_EMAIL")
    password = os.getenv("GARMIN_PASSWORD")

    client = Garmin(email, password)
    client.login()

    # Get today's health snapshot
    today = date.today()
    health_data = {
        "hrv": None,
        "resting_hr": None,
        "sleep_duration": None,
        "sleep_quality": None,
        "stress_level": None,
        "recovery_time": None,
        "body_battery": None,
    }

    try:
        # Heart Rate Variability - needs date parameter
        hrv_data = client.get_hrv_data(today)
        if hrv_data:
            health_data["hrv"] = hrv_data.get("lastNightAverage")
    except Exception as e:
        print(f"Could not fetch HRV: {e}")

    try:
        # Stress data
        stress_data = client.get_stress_data(today)
        if stress_data:
            health_data["stress_level"] = stress_data.get("currentStress")
    except Exception as e:
        print(f"Could not fetch stress data: {e}")

    try:
        # Sleep data - needs date parameter
        sleep_data = client.get_sleep_data(today)
        if sleep_data:
            health_data["sleep_duration"] = sleep_data.get("totalSleepTime")
            health_data["sleep_quality"] = sleep_data.get("sleepQuality")
    except Exception as e:
        print(f"Could not fetch sleep data: {e}")

    try:
        # Body Battery - needs date parameter
        body_battery = client.get_body_battery(today)
        if body_battery:
            health_data["body_battery"] = body_battery.get("currentBattery")
    except Exception as e:
        print(f"Could not fetch body battery: {e}")

    try:
        # Resting HR from stats
        stats = client.get_stats(today)
        if stats:
            health_data["resting_hr"] = stats.get("restingHeartRate")
    except Exception as e:
        print(f"Could not fetch resting HR: {e}")

    return health_data


def fetch_daily_health_data(activity_dates):
    """Fetch health metrics for each activity date"""
    email = os.getenv("GARMIN_EMAIL")
    password = os.getenv("GARMIN_PASSWORD")

    client = Garmin(email, password)
    client.login()

    health_by_date = {}

    for activity_date in activity_dates:
        try:
            date_obj = datetime.fromisoformat(activity_date.replace("Z", "+00:00")).date()
            health_metrics = {}

            try:
                hrv_data = client.get_hrv_data(date_obj)
                if hrv_data:
                    health_metrics["hrv"] = hrv_data.get("lastNightAverage")
            except:
                pass

            try:
                stress_data = client.get_stress_data(date_obj)
                if stress_data:
                    health_metrics["stress"] = stress_data.get("currentStress")
            except:
                pass

            try:
                sleep_data = client.get_sleep_data(date_obj)
                if sleep_data:
                    health_metrics["sleep_duration"] = sleep_data.get("totalSleepTime")
                    health_metrics["sleep_quality"] = sleep_data.get("sleepQuality")
            except:
                pass

            try:
                body_battery = client.get_body_battery(date_obj)
                if body_battery:
                    health_metrics["body_battery"] = body_battery.get("currentBattery")
            except:
                pass

            if health_metrics:
                health_by_date[activity_date.split("T")[0]] = health_metrics
        except:
            continue

    return health_by_date


def fetch_activities(weeks=None):
    """Fetch all running activities from Garmin Connect (all historical data by default)"""
    email = os.getenv("GARMIN_EMAIL")
    password = os.getenv("GARMIN_PASSWORD")

    client = Garmin(email, password)
    client.login()

    # Set cutoff date - if weeks is None, fetch all data
    if weeks is not None:
        cutoff = time.time() - (weeks * 7 * 24 * 3600)
        cutoff_dt = datetime.fromtimestamp(cutoff, tz=timezone.utc)
    else:
        cutoff_dt = None

    # Fetch all activities with pagination
    all_activities = []
    start = 0
    limit = 100

    while True:
        batch = client.get_activities(start, limit)
        if not batch:
            break

        for activity in batch:
            start_gmt = activity.get("startTimeGMT", "")
            try:
                activity_dt = datetime.fromisoformat(start_gmt).replace(tzinfo=timezone.utc)
            except ValueError:
                continue

            # Stop if we've reached the cutoff date (only if cutoff is set)
            if cutoff_dt and activity_dt < cutoff_dt:
                return all_activities

            activity_type = activity.get("activityType", {}).get("typeKey", "")
            if activity_type != "running":
                continue

            all_activities.append({
                "name": activity.get("activityName", "Run"),
                "distance": activity.get("distance", 0),
                "moving_time": int(activity.get("movingDuration") or activity.get("duration", 0)),
                "start_date": start_gmt + "Z" if start_gmt and not start_gmt.endswith("Z") else start_gmt,
                "type": "Run",
                "average_heartrate": activity.get("averageHR"),
            })

        start += limit

    return all_activities
