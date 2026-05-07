from flask import Blueprint, jsonify, request
from datetime import datetime, date
import json
import os

from app.zmanim import (
    calculate_zmanim,
    get_holiday_info,
    get_hebrew_date
)

api_bp = Blueprint("api", __name__)

# -----------------------
# PATHS
# -----------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STORED_DATE_PATH = os.path.join(BASE_DIR, "config", "current_date.json")


# -----------------------
# STORAGE
# -----------------------
def save_date(d: date):
    with open(STORED_DATE_PATH, "w") as f:
        json.dump({"date": d.isoformat()}, f)


def load_date():
    if not os.path.exists(STORED_DATE_PATH):
        return None

    try:
        with open(STORED_DATE_PATH, "r") as f:
            data = json.load(f)
            return datetime.strptime(data["date"], "%Y-%m-%d").date()
    except:
        return None


# -----------------------
# CONFIG
# -----------------------
def get_city():
    path = os.path.join(BASE_DIR, "config", "settings.json")
    with open(path, "r") as f:
        return json.load(f)["city"]


def get_config(city):
    path = os.path.join(BASE_DIR, "config", "settings.json")
    with open(path, "r") as f:
        cfg = json.load(f)

    cfg["city"] = city
    return cfg


# -----------------------
# CORE RESPONSE BUILDER
# -----------------------
def build_response(d: date):
    city = get_city()
    config = get_config(city)

    zmanim = calculate_zmanim(config, d)
    holiday = get_holiday_info(d)
    hebrew = get_hebrew_date(d)

    return {
        "status": "ok",
        "city": city,
        "date": d.isoformat(),

        "hebrew_date": hebrew["hebrew_date"],
        "holiday": holiday.get("holiday_name"),
        "is_yom_tov": holiday.get("is_yom_tov"),

        **zmanim
    }


# -----------------------
# 1. MAIN API (LOXONE SAFE)
# -----------------------
@api_bp.route("/api")
def api():
    raw = request.args.get("d") or request.args.get("date")

    # 1) set date if provided
    if raw:
        try:
            if "-" in raw:
                d = datetime.strptime(raw, "%Y-%m-%d").date()
            else:
                d = datetime.strptime(raw, "%Y%m%d").date()

            save_date(d)

        except ValueError:
            return jsonify({
                "status": "error",
                "message": "invalid date format (use YYYYMMDD or YYYY-MM-DD)"
            }), 400

    # 2) fallback stored date
    d = load_date()

    if not d:
        return jsonify({
            "status": "error",
            "message": "no date set"
        }), 400

    return jsonify(build_response(d))


# -----------------------
# 2. SET DATE ONLY (OPTIONAL BUT HANDY FOR LOXONE)
# -----------------------
@api_bp.route("/setdate")
def setdate():
    raw = request.args.get("d") or request.args.get("date")

    if not raw:
        return jsonify({"status": "error", "message": "missing date"}), 400

    try:
        if "-" in raw:
            d = datetime.strptime(raw, "%Y-%m-%d").date()
        else:
            d = datetime.strptime(raw, "%Y%m%d").date()

        save_date(d)

        return jsonify({
            "status": "ok",
            "date": d.isoformat()
        })

    except ValueError:
        return jsonify({"status": "error", "message": "invalid date"}), 400


# -----------------------
# 3. HEALTH CHECK
# -----------------------
@api_bp.route("/health")
def health():
    return jsonify({"status": "ok"})
