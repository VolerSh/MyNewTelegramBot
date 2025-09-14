import scrapy
from scrapy.http import HtmlResponse
from scrapy_playwright.page import PageMethod
from ..items import BrandItem
import asyncio

class FilterSpider(scrapy.Spider):
    name = 'filter_spider'
    allowed_domains = ['market.yandex.ru']

    # Стартуем на странице со всеми фильтрами. Этот URL используется для всех версий.
    start_urls = ["https://market.yandex.ru/catalog--noutbuki/26895412/list-filters"]

    def start_requests(self):
        """
        Запускает начальный запрос к странице фильтров.
        Чтобы выбрать нужную версию, закомментируйте две другие и раскомментируйте одну.
        """
        for url in self.start_urls:
            # --- ВЕРСИЯ 1 (закомментирована): Просто загрузка страницы (собирает ~5 брендов) ---
            # self.log("ЗАПУСК ВЕРСИИ 1: Просто загрузка страницы.")
            # yield scrapy.Request(
            #     url,
            #     meta={"playwright": True}, 
            #     callback=self.parse_brands
            # )

            # --- ВЕРСИЯ 2 (закомментирована): Клик + ожидание (собирает ~29 брендов) ---
            # self.log("ЗАПУСК ВЕРСИИ 2: Клик + ожидание.")
            # yield scrapy.Request(
            #      url,
            #      meta={
            #          "playwright": True,
            #          "playwright_page_methods": [
            #              # Шаг 1: Находим кнопку "показать все", у которой список свернут (aria-expanded="false"), и кликаем.
            #              PageMethod("click", selector='div[data-filter-id="7893318"] button[aria-expanded="false"]'),
            #              # Шаг 2: Ждем, пока на странице не появится эта же кнопка, но уже с атрибутом "развернуто" (aria-expanded="true").
            #              PageMethod("wait_for_selector", 'div[data-filter-id="7893318"] button[aria-expanded="true"]')
            #          ],
            #      },
            #      callback=self.parse_brands)
            
            # --- ВЕРСИЯ 3 (АКТИВНАЯ): Клик + ожидание + скроллинг ---
            self.log("ЗАПУСК ВЕРСИИ 3: Клик + ожидание + скроллинг.")
            yield scrapy.Request(
                url,
                meta={"playwright": True, "playwright_include_page": True, "errback": self.errback},
                callback=self.parse_and_scroll
            )

    # --- КОД ДЛЯ ВЕРСИИ 3 ---
    async def parse_and_scroll(self, response):
        """
        CALLBACK ДЛЯ ВЕРСИИ 3.
        Управляет страницей: кликает, ждет, скроллит и затем вызывает parse_brands.
        """
        page = response.meta["playwright_page"]
        self.log(f"Загружена страница '{await page.title()}'. Начинаем манипуляции в parse_and_scroll.")
        try:
            # Шаг 1: Делаем скриншот до каких-либо действий
            await page.screenshot(path="before_click.png")
            self.log("Сделан скриншот 'before_click.png'.")

            # Шаг 2: Кликнуть на кнопку "показать все"
            show_all_button_selector = 'div[data-filter-id="7893318"] button[aria-expanded="false"]'
            self.log(f"Ищем кнопку 'показать все' по селектору: {show_all_button_selector}")
            await page.click(show_all_button_selector, timeout=5000)
            self.log("Кнопка 'показать все' нажата.")

            # Шаг 3: Дождаться, пока список раскроется
            expanded_button_selector = 'div[data-filter-id="7893318"] button[aria-expanded="true"]'
            await page.wait_for_selector(expanded_button_selector, timeout=5000)
            self.log("Список брендов раскрыт.")

            # Шаг 4: Делаем скриншот после клика
            await page.screenshot(path="after_click.png")
            self.log("Сделан скриншот 'after_click.png'.")
            
            # Шаг 5: Получаем HTML после клика и передаем его в парсер
            self.log("Получаем HTML после клика и передаем в parse_brands.")
            final_html = await page.content()
            
            new_response = HtmlResponse(
                url=page.url,
                body=final_html,
                encoding='utf-8',
                request=response.request
            )
            
            async for item in self.parse_brands(new_response):
                yield item

        except Exception as e:
            self.log(f"Произошла ошибка в parse_and_scroll: {e}")
        finally:
            self.log("Закрываем страницу Playwright в parse_and_scroll.")
            await page.close()

    async def parse_brands(self, response):
        """
        УНИВЕРСАЛЬНЫЙ ПАРСЕР.
        Вызывается Версией 1 и Версией 2. Просто парсит то, что есть на странице.
        """
        self.log(f"Парсим бренды со страницы: {response.url}")

        brand_filter_container = response.css('div[data-auto="filter"][data-filter-id="7893318"]')
        if brand_filter_container:
            brand_elements = brand_filter_container.css('label[data-auto^="filter-list-item-"]')
            self.log(f"ИТОГО найдено {len(brand_elements)} брендов.")
            
            for brand_element in brand_elements:
                brand_name = brand_element.css('span._1-LFf._2KcG8::text').get()
                if brand_name:
                    item = BrandItem()
                    item['brand'] = brand_name.strip()
                    yield item
        else:
            self.log("Контейнер фильтра 'Бренд' не найден")

    async def errback(self, failure):
        self.log(f"Playwright-запрос провалился: {failure.value}")
        page = failure.request.meta.get("playwright_page")
        if page:
            await page.close()