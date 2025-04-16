import os
import sys
import time
import logging
import tiktoken
import openai
from app.config import *

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "app"))
# Configure basic logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s]: %(message)s")

class GPTClient:
    """
    A minimal GPT client for sentiment classification, built for the 
    Sentiment Escalation Engine MVP.
    """
    def __init__(self, api_key=None, model="gpt-4o-mini", max_tokens=50, prompt_template=None):
        # Retrieve API key from argument or environment variable.
        self._api_key = api_key if api_key else os.getenv('OPENAI_API_KEY')
        self.client = openai.OpenAI(api_key=self._api_key)
        if not self._api_key:
            logging.error("API Key not found. Ensure it's set in the environment variables.")
            raise ValueError("API Key not found. Ensure it's set in the environment variables.")
        
        # Set model and maximum tokens for output.
        self._model = model
        self._max_tokens = max_tokens
        self.temperature = GPT_TEMPERATURE
        # Set a default prompt template for sentiment classification.
        self._prompt_template = prompt_template or (
            "Determine if the following review is positive, neutral, or negative:\n\n{review}"
        )
        
        # Set OpenAI API key
        openai.api_key = self._api_key
        
    def count_tokens(self, text):
        """
        Count the tokens in a given text using tiktoken.
        """
        encoding = tiktoken.encoding_for_model(self._model)
        return len(encoding.encode(text))
    
    def classify_review(self, review_text):
        """
        Classify the sentiment of the provided review text.
        Returns 'positive', 'neutral', or 'negative'.
        """
        prompt = self._prompt_template.format(review=review_text)
        max_retries = 3
        
        for attempt in range(1, max_retries + 1):
            try:
                response = self.client.chat.completions.create(
					model=self._model,
					messages=[{"role": "user", "content": prompt}],
					max_tokens=self._max_tokens,
					temperature=self.temperature,
				)
                logging.info(f"API call succeeded on attempt {attempt}")
                # Extract and return the content of the response.
                return response.choices[0].message.content.strip().lower()
            except Exception as e:
                logging.error(f"API call failed on attempt {attempt}: {e}")
                if attempt == max_retries:
                    raise e
                time.sleep(2)
                
if __name__ == "__main__":
    # Example usage: Classify a sample product review.
    client = GPTClient()
    sample_review = "The product stopped working after one week and didn't turn on anymore."
    sentiment = client.classify_review(sample_review)
    print(f"Sentiment: {sentiment}")
