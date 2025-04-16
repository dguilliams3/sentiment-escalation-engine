# run_smart_escalation.py
import json
import os
from datetime import datetime, timedelta, timezone
from collections import defaultdict
import sys
import logging

# Add app and agents folders to path for local modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "app"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "agents"))

from logging_utils import configure_logging, ensure_log_dir

from datastore import get_stores, DecisionLogStore, EscalationStore
from GPTClient import GPTClient
from pipeline import group_reviews_by_product, evaluate_product

from config import *
from novelty_agent import NoveltyAgent

# Configure application-level logging
APP_LOG_PATH = "output/smart_escalation.log"
ensure_log_dir(APP_LOG_PATH)
configure_logging(APP_LOG_PATH)

# Load classified reviews and cooldown state using modular functions
review_store, cooldown_store = get_stores()
reviews = review_store.load_reviews()
cooldown_state = cooldown_store.load_cooldowns()
decision_log = DecisionLogStore()
escalation_store = EscalationStore()

# Initialize variables
escalations = []
log_lines = []
now = datetime.now(timezone.utc)

# Assign GPT Client and Novelty Agent
novelty_client = GPTClient()
novelty_agent = NoveltyAgent(novelty_client)

# Group reviews by product
groups = group_reviews_by_product(reviews)

# Process each product group
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
        # Update cooldown state and add escalation entry
        cooldown_state[product_id] = now.isoformat()
        escalations.append(escalation_data)

# Save outputs using modular save_json function
escalation_store.save(escalations)
cooldown_store.save_cooldowns(cooldown_state)
decision_log.write(log_lines)

logging.info("Smart escalation complete. Results written to:")
logging.info(f" - {ESCALATIONS_OUTPUT}")
logging.info(f" - {COOLDOWN_FILE}")
logging.info(f" - {DECISION_LOG_FILE}")