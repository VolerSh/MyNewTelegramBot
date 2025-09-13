# Этот файл содержит функции для работы с базой данных
# Перенесено из app/telegram_bot/handlers.py

import logging
from ..database.database import init_db, SessionLocal
from ..database.models import Product

logger = logging.getLogger(__name__)

def save_products_to_db(products):
    """
    Сохраняет список продуктов в базу данных.
    """
    # Инициализируем базу данных
    init_db()
    
    # Создаем сессию
    db = SessionLocal()
    
    try:
        for product_data in products:
            # Проверяем, существует ли уже продукт с таким URL
            existing_product = db.query(Product).filter(Product.url == product_data.get('link', '')).first()
            
            if existing_product:
                # Если продукт существует, обновляем его данные
                existing_product.name = product_data.get('title', '')
                existing_product.price = float(product_data.get('price', 0) or 0)
                logger.info(f"Обновлен продукт: {existing_product.name}")
            else:
                # Если продукт не существует, создаем новый
                new_product = Product(
                    name=product_data.get('title', ''),
                    price=float(product_data.get('price', 0) or 0),
                    url=product_data.get('link', ''),
                    marketplace='Yandex Market'
                )
                db.add(new_product)
                logger.info(f"Добавлен новый продукт: {new_product.name}")
        
        # Сохраняем изменения
        db.commit()
        logger.info(f"Сохранено {len(products)} продуктов в базу данных.")
        
    except Exception as e:
        logger.error(f"Ошибка при сохранении продуктов в базу данных: {e}", exc_info=True)
        db.rollback()
    finally:
        db.close()