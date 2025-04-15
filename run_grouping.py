import json
from collections import defaultdict
from datetime import datetime, timezone

with open("output/classified_reviews.json", "r", encoding="utf-8") as f:
    reviews = json.load(f)

groups = defaultdict(list)
for review in reviews:
    groups[review["product_id"]].append(review)

escalations = []
threshold = 3  # can be made dynamic later

for product, product_reviews in groups.items():
    negative_reviews = [r for r in product_reviews if "negative" in r.get("sentiment", "")]
    if len(negative_reviews) >= threshold:
        escalations.append({
            "product_id": product,
            "negative_count": len(negative_reviews),
            "reason": f"{len(negative_reviews)} negative reviews detected",
            "escalated_at": datetime.now(timezone.utc).isoformat(),
            "reviews": negative_reviews
        })

with open("output/escalations.json", "w", encoding="utf-8") as f:
    json.dump(escalations, f, indent=4, ensure_ascii=False)

print("Escalations processed and saved.")
print(f"Total escalations: {len(escalations)}")