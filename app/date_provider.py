from datetime import datetime, timedelta
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

        response = client.request(
            "pool.ntp.org",
            version=3,
            timeout=2
        )

        return datetime.utcfromtimestamp(
            response.tx_time
        ).date()

    except:

        return None


# =========================================================
# SAVE CACHE
# =========================================================
def save_cached_date(date_obj):

    os.makedirs(
        os.path.dirname(DATE_FILE),
        exist_ok=True
    )

    with open(DATE_FILE, "w") as f:

        json.dump({

            "date": date_obj.isoformat(),

            "saved_at": datetime.utcnow().isoformat()

        }, f)


# =========================================================
# LOAD CACHE
# =========================================================
def load_cached_date():

    if not os.path.exists(DATE_FILE):
        return None

    try:

        with open(DATE_FILE, "r") as f:
            data = json.load(f)

        cached_date = datetime.strptime(
            data["date"],
            "%Y-%m-%d"
        ).date()

        saved_at = datetime.fromisoformat(
            data["saved_at"]
        )

        # hoeveel dagen oud?
        delta_days = (
            datetime.utcnow().date() -
            saved_at.date()
        ).days

        # auto-forward indien nodig
        corrected_date = cached_date + timedelta(
            days=delta_days
        )

        return corrected_date

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

            return datetime(
                int(y),
                int(m),
                int(d)
            ).date()

        except:

            pass

    return None


# =========================================================
# MAIN ENGINE
# =========================================================
def get_current_date(request):

    # -----------------------------------------------------
    # 1. INTERNET
    # -----------------------------------------------------

    internet_date = fetch_internet_date()

    if internet_date:

        save_cached_date(internet_date)

        return internet_date

    # -----------------------------------------------------
    # 2. CACHE (AUTO ADVANCING)
    # -----------------------------------------------------

    cached = load_cached_date()

    if cached:
        return cached

    # -----------------------------------------------------
    # 3. LOXONE
    # -----------------------------------------------------

    loxone_date = get_loxone_date(request)

    if loxone_date:
        return loxone_date

    # -----------------------------------------------------
    # 4. SYSTEM CLOCK
    # -----------------------------------------------------

    return datetime.utcnow().date()
