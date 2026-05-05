from datetime import datetime
from pyluach import dates


def calculate_zmanim(city, d):
    """
    Dummy tijden (later vervangbaar door echte berekening)
    """
    return {
        "alos": "05:12",
        "chatzos": "12:44",
        "plag_hamincha": "18:10",
        "shkia": "20:58",
        "tzeis": "21:35"
    }


def get_holiday_info(city, d):
    month_day = (d.month, d.day)

    holidays = {
        (5, 15): "Lag BaOmer",
        (1, 1): "Rosh Hashanah",
        (9, 10): "Yom Kippur"
    }

    if month_day in holidays:
        return {
            "is_yom_tov": True,
            "name": holidays[month_day]
        }

    return {
        "is_yom_tov": False,
        "name": None
    }


def get_hebrew_date(d):
    g = dates.GregorianDate(d.year, d.month, d.day)
    h = g.to_heb()

    return {
        "hebrew_date": str(h),
        "hebrew_day": h.day,
        "hebrew_month": h.month,
        "hebrew_year": h.year
    }
