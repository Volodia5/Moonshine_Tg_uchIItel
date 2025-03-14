import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.utils import executor

# Замените 'YOUR_TOKEN' на токен вашего бота
TELEGRAM_API_TOKEN = 'YOUR_TOKEN'

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Инициализация бота и диспетчера
bot = Bot(token=TELEGRAM_API_TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def start_command(message: types.Message):
    await message.answer("Привет! Я ваш Telegram-бот. Чем могу помочь?")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
