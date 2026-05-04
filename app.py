from flask import Flask, jsonify, render_template
from zmanim import get_zmanim

app = Flask(__name__)

# ---------------------------
# API endpoint (voor Loxone)
# ---------------------------
@app.route("/zmanim", methods=["GET"])
def api_zmanim():
    return jsonify(get_zmanim())

# ---------------------------
# Web dashboard (Bootstrap UI)
# ---------------------------
@app.route("/")
def dashboard():
    return render_template("index.html")

# ---------------------------
# Health check (handig voor Pi/Loxone debug)
# ---------------------------
@app.route("/health")
def health():
    return jsonify({"status": "ok"})

# ---------------------------
# Start server
# ---------------------------
if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False
    )
