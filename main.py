import asyncio
import os
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message

from app.handlers.start import start
from app.handlers.chat_gpt import chatgpt, process_chatgpt
from app.states.state import UserState

async def main() -> None:
    load_dotenv()
    bot_token = os.getenv("API_TELEGRAM")

    dp = Dispatcher()

    # ChatGPT handlers
    dp.message.register(chatgpt, Command("chatgpt"))
    dp.message.register(process_chatgpt, UserState.chat_gpt)

    # Start handler
    dp.message.register(start, Command("start"))

    bot = Bot(token=bot_token)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
