import logging
import sys

def setup_logging():
    """
    Настраивает базовую конфигурацию логирования для проекта.
    """
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        handlers=[
            logging.FileHandler("bot.log"), # Логирование в файл
            logging.StreamHandler(sys.stdout) # Логирование в консоль
        ]
    )
    # Устанавливаем уровень логирования для сторонних библиотек повыше, чтобы избежать спама
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("google.api_core").setLevel(logging.WARNING)

    print("Logging configured successfully.")