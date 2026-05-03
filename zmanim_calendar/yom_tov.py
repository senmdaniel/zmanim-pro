from convertdate import hebrew

def get_yom_tov_day(date):
    h = hebrew.from_gregorian(date.year, date.month, date.day)
    month = h[1]
    day = h[2]

    # -------------------------
    # PESACH
    # -------------------------
    if month == 1:
        if day == 15:
            return "pesach_1"
        if day == 16:
            return "pesach_2"
        if day in [17, 18, 19, 20]:
            return "chol_hamoed_pesach"
        if day == 21:
            return "shevi_i_shel_pesach"
        if day == 22:
            return "acharon_shel_pesach"

    # -------------------------
    # SHAVUOT
    # -------------------------
    if month == 3:
        if day == 6:
            return "shavuot_1"
        if day == 7:
            return "shavuot_2"

    # -------------------------
    # ROSH HASHANA / YK / SUKKOT
    # -------------------------
    if month == 7:
        if day == 1:
            return "rosh_hashana_1"
        if day == 2:
            return "rosh_hashana_2"
        if day == 10:
            return "yom_kippur"

        if day == 15:
            return "sukkot_1"
        if day == 16:
            return "sukkot_2"
        if day in [17, 18, 19, 20]:
            return "chol_hamoed_sukkot"
        if day == 21:
            return "hoshana_rabba"
        if day == 22:
            return "shemini_atzeret"
        if day == 23:
            return "simchat_torah"

    return None


def is_yom_tov(date):
    return get_yom_tov_day(date) is not None


def is_erev_yom_tov(date):
    """Erev Yom Tov = dag vóór een YT"""
    from datetime import timedelta
    return is_yom_tov(date + timedelta(days=1))
