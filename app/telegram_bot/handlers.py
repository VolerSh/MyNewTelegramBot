import logging
import csv
import os
from telebot import types
import asyncio
import threading
from ..config import BOT_TOKEN, YOUR_TELEGRAM_CHAT_ID
from ..logging_config import setup_logging
from ..scraping.utils import run_spider, save_to_csv
from ..scraping.decomposer import LaptopDecomposer
from ..database.database import init_db, SessionLocal
from ..database.models import Product
from .handlers_telegram_utils import send_telegram_message
from .handlers_data_processing import filter_and_sort_results
from .handlers_database_utils import save_products_to_db
from .handlers_reporting import create_results_html

# Настройка логирования
setup_logging()
logger = logging.getLogger(__name__)








# Этот обработчик ловит абсолютно все сообщения
def send_file_handler(message):
    """
    Отправляет файл results.html. Вызывается при нажатии на кнопку "Запрос".
    """
    user_id = message.chat.id
    username = message.from_user.username
    
    logger.info(f"Получен запрос на файл от пользователя ID: {user_id}, Username: {username}.")
    
    relative_path = "results/results.html"
    
    if os.path.exists(relative_path):
        send_telegram_message(user_id, "Вот ваш файл.", file_path=relative_path)
    else:
        error_message = f"Файл не найден по пути: {relative_path}"
        logger.error(error_message)
        send_telegram_message(user_id, error_message)

def register_all_handlers(bot):
    """
    Регистрирует все обработчики сообщений для переданного экземпляра бота.
    """
    @bot.message_handler(commands=['start', 'help'])
    def send_welcome(message):
        # Создаем клавиатуру с одной кнопкой
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
        btn = types.KeyboardButton("Запрос")
        markup.add(btn)
        
        # Отправляем приветственное сообщение с клавиатурой
        bot.reply_to(message, "Привет! Нажми на кнопку 'Запрос', чтобы получить файл.", reply_markup=markup)

    # Обработчик для кнопки "Запрос"
    @bot.message_handler(func=lambda message: message.text == "Запрос")
    def handle_request_button(message):
        send_file_handler(message)

    # Обработчик для любого другого текста
    @bot.message_handler(func=lambda message: True)
    def handle_other_text(message):
        bot.reply_to(message, "Пожалуйста, используйте кнопку 'Запрос' для получения файла.")

    logger.info("Обработчики успешно зарегистрированы.")