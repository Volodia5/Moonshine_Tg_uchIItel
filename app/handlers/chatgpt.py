import os
from openai import OpenAI
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from pydantic import BaseModel
from typing import List
from app.states.state import ChatGptStates

async def chatgpt(message: Message, state: FSMContext) -> None:
    """Handle /chatgpt command and set the state"""
    await message.answer("Введите текст для обработки:")
    await state.set_state(ChatGptStates.chat_gpt)

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

        class Question(BaseModel):
            question: str
            options: List[str]
            correctAnswer: int
        
        class Quiz(BaseModel):
            questions: List[Question]
        
        # Используем beta.chat.completions.parse вместо chat.completions.create
        response = client.beta.chat.completions.parse(
            model="openai/gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "Ты - помощник для учителя. Твоя задача сделать квиз 3 вопроса и 4 варианта ответа по данному тексту: "
                },
                {
                    "role": "user",
                    "content": text
                }
            ],
            temperature=0.4,
            response_format=Quiz
        )
        
        # Теперь response - это уже объект Quiz, можно работать с ним напрямую
        quiz_result = "📝 Квиз по вашему тексту:\n\n"
        
        # Получаем доступ к parsed объекту из ответа
        quiz_data = response.choices[0].message.parsed
        
        for i, question in enumerate(quiz_data.questions, 1):
            quiz_result += f"Вопрос {i}: {question.question}\n"
            for j, option in enumerate(question.options, 1):
                quiz_result += f"{j}. {option}\n"
            quiz_result += f"\nПравильный ответ: {question.correctAnswer}\n\n"
        
        # Send answer back to user
        await message.answer(quiz_result)
        
    except Exception as e:
        await message.answer(f"Ошибка обработки: {str(e)}\nПроверьте правильность API ключа и endpoint в файле .env")
    finally:
        # Clear state regardless of success or failure
        await state.clear()
