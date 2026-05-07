from flask import jsonify, request
from app import app

@app.route("/health")
def health():
    return jsonify({"status": "ok"})

@app.route("/api")
def api():
    return jsonify({"status": "ok"})
