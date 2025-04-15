# agents/sentiment_agent.py

class SentimentAgent:
    """
    Responsible for classifying sentiment from product reviews.
    Wraps a GPTClient with a fixed prompt.
    """
    def __init__(self, gpt_client):
        self.client = gpt_client
        self.prompt_template = (
            "Determine if the following review is positive, neutral, or negative:\n\n{review}"
        )

    def classify(self, review_text: str) -> str:
        prompt = self.prompt_template.format(review=review_text)
        return self.client.classify_review(prompt)
