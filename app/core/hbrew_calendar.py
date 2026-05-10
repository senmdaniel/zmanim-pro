from convertdate import hebrew


def get_hebrew_date(gregorian_date):
    h_year, h_month, h_day = hebrew.from_gregorian(
        gregorian_date.year,
        gregorian_date.month,
        gregorian_date.day
    )

    return {
        "hebrew_year": h_year,
        "hebrew_month": h_month,
        "hebrew_day": h_day
    }
