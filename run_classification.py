# run_classification.py
import os
import sys
import json
import html
import logging
import ftfy
import redis
from datetime import datetime, timezone

# Add app and agents directories to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "app"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "agents"))

from GPTClient import GPTClient
from datastore import get_stores
from logging_utils import configure_logging, ensure_log_dir
from sentiment_agent import SentimentAgent
from explainability_agent import ExplainabilityAgent
from config import *

# Configure logging
LOG_PATH = "output/classification.log"
ensure_log_dir(LOG_PATH)
configure_logging(LOG_PATH)

# Initialize GPT clients + agents
sentiment_agent = SentimentAgent(GPTClient())
explain_agent = ExplainabilityAgent(GPTClient())

# Get data store and load reviews
review_store, _ = get_stores()
reviews = review_store.load_reviews()

# Fallback if empty
if not reviews:
    try:
        with open("data/sample_reviews.json", "r", encoding="utf-8") as f:
            reviews = json.load(f)
        logging.info("No reviews found in store — loaded fallback sample_reviews.json")
    except FileNotFoundError:
        logging.error("No reviews found and no sample_reviews.json file available.")
        sys.exit(1)

# Classify and annotate reviews
classified_reviews = []
for review in reviews:
    raw_text = review.get("text", "")
    clean_text = ftfy.fix_text(html.unescape(raw_text))

    sentiment = sentiment_agent.classify(clean_text)
    explanation = explain_agent.explain(clean_text, sentiment)

    review["text"] = clean_text
    review["sentiment"] = sentiment
    review["explanation"] = explanation
    review.setdefault("created_at", datetime.now(timezone.utc).isoformat())
    review["classified_at"] = datetime.now(timezone.utc).isoformat()

    classified_reviews.append(review)
    logging.info(f"[{review['product_id']}] Classified review: {clean_text} -> {sentiment}")

# Save to store
os.makedirs("output", exist_ok=True)
review_store.save_reviews(classified_reviews)

# If using Redis, publish to trigger the next step
if DATA_STORE == "redis":
    redis_host = os.getenv("REDIS_HOST", "localhost")
    redis_client = redis.Redis(host=redis_host, port=6379, db=0)
    redis_client.publish("escalation_trigger", "run")
    logging.info("Published escalation trigger to Redis.")

logging.info("Classification complete. Results saved to data store.")
