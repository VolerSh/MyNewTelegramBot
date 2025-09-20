import scrapy
from scrapy.http import HtmlResponse
from scrapy_playwright.page import PageMethod
from ..items import BrandItem
import asyncio

class FilterSpider(scrapy.Spider):
    name = 'filter_spider'
    allowed_domains = ['market.yandex.ru']

    def __init__(self, *args, **kwargs):
        super(FilterSpider, self).__init__(*args, **kwargs)
        self.successful_sleeps = {}

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
            
            initial_sleep_time = 0.0001 # Начальная пауза
            max_sleep_time = 1.0     # Максимальная пауза
            sleep_increase_factor = 10 # Коэффициент увеличения паузы
            current_sleep_time = initial_sleep_time

            while True:
                brands_before = len(all_brands)

                # Парсим видимые бренды напрямую через Playwright API
                newly_found_brands = await self.parse_brands(page)
                all_brands.update(newly_found_brands)
                
                brands_after = len(all_brands)
                new_brands_count = brands_after - brands_before

                self.log(f"Найдено {len(newly_found_brands)} на экране. Добавлено {new_brands_count} новых. Всего: {brands_after}.")

                # Проверяем, были ли найдены новые бренды
                if new_brands_count == 0:
                    scrolls_without_new_brands += 1
                    self.log(f"Новых брендов не найдено. Счетчик 'пустых' прокруток: {scrolls_without_new_brands}.")
                    # Увеличиваем паузу, если новые бренды не найдены, но не превышаем максимум
                    if current_sleep_time < max_sleep_time:
                        current_sleep_time = min(current_sleep_time * sleep_increase_factor, max_sleep_time)
                        self.log(f"Увеличиваем паузу до {current_sleep_time:.2f} сек.")
                else:
                    scrolls_without_new_brands = 0  # Сбрасываем счетчик, если что-то нашли
                    # Записываем статистику успешной паузы
                    sleep_key = f"{current_sleep_time:.2f}"
                    self.successful_sleeps[sleep_key] = self.successful_sleeps.get(sleep_key, 0) + 1
                    current_sleep_time = initial_sleep_time # Сбрасываем паузу до начального значения
                    self.log(f"Новые бренды найдены. Сбрасываем паузу до {current_sleep_time:.2f} сек.")

                # Условие выхода из цикла:
                # Завершаем, если достигнуто max_scrolls_without_new "пустых" прокруток
                # И текущая пауза достигла максимального значения (чтобы дать сайту время на загрузку)
                if scrolls_without_new_brands >= max_scrolls_without_new and current_sleep_time >= max_sleep_time:
                    self.log(f"После {max_scrolls_without_new} прокруток без новых брендов и при максимальной паузе завершаем скроллинг.")
                    break

                # Прокручиваем контейнер трижды за итерацию
                scroll_count = 3 # Количество прокруток за один раз
                await page.evaluate(f'''
                    const container = document.querySelector('{scroll_container_selector}');
                    if (container) {{
                        for (let i = 0; i < {scroll_count}; i++) {{
                            container.scrollTop += container.clientHeight;
                        }}
                    }}
                ''')
                await asyncio.sleep(current_sleep_time) # Пауза после всех прокруток
            
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

    async def parse_brands(self, page):
        """
        ПАРСЕР, РАБОТАЮЩИЙ НАПРЯМУЮ С PLAYWRIGHT.
        Извлекает текст брендов, используя page.locator.
        """
        self.log(f"Парсим бренды напрямую со страницы: {page.url}")
        
        # Селектор для текстовых элементов брендов
        brand_selector = 'div[data-filter-id="7893318"] div[data-test-id="virtuoso-item-list"] label[data-auto^="filter-list-item-"] span._1-LFf._2KcG8'
        
        try:
            # Находим все элементы, соответствующие селектору
            brand_elements = await page.locator(brand_selector).all_inner_texts()
            self.log(f"Найдено {len(brand_elements)} текстовых элементов брендов на текущем экране.")
            
            # Очищаем и добавляем в set
            found_brands = {name.strip() for name in brand_elements}
            return found_brands
            
        except Exception as e:
            self.log(f"Ошибка при парсинге брендов через Playwright: {e}")
            return set()

    def close(self, reason):
        self.log("Паук завершает работу.")
        if self.successful_sleeps:
            self.log("Статистика по успешным паузам (время в сек.: кол-во успешных находок):")
            sorted_sleeps = sorted(self.successful_sleeps.items(), key=lambda item: float(item[0]))
            for sleep_time, count in sorted_sleeps:
                self.log(f"- {sleep_time}: {count} раз")
        else:
            self.log("Статистика по успешным паузам не собрана.")

    async def errback(self, failure):
        self.log(f"Playwright-запрос провалился: {failure.value}")
        page = failure.request.meta.get("playwright_page")
        if page:
            await page.close()