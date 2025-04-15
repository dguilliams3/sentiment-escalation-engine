# run_classification.py
import json
import os
import sys
import html
from datetime import datetime, timezone

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "app"))
from GPTClient import GPTClient
from logging_utils import configure_logging, ensure_log_dir
import logging

# Configure logging for classification
LOG_PATH = "output/classification.log"
ensure_log_dir(LOG_PATH)
configure_logging(LOG_PATH)

# Initialize GPTClient
client = GPTClient()

# Load sample reviews
with open("data/sample_reviews.json", "r", encoding="utf-8") as f:
    reviews = json.load(f)

classified_reviews = []
for review in reviews:
    # Normalize and fix text encoding issues
    raw_text = review.get("text", "")
    clean_text = html.unescape(raw_text).replace("â€™", "'").replace("â€œ", "\"").replace("â€�", "\"")
    sentiment = client.classify_review(clean_text)
    review["text"] = clean_text
    review["sentiment"] = sentiment

    # Set `created_at` only if not already provided (this mimics real review timestamps)
    if "created_at" not in review:
        review["created_at"] = datetime.now(timezone.utc).isoformat()
    # Always set `classified_at` to indicate when classification happened
    review["classified_at"] = datetime.now(timezone.utc).isoformat()
    
    classified_reviews.append(review)
    logging.info(f"[{review['product_id']}] Classified review: {clean_text} -> {sentiment}")

# Ensure the output directory exists
os.makedirs("output", exist_ok=True)
with open("output/classified_reviews.json", "w", encoding="utf-8") as f:
    json.dump(classified_reviews, f, indent=4, ensure_ascii=False)

logging.info("Classification complete. Results saved to output/classified_reviews.json")
print("Classification complete. Results saved to output/classified_reviews.json")
