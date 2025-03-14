from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

async def start(message: Message) -> None:
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Учитель", callback_data="role_teacher"),
                InlineKeyboardButton(text="Ученик", callback_data="role_student")
            ]
        ]
    )
    await message.answer("Добро пожаловать! Выберите вашу роль:", reply_markup=keyboard)
    await message.answer("Учитель сможет создавать задачи и приглашать учеников.\nУченик сможет получать и выполнять задачи от учителя.")