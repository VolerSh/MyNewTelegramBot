import scrapy

class ProductItem(scrapy.Item):
    """
    Элемент данных для хранения информации о продукте.
    """
    title = scrapy.Field()
    price = scrapy.Field()
    link = scrapy.Field()
    source = scrapy.Field()

class BrandItem(scrapy.Item):
    """
    Элемент данных для хранения названия бренда.
    """
    brand = scrapy.Field()

class FilterInfoItem(scrapy.Item):
    """
    Элемент данных для хранения мета-информации о фильтре.
    """
    filter_name = scrapy.Field()
    filter_id = scrapy.Field()
    filter_type = scrapy.Field()