import telebot
import os
import sys


def load_secret(filename, error_message):
    """Загружает секретный ключ из файла в той же директории."""
    try:
        path = os.path.join(os.path.dirname(__file__), filename)
        with open(path, 'r') as f:
            return f.read().strip()
    except FileNotFoundError:
        print(f"ОШИБКА: {error_message}")
        return None

BOT_TOKEN = load_secret('Bot_TG_token.txt', "Файл с токеном бота 'Bot_TG_token.txt' не найден.")

if not BOT_TOKEN:
    sys.exit("Один из ключей не загружен. Бот не может быть запущен.")

print("Ключи успешно загружены. Инициализация сервисов...")


# Инициализация бота
bot = telebot.TeleBot(BOT_TOKEN)

# --- Обработчики команд ---

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(message.chat.id, f"Привет, {message.from_user.first_name}! Я бот, усиленный интеллектом Gemini. Задайте мне любой вопрос.")

@bot.message_handler(commands=['help'])
def send_help(message):
    bot.send_message(message.chat.id, "Просто отправьте мне любой текстовый вопрос, и я постараюсь на него ответить.")



print("Бот запущен и готов к работе. Нажмите Ctrl+C для остановки.")
bot.polling(non_stop=True)