from flask import Flask, jsonify
from zmanim import get_active_event

app = Flask(__name__)

@app.route("/status")
def status():
    event = get_active_event("data/antwerp.json")

    return jsonify({
        "active": event is not None,
        "event": event
    })
