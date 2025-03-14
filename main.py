import asyncio
import os
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from app.handlers.start import start, process_lesson_text
from app.handlers.start import TeacherStates
# from app.handlers.role_selection import process_role_selection
# from app.handlers.invite_code import process_invite_code
# from app.states import RegistrationStates


async def main() -> None:
    load_dotenv()
    bot_token = os.getenv("API_TELEGRAM")

    dp = Dispatcher()

    dp.message.register(start, Command("start"))
    dp.message.register(process_lesson_text, TeacherStates.waiting_for_lesson_text)
    # dp.callback_query.register(process_role_selection, F.data.startswith("role_"))
    # dp.message.register(process_invite_code, RegistrationStates.waiting_for_invite_code)

    bot = Bot(token=bot_token)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
