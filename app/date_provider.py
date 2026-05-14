from datetime import datetime
from zoneinfo import ZoneInfo
import ntplib
import requests
import json
import os

CACHE_FILE = os.path.join("config", "date_now.json")

# 👉 fallback URL (bijvoorbeeld jouw eigen server)
DATE_URL = "https://your-domain.com/api/date"

# 👉 timezone
TIMEZONE = ZoneInfo("Europe/Brussels")


# =========================================================
# 1. NTP (best effort)
# =========================================================
def fetch_ntp_date():
    try:
        client = ntplib.NTPClient()
        response = client.request("pool.ntp.org", version=3, timeout=2)

        return datetime.fromtimestamp(
            response.tx_time,
            TIMEZONE
        ).date()

    except:
        return None


# =========================================================
# 2. HTTP URL fallback
# =========================================================
def fetch_http_date():
    try:
        r = requests.get(DATE_URL, timeout=2)

        if r.status_code != 200:
            return None

        data = r.json()

        # verwacht: {"date": "2026-05-10"}
        return datetime.strptime(
            data["date"],
            "%Y-%m-%d"
        ).date()

    except:
        return None


# =========================================================
# 3. CACHE
# =========================================================
def save_cache(date_obj):
    os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)

    with open(CACHE_FILE, "w") as f:
        json.dump({
            "date": date_obj.isoformat(),
            "saved_at": datetime.now(TIMEZONE).isoformat()
        }, f)


def load_cache():
    if not os.path.exists(CACHE_FILE):
        return None

    try:
        with open(CACHE_FILE, "r") as f:
            data = json.load(f)

        return datetime.strptime(
            data["date"],
            "%Y-%m-%d"
        ).date()

    except:
        return None


# =========================================================
# 4. MAIN LOGIC
# =========================================================
def get_current_date(request=None):

    # -------------------------------------------------
    # 1. NTP (primary)
    # -------------------------------------------------
    ntp_date = fetch_ntp_date()

    if ntp_date:
        save_cache(ntp_date)
        return ntp_date

    # -------------------------------------------------
    # 2. HTTP fallback URL
    # -------------------------------------------------
    http_date = fetch_http_date()

    if http_date:
        save_cache(http_date)
        return http_date

    # -------------------------------------------------
    # 3. CACHE fallback
    # -------------------------------------------------
    cached = load_cache()

    if cached:
        return cached

    # -------------------------------------------------
    # 4. SYSTEM CLOCK (last resort)
    # -------------------------------------------------
    return datetime.now(TIMEZONE).date()
