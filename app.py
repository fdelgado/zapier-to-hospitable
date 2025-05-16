from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

HOSPITABLE_API_BASE = "https://public.api.hospitable.com/v2"
HOSPITABLE_TOKEN = os.getenv("HOSPITABLE_TOKEN")

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json

    conversation_id = data.get("conversation_id")
    message = data.get("message")
    image_url = data.get("image_url")  # <-- NEW
    msg_type = data.get("type", "reservation")

    if not message or not conversation_id:
        return jsonify({"error": "Missing 'message' or 'conversation_id'"}), 400

    if msg_type not in ["reservation", "inquiry"]:
        return jsonify({"error": "Invalid 'type'. Must be 'reservation' or 'inquiry'"}), 400

    # Create base payload
    payload = {"body": message}
    if image_url:
        payload["images"] = [image_url]

    if msg_type == "reservation":
        endpoint = f"/reservations/{conversation_id}/messages"
        payload["direction"] = "guest"
    else:  # inquiry
        endpoint = f"/inquiries/{conversation_id}/messages"

    url = f"{HOSPITABLE_API_BASE}{endpoint}"

    headers = {
        "Authorization": f"Bearer {HOSPITABLE_TOKEN}",
        "Content-Type": "application/json"
    }

    response = requests.post(url, headers=headers, json=payload)

    if 200 <= response.status_code < 300:
        return jsonify({"status": "Message sent successfully"}), 200
    else:
        return jsonify({
            "error": response.text,
            "status_code": response.status_code
        }), response.status_code