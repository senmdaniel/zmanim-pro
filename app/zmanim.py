def calculate_zmanim(config, d):
    """
    Production-safe zmanim engine
    """

    # ----------------------------
    # CONFIG SAFETY CHECK
    # ----------------------------
    required_keys = ["timezone", "city", "latitude", "longitude"]

    for key in required_keys:
        if key not in config:
            raise ValueError(f"Missing config key: {key}")

    tz = pytz.timezone(config["timezone"])

    location = LocationInfo(
        name=config["city"],
        region="",
        timezone=config["timezone"],
        latitude=float(config["latitude"]),
        longitude=float(config["longitude"])
    )

    s = sun(location.observer, date=d, tzinfo=tz)

    sunrise = s["sunrise"]
    sunset = s["sunset"]

    # ----------------------------
    # SHAOT ZMANIOT (Gra)
    # ----------------------------
    day_length = sunset - sunrise
    shaah_zmanit = day_length / 12

    chatzos = sunrise + (day_length / 2)
    plag = sunset - (1.25 * shaah_zmanit)

    # ----------------------------
    # SAFE CONFIG VALUES
    # ----------------------------
    alos_cfg = config.get("alos", {"method": "fixed", "minutes": 72})
    tzeis_cfg = config.get("tzeis", {"method": "fixed", "minutes": 40})
    candle_min = config.get("candle_lighting", 18)

    # Alos
    if alos_cfg["method"] == "fixed":
        alos = sunrise - timedelta(minutes=alos_cfg["minutes"])
    else:
        raise ValueError("Unsupported alos method")

    # Tzeis
    if tzeis_cfg["method"] == "fixed":
        tzeis = sunset + timedelta(minutes=tzeis_cfg["minutes"])
    else:
        raise ValueError("Unsupported tzeis method")

    candle_lighting = sunset - timedelta(minutes=candle_min)

    # ----------------------------
    # RESPONSE
    # ----------------------------
    zmanim = {
        "alos": format_time(alos),
        "chatzos": format_time(chatzos),
        "plag_hamincha": format_time(plag),
        "shkia": format_time(sunset),
        "tzeis": format_time(tzeis),
        "candle_lighting": format_time(candle_lighting),

        "alos_ts": to_timestamp(alos),
        "plag_ts": to_timestamp(plag),
        "shkia_ts": to_timestamp(sunset),
        "tzeis_ts": to_timestamp(tzeis)
    }

    # ----------------------------
    # OVERRIDES (SAFE)
    # ----------------------------
    try:
        overrides = load_overrides(config["city"])
        zmanim = apply_overrides(zmanim, overrides, d)
    except Exception as e:
        # never crash API on overrides
        print("Override error:", e)

    return zmanim
