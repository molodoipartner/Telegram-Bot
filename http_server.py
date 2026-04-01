from flask import Flask, send_file, request, abort, jsonify
import os
import json

app = Flask(__name__)

API_KEY = "SECRET123"

DATA_PATH = os.path.join("data", "users.json")

@app.route("/users", methods=["GET"])
def get_users():
    key = request.headers.get("X-API-KEY")
    if key != API_KEY:
        abort(403)

    return send_file(DATA_PATH)


# 🔥 НОВОЕ: приём данных
@app.route("/users", methods=["POST"])
def upload_users():
    key = request.headers.get("X-API-KEY")
    if key != API_KEY:
        abort(403)

    try:
        data = request.json  # получаем JSON

        # 💾 сохраняем
        with open(DATA_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

        return jsonify({"status": "success"})

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


def run_http():
    app.run(host="0.0.0.0", port=8000)