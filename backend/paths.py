import os

# Resolve paths relative to this file so they work regardless of CWD.
BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BACKEND_DIR, "data")
ACTIVITIES_PATH = os.path.join(DATA_DIR, "activities.json")
