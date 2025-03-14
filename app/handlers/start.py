from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from app.utils.database import store_lesson_text

class TeacherStates(StatesGroup):
    waiting_for_lesson_text = State()

async def start(message: Message, state: FSMContext) -> None:
    # Check if the message contains a deep link
    if message.text and len(message.text.split()) > 1:
        # This is a deep link start
        deep_link_data = message.text.split()[1]
        await message.answer(f"👋 Привет! Вы запустили бота в режиме ученика.\nКод приглашения: {deep_link_data}")
    else:
        # This is a regular start - teacher mode
        await state.set_state(TeacherStates.waiting_for_lesson_text)
        await message.answer("👋 Добро пожаловать в режим учителя!\nПожалуйста, отправьте текст урока.")

async def process_lesson_text(message: Message, state: FSMContext) -> None:
    try:
        # Store the lesson text in Supabase
        lesson_id = await store_lesson_text(
            text=message.text,
            author_id=float(message.from_user.id)
        )
        
        # Generate student link
        bot_username = message.bot.username
        student_link = f"https://t.me/{bot_username}?start={lesson_id}"
        
        await message.answer(
            "✅ Текст урока успешно сохранен!\n\n"
            f"🔗 Ссылка для учеников:\n{student_link}"
        )
    except Exception as e:
        await message.answer("❌ Произошла ошибка при сохранении текста урока. Пожалуйста, попробуйте позже.")
    finally:
        await state.clear()
        