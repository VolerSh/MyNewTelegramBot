# Этот файл содержит функции для создания отчетов
# Перенесено из app/telegram_bot/handlers.py

import logging
import os
from datetime import datetime
from ..scraping.utils import run_spider, save_to_csv
from ..scraping.decomposer import LaptopDecomposer
from .handlers_telegram_utils import send_telegram_message
from .handlers_data_processing import filter_and_sort_results
from .handlers_database_utils import save_products_to_db

logger = logging.getLogger(__name__)

async def create_results_html(chat_id: str, search_query: str, search_mode: str = "basic"):
    """
    Запускает скрапинг, обрабатывает результаты и отправляет HTML-файл в Telegram.
    
    Args:
        chat_id (str): ID чата для отправки уведомлений и результата.
        search_query (str): Поисковый запрос.
        search_mode (str): Режим поиска - "basic" или "advanced".
    """
    if search_mode == "basic":
        # Базовый режим поиска
        message = f"--- Начинаю сбор всех ноутбуков {search_query} (базовый режим) ---"
        logger.info(message)
        send_telegram_message(chat_id, message)
        
        all_lenovo_laptops = await run_spider(search_query=search_query)
        
        if not all_lenovo_laptops:
            message = "Не удалось собрать данные о ноутбуках Lenovo Thinkbook. Поиск остановлен."
            logger.warning(message)
            send_telegram_message(chat_id, message)
            return

        # Декомпозиция
        decomposer = LaptopDecomposer()
        message = "Начинаю декомпозицию данных о ноутбуках..."
        logger.info(message)
        send_telegram_message(chat_id, message)
        decomposed_laptops = decomposer.decompose_all_laptops(all_lenovo_laptops)
        message = f"Декомпозиция завершена. Обработано {len(decomposed_laptops)} ноутбуков."
        logger.info(message)
        send_telegram_message(chat_id, message)

        # Сохранение в CSV
        save_to_csv(decomposed_laptops, "results/lenovo_laptops.csv")
        logger.info(f"Полный список ноутбуков сохранен в results/lenovo_laptops.csv.")

        # Сохранение в БД
        message = "Сохраняю результаты в базу данных..."
        logger.info(message)
        send_telegram_message(chat_id, message)
        save_products_to_db(decomposed_laptops)
        logger.info(f"Полный список ноутбуков сохранен в базу данных.")

        # Фильтрация
        message = "Фильтрую и ищу лучшие предложения..."
        logger.info(message)
        send_telegram_message(chat_id, message)
        models_to_find = {
            "Thinkbook 16, Ryzen AI 9 365": {'keywords': ['thinkbook', 'ryzen', 'ai', '365'], 'exclude': ['rtx', '5060']},
            "Thinkbook 16, Core Ultra 285H": {'keywords': ['thinkbook', 'core', 'ultra', '285h'], 'exclude': ['rtx', '5060']},
            "Thinkbook 16, Ryzen AI 7 350": {'keywords': ['thinkbook', 'ryzen', '350'], 'exclude': ['rtx', '5060']},
            "Thinkbook 16, Ryzen AI 9 365 + RTX 5060": {'keywords': ['thinkbook', 'ryzen', 'ai', '365', 'rtx', '5060'], 'exclude': None},
            "Thinkbook 16, Core Ultra 285H + RTX 5060": {'keywords': ['thinkbook', 'core', 'ultra', '285h', 'rtx', '5060'], 'exclude': None},
            "Thinkbook 16, Ryzen AI 7 350 + RTX 5060": {'keywords': ['thinkbook', 'ryzen', '350', 'rtx', '5060'], 'exclude': None},
        }
        
        final_results = {}
        for model_name, filters in models_to_find.items():
            final_results[model_name] = filter_and_sort_results(decomposed_laptops, filters['keywords'], filters['exclude'])
            logger.info(f"Для модели '{model_name}' найдено {len(final_results[model_name])} лучших предложений.")

        # Сохраняем отфильтрованные результаты в CSV
        filtered_data = []
        for model_name, items in final_results.items():
            for item in items:
                item['model_group'] = model_name # Добавляем колонку с названием группы
                filtered_data.append(item)
                
        save_to_csv(filtered_data, "results/filtered_results.csv")
        logger.info(f"Отфильтрованные результаты сохранены в results/filtered_results.csv. Всего {len(filtered_data)} записей.")

        # Генерация HTML с гиперссылками
        html_content = """
        <html>
        <head>
            <title>Результаты поиска</title>
            <style>
                body { font-family: sans-serif; }
                table { border-collapse: collapse; width: 90%; margin: 20px auto; }
                th, td { border: 1px solid #dddddd; text-align: left; padding: 8px; }
                th { background-color: #f2f2f2; }
                .model-header { background-color: #e0e0e0; font-weight: bold; }
            </style>
        </head>
        <body>
            <h1>Сводная таблица предложений</h1>
            <table>
                <tr>
                    <th>Модель</th>
                    <th>Найденное предложение</th>
                    <th>Цена</th>
                </tr>
        """
        for model_name, items in final_results.items():
            html_content += f'<tr><td colspan="3" class="model-header">{model_name}</td></tr>'
            if items:
                for item in items:
                    title = item.get('title', 'Без названия')
                    price = item.get('price', 'N/A')
                    link = item.get('link', '#')
                    html_content += f'<tr><td></td><td><a href="{link}" target="_blank">{title}</a></td><td>{price} руб.</td></tr>'
            else:
                html_content += '<tr><td colspan="3">Предложений не найдено</td></tr>'
                
        html_content += """
            </table>
        </body>
        </html>
        """
        
        filepath = "results/results.html"
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(html_content)
        
        logger.info(f"Итоговый HTML-файл с гиперссылками сохранен как: {filepath}")
        
        # Проверяем и сообщаем время модификации файла
        if os.path.exists(filepath):
            stat = os.stat(filepath)
            modification_time = datetime.fromtimestamp(stat.st_mtime)
            iso_time = modification_time.isoformat()
            logger.info(f"Файл {filepath} был последний раз изменен: {iso_time}")
            
            # Отправляем результат пользователю
            send_telegram_message(chat_id, "Поиск завершен! Отправляю таблицу с результатами.", file_path=filepath)
            
        else:
            message = f"Файл {filepath} не был найден после сохранения."
            logger.error(message)
            send_telegram_message(chat_id, message)
            
    elif search_mode == "advanced":
        # Расширенный режим поиска - поиск по конкретным комбинациям модель+процессор+видеокарта
        message = "--- Начинаю расширенный сбор ноутбуков по процессору и видеокарте ---"
        logger.info(message)
        send_telegram_message(chat_id, message)
        
        # Определяем конкретные комбинации для поиска
        # Оптимизированная стратегия поиска с меньшим количеством запросов
        search_combinations = [
            # Более общие запросы, которые затем фильтруются
            "lenovo thinkbook 16 ryzen",
            "lenovo thinkbook 16 core",
            "lenovo thinkbook 16 rtx",
            # Дополнительные запросы для охвата всех вариантов
            "lenovo thinkbook 16 ai 9",
            "lenovo thinkbook 16 ultra 285",
            "lenovo thinkbook 16 ai 7",
        ]
        
        # Собираем данные по каждой комбинации
        all_laptops = []
        for i, search_query in enumerate(search_combinations, 1):
            message = f"[{i}/{len(search_combinations)}] Поиск по запросу: *{search_query}*"
            logger.info(message)
            send_telegram_message(chat_id, message)
            
            laptops = await run_spider(search_query=search_query)
            if laptops:
                message = f"Найдено {len(laptops)} ноутбуков по запросу: *{search_query}*"
                logger.info(message)
                send_telegram_message(chat_id, message)
                all_laptops.extend(laptops)
            else:
                message = f"По запросу '{search_query}' ничего не найдено."
                logger.warning(message)
                send_telegram_message(chat_id, message)
        
        if not all_laptops:
            message = "Не удалось собрать данные о ноутбуках в расширенном режиме. Поиск остановлен."
            logger.warning(message)
            send_telegram_message(chat_id, message)
            return
        
        # Удаляем дубликаты по ссылке
        unique_laptops = {}
        for laptop in all_laptops:
            link = laptop.get('link', '')
            if link and link not in unique_laptops:
                unique_laptops[link] = laptop
            elif link and link in unique_laptops:
                # Если нашли дубликат, выбираем тот, у которого цена ниже
                if laptop.get('price', 0) < unique_laptops[link].get('price', float('inf')):
                    unique_laptops[link] = laptop
        
        unique_laptops_list = list(unique_laptops.values())
        message = f"После удаления дубликатов осталось {len(unique_laptops_list)} уникальных ноутбуков."
        logger.info(message)
        send_telegram_message(chat_id, message)
        
        # Декомпозиция
        decomposer = LaptopDecomposer()
        message = "Начинаю декомпозицию данных о ноутбуках..."
        logger.info(message)
        send_telegram_message(chat_id, message)
        decomposed_laptops = decomposer.decompose_all_laptops(unique_laptops_list)
        message = f"Декомпозиция завершена. Обработано {len(decomposed_laptops)} ноутбуков."
        logger.info(message)
        send_telegram_message(chat_id, message)

        # Сохранение в БД
        message = "Сохраняю результаты в базу данных..."
        logger.info(message)
        send_telegram_message(chat_id, message)
        save_products_to_db(decomposed_laptops)
        logger.info(f"Полный список ноутбуков сохранен в базу данных.")

        # Сохранение в CSV
        save_to_csv(decomposed_laptops, "results/lenovo_laptops_advanced.csv")
        logger.info(f"Полный список ноутбуков сохранен в results/lenovo_laptops_advanced.csv. Всего {len(decomposed_laptops)} записей.")

        # Фильтрация
        message = "Фильтрую и ищу лучшие предложения..."
        logger.info(message)
        send_telegram_message(chat_id, message)
        models_to_find = {
            "Thinkbook 16, Ryzen AI 9 365": {'keywords': ['thinkbook', 'ryzen', 'ai', '365'], 'exclude': ['rtx', '5060']},
            "Thinkbook 16, Core Ultra 285H": {'keywords': ['thinkbook', 'core', 'ultra', '285h'], 'exclude': ['rtx', '5060']},
            "Thinkbook 16, Ryzen AI 7 350": {'keywords': ['thinkbook', 'ryzen', '350'], 'exclude': ['rtx', '5060']},
            "Thinkbook 16, Ryzen AI 9 365 + RTX 5060": {'keywords': ['thinkbook', 'ryzen', 'ai', '365', 'rtx', '5060'], 'exclude': None},
            "Thinkbook 16, Core Ultra 285H + RTX 5060": {'keywords': ['thinkbook', 'core', 'ultra', '285h', 'rtx', '5060'], 'exclude': None},
            "Thinkbook 16, Ryzen AI 7 350 + RTX 5060": {'keywords': ['thinkbook', 'ryzen', '350', 'rtx', '5060'], 'exclude': None},
        }
        
        final_results = {}
        for model_name, filters in models_to_find.items():
            final_results[model_name] = filter_and_sort_results(decomposed_laptops, filters['keywords'], filters['exclude'])
            logger.info(f"Для модели '{model_name}' найдено {len(final_results[model_name])} лучших предложений.")

        # Сохраняем отфильтрованные результаты в CSV
        filtered_data = []
        for model_name, items in final_results.items():
            for item in items:
                item['model_group'] = model_name # Добавляем колонку с названием группы
                filtered_data.append(item)
                
        save_to_csv(filtered_data, "results/filtered_results_advanced.csv")
        logger.info(f"Отфильтрованные результаты сохранены в results/filtered_results_advanced.csv. Всего {len(filtered_data)} записей.")

        # Генерация HTML с гиперссылками
        html_content = """
        <html>
        <head>
            <title>Результаты поиска</title>
            <style>
                body { font-family: sans-serif; }
                table { border-collapse: collapse; width: 90%; margin: 20px auto; }
                th, td { border: 1px solid #dddddd; text-align: left; padding: 8px; }
                th { background-color: #f2f2f2; }
                .model-header { background-color: #e0e0e0; font-weight: bold; }
            </style>
        </head>
        <body>
            <h1>Сводная таблица предложений</h1>
            <table>
                <tr>
                    <th>Модель</th>
                    <th>Найденное предложение</th>
                    <th>Цена</th>
                </tr>
        """
        for model_name, items in final_results.items():
            html_content += f'<tr><td colspan="3" class="model-header">{model_name}</td></tr>'
            if items:
                for item in items:
                    title = item.get('title', 'Без названия')
                    price = item.get('price', 'N/A')
                    link = item.get('link', '#')
                    html_content += f'<tr><td></td><td><a href="{link}" target="_blank">{title}</a></td><td>{price} руб.</td></tr>'
            else:
                html_content += '<tr><td colspan="3">Предложений не найдено</td></tr>'
                
        html_content += """
            </table>
        </body>
        </html>
        """
        
        filepath = "results/results_advanced.html"
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(html_content)
        
        logger.info(f"Итоговый HTML-файл с гиперссылками сохранен как: {filepath}")
        
        # Проверяем и сообщаем время модификации файла
        if os.path.exists(filepath):
            stat = os.stat(filepath)
            modification_time = datetime.fromtimestamp(stat.st_mtime)
            iso_time = modification_time.isoformat()
            logger.info(f"Файл {filepath} был последний раз изменен: {iso_time}")
            
            # Отправляем результат пользователю
            send_telegram_message(chat_id, "Поиск завершен! Отправляю таблицу с результатами.", file_path=filepath)

        else:
            message = f"Файл {filepath} не был найден после сохранения."
            logger.error(message)
            send_telegram_message(chat_id, message)