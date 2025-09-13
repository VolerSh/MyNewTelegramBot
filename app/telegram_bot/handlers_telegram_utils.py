# Этот файл содержит вспомогательные функции для работы с Telegram API
# Перенесено из app/telegram_bot/handlers.py

import telebot
import logging
import os
import asyncio
import threading
from datetime import datetime
from ..config import BOT_TOKEN, YOUR_TELEGRAM_CHAT_ID

# Настройка логирования - перенесено из handlers.py
logger = logging.getLogger(__name__)

# Глобальный экземпляр бота, чтобы не создавать его каждый раз - перенесено из handlers.py
bot = telebot.TeleBot(BOT_TOKEN)

def send_telegram_message(chat_id: str, message_text: str, file_path: str = None):
    """
    Отправляет текстовое сообщение и/или файл в указанный чат.
    Перенесено из handlers.py, строки 23-48
    
    Args:
        chat_id (str): ID чата для отправки.
        message_text (str): Текст сообщения.
        file_path (str, optional): Путь к файлу для отправки. Defaults to None.
    """
    if not chat_id:
        logger.error("Cannot send message: chat_id is not provided.")
        return False
    try:
        logger.info(f"Sending message to chat_id: {chat_id}")
        bot.send_message(chat_id, message_text, parse_mode='Markdown')
        if file_path and os.path.exists(file_path):
            logger.info(f"Sending file {file_path} to chat_id: {chat_id}")
            with open(file_path, 'rb') as file:
                bot.send_document(chat_id, file)
            logger.info("File sent successfully.")
        
        logger.info("Message sent successfully.")
        return True
    except Exception as e:
        logger.error(f"Failed to send message to {chat_id}: {e}", exc_info=True)
        return False

def check_file_creation_time(filepath: str) -> str:
    """
    Проверяет время создания/модификации файла и возвращает его в формате ISO 8601.
    Перенесено из handlers.py, строки 50-68
    """
    if not os.path.exists(filepath):
        logger.error(f"File {filepath} does not exist.")
        return "N/A"
    
    try:
        stat = os.stat(filepath)
        # On Windows, st_ctime is creation time, st_mtime is modification time
        # We want to check the most recent time the file was changed
        modification_time = datetime.fromtimestamp(stat.st_mtime)
        iso_time = modification_time.isoformat()
        logger.info(f"File {filepath} was last modified at: {iso_time}")
        return iso_time
    except Exception as e:
        logger.error(f"Failed to get modification time for {filepath}: {e}", exc_info=True)
        return "N/A"

def run_async_task(target_func, *args):
    """
    Запускает асинхронную функцию в новом цикле событий в отдельном потоке.
    Перенесено из handlers.py, строки 424-435
    """
    def worker():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(target_func(*args))
        finally:
            loop.close()
    
    thread = threading.Thread(target=worker)
    thread.start()