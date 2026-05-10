from datetime import datetime
import ntplib
import json
import os


DATE_FILE = os.path.join("config", "date_now.json")


# =========================================================
# INTERNET (NTP)
# =========================================================
def fetch_internet_date():
    try:
        client = ntplib.NTPClient()
        response = client.request("pool.ntp.org", version=3)
        return datetime.fromtimestamp(response.tx_time).date()
    except:
        return None


# =========================================================
# CACHE (BELANGRIJKSTE STUK)
# =========================================================
def save_cached_date(date_obj):
    os.makedirs(os.path.dirname(DATE_FILE), exist_ok=True)

    with open(DATE_FILE, "w") as f:
        json.dump({
            "date": date_obj.isoformat(),
            "timestamp": datetime.now().isoformat()
        }, f)


def load_cached_date():
    if not os.path.exists(DATE_FILE):
        return None

    try:
        with open(DATE_FILE, "r") as f:
            data = json.load(f)

        return datetime.strptime(data["date"], "%Y-%m-%d").date()
    except:
        return None


# =========================================================
# LOXONE INPUT
# =========================================================
def get_loxone_date(request):
    y = request.values.get("y")
    m = request.values.get("m")
    d = request.values.get("d")

    if y and m and d:
        try:
            return datetime(int(y), int(m), int(d)).date()
        except:
            pass

    return None


# =========================================================
# MAIN LOGIC (FAILSAFE ENGINE)
# =========================================================
def get_current_date(request):

    # 1. probeer internet
    internet_date = fetch_internet_date()

    if internet_date:
        save_cached_date(internet_date)
        return internet_date

    # 2. als geen internet → gebruik cache (BELANGRIJK)
    cached = load_cached_date()
    if cached:
        return cached

    # 3. fallback → Loxone
    loxone_date = get_loxone_date(request)
    if loxone_date:
        return loxone_date

    # 4. laatste fallback → systeem
    return datetime.today().date()
