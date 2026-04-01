from flask import Flask, send_file, request, abort

app = Flask(__name__)

API_KEY = "SECRET123"  # 🔑 придумай свой сложный ключ

@app.route("/users")
def get_users():
    key = request.args.get("api_key")

    if key != API_KEY:
        abort(403)  # 🚫 доступ запрещён

    return send_file("data/users.json")

def run_http():
    app.run(host="0.0.0.0", port=8000)