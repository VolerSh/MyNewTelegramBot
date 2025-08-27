import telebot
import logging

logger = logging.getLogger(__name__)

def register_handlers(bot: telebot.TeleBot):
    """
    Registers basic command handlers (start, help) for the bot.
    """
    @bot.message_handler(commands=['start'])
    def send_welcome(message):
        logger.info(f"Received /start command from user {message.from_user.id} ({message.from_user.first_name})")
        bot.send_message(message.chat.id, f"Привет, {message.from_user.first_name}! Я бот, усиленный интеллектом Gemini. Задайте мне любой вопрос.")

    @bot.message_handler(commands=['help'])
    def send_help(message):
        logger.info(f"Received /help command from user {message.from_user.id} ({message.from_user.first_name})")
        bot.send_message(message.chat.id, "Просто отправьте мне любой текстовый вопрос, и я постараюсь на него ответить.")