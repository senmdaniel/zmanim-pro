from hdate import HDate

def get_calendar_info(date):
    h = HDate(date)

    hebrew_day = h.hd.day
    hebrew_month = h.hd.month

    yom_tov = None

    # -----------------------
    # CHAGIM (DIASPORA)
    # -----------------------

    # Rosh Hashanah
    if hebrew_month == 1 and hebrew_day in (1, 2):
        yom_tov = "Rosh Hashanah"

    # Yom Kippur
    elif hebrew_month == 1 and hebrew_day == 10:
        yom_tov = "Yom Kippur"

    # Sukkot
    elif hebrew_month == 1 and 15 <= hebrew_day <= 21:
        yom_tov = "Sukkot"

    # Shemini Atzeret / Simchat Torah
    elif hebrew_month == 1 and hebrew_day in (22, 23):
        yom_tov = "Shemini Atzeret / Simchat Torah"

    # Pesach
    elif hebrew_month == 8 and 15 <= hebrew_day <= 21:
        yom_tov = "Pesach"

    # Shavuot
    elif hebrew_month == 3 and hebrew_day in (6, 7):
        yom_tov = "Shavuot"

    # -----------------------
    # FLAGS
    # -----------------------

    is_shabbat = date.weekday() == 5
    is_erev_yom_tov = h.is_erev_yom_tov()

    return {
        "hebrew_date": str(h.hd),
        "is_yom_tov": yom_tov is not None,
        "yom_tov": yom_tov,
        "is_erev_yom_tov": is_erev_yom_tov,
        "is_shabbat": is_shabbat
    }
