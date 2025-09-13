import scrapy
from scrapy_playwright.page import PageMethod
from ..items import ProductItem

class YandexMarketSpider(scrapy.Spider):
    name = 'yandex_market'
    allowed_domains = ['market.yandex.ru']

    def start_requests(self):
        # URL для выборки из каталога
        catalog_url = "https://market.yandex.ru/catalog--noutbuki/26895412/list?hid=91013"
        yield scrapy.Request(
            url=catalog_url,
            meta={
                "playwright": True,
                "playwright_page_methods": [
                    PageMethod("wait_for_selector", "article[data-auto='searchOrganic']"),
                ],
                "source": "catalog"
            },
            callback=self.parse
        )
        
        # URL для выборки через поиск
        search_url = "https://market.yandex.ru/search?text=ноутбуки%20lenovo&hid=91013"
        yield scrapy.Request(
            url=search_url,
            meta={
                "playwright": True,
                "playwright_page_methods": [
                    PageMethod("wait_for_selector", "article[data-auto='searchOrganic']"),
                ],
                "source": "search"
            },
            callback=self.parse
        )

    async def parse(self, response):
        source = response.meta['source']
        page_number = response.meta.get('page_number', 1)
        self.log(f"Парсим страницу {page_number} для источника '{source}': {response.url}")

        # Извлекаем данные с текущей страницы
        products = response.css('article[data-auto="searchOrganic"]')
        if not products:
            self.log(f"Товары не найдены на странице {page_number}. Завершаем парсинг для источника '{source}'.")
            return
            
        for product in products:
            item = ProductItem()
            item['title'] = product.css('span[data-auto="snippet-title"]::attr(title)').get(default='').strip()
            price_text = product.css('span[data-auto="snippet-price-current"] span::text').get()
            item['price'] = ''.join(filter(str.isdigit, price_text)) if price_text else '0'
            link = product.css('a[data-auto="snippet-image"]::attr(href)').get()
            item['link'] = response.urljoin(link) if link else 'N/A'
            item['source'] = source
            yield item

        # Пагинация с помощью response.follow и сохранением meta Playwright
        next_page_url = response.css('a[data-auto="pagination-next"]::attr(href)').get()

        if next_page_url:
            next_page_number = page_number + 1
            self.log(f"Найдена следующая страница ({next_page_number}) для источника '{source}'")
            yield response.follow(
                url=next_page_url,
                callback=self.parse,
                meta={
                    "playwright": True,
                    "playwright_page_methods": [
                        PageMethod("wait_for_selector", "article[data-auto='searchOrganic']"),
                    ],
                    "source": source,
                    "page_number": next_page_number
                }
            )
        else:
            self.log(f"Больше страниц для источника '{source}' не найдено или достигнут лимит в 5 страниц.")