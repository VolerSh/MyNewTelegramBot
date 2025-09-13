# Этот файл содержит функции для обработки данных
# Перенесено из app/telegram_bot/handlers.py

def filter_and_sort_results(items, keywords, exclude_keywords=None):
    """Фильтрует и сортирует список товаров по заданным ключевым словам."""
    filtered = []
    for item in items:
        title_lower = item.get('title', '').lower()
        # Проверяем, что все ключевые слова есть в названии
        if all(k in title_lower for k in keywords):
            # Если есть слова для исключения, проверяем, что их нет
            if exclude_keywords and any(ex_k in title_lower for ex_k in exclude_keywords):
                continue
            filtered.append(item)
    return sorted(filtered, key=lambda x: x['price'])[:3]