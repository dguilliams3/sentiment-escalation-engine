import json
import os
import sys
import html
from datetime import datetime, timezone

# Add the app folder to the path so we can import GPTClient
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "app"))

from GPTClient import GPTClient

# Initialize your GPTClient
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

    # Set `created_at` only if missing
    if "created_at" not in review:
        review["created_at"] = datetime.now(timezone.utc).isoformat()

    # Always set `classified_at`
    review["classified_at"] = datetime.now(timezone.utc).isoformat()

    classified_reviews.append(review)
    print(f"Review: {clean_text}\nSentiment: {sentiment}\n---")

# Ensure the output directory exists
os.makedirs("output", exist_ok=True)

with open("output/classified_reviews.json", "w", encoding="utf-8") as f:
    json.dump(classified_reviews, f, indent=4, ensure_ascii=False)

print("Classification complete. Results saved to output/classified_reviews.json")
