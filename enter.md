
# План Действий для Orchestrator: Полное Ознакомление с Проектом

Твоя задача — провести полный анализ проекта, сопоставить его с документацией и определить следующий шаг.

## Твои Действия:

**Шаг 1: Сбор Всей Информации (за один вызов `code-executor`)**
Делегируй `code-executor`'у задачу прочитать содержимое следующих файлов. Если файл не найден, он должен быть пропущен.

*   **Memory Bank:**
    *   `Memory-Bank/activeContext.md`
    *   `Memory-Bank/productContext.md`
    *   `Memory-Bank/progress.md`
    *   `Memory-Bank/projectbrief.md`
    *   `Memory-Bank/systemPatterns.md`
    *   `Memory-Bank/techContext.md`
*   **Документация и Правила:**
    *   `docs/0_documentation_rules.md`
    *   `docs/1_project_diagram.html`
    *   `docs/1.1_telegram_module.html`
    *   `docs/1.2_scraping_module.html`
    *   `docs/1.3_database_module.html`
    *   `docs/1.4_analysis_module.html`
    *   `.kilocode/rules/rules.md`
*   **Конфигурация и Зависимости:**
    *   `requirements.txt`
    *   `app/config.py`
    *   `scrapy.cfg`
*   **Ключевые файлы логики:**
    *   `run_bot.py`
    *   `run_scraper.py`
    *   `app/telegram_bot/bot.py`
    *   `app/telegram_bot/handlers.py`

**Шаг 2: Анализ и Синтез**
Далее `code-executor`
1.  читает все рабчие файлы проекта
2.  возвращает всю информацию тебе.


**Шаг 3: **Сформулируй** краткое резюме о текущем состоянии проекта.
1.  Предложи дальнейший шаг.