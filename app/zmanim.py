import json


def is_yom_tov(path, date_obj):
    with open(path, "r") as f:
        data = json.load(f)

    for event in data.get("events", []):
        if event["type"] == "yom_tov":
            if event["date"] == str(date_obj):
                return True

    return False


def calculate_times(date_obj):
    # voorlopig dummy (later echte astronomische berekening)
    return {
        "plag_hamincha": "18:42",
        "tzeis": "21:31"
    }
