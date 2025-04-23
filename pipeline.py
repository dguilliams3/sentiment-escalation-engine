# pipeline.py
import os
from collections import defaultdict
from datetime import datetime, timedelta, timezone
import sys

# Add the app and agents directories to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "app"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "agents"))

# Add agents 
from remote_sentiment_agent      import RemoteSentimentAgent
from remote_explainability_agent import RemoteExplainabilityAgent

# Add config
from config import *

# Check whether to add explainations to the classification/escalation determinations
ENABLE_EXPLAINABILITY = os.getenv("ENABLE_EXPLAINABILITY", "true").lower() == "true"
    
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

def classify_reviews(reviews, now, sentiment_agent=None, explain_agent=None):
    """
    Classify and (optionally) explain a batch of reviews.
    Defaults to calling your HTTP services if no agents are passed in.
    """
    # default to remote HTTP services
    if sentiment_agent is None:
        sentiment_agent = RemoteSentimentAgent()
    if ENABLE_EXPLAINABILITY:
        if explain_agent is None:
            explain_agent = RemoteExplainabilityAgent()
    else:
        explain_agent = None

    classified = []
    for r in reviews:
        # call the remote sentiment-service
        sentiment   = sentiment_agent.classify(r["text"])
        # call the remote explainability-service
        explanation = explain_agent.explain(r["text"], sentiment) if explain_agent else None

        r["sentiment"]     = sentiment
        r["classified_at"] = now.isoformat()
        r["explanation"]   = explanation
        classified.append(r)

    return classified

def write_decision_log(log_lines, log_filepath="output/escalation_decision_log.jsonl"):
    with open(log_filepath, "a", encoding="utf-8") as f:
        for line in log_lines:
            f.write(line + "\n")
