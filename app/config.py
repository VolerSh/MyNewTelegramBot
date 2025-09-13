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

# Ваш ID для отправки сообщений от скрапера
YOUR_TELEGRAM_CHAT_ID = os.getenv('YOUR_TELEGRAM_CHAT_ID')
if not YOUR_TELEGRAM_CHAT_ID:
    logger.warning("YOUR_TELEGRAM_CHAT_ID not found in .env file. The bot will not be able to send scraping results.")
else:
    YOUR_TELEGRAM_CHAT_ID = int(YOUR_TELEGRAM_CHAT_ID)


# --- Bot Settings ---
ADMIN_USER_IDS = [123456789, 987654321] # Example admin IDs

logger.info("Configuration loaded successfully.")