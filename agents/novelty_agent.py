class NoveltyAgent:
    """
    Determines whether the newest review introduces a novel concern during cooldown.
    """
    def __init__(self, gpt_client):
        self.client = gpt_client
        self.prompt_template = (
            "You're reviewing product complaints.\n\n"
            "Prior negative reviews:\n{prior}\n\n"
            "Newest review:\n- {latest}\n\n"
            "Does the newest review raise a novel or significantly different issue?\n"
            "Respond 'yes' or 'no' and briefly justify your answer."
        )

    def assess_novelty(self, prior_reviews: list[str], latest_review: str) -> str:
        prior = "\n".join(f"- {r}" for r in prior_reviews)
        prompt = self.prompt_template.format(prior=prior, latest=latest_review)
        return self.client.classify_review(prompt)
