# app/yomim_tovim.py


# ----------------------------
# EVENTS DATABASE
# ----------------------------
EVENTS = {
    # ---------------- PESSACH ----------------
    (1, 14): "12_erev_pesach",
    (1, 15): "13_pesach_1",
    (1, 16): "14_pesach_2",
    (1, 20): "15_erev_pesach_6",
    (1, 21): "16_pesach_7",
    (1, 22): "17_pesach_8",

    # ---------------- SHAVUOT ----------------
    (3, 5): "18_erev_shavuot",
    (3, 6): "19_shavuot_1",
    (3, 7): "20_shavuot_2",

    # ---------------- ROSH HASHANAH ----------------
    (6, 29): "1_erev_rosh_hashanah",
    (7, 1): "2_rosh_hashanah_1",
    (7, 2): "3_rosh_hashanah_2",

    # ---------------- YOM KIPPUR ----------------
    (7, 9): "4_erev_yom_kippur",
    (7, 10): "5_yom_kippur",

    # ---------------- SUKKOT ----------------
    (7, 14): "6_erev_sukkot",
    (7, 15): "7_sukkot_1",
    (7, 16): "8_sukkot_2",
    (7, 21): "9_erev_shemini_atzeret",
    (7, 22): "10_shemini_atzeret",
    (7, 23): "11_simchat_torah",
}


# ----------------------------
# MAIN LOOKUP FUNCTION
# ----------------------------
def get_event(h_month: int, h_day: int):
    """
    Returns Loxone trigger ID for given Hebrew date.
    Example: "12_erev_pesach"
    """

    return EVENTS.get((h_month, h_day))


# ----------------------------
# OPTIONAL HELPERS (future-proof)
# ----------------------------
def is_event(h_month: int, h_day: int) -> bool:
    """Check if date has an event"""
    return (h_month, h_day) in EVENTS


def get_all_events():
    """Return full event map (useful for debugging/admin UI)"""
    return EVENTS
