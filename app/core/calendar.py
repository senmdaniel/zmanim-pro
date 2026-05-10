from app.data.events import EVENTS


def get_event(h_month: int, h_day: int):
    return EVENTS.get((h_month, h_day))


def is_event(h_month: int, h_day: int) -> bool:
    return (h_month, h_day) in EVENTS
