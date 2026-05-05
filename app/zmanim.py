from pyluach import dates


def get_hebrew_date(d):
    """
    Offline conversie van Gregorian → Hebreeuwse datum
    """

    g = dates.GregorianDate(d.year, d.month, d.day)
    h = g.to_heb()

    return {
        "hebrew_date": str(h),
        "hebrew_day": h.day,
        "hebrew_month": h.month,
        "hebrew_year": h.year
    }
