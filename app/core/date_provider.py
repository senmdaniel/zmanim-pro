from datetime import datetime


def get_current_date(request=None):
    # later: timezone / query override
    return datetime.now()
