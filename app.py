from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

HOSPITABLE_API = "https://api.hospitable.com/v1/reservations"
HOSPITABLE_TOKEN = os.getenv("HOSPITABLE_TOKEN")  # Securely inject this on Render

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    message = data.get("message")
    reservation_id = data.get("reservation_id")

    if not message or not reservation_id:
        return jsonify({"error": "Missing message or reservation_id"}), 400

    hospitable_url = f"{HOSPITABLE_API}/{reservation_id}/messages"
    headers = {
        "Authorization": f"Bearer {HOSPITABLE_TOKEN}",
        "Content-Type": "application/json"
    }

    payload = {
        "body": message,
        "direction": "guest"
    }

    response = requests.post(hospitable_url, json=payload, headers=headers)

    if response.status_code >= 200 and response.status_code < 300:
        return jsonify({"status": "success"}), 200
    else:
        return jsonify({"error": response.text}), response.status_code