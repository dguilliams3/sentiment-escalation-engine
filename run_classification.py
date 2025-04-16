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
gpt_client = GPTClient()

# --- Classification function ---
def run_classification():
    logging.info("Starting classification pipeline...")
    reviews = review_store.load_reviews()

    now = datetime.now(timezone.utc)
    classified_reviews = classify_reviews(reviews, gpt_client, now)

    review_store.save_reviews(classified_reviews)

    # Only publish escalation trigger in Redis mode
    if DATA_STORE == "redis":
        redis_host = os.getenv("REDIS_HOST", "localhost")
        redis_client = redis.Redis(host=redis_host, port=6379, db=0)
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