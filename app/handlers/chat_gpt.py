import os
from openai import OpenAI
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from app.states.state import state as UserState

async def chatgpt(message: Message, state: FSMContext) -> None:
    """Handle /chatgpt command and set the state"""
    await message.answer("Введите текст для обработки:")
    await state.set_state(UserState.chat_gpt)

async def process_chatgpt(message: Message, state: FSMContext) -> None:
    """Process user input when in chat_gpt state"""
    text = message.text
    api_key = os.getenv("API_CHATGPT")
    api_base = os.getenv("API_BASE")  # Получаем базовый URL из переменных окружения
    
    if not api_key:
        await message.answer("Ошибка: API ключ не настроен. Проверьте файл .env и убедитесь, что API_CHATGPT установлен.")
        await state.clear()
        return

    try:
        await message.answer("Обрабатываю ваш запрос...")
        
        # Initialize OpenAI client with custom base URL
        client = OpenAI(
            api_key=api_key,
            base_url=api_base  # Указываем кастомный endpoint
        )
        
        # Create chat completion
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "Ты - помощник для учителя. Твоя задача сделать подобное задание с ответом по тексту пользователя"
                },
                {
                    "role": "user",
                    "content": text
                }
            ],
            temperature=0.7
        )
        
        # Extract answer from response
        answer = response.choices[0].message.content
        
        # Send answer back to user
        await message.answer(answer)
        
    except Exception as e:
        await message.answer(f"Ошибка обработки: {str(e)}\nПроверьте правильность API ключа и endpoint в файле .env")
    finally:
        # Clear state regardless of success or failure
        await state.clear()

