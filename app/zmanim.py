def get_active_event(path):
    import json
    from datetime import datetime

    try:
        with open(path, "r") as f:
            data = json.load(f)
    except:
        return None

    today = datetime.now().strftime("%Y-%m-%d")

    return data.get(today)
