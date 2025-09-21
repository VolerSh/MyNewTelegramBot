# -*- coding: utf-8 -*-
import scrapy
from scrapy_playwright.page import PageMethod
from ..items import FilterInfoItem
import asyncio
import logging
import os
import json

class StructureSpider(scrapy.Spider):
    """
    Этот паук предназначен для анализа структуры страницы фильтров на Яндекс.Маркете.
    Его задача - не собирать значения конкретных фильтров (как filter_spider),
    а составить карту всех доступных фильтров: их названия и технические ID.
    """
    name = 'structure_spider'
    allowed_domains = ['market.yandex.ru']

    # URL страницы, на которой находятся все фильтры
    start_urls = ["https://market.yandex.ru/catalog--noutbuki/26895412/list-filters"]

    def start_requests(self):
        """
        Запускает начальный запрос к странице.
        Мы используем Playwright, чтобы страница полностью загрузилась со всем динамическим контентом.
        """
        self.log("ЗАПУСК: Анализ структуры фильтров.")
        for url in self.start_urls:
            yield scrapy.Request(
                url,
                meta={
                    "playwright": True,
                    "playwright_include_page": True, # Дает нам доступ к объекту страницы Playwright
                    "errback": self.errback
                },
                callback=self.parse_structure
            )

    async def parse_structure(self, response):
        """
        Основной метод для парсинга структуры фильтров.
        Извлекает ID, название и тип для каждого фильтра на странице.
        """
        page = response.meta["playwright_page"]
        self.log(f"Страница '{await page.title()}' загружена. Начинаем анализ структуры.")

        # Шаг 1: Найти все контейнеры фильтров по общему атрибуту.
        # Это самый надежный способ, так как он не зависит от тегов.
        filter_containers_selector = "div[data-filter-id]"
        filter_containers = await page.locator(filter_containers_selector).all()
        self.log(f"Найдено {len(filter_containers)} потенциальных контейнеров фильтров.")

        if not filter_containers:
            self.log("Контейнеры фильтров не найдены. Проверьте селектор.", level=logging.WARNING)
            await page.close()
            return

        # Шаг 2: Обработать каждый контейнер.
        for container in filter_containers:
            try:
                # Извлекаем тип фильтра. Это поможет нам понять, как с ним работать.
                filter_type = await container.get_attribute('data-filter-type')

                # Всю остальную информацию берем из data-zone-data, где она в удобном JSON-формате.
                zone_data_element = container.locator('> div[data-zone-data]')
                if not zone_data_element:
                    self.log("Не найден элемент с data-zone-data, пропускаем.", level=logging.INFO)
                    continue
                
                zone_data_str = await zone_data_element.get_attribute('data-zone-data')
                zone_data = json.loads(zone_data_str)

                filter_id = zone_data.get('filterId')
                filter_name = zone_data.get('filterName')

                # Если у нас есть все три компонента, создаем и возвращаем Item.
                if filter_id and filter_name and filter_type:
                    item = FilterInfoItem()
                    item['filter_id'] = filter_id
                    item['filter_name'] = filter_name
                    item['filter_type'] = filter_type
                    
                    self.log(f"Найден фильтр: ID='{filter_id}', Имя='{filter_name}', Тип='{filter_type}'")
                    yield item
                else:
                    self.log(f"Пропущен блок: не удалось извлечь все данные (id={filter_id}, name={filter_name}, type={filter_type})", level=logging.INFO)

            except Exception as e:
                self.log(f"Ошибка при обработке контейнера: {e}", level=logging.ERROR)

        # В конце обязательно закрываем страницу
        await page.close()
        self.log("Страница Playwright закрыта.")

    async def errback(self, failure):
        """
        Обработчик ошибок для Playwright запросов.
        """
        self.log(f"Playwright-запрос провалился: {failure.value}", level=logging.ERROR)
        page = failure.request.meta.get("playwright_page")
        if page:
            await page.close()

    def close(self, reason):
        """
        Вызывается при завершении работы паука.
        """
        self.log(f"Паук {self.name} завершил работу. Причина: {reason}")