# remote_sentiment_agent.py
import requests

class RemoteSentimentAgent:
    """
    Wraps your sentiment-service HTTP endpoint at port 5001.
    """
    def __init__(self, url: str = "http://sentiment-service:5001/classify_sentiment"):
        self.url = url

    def classify(self, text: str) -> str:
        resp = requests.post(self.url, json={"text": text})
        if resp.status_code != 200:
            raise RuntimeError(f"Sentiment service error: {resp.text}")
        return resp.json().get("sentiment", "")
