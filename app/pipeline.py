# pipeline.py
import json
import os
from collections import defaultdict
from datetime import datetime, timedelta, timezone
import logging

def load_json(filepath, encoding="utf-8"):
    if os.path.exists(filepath):
        with open(filepath, "r", encoding=encoding) as f:
            return json.load(f)
    return None

def save_json(data, filepath, encoding="utf-8", indent=4, ensure_ascii=False):
    with open(filepath, "w", encoding=encoding) as f:
        json.dump(data, f, indent=indent, ensure_ascii=ensure_ascii)

def load_classified_reviews(filepath="output/classified_reviews.json"):
    reviews = load_json(filepath)
    if reviews is None:
        logging.warning(f"File {filepath} not found. Returning empty list.")
        reviews = []
    return reviews

def load_cooldown_state(filepath="output/cooldown_state.json"):
    state = load_json(filepath)
    if state is None:
        state = {}
    return state

def group_reviews_by_product(reviews):
    groups = defaultdict(list)
    for r in reviews:
        groups[r["product_id"]].append(r)
    return groups

def evaluate_product(product_id, product_reviews, cooldown_state, now, client, cooldown_hours, escalation_threshold):
    # Filter negative reviews (using a case-insensitive match)
    neg_reviews = [r for r in product_reviews if "negative" in r.get("sentiment", "").lower()]
    neg_texts = [r["text"] for r in neg_reviews]
    if not neg_reviews:
        return (False, "No negative reviews", None)
    
    # Check if product is under cooldown
    last_escalated_at = cooldown_state.get(product_id)
    under_cooldown = False
    if last_escalated_at:
        cooldown_expiry = datetime.fromisoformat(last_escalated_at) + timedelta(hours=cooldown_hours)
        under_cooldown = now < cooldown_expiry

    escalate = False
    reason = ""
    escalation_data = None

    if len(neg_reviews) >= escalation_threshold and not under_cooldown:
        escalate = True
        reason = f"{len(neg_reviews)} negative reviews detected"
    elif under_cooldown:
        prompt = f"""You're reviewing product complaints.

Prior negative reviews:
{chr(10).join('- ' + text for text in neg_texts[:-1])}

Newest review:
- {neg_texts[-1]}

Does the newest review raise a novel or significantly different issue?
Respond "yes" or "no" and briefly justify your answer.
"""
        response = client.classify_review(prompt).lower()
        if "yes" in response:
            escalate = True
            reason = "Novel issue detected during cooldown"
        else:
            escalate = False
            reason = "Suppressed by cooldown (no novelty)"
    else:
        escalate = False
        reason = "Below escalation threshold"
    
    if escalate:
        escalation_data = {
            "product_id": product_id,
            "negative_count": len(neg_reviews),
            "reason": reason,
            "escalated_at": now.isoformat(),
            "reviews": neg_reviews
        }
    return (escalate, reason, escalation_data)

def write_decision_log(log_lines, log_filepath="output/escalation_decision_log.jsonl"):
    with open(log_filepath, "a", encoding="utf-8") as f:
        for line in log_lines:
            f.write(line + "\n")
