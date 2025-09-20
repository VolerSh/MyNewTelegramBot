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
        self.log(f"Загружена страница '{await page.title()}'. Начинаем манипуляции.")
        
        all_brands = set()

        try:
            # Шаг 1: Кликнуть на кнопку "показать все"
            show_all_button_selector = 'div[data-filter-id="7893318"] button[aria-expanded="false"]'
            await page.click(show_all_button_selector, timeout=5000)
            self.log("Кнопка 'показать все' нажата.")
            await page.wait_for_selector('div[data-test-id="virtuoso-scroller"]', timeout=5000)
            self.log("Список брендов раскрыт, virtuoso-scroller появился.")

            # Шаг 2: Скроллинг и парсинг на лету
            scroll_container_selector = 'div[data-test-id="virtuoso-scroller"]'
            scrolls_without_new_brands = 0
            max_scrolls_without_new = 3  # Количество "пустых" прокруток для завершения

            while True:
                brands_before = len(all_brands)

                # Парсим видимые бренды
                current_html = await page.content()
                temp_response = HtmlResponse(url=page.url, body=current_html, encoding='utf-8')
                newly_found_brands = await self.parse_brands(temp_response)
                all_brands.update(newly_found_brands)
                
                brands_after = len(all_brands)
                new_brands_count = brands_after - brands_before

                self.log(f"Найдено {len(newly_found_brands)} на экране. Добавлено {new_brands_count} новых. Всего: {brands_after}.")

                # Проверяем, были ли найдены новые бренды
                if new_brands_count == 0:
                    scrolls_without_new_brands += 1
                    self.log(f"Новых брендов не найдено. Счетчик 'пустых' прокруток: {scrolls_without_new_brands}.")
                else:
                    scrolls_without_new_brands = 0  # Сбрасываем счетчик, если что-то нашли

                # Условие выхода из цикла
                if scrolls_without_new_brands >= max_scrolls_without_new:
                    self.log(f"После {max_scrolls_without_new} прокруток без новых брендов завершаем скроллинг.")
                    break

                # Прокручиваем контейнер
                await page.evaluate(f'''
                    const container = document.querySelector('{scroll_container_selector}');
                    if (container) {{ container.scrollTop += container.clientHeight; }}
                ''')
                await asyncio.sleep(1.5) # Немного увеличим паузу для надежности
            
            self.log(f"Скроллинг завершен. Всего собрано {len(all_brands)} уникальных брендов.")

            # Шаг 3: Генерируем BrandItem из собранного набора
            for brand_name in sorted(list(all_brands)):
                item = BrandItem()
                item['brand'] = brand_name
                yield item

        except Exception as e:
            self.log(f"Произошла ошибка в parse_and_scroll: {e}")
        finally:
            self.log("Закрываем страницу Playwright.")
            await page.close()

    async def parse_brands(self, response):
        """
        УНИВЕРСАЛЬНЫЙ ПАРСЕР.
        Вызывается Версией 1 и Версией 2. Просто парсит то, что есть на странице.
        """
        self.log(f"Парсим бренды со страницы: {response.url}")
        
        # Находим контейнер фильтра "Бренд"
        brand_filter_container = response.css('div[data-auto="filter"][data-filter-id="7893318"]')
        
        found_brands = set()
        if brand_filter_container:
            # Ищем элементы брендов только внутри этого контейнера, используя более специфичный селектор
            # Селектор: ищем span с классами _1-LFf и _2KcG8, который содержит текст бренда.
            # Этот span находится внутри label, который имеет data-auto="filter-list-item-..."
            # И все это находится внутри virtuoso-item-list, который содержит сами элементы списка.
            brand_elements = brand_filter_container.css('div[data-test-id="virtuoso-item-list"] label[data-auto^="filter-list-item-"] span._1-LFf._2KcG8::text')
            self.log(f"Найдено {len(brand_elements)} текстовых элементов брендов на текущем экране.")
            
            for brand_name in brand_elements.getall():
                found_brands.add(brand_name.strip())
        else:
            self.log("Контейнер фильтра 'Бренд' не найден.")
        
        return found_brands

    async def errback(self, failure):
        self.log(f"Playwright-запрос провалился: {failure.value}")
        page = failure.request.meta.get("playwright_page")
        if page:
            await page.close()