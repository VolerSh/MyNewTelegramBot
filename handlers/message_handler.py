import telebot
import logging

logger = logging.getLogger(__name__)

def register_message_handlers(bot: telebot.TeleBot):
    """
    Registers a handler for all text messages.
    """
    @bot.message_handler(func=lambda message: True)
    def handle_message(message):
        """
        Handles any text message by echoing it back to the user.
        """
        user_id = message.from_user.id
        text = message.text
        logger.info(f"Received message from user {user_id}: '{text[:50]}...'")
        
        # Echo the message back to the user
        bot.reply_to(message, f"Вы написали: {text}")
        logger.info(f"Echoed message back to user {user_id}.")