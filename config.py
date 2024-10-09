# File: config.py
import os
from dotenv import load_dotenv

load_dotenv()

REQUIRED_VARS = ["TWITCH_CLIENT_ID", "TWITCH_SECRET", "OPENAI_API_KEY", "BOT_TOKEN"]

# Validate environment variables
def validate_config():
    missing_vars = [var for var in REQUIRED_VARS if not os.getenv(var)]
    if missing_vars:
        raise EnvironmentError(f"Missing required environment variables: {', '.join(missing_vars)}")

# Call the validation function
validate_config()

def get_env_variable(var_name, default=None):
    """Fetches environment variable or provides a default."""
    return os.getenv(var_name, default)

# Bot configuration
MAX_RETRIES = int(os.getenv('MAX_RETRIES', 5))
RETRY_DELAY = int(os.getenv('RETRY_DELAY', 5))
MAX_TOKENS = int(os.getenv('MAX_TOKENS', 500))

# Twitch configuration
TWITCH_OAUTH_TOKEN = os.getenv('TWITCH_OAUTH_TOKEN')
TWITCH_CHANNEL = os.getenv('TWITCH_CHANNEL')
BOT_NAME = os.getenv('BOT_NAME')
BROADCASTER_ID = os.getenv('BROADCASTER_ID')
TWITCH_CLIENT_ID = os.getenv('TWITCH_CLIENT_ID')

# Speaker.bot configuration
STREAMERBOT_WS_URI = os.getenv('STREAMERBOT_WS_URI')

# OpenAI configuration
CHATGPT_API_KEY = os.getenv('CHATGPT_API_KEY')
OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')

# MongoDB configuration
MONGO_URI = os.getenv('MONGO_URI')
MONGO_DB_NAME = os.getenv('MONGO_DB_NAME')

# LittleNavMap configuration
LITTLENAVMAP_API_URL = os.getenv('LITTLENAVMAP_API_URL')

# Logging configuration
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FILE = os.getenv('LOG_FILE', 'bot.log')

# Voice command configuration
VOICE_COMMAND_PREFIX = os.getenv('VOICE_COMMAND_PREFIX', 'hey bot')

# Bot personality
DEFAULT_BOT_PERSONALITY = os.getenv('DEFAULT_BOT_PERSONALITY', "You are a helpful Twitch chat assistant.")

# Rate limiting
RATE_LIMIT_CALLS = int(os.getenv('RATE_LIMIT_CALLS', 20))
RATE_LIMIT_PERIOD = int(os.getenv('RATE_LIMIT_PERIOD', 30))

# Cache configuration
CACHE_MAXSIZE = int(os.getenv('CACHE_MAXSIZE', 100))
CACHE_TTL = int(os.getenv('CACHE_TTL', 300))  # Time in seconds