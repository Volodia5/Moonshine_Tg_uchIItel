from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from app.utils.language import LANGUAGES, get_text, get_user_language, set_user_language

async def language_command(message: Message, state: FSMContext) -> None:
    """Handle /language command to change language"""
    user_id = float(message.from_user.id)
    current_language = await get_user_language(user_id)
    
    # Create keyboard with language options
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=name, callback_data=f"lang_{code}")] 
        for code, name in LANGUAGES.items()
    ])
    
    await message.answer(
        get_text("language_command", current_language),
        reply_markup=keyboard
    )

async def language_callback(callback: CallbackQuery, state: FSMContext) -> None:
    """Handle language selection callback"""
    # Extract language code from callback data
    language_code = callback.data.split('_')[1]
    user_id = float(callback.from_user.id)
    
    # Set user language in database
    success = await set_user_language(user_id, language_code)
    
    if success:
        # Send confirmation message in the new language
        await callback.message.edit_text(
            get_text("language_selected", language_code)
        )
    else:
        # Send error message
        current_language = await get_user_language(user_id)
        await callback.message.edit_text(
            get_text("general_error", current_language)
        )
    
    await callback.answer() 