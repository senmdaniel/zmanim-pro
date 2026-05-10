from datetime import datetime
import ntplib
import requests


# =========================================================
# LOXONE (PRIMARY SOURCE)
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
# INTERNET VALIDATION (NOT LEADING)
# =========================================================
def fetch_internet_date():

    try:
        client = ntplib.NTPClient()
        response = client.request("pool.ntp.org", timeout=2)

        return datetime.utcfromtimestamp(response.tx_time).date()

    except:
        return None


# =========================================================
# MAIN LOGIC (CORRECT PRIORITY)
# =========================================================
def get_current_date(request):

    # 1. LOXONE (ALWAYS PRIMARY)
    loxone_date = get_loxone_date(request)
    if loxone_date:
        return loxone_date

    # 2. INTERNET (OPTIONAL CHECK / VALIDATION ONLY)
    internet_date = fetch_internet_date()
    if internet_date:
        return internet_date

    # 3. SYSTEM CLOCK (LAST RESORT)
    return datetime.now().date()
