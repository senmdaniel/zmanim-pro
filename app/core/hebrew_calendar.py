from convertdate import hebrew


def get_hebrew_date(gregorian_date):
    """
    Convert Gregorian date → Hebrew date (offline)
    """

    h_year, h_month, h_day = hebrew.from_gregorian(
        gregorian_date.year,
        gregorian_date.month,
        gregorian_date.day
    )

    # debug (optioneel, kan je later verwijderen)
    print("INPUT:", gregorian_date)
    print("HEBREW:", h_year, h_month, h_day)

    return {
        "hebrew_year": h_year,
        "hebrew_month": h_month,
        "hebrew_day": h_day
    }
