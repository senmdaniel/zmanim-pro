from datetime import datetime
import json
import os

# ⚠️ simpele astronomische placeholder (vervang door echte library indien gewenst)
# Dit maakt je systeem NIET meer afhankelijk van JSON nulls

def calculate_zmanim(city, d):
    # dummy berekening structuur (vervang later met real zmanim lib)
    return {
        "alos": "05:12",
        "chatzos": "12:44",
        "plag_hamincha": "18:10",
        "shkia": "20:58",
        "tzeis": "21:35"
    }


def get_holiday_info(city, d):
    """
    Check simpel op vaste Joodse feestdagen (placeholder logica)
    Vervang later door echte Jewish calendar lib indien gewenst
    """

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
