import os
from dotenv import load_dotenv
from pathlib import Path

current_dir = Path(__file__).resolve().parent
dotenv_path = current_dir.parent / '.env'

if not dotenv_path.is_file():
    raise FileNotFoundError(f"Could not find .env file at expected location: {dotenv_path}")
print(f"Pulling environment variables from {dotenv_path} ...")
load_dotenv(dotenv_path)

# Initialize logging variables
LOG_USERNAME = os.getenv("LOG_USERNAME", "admin")
LOG_PASSWORD = os.getenv("LOG_PASSWORD", "password")
LOG_FILE_PATH = os.getenv("LOG_FILE_PATH","./logs/context_log.log")

# Load GPT/OpenAI variables
GPT_MODEL = os.getenv("GPT_MODEL", "gpt-4o-mini")
GPT_MAX_TOKENS = int(os.getenv("GPT_MAX_TOKENS", 6000))
GPT_TEMPERATURE = 0.7
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
# Output the initial settings
print(f"GPT_MODEL: {GPT_MODEL}")
print(f"GPT_MAX_TOKENS: {GPT_MAX_TOKENS}")
print(f"GPT_TEMPERATURE: {GPT_TEMPERATURE}")

# --- ESCALATION VARIABLES ---
COOLDOWN_HOURS = int(os.getenv("COOLDOWN_HOURS", 6))
ESCALATION_THRESHOLD = int(os.getenv("ESCALATION_THRESHOLD", 3))
COOLDOWN_FILE = os.getenv("COOLDOWN_FILE", "output/cooldown_state.json")