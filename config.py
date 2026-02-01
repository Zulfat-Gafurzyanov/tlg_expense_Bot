import os

from dotenv import load_dotenv
from pathlib import Path

# Загружаем переменные окружения из .env файла
load_dotenv()

# Токен Telegram бота
TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")

# Список допустимых user_id
ALLOWED_USER_IDS: list[int] = [
    int(user_id.strip())
    for user_id in os.getenv("ALLOWED_USER_IDS", "").split(",")
    if user_id.strip().isdigit()
]

# Путь к папке с данными
DATA_DIR: Path = Path(__file__).parent / "data"
DATA_DIR.mkdir(exist_ok=True)

# Предопределённые категории расходов
CATEGORIES: list[str] = [
    "ЗП",
    "Постоянный расход",
    "Доп расход",
    "Товарка",
    "Поставщикам",
    "Развитие магазина"
]
