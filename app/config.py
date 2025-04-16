import os
from dotenv import load_dotenv
from pathlib import Path

current_dir = Path(__file__).resolve().parent
dotenv_path = current_dir.parent / '.env'

# Load environment variables from .env file
if not dotenv_path.is_file():
    raise FileNotFoundError(f"Could not find .env file at expected location: {dotenv_path}")

# config.py
if not os.environ.get("ENV_LOADED"):  # Only do this once
    print(f"Pulling environment variables from {dotenv_path} ...")
    load_dotenv(dotenv_path)
    os.environ["ENV_LOADED"] = "true"

# --- LOGGING VARIABLES ---
LOG_USERNAME = os.getenv("LOG_USERNAME", "admin")
LOG_PASSWORD = os.getenv("LOG_PASSWORD", "password")
LOG_FILE_PATH = os.getenv("LOG_FILE_PATH","./logs/context_log.log")

# --- GPT VARIABLES ---
GPT_MODEL = os.getenv("GPT_MODEL", "gpt-4o-mini")
GPT_MAX_TOKENS = int(os.getenv("GPT_MAX_TOKENS", 6000))
GPT_TEMPERATURE = float(os.getenv("GPT_TEMPERATURE", 0.5))
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Output the initial settings
print(f"GPT_MODEL: {GPT_MODEL}")
print(f"GPT_MAX_TOKENS: {GPT_MAX_TOKENS}")
print(f"GPT_TEMPERATURE: {GPT_TEMPERATURE}")

# --- ESCALATION VARIABLES ---
COOLDOWN_HOURS = int(os.getenv("COOLDOWN_HOURS", 6))
ESCALATION_THRESHOLD = int(os.getenv("ESCALATION_THRESHOLD", 3))

# --- FILE PATHS ---
ESCALATIONS_OUTPUT = os.getenv("ESCALATIONS_OUTPUT","output/escalations.json")
COOLDOWN_FILE = os.getenv("COOLDOWN_FILE", "output/cooldown_state.json")
DECISION_LOG_FILE = os.getenv("DECISION_LOG_FILE", "output/escalation_decision_log.jsonl")
CLASSIFIED_REVIEWS_FILE = os.getenv("CLASSIFIED_REVIEWS_FILE", "output/classified_reviews.json")

# --- DATA STORE SETTINGS ---
DATA_STORE = os.getenv("DATA_STORE", "local")  # or "redis"
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")

# Output the data store settings
print(f"DATA_STORE: {DATA_STORE}")
print(f"REDIS_HOST: {REDIS_HOST}")