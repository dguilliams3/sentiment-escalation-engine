import json
import os
import redis
import logging
from config import *

# Base interface
class ReviewStore:
    def load_reviews(self):
        raise NotImplementedError

    def save_reviews(self, reviews):
        raise NotImplementedError

class CooldownStore:
    def load_cooldowns(self):
        raise NotImplementedError

    def save_cooldowns(self, cooldown_state):
        raise NotImplementedError

# ----------------------------
# Local JSON Implementation
# ----------------------------

class LocalReviewStore(ReviewStore):
    def load_reviews(self):
        if os.path.exists(CLASSIFIED_REVIEWS_FILE):
            with open(CLASSIFIED_REVIEWS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        return []

    def save_reviews(self, reviews):
        with open(CLASSIFIED_REVIEWS_FILE, "w", encoding="utf-8") as f:
            json.dump(reviews, f, indent=4, ensure_ascii=False)

class LocalCooldownStore(CooldownStore):
    def load_cooldowns(self):
        if os.path.exists(COOLDOWN_FILE):
            with open(COOLDOWN_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def save_cooldowns(self, cooldown_state):
        with open(COOLDOWN_FILE, "w", encoding="utf-8") as f:
            json.dump(cooldown_state, f, indent=4, ensure_ascii=False)

# ----------------------------
# Redis Implementation (Stub)
# ----------------------------

class RedisReviewStore(ReviewStore):
    def __init__(self):
        self.client = redis.Redis(host=REDIS_HOST, port=6379, db=0)
        self.key = "classified_reviews"

    def load_reviews(self):
        raw = self.client.get(self.key)
        if raw:
            return json.loads(raw)
        return []

    def save_reviews(self, reviews):
        self.client.set(self.key, json.dumps(reviews))

class RedisCooldownStore(CooldownStore):
    def __init__(self):
        self.client = redis.Redis(host=REDIS_HOST, port=6379, db=0)

    def load_cooldowns(self):
        raw = self.client.get("cooldown_state")
        if raw:
            return json.loads(raw)
        return {}

    def save_cooldowns(self, cooldown_state):
        self.client.set("cooldown_state", json.dumps(cooldown_state))

# ----------------------------
# Factory Selector
# ----------------------------

def get_stores():
    if DATA_STORE == "redis":
        logging.info("Using Redis data store")
        return RedisReviewStore(), RedisCooldownStore()
    else:
        logging.info("Using local JSON data store")
        return LocalReviewStore(), LocalCooldownStore()

# ----------------------------
# Logging Decisions
# ----------------------------

class DecisionLogStore:
    def __init__(self, log_filepath="output/escalation_decision_log.jsonl"):
        self.path = log_filepath

    def write(self, log_lines):
        with open(self.path, "a", encoding="utf-8") as f:
            for line in log_lines:
                f.write(line + "\n")

    def clear(self):
        if os.path.exists(self.path):
            os.remove(self.path)

    def exists(self):
        return os.path.exists(self.path)

class EscalationStore:
    def __init__(self):
        self.client = redis.Redis(host=REDIS_HOST, port=6379, db=0)
        self.key = "escalations"

    def save(self, escalations):
        self.client.set(self.key, json.dumps(escalations))

    def load(self):
        data = self.client.get(self.key)
        return json.loads(data) if data else []

    def clear(self):
        self.client.delete(self.key)
