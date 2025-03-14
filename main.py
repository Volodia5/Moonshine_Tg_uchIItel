import asyncio
import os
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from supabase import create_client, Client

supabase: Client = create_client(
    os.getenv("SUPABASE_URL", ""),
    os.getenv("SUPABASE_KEY", "")
)

async def main() -> None:
    load_dotenv()
    bot_token = os.getenv("API_TELEGRAM")

    dp = Dispatcher()

    dp.message.register(start, Command("start"))
    dp.callback_query.register(process_role_selection, F.data.startswith("role_"))
    dp.message.register(process_invite_code, RegistrationStates.waiting_for_invite_code)

    bot = Bot(token=bot_token)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
