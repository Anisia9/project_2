import os
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

# Токен бота
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Настройки логирования
LOG_LEVEL = "INFO"
LOG_FILE = "bot.log"
