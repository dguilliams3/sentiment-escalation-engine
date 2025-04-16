# pipeline.py
import os
from collections import defaultdict
from datetime import datetime, timedelta, timezone
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "app"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "agents"))

from datastore import get_stores
from agents.sentiment_agent import SentimentAgent

def group_reviews_by_product(reviews):
    groups = defaultdict(list)
    for r in reviews:
        groups[r["product_id"]].append(r)
    return groups

def evaluate_product(product_id, product_reviews, cooldown_state, now, agent, cooldown_hours, escalation_threshold):
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
        response = agent.assess_novelty(neg_texts[:-1], neg_texts[-1]).lower()

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

def classify_reviews(reviews, gpt_client, now):
    sentiment_agent = SentimentAgent(gpt_client)
    classified_reviews = []

    for r in reviews:
        sentiment = sentiment_agent.classify(r["text"])
        r["sentiment"] = sentiment
        r["classified_at"] = now.isoformat()
        classified_reviews.append(r)

    return classified_reviews

def write_decision_log(log_lines, log_filepath="output/escalation_decision_log.jsonl"):
    with open(log_filepath, "a", encoding="utf-8") as f:
        for line in log_lines:
            f.write(line + "\n")
