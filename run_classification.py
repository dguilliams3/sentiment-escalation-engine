import json
import os
import sys

# Add the app folder to the path so we can import GPTClient
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "app"))

from GPTClient import GPTClient

# rest of your code…


# Initialize your GPTClient
client = GPTClient()

# Load sample reviews
with open("data/sample_reviews.json", "r") as f:
    reviews = json.load(f)

classified_reviews = []
for review in reviews:
    text = review.get("text", "")
    sentiment = client.classify_review(text)
    review["sentiment"] = sentiment
    classified_reviews.append(review)
    print(f"Review: {text}\nSentiment: {sentiment}\n---")

# Ensure the output directory exists
os.makedirs("output", exist_ok=True)

# Save the results to the output JSON file
with open("output/classified_reviews.json", "w") as f:
    json.dump(classified_reviews, f, indent=4)

print("Classification complete. Results saved to output/classified_reviews.json")
