from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

async def start(message: Message) -> None:
    # Check if the message contains a deep link
    if message.text and len(message.text.split()) > 1:
        # This is a deep link start
        deep_link_data = message.text.split()[1]
        await message.answer(f"👋 Hi! You're starting in student mode.\nDeep link data: {deep_link_data}")
    else:
        # This is a regular start
        await message.answer("👋 Hi teacher! Welcome to the bot.")