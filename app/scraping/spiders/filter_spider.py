import scrapy
from scrapy_playwright.page import PageMethod
from ..items import BrandItem

class FilterSpider(scrapy.Spider):
    name = 'filter_spider'
    allowed_domains = ['market.yandex.ru']

    def start_requests(self):
        """
        Определяет начальные URL для получения справочников.
        """
        # URL для получения списка брендов
        brands_url = "https://market.yandex.ru/catalog--noutbuki/26895412/list?hid=91013"
        
        yield scrapy.Request(
            url=brands_url,
            meta={
                "playwright": True,
                "playwright_page_methods": [
                    PageMethod("wait_for_selector", "article[data-auto='searchOrganic']"),
                ],
            },
            callback=self.parse_brands
        )

    async def parse_brands(self, response):
        """
        Парсит бренды с указанной страницы.
        """
        self.log(f"Парсим бренды: {response.url}")
        
        # Извлекаем данные о брендах
        # Сначала находим контейнер фильтра "Бренд"
        brand_filter_container = response.css('div[data-auto="filter"][data-filter-id="7893318"]')
        
        if brand_filter_container:
            # Затем находим все элементы брендов внутри этого контейнера
            brand_elements = brand_filter_container.css('label[data-auto^="filter-list-item-"]')
            
            for brand_element in brand_elements:
                brand_name = brand_element.css('span._1-LFf._2KcG8::text').get()
                if brand_name:
                    item = BrandItem()
                    item['brand'] = brand_name.strip()
                    yield item
        else:
            self.log("Контейнер фильтра 'Бренд' не найден")
                
    def parse_other_filters(self, response):
        """
        Заглушка для парсинга других фильтров.
        """
        pass