from astral import LocationInfo
from astral.sun import sun
from datetime import datetime, timedelta
import json

def load_config():
    with open("config.json", "r") as f:
        return json.load(f)

def get_zmanim():
    cfg = load_config()

    location = LocationInfo(
        name="home",
        region="",
        timezone=cfg["timezone"],
        latitude=cfg["latitude"],
        longitude=cfg["longitude"]
    )

    today = datetime.now().date()
    s = sun(location.observer, date=today, tzinfo=location.timezone)

    shkia = s["sunset"]

    return {
        "sunrise": str(s["sunrise"].time()),
        "shkia": str(shkia.time()),
        "candle_lighting": str((shkia - timedelta(minutes=cfg["candle_lighting_offset"])).time()),
        "tzeit": str((shkia + timedelta(minutes=cfg["tzeit_offset"])).time())
    }
