from datetime import timedelta
from astral import LocationInfo
from astral.sun import sun
import pytz


# =========================================================
# HELPERS
# =========================================================

UTC = pytz.UTC


def fmt(dt):
    return dt.strftime("%H:%M")


def ts(dt):
    return int(dt.astimezone(UTC).timestamp())


def before(dt, minutes):
    return dt - timedelta(minutes=minutes)


def after(dt, minutes):
    return dt + timedelta(minutes=minutes)


def zman_object(dt):
    """
    Minimal clean output for automation
    """

    return {
        "time": fmt(dt),
        "ts": ts(dt)
    }


# =========================================================
# MAIN ENGINE
# =========================================================

def calculate_zmanim(config, date_obj):

    # =====================================================
    # CONFIG
    # =====================================================

    timezone_name = config.get("timezone", "UTC")

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
    # GRA DAY
    # =====================================================

    day_length = sunset - sunrise
    shaah_zmanit = day_length / 12

    # =====================================================
    # MAGEN AVRAHAM DAY
    # =====================================================

    alos_ma = before(sunrise, 72)
    tzeis_ma = after(sunset, 72)

    ma_day_length = tzeis_ma - alos_ma
    shaah_zmanit_ma = ma_day_length / 12

    # =====================================================
    # MAIN ZMANIM
    # =====================================================

    chatzos = sunrise + (day_length / 2)

    # =====================================================
    # PLAG HAMINCHA
    # =====================================================

    plag_gra = sunset - (1.25 * shaah_zmanit)
    plag_ma = tzeis_ma - (1.25 * shaah_zmanit_ma)

    # =====================================================
    # SOF ZMAN KRIAS SHEMA
    # =====================================================

    shema_gra = sunrise + (3 * shaah_zmanit)
    shema_ma = alos_ma + (3 * shaah_zmanit_ma)

    # =====================================================
    # SOF ZMAN TFILA
    # =====================================================

    tefila_gra = sunrise + (4 * shaah_zmanit)
    tefila_ma = alos_ma + (4 * shaah_zmanit_ma)

    # =====================================================
    # SHABBAT OPTIONS
    # =====================================================

    candle_options = [18, 20, 30, 40]
    tzeis_options = [42, 50, 72, 90]

    candle_list = [
        {
            "id": f"c{m}",
            "minutes": m,
            "label": f"{m} min before shkia",
            "time": fmt(before(sunset, m)),
            "ts": ts(before(sunset, m))
        }
        for m in candle_options
    ]

    tzeis_list = [
        {
            "id": f"t{m}",
            "minutes": m,
            "label": f"{m} min after shkia",
            "ts": ts(after(sunset, m)),
            "time": fmt(after(sunset, m))
        }
        for m in tzeis_options
    ]

    # =====================================================
    # OUTPUT
    # =====================================================

    return {

        "zmanim": {

            "shkia": zman_object(sunset),

            "chatzos": zman_object(chatzos),

            "plag_hamincha": {
                "pla_gra": zman_object(plag_gra),
                "plag_magen_avraham": zman_object(plag_ma)
            },

            "sof_zman_krias_shema": {
                "gra": zman_object(shema_gra),
                "magen_avraham": zman_object(shema_ma)
            },

            "sof_zman_tefila": {
                "gra": zman_object(tefila_gra),
                "magen_avraham": zman_object(tefila_ma)
            }
        },

        "shabbat_options": {
            "candle_lighting": candle_list,
            "tzeis": tzeis_list
        }
    }
