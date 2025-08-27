import telebot
import logging
from config import BOT_TOKEN
from handlers import basic_commands, message_handler
from logging_config import setup_logging

# Настройка логирования
setup_logging()
logger = logging.getLogger(__name__)


def main():
    """Основная функция для запуска бота."""
    try:
        logger.info("Initializing bot...")
        bot = telebot.TeleBot(BOT_TOKEN)

        # Регистрация обработчиков
        logger.info("Registering handlers...")
        basic_commands.register_handlers(bot)
        message_handler.register_message_handlers(bot)

        logger.info("Bot started and polling. Press Ctrl+C to stop.")
        bot.polling(non_stop=True)

    except Exception as e:
        logger.critical(f"A critical error occurred: {e}", exc_info=True)
        # В реальном приложении здесь можно было бы отправить уведомление администратору

if __name__ == '__main__':
    main()