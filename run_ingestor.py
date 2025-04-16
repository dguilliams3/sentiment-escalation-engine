# run_ingestor.py
import os
import json
import redis
import logging
from datetime import datetime, timezone
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "app"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "agents"))
from config import *

logging.basicConfig(level=logging.INFO)

# Sample hardcoded review set (we'll improve this later)
SAMPLE_REVIEWS = [
    {"product_id": "widget-01", "text": "Completely useless, doesn't even light up."},
    {"product_id": "widget-02", "text": "Exceeded expectations, great product!"},
    {"product_id": "widget-03", "text": "Burned my hand. Unsafe!"},
    {"product_id": "widget-04", "text": "Cosmetic defects, but functions fine."}
]

def enrich_reviews(reviews):
    now = datetime.now(timezone.utc).isoformat()
    return [
        {
            **r,
            "created_at": now,
            "classified_at": None,
            "sentiment": None,
            "explanation": None
        }
        for r in reviews
    ]

def main():
    enriched = enrich_reviews(SAMPLE_REVIEWS)

    redis_host = os.getenv("REDIS_HOST", "localhost")
    r = redis.Redis(host=redis_host, port=6379, db=0)

    # Write enriched reviews to raw_reviews key
    r.set(RAW_REVIEW_KEY, json.dumps(enriched, indent=2))
    logging.info(f"{len(enriched)} reviews loaded into Redis under key '{RAW_REVIEW_KEY}'")

    # Optionally trigger classification pipeline
    if os.getenv("TRIGGER_CLASSIFICATION", "true").lower() == "true":
        r.publish("classification_trigger", "run")
        logging.info("Published classification trigger to Redis.")

if __name__ == "__main__":
    main()
