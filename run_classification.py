# run_classification.py
import json
import os
import sys
import html
from datetime import datetime, timezone
import ftfy

# Add app and agents directories to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "app"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "agents"))

from GPTClient import GPTClient
from logging_utils import configure_logging, ensure_log_dir
from sentiment_agent import SentimentAgent
from explainability_agent import ExplainabilityAgent

import logging

# Configure logging
LOG_PATH = "output/classification.log"
ensure_log_dir(LOG_PATH)
configure_logging(LOG_PATH)

# Initialize GPT clients + agents
# We create unique GPTClients for each in case we later want to change the model, max tokens, or other attributes by-agent
sentiment_client = GPTClient()
explain_client = GPTClient()

sentiment_agent = SentimentAgent(sentiment_client)
explain_agent = ExplainabilityAgent(explain_client)

# Load raw reviews
with open("data/sample_reviews.json", "r", encoding="utf-8") as f:
    reviews = json.load(f)

classified_reviews = []
for review in reviews:
    raw_text = review.get("text", "")
    clean_text = ftfy.fix_text(html.unescape(raw_text))

    sentiment = sentiment_agent.classify(clean_text)
    explanation = explain_agent.explain(clean_text, sentiment)

    review["text"] = clean_text
    review["sentiment"] = sentiment
    review["explanation"] = explanation

    if "created_at" not in review:
        review["created_at"] = datetime.now(timezone.utc).isoformat()
    review["classified_at"] = datetime.now(timezone.utc).isoformat()

    classified_reviews.append(review)
    logging.info(f"[{review['product_id']}] Classified review: {clean_text} -> {sentiment}")


# Output results
os.makedirs("output", exist_ok=True)
with open("output/classified_reviews.json", "w", encoding="utf-8") as f:
    json.dump(classified_reviews, f, indent=4, ensure_ascii=False)

logging.info("Classification complete. Results saved to output/classified_reviews.json")
