import os
import json
import logging

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from sync import sync
from formatter import format_activities
from coach import ask_coach
from recovery import get_recovery_recommendation
from dashboard import build_dashboard
from paths import ACTIVITIES_PATH

logging.basicConfig(level=logging.INFO)

app = FastAPI()

# Allow the Vite dev server to call the API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _load_data():
    """Read the synced activities file. Raises 404 if no sync has run yet."""
    if not os.path.exists(ACTIVITIES_PATH):
        raise HTTPException(status_code=404, detail="No data — run a sync first.")
    with open(ACTIVITIES_PATH) as f:
        return json.load(f)


@app.get("/api/status")
def get_status():
    """Report whether synced data exists and when it was last refreshed."""
    if not os.path.exists(ACTIVITIES_PATH):
        return {"has_data": False, "activity_count": 0, "synced_at": None}

    with open(ACTIVITIES_PATH) as f:
        data = json.load(f)

    return {
        "has_data": True,
        "activity_count": len(data.get("activities", [])),
        "synced_at": data.get("synced_at"),
    }


@app.post("/api/sync")
def sync_garmin():
    """Pull latest activities + health data from Garmin."""
    count, synced_at = sync()
    return {"status": "ok", "count": count, "synced_at": synced_at}


@app.post("/api/chat")
def chat(request: dict):
    """Answer a coaching question using the athlete's recent training data."""
    question = request.get("question", "")
    history = request.get("history", [])

    data = _load_data()
    activities_summary = format_activities(data.get("activities", []))
    answer = ask_coach(question, history, activities_summary)
    return {"answer": answer}


@app.get("/api/recovery")
def recovery():
    """Return a rest-vs-train recommendation based on health trends."""
    data = _load_data()
    return get_recovery_recommendation(
        data.get("activities", []),
        data.get("health_data", {}),
    )


@app.get("/api/dashboard")
def dashboard():
    """Aggregated stats + most recent health snapshot for the dashboard view."""
    data = _load_data()
    return build_dashboard(
        data.get("activities", []),
        data.get("health_data", {}),
    )
