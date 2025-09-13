# Technical Context

## 1. Core Technologies

*   **Python:** 3.x
*   **Telegram Bot Framework:** `python-telegram-bot`
*   **Web Scraping:** `Scrapy`
*   **Database ORM:** `SQLAlchemy`

## 2. Development Environment

*   **ОС:** Windows
*   **Менеджер зависимостей:** `pip` и `requirements.txt`.
*   **Запуск:** `run_bot.py` для бота, `run_scraper.py` для парсера.

## 3. Key Dependencies

(Здесь будет список ключевых библиотек из `requirements.txt` с кратким пояснением, зачем они нужны.)

*   `python-telegram-bot`: Для взаимодействия с Telegram API.
*   `scrapy`: Для извлечения данных с веб-сайтов.
*   `scrapy-playwright`: Для рендеринга динамических страниц (JavaScript) внутри Scrapy.
*   `sqlalchemy`: Для работы с базой данных.
*   `apscheduler`: Для планирования периодических задач (например, регулярного парсинга).

## 4. Technical Constraints

*   (Есть ли какие-то технические ограничения? Например: "Необходимость обходить защиту от ботов на целевых сайтах" или "Ограничения Telegram API на частоту отправки сообщений".)