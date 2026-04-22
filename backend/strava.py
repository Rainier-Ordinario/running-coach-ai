import os
import time
import requests
from dotenv import load_dotenv

load_dotenv()


def get_access_token():
    """Exchange refresh token for a short-lived access token"""
    client_id = os.getenv("STRAVA_CLIENT_ID")
    client_secret = os.getenv("STRAVA_CLIENT_SECRET")
    refresh_token = os.getenv("STRAVA_REFRESH_TOKEN")

    response = requests.post(
        "https://www.strava.com/oauth/token",
        data={
            "client_id": client_id,
            "client_secret": client_secret,
            "refresh_token": refresh_token,
            "grant_type": "refresh_token",
        },
    )
    response.raise_for_status()
    print(response.json())
    return response.json()["access_token"]


def fetch_activities(weeks=12):
    """Fetch all running activities from the past N weeks (Strava returns max 200 per page)"""
    access_token = get_access_token()
    print(f"Access token: {access_token}")
    # Calculate timestamp for N weeks ago
    after_timestamp = int(time.time()) - (weeks * 7 * 24 * 3600)

    headers = {"Authorization": f"Bearer {access_token}"}
    print(f"Headers: {headers}")
    all_activities = []
    page = 1

    # Paginate through all activities
    while True:
        response = requests.get(
            "https://www.strava.com/api/v3/athlete/activities",
            headers=headers,
            params={"after": after_timestamp, "per_page": 200, "page": page},
        )
        response.raise_for_status()
        activities = response.json()

        # Stop when no more activities returned
        if not activities:
            break

        all_activities.extend(activities)
        page += 1

    return all_activities
