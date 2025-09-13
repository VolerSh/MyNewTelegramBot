import logging
import sys

def setup_logging():
    """
    Настраивает конфигурацию логирования для проекта с явным указанием кодировки UTF-8.
    """
    # Получаем корневой логгер
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    # Убираем все существующие обработчики, чтобы избежать дублирования
    if root_logger.hasHandlers():
        root_logger.handlers.clear()

    # Создаем форматтер
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

    # Создаем и настраиваем обработчик для файла
    file_handler = logging.FileHandler("bot.log", encoding='utf-8')
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)

    # Создаем и настраиваем обработчик для консоли
    # Оборачиваем sys.stdout для явного указания кодировки
    stream_handler = logging.StreamHandler(stream=sys.stdout)
    stream_handler.setLevel(logging.INFO)
    stream_handler.setFormatter(formatter)
    
    # Добавляем обработчики к корневому логгеру
    root_logger.addHandler(file_handler)
    root_logger.addHandler(stream_handler)

    # Устанавливаем уровень логирования для сторонних библиотек повыше, чтобы избежать спама
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("google.api_core").setLevel(logging.WARNING)
    
    print("Logging configured successfully with UTF-8 encoding for all handlers.")