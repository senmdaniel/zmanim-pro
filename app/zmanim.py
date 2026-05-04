import json
from datetime import datetime

def load_calendar(path):
    with open(path, "r") as f:
        return json.load(f)

def get_active_event(path):
    data = load_calendar(path)
    now = datetime.now()

    for event in data["holidays"]:
        start = datetime.fromisoformat(event["start"])
        end = datetime.fromisoformat(event["end"])

        if start <= now <= end:
            return event["name"]

    return None
