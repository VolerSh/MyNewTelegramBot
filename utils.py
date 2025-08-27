import os

def read_token(file_path):
    """Читает токен из файла."""
    if not os.path.exists(file_path):
        print(f"ОШИБКА: Файл с токеном не найден по пути: {file_path}")
        return None
    try:
        with open(file_path, 'r') as f:
            # .strip() удаляет лишние пробелы и символы новой строки
            token = f.read().strip()
            if not token:
                print(f"ОШИБКА: Файл с токеном '{file_path}' пуст.")
                return None
            return token
    except Exception as e:
        print(f"Произошла ошибка при чтении файла с токеном: {e}")
        return None