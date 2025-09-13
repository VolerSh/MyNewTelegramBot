import asyncio
import logging
import csv
import os
import json
import time
import sys
from typing import List, Dict

# В Windows для Scrapy и asyncio требуется SelectorEventLoop
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from scrapy.crawler import CrawlerRunner
from scrapy.utils.project import get_project_settings
from twisted.internet import reactor, defer
from twisted.internet.task import deferLater
from app.scraping.spiders.yandex_market import YandexMarketSpider

logger = logging.getLogger(__name__)

# Константа для времени жизни кэша (в секундах) - 1 час
CACHE_TTL = 3600

def get_cache_filename(search_query: str) -> str:
    """
    Генерирует имя файла для кэширования результатов поиска.
    """
    # Очищаем поисковый запрос от недопустимых символов для имени файла
    safe_query = "".join(c for c in search_query if c.isalnum() or c in (' ', '-', '_')).rstrip()
    return f"cache_{safe_query}.json"

def is_cache_valid(cache_filename: str) -> bool:
    """
    Проверяет, действителен ли кэш (не истек ли срок его жизни).
    """
    if not os.path.exists(cache_filename):
        return False
    
    # Проверяем время модификации файла
    file_mod_time = os.path.getmtime(cache_filename)
    current_time = time.time()
    
    return (current_time - file_mod_time) < CACHE_TTL

def load_from_cache(cache_filename: str) -> List[Dict]:
    """
    Загружает результаты из кэш-файла.
    """
    try:
        with open(cache_filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
            logger.info(f"Результаты загружены из кэша: {cache_filename}")
            return data
    except Exception as e:
        logger.error(f"Ошибка при загрузке данных из кэша {cache_filename}: {e}", exc_info=True)
        return []

def save_to_cache(cache_filename: str, data: List[Dict]) -> None:
    """
    Сохраняет результаты в кэш-файл.
    """
    try:
        with open(cache_filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            logger.info(f"Результаты сохранены в кэш: {cache_filename}")
    except Exception as e:
        logger.error(f"Ошибка при сохранении данных в кэш {cache_filename}: {e}", exc_info=True)

class SpiderRunner:
    """
    Класс для запуска пауков Scrapy в асинхронном режиме без использования subprocess.
    """
    def __init__(self):
        self.runner = None
        self.items = []
    
    def item_scraped(self, item, response, spider):
        """Callback для обработки собранных элементов."""
        self.items.append(item)
    
    async def run_spider(self, search_query: str) -> List[Dict]:
        """
        Запускает паука в асинхронном режиме и возвращает результаты.
        """
        max_retries = 3
        retry_delay = 5  # seconds
        
        for attempt in range(max_retries):
            try:
                logger.info(f"Запуск паука в асинхронном режиме для запроса: {search_query} (попытка {attempt + 1}/{max_retries})")
                
                # Очищаем список элементов перед новым запуском
                self.items = []
                
                # Создаем новый процесс для каждого запуска
                settings = get_project_settings()
                settings.set('SPIDER_MODULES', ['app.scraping.spiders'])
                # Отключаем логи Scrapy, чтобы не засорять вывод
                settings.set('LOG_LEVEL', 'ERROR')
                
                from scrapy.crawler import CrawlerProcess
                process = CrawlerProcess(settings)
                
                # Подписываемся на событие item_scraped
                from scrapy import signals
                from scrapy.signalmanager import dispatcher
                dispatcher.connect(self.item_scraped, signal=signals.item_scraped)
                
                # Запускаем паука
                process.crawl(YandexMarketSpider, search_query=search_query)
                process.start()  # Блокирующий вызов
                
                logger.info(f"Скрапинг для '{search_query}' успешно завершен. Найдено {len(self.items)} товаров.")
                return self.items
                
            except Exception as e:
                logger.error(f"Ошибка при запуске паука (попытка {attempt + 1}/{max_retries}): {e}", exc_info=True)
                if attempt < max_retries - 1:
                    logger.info(f"Ожидание {retry_delay} секунд перед следующей попыткой...")
                    await asyncio.sleep(retry_delay)
                else:
                    logger.error(f"Все попытки запуска паука для запроса '{search_query}' исчерпаны.")
                    return []

# Глобальный экземпляр runner
spider_runner = SpiderRunner()

async def run_spider(search_query: str) -> List[Dict]:
    """
    Запускает паука в асинхронном режиме и возвращает результаты.
    Использует кэширование для избежания повторных запросов.
    """
    # Генерируем имя файла для кэша
    cache_filename = get_cache_filename(search_query)
    
    # Проверяем, есть ли действительный кэш
    if is_cache_valid(cache_filename):
        logger.info(f"Найден действительный кэш для запроса '{search_query}'. Загружаем данные из кэша.")
        return load_from_cache(cache_filename)
    
    # Если кэш недействителен или отсутствует, запускаем паука
    logger.info(f"Кэш для запроса '{search_query}' отсутствует или недействителен. Запускаем паука.")
    results = await spider_runner.run_spider(search_query)
    
    # Сохраняем результаты в кэш
    if results:
        save_to_cache(cache_filename, results)
    
    return results

def save_to_csv(items, filename):
    """
    Сохраняет список словарей в CSV-файл.
    """
    if not items:
        logger.warning(f"Нет данных для сохранения в {filename}.")
        return

    keys = items[0].keys()
    with open(filename, 'w', newline='', encoding='utf-8') as output_file:
        dict_writer = csv.DictWriter(output_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(items)
    logger.info(f"Данные сохранены в {filename}.")