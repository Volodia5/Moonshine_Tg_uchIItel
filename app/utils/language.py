from typing import Dict, Any, Optional
from aiogram.types import Message, User
from aiogram.fsm.context import FSMContext

# Default language
DEFAULT_LANGUAGE = "ru"

# Available languages
LANGUAGES = {
    "ru": "Русский",
    "en": "English"
}

# Translations dictionary
TRANSLATIONS = {
    # Start messages
    "welcome_teacher": {
        "ru": "👋 Добро пожаловать в режим учителя!\nПожалуйста, отправьте текст урока. Что бы запустить тест - перейдите по его ссылке.",
        "en": "👋 Welcome to teacher mode!\nPlease send the lesson text. To start the test, go to its link."
    },
    "welcome_student": {
        "ru": "👋 Привет! Похоже, вы впервые используете нашего бота. \n\nЕсли вам нужно создать тест - напишите /start \n\nПожалуйста, введите ваше имя:",
        "en": "👋 Hello! It seems you're using our bot for the first time.\n\nIf you need to create a test, write /start \n\nPlease enter your name:"
    },
    "welcome_back_student": {
        "ru": "👋 Привет, {}! Вы запустили бота в режиме ученика.\n\n🎯 Сейчас я сгенерирую вопросы по материалу... \n\nЕсли вам нужно создать тест - напишите /start",
        "en": "👋 Hello, {}! You've launched the bot in student mode.\n\n🎯 I'll now generate questions based on the material... \n\nIf you need to create a test, write /start"
    },
    
    # Error messages
    "api_key_error": {
        "ru": "❌ Ошибка: API ключ не настроен.",
        "en": "❌ Error: API key is not configured."
    },
    "lesson_not_found": {
        "ru": "❌ Урок не найден. Пожалуйста, проверьте ссылку.",
        "en": "❌ Lesson not found. Please check the link."
    },
    "general_error": {
        "ru": "❌ Произошла ошибка. Пожалуйста, попробуйте позже.",
        "en": "❌ An error occurred. Please try again later."
    },
    "lesson_save_error": {
        "ru": "❌ Произошла ошибка при сохранении текста урока. Пожалуйста, попробуйте позже.",
        "en": "❌ An error occurred while saving the lesson text. Please try again later."
    },
    "name_save_error": {
        "ru": "❌ Произошла ошибка при сохранении вашего имени. Пожалуйста, попробуйте позже.",
        "en": "❌ An error occurred while saving your name. Please try again later."
    },
    "links_error": {
        "ru": "❌ Произошла ошибка при получении списка ссылок. Пожалуйста, попробуйте позже.",
        "en": "❌ An error occurred while retrieving the list of links. Please try again later."
    },
    "results_error": {
        "ru": "❌ Произошла ошибка при получении результатов. Пожалуйста, попробуйте позже.",
        "en": "❌ An error occurred while retrieving the results. Please try again later."
    },
    
    # Quiz messages
    "lesson_text": {
        "ru": "📚 Текст урока:\n{}",
        "en": "📚 Lesson text:\n{}"
    },
    "quiz_start": {
        "ru": "⏱️ На каждый вопрос у вас будет 15 секунд. Готовы? Начинаем!",
        "en": "⏱️ You'll have 15 seconds for each question. Ready? Let's start!"
    },
    "question_number": {
        "ru": "❓ Вопрос {} из {}:",
        "en": "❓ Question {} of {}:"
    },
    "time_up": {
        "ru": "⏱️ Время вышло! Правильный ответ: {}\n\nПереходим к следующему вопросу...",
        "en": "⏱️ Time's up! Correct answer: {}\n\nMoving to the next question..."
    },
    "quiz_completed": {
        "ru": "🎉 Квиз завершен! Ваш результат: {}/{} ({}%)",
        "en": "🎉 Quiz completed! Your result: {}/{} ({}%)"
    },
    
    # Teacher messages
    "lesson_saved": {
        "ru": "✅ Текст урока успешно сохранен!\n\n🔗 Ссылка для учеников:\n{}\n\nЧтобы просмотреть все созданные вами ссылки и результаты, используйте команду /links",
        "en": "✅ Lesson text successfully saved!\n\n🔗 Link for students:\n{}\n\nTo view all links you've created and their results, use the /links command"
    },
    "no_links": {
        "ru": "У вас пока нет созданных ссылок. Отправьте текст урока, чтобы создать новую ссылку.",
        "en": "You don't have any created links yet. Send a lesson text to create a new link."
    },
    "choose_link": {
        "ru": "Выберите ссылку, чтобы просмотреть результаты:",
        "en": "Choose a link to view results:"
    },
    "link_prefix": {
        "ru": "Урок {}:",
        "en": "Lesson {}:"
    },
    "no_results": {
        "ru": "По ссылке #{} пока нет результатов.",
        "en": "There are no results for link #{} yet."
    },
    "results_title": {
        "ru": "📊 Результаты по ссылке #{}:",
        "en": "📊 Results for link #{}:"
    },
    "back_button": {
        "ru": "◀️ Назад к списку",
        "en": "◀️ Back to list"
    },
    "loading_links": {
        "ru": "Загрузка списка ссылок...",
        "en": "Loading links list..."
    },
    
    # Student messages
    "name_saved": {
        "ru": "✅ Спасибо, {}! Ваше имя сохранено.\n\n👋 Вы запустили бота в режиме ученика.\n\n🎯 Сейчас я сгенерирую вопросы по материалу...",
        "en": "✅ Thank you, {}! Your name has been saved.\n\n👋 You've launched the bot in student mode.\n\n🎯 I'll now generate questions based on the material..."
    },
    
    # Language settings
    "language_command": {
        "ru": "🌐 Выберите язык:",
        "en": "🌐 Choose language:"
    },
    "language_selected": {
        "ru": "✅ Язык изменен на русский.",
        "en": "✅ Language changed to English."
    },
    
    # System prompts
    "quiz_system_prompt": {
        "ru": "Ты - помощник для учителя. Твоя задача сделать квиз на русском языке 3 вопроса и 4 варианта ответа по данному тексту. Для каждого вопроса добавь объяснение правильного ответа. Время ответа на каждый вопрос: 15 секунд. Правильный ответ только один. ВАЖНО: индекс правильного ответа должен начинаться с 0 (нумерация с нуля).",
        "en": "You are a teacher's assistant. Your task is to create a quiz in English with 3 questions and 4 answer options based on the given text. For each question, add an explanation of the correct answer. Time to answer each question: 15 seconds. There is only one correct answer. IMPORTANT: the index of the correct answer should start from 0 (zero-based numbering)."
    }
}

async def get_user_language(user_id: float) -> str:
    """Get user language from database or return default"""
    from app.utils.database import get_user_language as db_get_user_language
    
    try:
        language = await db_get_user_language(user_id)
        return language if language else DEFAULT_LANGUAGE
    except:
        return DEFAULT_LANGUAGE

async def set_user_language(user_id: float, language: str) -> bool:
    """Set user language in database"""
    from app.utils.database import set_user_language as db_set_user_language
    
    try:
        await db_set_user_language(user_id, language)
        return True
    except:
        return False

def get_text(key: str, language: str = DEFAULT_LANGUAGE, **kwargs) -> str:
    """Get translated text by key and language"""
    if key not in TRANSLATIONS:
        return f"Missing translation: {key}"
    
    if language not in TRANSLATIONS[key]:
        language = DEFAULT_LANGUAGE
    
    text = TRANSLATIONS[key][language]
    
    # Format text with kwargs if provided
    if kwargs:
        try:
            return text.format(**kwargs)
        except:
            try:
                # Try positional formatting if keyword formatting fails
                return text.format(*kwargs.values())
            except:
                return text
    
    return text

async def get_user_text(key: str, user_id: float, **kwargs) -> str:
    """Get translated text for a specific user"""
    language = await get_user_language(user_id)
    return get_text(key, language, **kwargs) 