import asyncio
import os
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, PollAnswer
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from app.routes import register_handlers


async def main() -> None:
    print("Starting bot...")
    load_dotenv()
    bot_token = os.getenv("API_TELEGRAM")

    dp = Dispatcher()
    bot = Bot(token=bot_token)

    # Register all handlers from routes.py
    register_handlers(dp)

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
