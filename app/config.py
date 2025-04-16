import os
from dotenv import load_dotenv
from pathlib import Path

current_dir = Path(__file__).resolve().parent
dotenv_path = os.path.join(current_dir.parent, ".env")

# Only manually load .env if not running in Docker
if os.getenv("DATA_STORE", "").lower() != "redis" and not os.getenv("ENV_LOADED"):
    if os.path.exists(dotenv_path):
        print(f"Loading .env from {dotenv_path}")
        load_dotenv(dotenv_path)
        os.environ["ENV_LOADED"] = "true"

# --- LOGGING VARIABLES ---
LOG_USERNAME = os.getenv("LOG_USERNAME", "admin")
LOG_PASSWORD = os.getenv("LOG_PASSWORD", "password")
LOG_FILE_PATH = os.getenv("LOG_FILE_PATH", "./logs/context_log.log")

# --- GPT VARIABLES ---
GPT_MODEL = os.getenv("GPT_MODEL", "gpt-4o-mini")
GPT_MAX_TOKENS = int(os.getenv("GPT_MAX_TOKENS", 6000))
GPT_TEMPERATURE = float(os.getenv("GPT_TEMPERATURE", 0.5))
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Print once only
if not os.getenv("ENV_LOG_PRINTED"):
    print(f"GPT_MODEL: {GPT_MODEL}")
    print(f"GPT_MAX_TOKENS: {GPT_MAX_TOKENS}")
    print(f"GPT_TEMPERATURE: {GPT_TEMPERATURE}")
    print(f"DATA_STORE: {os.getenv('DATA_STORE')}")
    print(f"REDIS_HOST: {os.getenv('REDIS_HOST')}")
    os.environ["ENV_LOG_PRINTED"] = "true"

# --- ESCALATION VARIABLES ---
COOLDOWN_HOURS = int(os.getenv("COOLDOWN_HOURS", 6))
ESCALATION_THRESHOLD = int(os.getenv("ESCALATION_THRESHOLD", 3))

# --- FILE PATHS ---
ESCALATIONS_OUTPUT = os.getenv("ESCALATIONS_OUTPUT", "output/escalations.json")
COOLDOWN_FILE = os.getenv("COOLDOWN_FILE", "output/cooldown_state.json")
DECISION_LOG_FILE = os.getenv("DECISION_LOG_FILE", "output/escalation_decision_log.jsonl")
CLASSIFIED_REVIEWS_FILE = os.getenv("CLASSIFIED_REVIEWS_FILE", "output/classified_reviews.json")

# --- DATA STORE SETTINGS ---
DATA_STORE = os.getenv("DATA_STORE", "local")
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")

# --- MICROSERVICE SETTINGS ---
RAW_REVIEW_KEY = os.getenv("RAW_REVIEW_KEY", "raw_reviews")
