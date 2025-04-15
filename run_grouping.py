import json
from collections import defaultdict

with open("output/classified_reviews.json", "r") as f:
    reviews = json.load(f)

# Group reviews by product_id
groups = defaultdict(list)
for review in reviews:
    groups[review["product_id"]].append(review)

escalations = []
threshold = 3  # adjust as desired

# Evaluate each group
for product, product_reviews in groups.items():
    negative_count = sum(1 for r in product_reviews if "negative" in r.get("sentiment", ""))
    if negative_count >= threshold:
        escalations.append({
            "product_id": product,
            "negative_count": negative_count,
            "reason": f"{negative_count} negative reviews detected",
            "reviews": product_reviews
        })

with open("output/escalations.json", "w") as f:
    json.dump(escalations, f, indent=4)
print("Escalations processed and saved.")
