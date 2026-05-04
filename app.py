from flask import Flask, jsonify
from zmanim import get_zmanim

app = Flask(__name__)

@app.route("/zmanim")
def zmanim():
    return jsonify(get_zmanim())

@app.route("/")
def home():
    return "Zmanim API running"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
