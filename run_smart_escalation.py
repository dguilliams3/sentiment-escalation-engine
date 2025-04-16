# run_smart_escalation.py
import os
import sys
import json
import logging
import time
from datetime import datetime, timezone

# Add app and agents folders to path for local modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "app"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "agents"))

import redis
from logging_utils import configure_logging, ensure_log_dir
from datastore import get_stores, DecisionLogStore, EscalationStore
from GPTClient import GPTClient
from novelty_agent import NoveltyAgent
from pipeline import group_reviews_by_product, evaluate_product
from config import *

# Setup logging
APP_LOG_PATH = "output/smart_escalation.log"
ensure_log_dir(APP_LOG_PATH)
configure_logging(APP_LOG_PATH)

# Load stores and decision log
review_store, cooldown_store = get_stores()
decision_log = DecisionLogStore()
escalation_store = EscalationStore()

def run_pipeline():
    now = datetime.now(timezone.utc)
    novelty_client = GPTClient()
    novelty_agent = NoveltyAgent(novelty_client)

    reviews = review_store.load_reviews()
    cooldown_state = cooldown_store.load_cooldowns()
    groups = group_reviews_by_product(reviews)

    escalations = []
    log_lines = []

    for product_id, product_reviews in groups.items():
        logging.info(f"Evaluating product {product_id} with {len(product_reviews)} reviews")
        escalate, reason, escalation_data = evaluate_product(
            product_id,
            product_reviews,
            cooldown_state,
            now,
            novelty_agent,
            COOLDOWN_HOURS,
            ESCALATION_THRESHOLD
        )
        log_entry = {
            "product_id": product_id,
            "evaluated_at": now.isoformat(),
            "escalated": escalate,
            "reason": reason
        }
        log_lines.append(json.dumps(log_entry))
        logging.info(f"Decision for {product_id}: escalate={escalate}, reason='{reason}'")

        if escalate:
            cooldown_state[product_id] = now.isoformat()
            escalations.append(escalation_data)

    review_store.save_reviews(reviews)
    cooldown_store.save_cooldowns(cooldown_state)
    escalation_store.save(escalations)
    decision_log.write(log_lines)

    logging.info("Smart escalation complete. Results written to:")
    logging.info(f" - {ESCALATIONS_OUTPUT}")
    logging.info(f" - {COOLDOWN_FILE}")
    logging.info(f" - {DECISION_LOG_FILE}")

# Redis trigger mode
if DATA_STORE == "redis":
    logging.info("Listening for Redis trigger on channel: escalation_trigger")
    redis_client = redis.Redis(host=os.getenv("REDIS_HOST", "localhost"), port=6379, db=0)
    pubsub = redis_client.pubsub()
    pubsub.subscribe("escalation_trigger")

    for message in pubsub.listen():
        if message["type"] == "message":
            logging.info("Trigger received — running escalation pipeline.")
            run_pipeline()
else:
    logging.info("Running escalation immediately (local mode).")
    run_pipeline()
