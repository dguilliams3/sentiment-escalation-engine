# remote_sentiment_agent.py
import requests

class RemoteExplainabilityAgent:
    """
    Wraps your explainability-service HTTP endpoint at port 5002.
    """
    def __init__(self, url: str = "http://explainability-service:5002/explain"):
        self.url = url

    def explain(self, text: str, sentiment: str) -> str:
        resp = requests.post(self.url, json={"text": text, "sentiment": sentiment})
        if resp.status_code != 200:
            raise RuntimeError(f"Explainability service error: {resp.text}")
        return resp.json().get("explanation", "")
