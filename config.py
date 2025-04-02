from dotenv import load_dotenv
import os

load_dotenv(dotenv_path=".env")  # Явно указываем путь к .env


# Токен Telegram-бота
BOT_TOKEN = os.getenv("BOT_TOKEN")

# ProxyAPI для GPT
PROXY_API_KEY = os.getenv("PROXY_API_KEY")
PROXY_API_URL = os.getenv("PROXY_API_URL")

if not BOT_TOKEN:
    raise ValueError("Токен бота не найден! Укажите его в файле .env")
