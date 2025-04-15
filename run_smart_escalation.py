# run_smart_escalation.py
import json
import os
from datetime import datetime, timedelta, timezone
from collections import defaultdict
import sys
import logging

# Add app folder to path for local modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "app"))

from logging_utils import configure_logging, ensure_log_dir
from GPTClient import GPTClient
from pipeline import (
    load_classified_reviews,
    load_cooldown_state,
    group_reviews_by_product,
    evaluate_product,
    save_json,
    write_decision_log
)
from config import *  # Assuming config defines COOLDOWN_HOURS and ESCALATION_THRESHOLD

# Configure application-level logging
APP_LOG_PATH = "output/smart_escalation.log"
ensure_log_dir(APP_LOG_PATH)
configure_logging(APP_LOG_PATH)

# Constants for file paths and thresholds
COOLDOWN_FILE = "output/cooldown_state.json"
DECISION_LOG_FILE = "output/escalation_decision_log.jsonl"
ESCALATIONS_OUTPUT = "output/escalations.json"

# Load classified reviews and cooldown state using modular functions
reviews = load_classified_reviews()
cooldown_state = load_cooldown_state()

# Initialize variables
escalations = []
log_lines = []
now = datetime.now(timezone.utc)
client = GPTClient()

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
        client,
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
save_json(escalations, ESCALATIONS_OUTPUT)
save_json(cooldown_state, COOLDOWN_FILE)
write_decision_log(log_lines, DECISION_LOG_FILE)

logging.info("Smart escalation complete. Results written to:")
logging.info(f" - {ESCALATIONS_OUTPUT}")
logging.info(f" - {COOLDOWN_FILE}")
logging.info(f" - {DECISION_LOG_FILE}")

print("Smart escalation complete. Results written to:")
print(f" - {ESCALATIONS_OUTPUT}")
print(f" - {COOLDOWN_FILE}")
print(f" - {DECISION_LOG_FILE}")
