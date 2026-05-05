import json
import os

def get_event(path, date):
    if not os.path.exists(path):
        return None

    try:
        with open(path, "r") as f:
            data = json.load(f)
    except:
        return None

    return data.get(date)
