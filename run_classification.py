# run_classification.py

import os
import sys
import json
import redis
import logging
from datetime import datetime, timezone

# Add app and agents folders to path for local modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "app"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "agents"))

from config import *
from GPTClient import GPTClient
from pipeline import classify_reviews
from datastore import get_stores
from logging_utils import configure_logging, ensure_log_dir

# --- Logging setup ---
LOG_PATH = "output/classification.log"
ensure_log_dir(LOG_PATH)
configure_logging(LOG_PATH)

# --- Load stores + client ---
review_store, _ = get_stores()
sentiment_agent = GPTClient()

# --- Classification function ---
def run_classification():
    logging.info("Starting classification pipeline...")

    if DATA_STORE == "redis":
        redis_client = redis.Redis(host=REDIS_HOST, port=6379, db=0)
        raw = redis_client.get(RAW_REVIEW_KEY)
        reviews = json.loads(raw) if raw else []
        if not reviews:
            logging.warning("No raw reviews found in Redis.")
    else:
        reviews = review_store.load_reviews()
        if not reviews:
            logging.warning("No reviews found in local fallback.")

    now = datetime.now(timezone.utc)
    classified_reviews = classify_reviews(reviews, sentiment_agent, now)

    review_store.save_reviews(classified_reviews)

    # Only publish escalation trigger in Redis mode
    if DATA_STORE == "redis":
        redis_client.publish("escalation_trigger", "run")
        logging.info("Published escalation trigger to Redis.")

    logging.info("Classification complete. Results saved to data store.")

# --- Listener setup ---
if DATA_STORE == "redis":
    logging.info("Listening for Redis trigger on channel: classification_trigger")
    redis_client = redis.Redis(host=os.getenv("REDIS_HOST", "localhost"), port=6379, db=0)
    pubsub = redis_client.pubsub()
    pubsub.subscribe("classification_trigger")

    for message in pubsub.listen():
        if message["type"] == "message":
            logging.info("Trigger received — running classification pipeline.")
            run_classification()
else:
    logging.info("Running classification immediately (local mode).")
    run_classification()