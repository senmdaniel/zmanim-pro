from datetime import timedelta
from astral import LocationInfo
from astral.sun import sun
import pytz


# =========================================================
# HELPERS
# =========================================================

def fmt(dt):
    """
    Format datetime -> HH:MM
    """
    return dt.strftime("%H:%M")


def sec_from_midnight(dt):
    """
    Seconds since midnight
    """

    return (
        dt.hour * 3600 +
        dt.minute * 60 +
        dt.second
    )


def before(dt, minutes):
    return dt - timedelta(minutes=minutes)


def after(dt, minutes):
    return dt + timedelta(minutes=minutes)


def zman_object(dt):
    """
    Standard zman object
    """

    return {
        "time": fmt(dt),
        "sec": sec_from_midnight(dt)
    }


# =========================================================
# MAIN ENGINE
# =========================================================

def calculate_zmanim(config, date_obj):

    # =====================================================
    # CONFIG
    # =====================================================

    timezone_name = config.get(
        "timezone",
        "UTC"
    )

    tz = pytz.timezone(timezone_name)

    location = LocationInfo(
        name=config.get("city", "unknown"),
        region="",
        timezone=timezone_name,
        latitude=float(config.get("latitude", 0)),
        longitude=float(config.get("longitude", 0))
    )

    # =====================================================
    # SUN DATA
    # =====================================================

    s = sun(
        location.observer,
        date=date_obj,
        tzinfo=tz
    )

    sunrise = s["sunrise"]
    sunset = s["sunset"]

    # =====================================================
    # HALACHIC CORE
    # =====================================================

    day_length = sunset - sunrise

    shaah_zmanit = (
        day_length / 12
    )

    # =====================================================
    # MAIN ZMANIM
    # =====================================================

    chatzos = sunrise + (
        day_length / 2
    )

    plag_hamincha = sunset - (
        1.25 * shaah_zmanit
    )

    # =====================================================
    # SOF ZMAN KRIAS SHEMA
    # =====================================================

    sof_shema_gra = sunrise + (
        3 * shaah_zmanit
    )

    sof_shema_ma = sunrise + (
        2.4 * shaah_zmanit
    )

    # =====================================================
    # SOF ZMAN TFILA
    # =====================================================

    sof_tefila_gra = sunrise + (
        4 * shaah_zmanit
    )

    sof_tefila_ma = sunrise + (
        3.2 * shaah_zmanit
    )

    # =====================================================
    # SHABBAT OPTIONS
    # =====================================================

    candle_options = [
        18,
        20,
        30,
        40
    ]

    tzeis_options = [
        42,
        50,
        72,
        90
    ]

    # =====================================================
    # CANDLE LIGHTING OPTIONS
    # =====================================================

    candle_list = []

    for m in candle_options:

        t = before(sunset, m)

        candle_list.append({
            "id": f"c{m}",
            "minutes": m,
            "label": f"{m} min before shkia",
            "time": fmt(t),
            "sec": sec_from_midnight(t)
        })

    # =====================================================
    # TZEIS OPTIONS
    # =====================================================

    tzeis_list = []

    for m in tzeis_options:

        t = after(sunset, m)

        tzeis_list.append({
            "id": f"t{m}",
            "minutes": m,
            "label": f"{m} min after shkia",
            "time": fmt(t),
            "sec": sec_from_midnight(t)
        })

    # =====================================================
    # FINAL OUTPUT
    # =====================================================

    return {

        # =================================================
        # CORE ZMANIM
        # =================================================

        "zmanim": {

            "shkia": zman_object(
                sunset
            ),

            "chatzos": zman_object(
                chatzos
            ),

            "plag_hamincha": zman_object(
                plag_hamincha
            ),

            "sof_zman_krias_shema": {

                "gra": zman_object(
                    sof_shema_gra
                ),

                "magen_avraham": zman_object(
                    sof_shema_ma
                )
            },

            "sof_zman_tefila": {

                "gra": zman_object(
                    sof_tefila_gra
                ),

                "magen_avraham": zman_object(
                    sof_tefila_ma
                )
            }
        },

        # =================================================
        # SHABBAT OPTIONS
        # =================================================

        "shabbat_options": {

            "candle_lighting": candle_list,

            "tzeis": tzeis_list
        }
    }
