import os
import sys
import logging
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

# Загружаем переменные окружения из .env файла
logger.info("Loading environment variables from .env file...")
load_dotenv()

# --- Bot Configuration ---
BOT_TOKEN = os.getenv('BOT_TOKEN')
if not BOT_TOKEN:
    logger.critical("BOT_TOKEN not found in .env file. The bot cannot be started.")
    sys.exit("CRITICAL: BOT_TOKEN not found in .env file.")


# --- Bot Settings ---
ADMIN_USER_IDS = [123456789, 987654321] # Example admin IDs

logger.info("Configuration loaded successfully.")