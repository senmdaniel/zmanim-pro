from flask import Flask, jsonify, request
import json
import os
from datetime import datetime
from app.zmanim import is_yom_tov, calculate_times

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def get_city():
    path = os.path.join(BASE_DIR, "config", "settings.json")
    with open(path, "r") as f:
        return json.load(f)["city"]


@app.route("/status")
def status():
    date_str = request.args.get("datum")

    if not date_str:
        return jsonify({"error": "missing datum (YYYY/MM/DD)"}), 400

    # normalize format
    date_str = date_str.replace("/", "-")
    date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()

    city = get_city()

    data_path = os.path.join(BASE_DIR, "data", f"{city}.json")

    yom_tov = is_yom_tov(data_path, date_obj)
    times = calculate_times(date_obj)

    return jsonify({
        "date": str(date_obj),
        "city": city,
        "is_yom_tov": yom_tov,
        "plag_hamincha": times["plag_hamincha"],
        "tzeis": times["tzeis"]
    })
