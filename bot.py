

from aiogram import types

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

import asyncio
import logging
from aiogram import Bot, Dispatcher
from config import BOT_TOKEN
from handlers import setup_handlers

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

setup_handlers(dp)  # Подключаем обработчики
# Главное меню
menu_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📜 Описание и правила")],
        [KeyboardButton(text="🧠 Викторина", request_contact=False)],
    ],
    resize_keyboard=True
)




# Обработчик команды /start
@dp.message(lambda message: message.text == "/start")
async def cmd_start(message: types.Message):
    await message.answer("Привет! Добро пожаловать в AI Quiz. Выберите действие:", reply_markup=menu_keyboard)
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())



