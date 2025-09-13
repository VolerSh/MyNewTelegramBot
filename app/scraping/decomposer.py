import re
import logging
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)

class LaptopDecomposer:
    """
    Класс для декомпозиции данных о ноутбуках на отдельные параметры.
    """
    
    def __init__(self):
        # Упрощенные регулярные выражения для извлечения параметров
        self.patterns = {
            'brand': re.compile(r'\b(Lenovo|HP|Dell|Asus|Acer|MSI|Apple|Samsung|Huawei|Xiaomi|Google|Microsoft|Razer|LG)\b', re.IGNORECASE),
            'series': re.compile(r'\b(ThinkPad|ThinkBook|IdeaPad|Yoga|Legion|Ideapad|V系列|Flex|Chromebook|YOGA|LOQ|Pavilion|Spectre|Envy|EliteBook|ProBook|ZBook|Omen|Inspiron|XPS|Alienware|Vostro|Latitude|G|ROG|TUF|VivoBook|ZenBook|AsusPro|Chromebook|Predator|Nitro|Swift|TravelMate|Extensa|Aspire|Spin|ConceptD|Blade|Stealth|Katana|Creator|Modern|Prestige|Megaport|Surface|Pixelbook|Chromebox|MacBook|Mac|iPad|Pro|Air|Studio|Book|Gram|Ultra|Chromebook|MateBook|MediaPad|Honor|MagicBook|RedmiBook|Mi)\b', re.IGNORECASE),
            'diagonal': re.compile(r'(\d{1,2}(\.\d{1,2})?)["”\'’″]', re.IGNORECASE),
            'cpu_line': re.compile(r'\b(Intel|AMD|Apple|Qualcomm|ARM|MediaTek|NVIDIA|Samsung|Snapdragon|Exynos|Kirin|Dimensity|Core|Celeron|Pentium|Xeon|Atom|Ryzen|Athlon|Turion|Sempron|Phenom|Opteron|EPYC|Threadripper|APU)\b', re.IGNORECASE),
            'cpu_model': re.compile(r'\b([A-Z]\d{3,5}|i\d-\d{4,5}|R\d{3,5}U?|U\d{3,5}|H\d{3,5}|HX\d{3,5}|G\d{3,5}|M\d{3,5}|N\d{3,5}|Celeron|Pentium|Xeon|Atom|Athlon|Turion|Sempron|Phenom|Opteron|EPYC|Threadripper)\b', re.IGNORECASE),
            'memory': re.compile(r'(\d{1,3})\s*(GB|ГБ|Гб|Gb|gb)', re.IGNORECASE),
            'storage_type': re.compile(r'\b(SSD|HDD|eMMC|NVMe|SATA|M\.2)\b', re.IGNORECASE),
            'storage_capacity': re.compile(r'(\d{1,4})\s*(GB|TB|ГБ|Гб|Gb|gb|ТБ|Тб|Tb|tb)', re.IGNORECASE),
            'gpu_brand': re.compile(r'\b(NVIDIA|AMD|Intel|GeForce|RTX|GTX|Radeon|Iris|UHD|HD|Iris|Arc)\b', re.IGNORECASE),
            'gpu_model': re.compile(r'\b(RTX|GTX|RTX\d{3,4}|GTX\d{3,4}|MX\d{3,4}|Quadro|Tesla|A\d{3,4}|R\d{3,4}|Radeon|Vega|Instinct|FirePro|FireGL|FireMV|FireStream|Stream|Pro|Mobility|Mobile|Discrete|Integrated|Graphics|GPU)\b', re.IGNORECASE),
            'gpu_memory': re.compile(r'(\d{1,2})\s*(GB|ГБ|Гб|Gb|gb)', re.IGNORECASE),
        }
        
        # Словарь для преобразования числовых обозначений в слова
        self.number_words = {
            '13': 'тринадцати',
            '14': 'четырнадцати',
            '15': 'пятнадцати',
            '16': 'шестнадцати',
            '17': 'семнадцати'
        }

    def extract_price_numeric(self, price_str) -> int:
        """
        Извлекает числовое значение цены из строки или числа.
        
        Args:
            price_str: Строка или число с ценой
            
        Returns:
            int: Числовое значение цены или 0, если не удалось извлечь
        """
        # Если цена уже является числом, возвращаем её как есть
        if isinstance(price_str, (int, float)):
            return int(price_str)
            
        # Если цена не является строкой, возвращаем 0
        if not isinstance(price_str, str):
            return 0
            
        if not price_str:
            return 0
            
        # Удаляем все символы кроме цифр
        numeric_part = re.sub(r'[^\d]', '', price_str)
        
        # Преобразуем в число
        try:
            return int(numeric_part) if numeric_part else 0
        except ValueError:
            return 0

    def extract_brand(self, title: str) -> str:
        """Извлекает бренд из названия."""
        match = self.patterns['brand'].search(title)
        return match.group(1).strip() if match else ''
    
    def extract_series(self, title: str) -> str:
        """Извлекает серию из названия."""
        match = self.patterns['series'].search(title)
        return match.group(1).strip() if match else ''
    
    def extract_diagonal(self, title: str) -> str:
        """Извлекает диагональ экрана из названия."""
        match = self.patterns['diagonal'].search(title)
        return match.group(1).strip() if match else ''
    
    def extract_cpu_line(self, title: str) -> str:
        """Извлекает линейку процессора из названия."""
        match = self.patterns['cpu_line'].search(title)
        return match.group(1).strip() if match else ''
    
    def extract_cpu_model(self, title: str) -> str:
        """Извлекает модель процессора из названия."""
        match = self.patterns['cpu_model'].search(title)
        return match.group(0).strip() if match else ''
    
    def extract_memory(self, title: str) -> str:
        """Извлекает объем оперативной памяти из названия."""
        match = self.patterns['memory'].search(title)
        return match.group(1).strip() if match else ''
    
    def extract_storage_type(self, title: str) -> str:
        """Извлекает тип накопителя из названия."""
        match = self.patterns['storage_type'].search(title)
        return match.group(1).strip() if match else ''
    
    def extract_storage_capacity(self, title: str) -> str:
        """Извлекает объем накопителя из названия."""
        match = self.patterns['storage_capacity'].search(title)
        return match.group(1).strip() if match else ''
    
    def extract_gpu_brand(self, title: str) -> str:
        """Извлекает бренд видеокарты из названия."""
        match = self.patterns['gpu_brand'].search(title)
        return match.group(1).strip() if match else ''
    
    def extract_gpu_model(self, title: str) -> str:
        """Извлекает модель видеокарты из названия."""
        match = self.patterns['gpu_model'].search(title)
        return match.group(0).strip() if match else ''
    
    def extract_gpu_memory(self, title: str) -> str:
        """Извлекает объем видеопамяти из названия."""
        match = self.patterns['gpu_memory'].search(title)
        return match.group(1).strip() if match else ''
    
    def decompose_laptop(self, title: str, price_str: str = '') -> Dict[str, str]:
        """
        Декомпозиция названия ноутбука на отдельные параметры.
        
        Args:
            title (str): Название ноутбука
            price_str (str): Строка с ценой (опционально)
            
        Returns:
            Dict[str, str]: Словарь с параметрами ноутбука
        """
        # Извлекаем все параметры
        brand = self.extract_brand(title)
        series = self.extract_series(title)
        diagonal = self.extract_diagonal(title)
        cpu_line = self.extract_cpu_line(title)
        cpu_model = self.extract_cpu_model(title)
        memory = self.extract_memory(title)
        storage_type = self.extract_storage_type(title)
        storage_capacity = self.extract_storage_capacity(title)
        gpu_brand = self.extract_gpu_brand(title)
        gpu_model = self.extract_gpu_model(title)
        gpu_memory = self.extract_gpu_memory(title)
        price_numeric = self.extract_price_numeric(price_str)
        
        # Возвращаем словарь с параметрами
        return {
            'full_title': title,
            'brand': brand,
            'series': series,
            'diagonal': diagonal,
            'cpu_line': cpu_line,
            'cpu_model': cpu_model,
            'memory': memory,
            'storage_type': storage_type,
            'storage_capacity': storage_capacity,
            'gpu_brand': gpu_brand,
            'gpu_model': gpu_model,
            'gpu_memory': gpu_memory,
            'price_numeric': str(price_numeric)
        }
    
    def decompose_all_laptops(self, laptops: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Декомпозиция списка ноутбуков.
        
        Args:
            laptops (List[Dict[str, Any]]): Список ноутбуков с данными
            
        Returns:
            List[Dict[str, Any]]: Список ноутбуков с декомпозированными данными
        """
        decomposed_laptops = []
        
        for laptop in laptops:
            # Получаем название ноутбука и цену
            title = laptop.get('title', '')
            price_str = laptop.get('price', '')
            
            # Декомпозиция названия и цены
            decomposed_data = self.decompose_laptop(title, price_str)
            
            # Объединяем исходные данные с декомпозированными
            result = {**laptop, **decomposed_data}
            decomposed_laptops.append(result)
        
        return decomposed_laptops
    
    def test_decomposition(self):
        """
        Тестирование функциональности декомпозиции на примерах.
        """
        test_cases = [
            "Ноутбук Lenovo ThinkBook 16, Ryzen AI 9 365, 16\" 3.2k/165hz, 32Гб/1Тб, RTX4060, Win 11 Home, Серый [21J504J9RK]",
            "Lenovo IdeaPad Slim 5, Intel Core i5-12450H, 16\" FHD, 16Гб, 512Гб SSD, Intel UHD Graphics, Win 11 Home, Серебристый [82XF009FRK]",
            "ASUS VivoBook 15, AMD Ryzen 5 5500U, 15.6\" FHD, 8Гб, 256Гб SSD, Radeon Graphics, Win 11, Синий [M515DA-BQ566]",
            "HP Pavilion 14, Intel Core i3-1125G4, 14\" FHD, 8Гб, 256Гб SSD, Intel UHD Graphics, Win 11 Home, Серебристый [14-dv0028nw]"
        ]
        
        print("Тестирование декомпозиции названий ноутбуков:")
        print("=" * 50)
        
        for i, title in enumerate(test_cases, 1):
            print(f"\nТест {i}:")
            print(f"Название: {title}")
            
            # Декомпозиция
            result = self.decompose_laptop(title)
            
            # Вывод результатов
            print("Результаты декомпозиции:")
            for key, value in result.items():
                if key != 'full_title':  # Не выводим полное название дважды
                    print(f"  {key}: {value}")
            print("-" * 30)