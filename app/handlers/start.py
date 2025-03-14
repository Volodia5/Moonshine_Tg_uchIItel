from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

async def start(message: Message) -> None:
    if message.text and len(message.text.split()) > 1:
        deep_link_data = message.text.split()[1]
        await message.answer(f"👋 Hi! You're starting in student mode.\nDeep link data: {deep_link_data}")
    else:
        # This is a regular start
        await message.answer("👋 Hi teacher! Welcome to the bot.")