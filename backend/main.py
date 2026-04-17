import os
import json
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sync import sync
from formatter import format_activities
from coach import ask_coach

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/status")
def get_status():
    activities_path = "backend/data/activities.json"

    if not os.path.exists(activities_path):
        return {"has_data": False, "activity_count": 0, "synced_at": None}

    with open(activities_path) as f:
        data = json.load(f)

    return {
        "has_data": True,
        "activity_count": len(data.get("activities", [])),
        "synced_at": data.get("synced_at"),
    }


@app.post("/api/sync")
def sync_strava():
    count, synced_at = sync()
    return {"status": "ok", "count": count, "synced_at": synced_at}


@app.post("/api/chat")
def chat(request: dict):
    question = request.get("question", "")
    history = request.get("history", [])

    activities_path = "backend/data/activities.json"
    with open(activities_path) as f:
        data = json.load(f)

    activities = data.get("activities", [])
    activities_summary = format_activities(activities)

    answer = ask_coach(question, history, activities_summary)
    return {"answer": answer}
