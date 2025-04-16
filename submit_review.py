from flask import Flask, request, jsonify
import redis
import os
import json
from datetime import datetime, timezone

app = Flask(__name__)

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
RAW_REVIEW_KEY = os.getenv("RAW_REVIEW_KEY", "raw_reviews")
TRIGGER_CLASSIFICATION = os.getenv("TRIGGER_CLASSIFICATION", "true").lower() == "true"

redis_client = redis.Redis(host=REDIS_HOST, port=6379, db=0)

@app.route("/submit_review", methods=["POST"])
def submit_review():
    data = request.get_json()
    required_fields = ["product_id", "text"]
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields"}), 400

    now = datetime.now(timezone.utc).isoformat()
    review = {
        "product_id": data["product_id"],
        "text": data["text"],
        "created_at": data.get("created_at", now), # Use provided timestamp or current time
        "classified_at": None,
        "sentiment": None,
        "explanation": None
    }

    # Load existing reviews, append new one
    raw_data = redis_client.get(RAW_REVIEW_KEY)
    existing_reviews = json.loads(raw_data) if raw_data else []
    existing_reviews.append(review)
    redis_client.set(RAW_REVIEW_KEY, json.dumps(existing_reviews, indent=2))

    if TRIGGER_CLASSIFICATION:
        redis_client.publish("classification_trigger", "run")

    return jsonify({"status": "review submitted"}), 200

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)