from pathlib import Path
import os

# Базовый каталог проекта
BASE_DIR = Path(__file__).resolve().parent.parent  # parent.parent — чтобы подняться на уровень выше до корня проекта


# Директории (с возможностью переопределения через переменные окружения)
IMAGES_DIR = Path(os.getenv('IMAGES_DIR', BASE_DIR / 'images'))
LOGS_DIR = Path(os.getenv('LOGS_DIR', BASE_DIR / 'logs'))

# Ограничения по размеру файлов
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 МБ
REQUEST_LIMIT = MAX_FILE_SIZE + 1024 * 1024  # Лимит запроса с запасом

# Поддерживаемые форматы изображений и их расширения
ALLOWED_IMAGE_FORMATS = {
    'JPEG': 'jpg',
    'PNG': 'png',
    'GIF': 'gif'
}

def ensure_directories_exist():
    """Создаёт необходимые директории, если их нет."""
    IMAGES_DIR.mkdir(exist_ok=True, parents=True)
    LOGS_DIR.mkdir(exist_ok=True, parents=True)
