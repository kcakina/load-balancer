from flask import Flask, request, jsonify
from app.db import DB
from app.service import LimiterInput, run_rate_check

app = Flask(__name__)
db = DB()


@app.route("/")
def health():
    return "OK", 200


@app.route("/check", methods=["POST"])
def check():
    body = request.get_json()
    if not body:
        return jsonify({"error": "missing JSON body"}), 400

    key = body.get("key")
    limit = body.get("limit")
    window_seconds = body.get("window_seconds")

    limiter_input = LimiterInput(key=key, limit=limit, window_seconds=window_seconds)
    result = run_rate_check(db, limiter_input)

    if result is None:
        return jsonify({"error": "invalid input"}), 400

    return jsonify({
        "allowed": result.allowed,
        "remaining": result.remaining,
        "reset_in_seconds": result.reset_in_seconds
    }), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)