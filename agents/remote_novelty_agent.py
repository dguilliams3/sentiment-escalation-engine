# agents/remote_novelty_agent.py

import requests

class RemoteNoveltyAgent:
    def __init__(self, url="http://novelty-service:5050/assess_novelty"):
        self.url = url

    def assess_novelty(self, prior_reviews, new_review):
        response = requests.post(self.url, json={
            "prior": prior_reviews,
            "new": new_review
        })
        if response.status_code != 200:
            raise RuntimeError(f"Novelty service error: {response.text}")
        return response.json().get("novel", "")
