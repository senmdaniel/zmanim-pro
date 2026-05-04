import json
from datetime import datetime

def get_active_event(path):
    try:
        with open(path, "r") as f:
            data = json.load(f)

        now = datetime.now()

        for event in data["holidays"]:
            start = datetime.fromisoformat(event["start"])
            end = datetime.fromisoformat(event["end"])

            if start <= now <= end:
                return event["name"]

        return None

    except Exception as e:
        print("Zmanim error:", e)
        return None
