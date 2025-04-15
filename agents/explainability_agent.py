class ExplainabilityAgent:
    """
    Given a review and its sentiment, returns a natural language explanation
    for why the sentiment was classified that way.
    """
    def __init__(self, gpt_client):
        self.client = gpt_client
        self.prompt_template = (
            "Explain why the following review is considered {sentiment}:\n\n{review}\n\n"
            "Return a short explanation suitable for non-technical stakeholders."
        )

    def explain(self, review_text: str, sentiment: str) -> str:
        prompt = self.prompt_template.format(review=review_text, sentiment=sentiment)
        return self.client.classify_review(prompt)
