import csv
import os
from .items import ProductItem, BrandItem

class SaveToCsvPipeline:
    """
    Pipeline для сохранения данных в разные CSV файлы в зависимости от источника.
    """
    def open_spider(self, spider):
        """
        Вызывается при открытии паука.
        Инициализирует файлы для записи.
        """
        self.results_dir = 'results'
        self.dictionaries_dir = os.path.join(self.results_dir, 'dictionaries')
        os.makedirs(self.dictionaries_dir, exist_ok=True)
        
        # Файл для результатов из каталога
        self.catalog_file = open(os.path.join(self.results_dir, 'catalog_results.csv'), 'w', newline='', encoding='utf-8')
        self.catalog_writer = csv.writer(self.catalog_file)
        self.catalog_writer.writerow(['title', 'price', 'link'])

        # Файл для результатов из поиска
        self.search_file = open(os.path.join(self.results_dir, 'search_results.csv'), 'w', newline='', encoding='utf-8')
        self.search_writer = csv.writer(self.search_file)
        self.search_writer.writerow(['title', 'price', 'link'])

        # Файл для брендов
        self.brands_file = open(os.path.join(self.dictionaries_dir, 'brands.csv'), 'w', newline='', encoding='utf-8')
        self.brands_writer = csv.writer(self.brands_file)
        self.brands_writer.writerow(['brand'])

    def close_spider(self, spider):
        """
        Вызывается при закрытии паука.
        Закрывает оба файла.
        """
        self.catalog_file.close()
        self.search_file.close()
        self.brands_file.close()

    async def process_item(self, item, spider):
        """
        Вызывается для каждого item, полученного от паука.
        Распределяет item по файлам в зависимости от источника.
        """
        if isinstance(item, ProductItem):
            source = item.get('source')
            line = [item.get('title'), item.get('price'), item.get('link')]
            if source == 'catalog':
                self.catalog_writer.writerow(line)
            elif source == 'search':
                self.search_writer.writerow(line)
        elif isinstance(item, BrandItem):
            self.brands_writer.writerow([item.get('brand')])
        
        return item