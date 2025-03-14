from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, Poll, PollAnswer
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from app.utils.database import store_lesson_text, get_lesson_text
from app.states.state import TeacherStates
from app.handlers.chatgpt import process_chatgpt
import os
from openai import OpenAI
from pydantic import BaseModel
from typing import List, Dict
import asyncio


class Question(BaseModel):
    question: str
    options: List[str]
    correctAnswer: int

class Quiz(BaseModel):
    questions: List[Question]


# Dictionary to store active polls and their associated data
active_polls: Dict[str, Dict] = {}


async def start(message: Message, state: FSMContext) -> None:
    # Check if the message contains a deep link
    if message.text and len(message.text.split()) > 1:
        # This is a deep link start
        try:
            deep_link_data = message.text.split()[1]
            lesson_id = int(deep_link_data)
            lesson_text = await get_lesson_text(lesson_id)
            
            # Send welcome message with lesson text
            await message.answer(
                f"👋 Привет! Вы запустили бота в режиме ученика.\n\n"
                "🎯 Сейчас я сгенерирую вопросы по материалу..."
            )

            # Generate quiz using ChatGPT
            api_key = os.getenv("API_CHATGPT")
            api_base = os.getenv("API_BASE")
            
            if not api_key:
                await message.answer("❌ Ошибка: API ключ не настроен.")
                return

            client = OpenAI(
                api_key=api_key,
                base_url=api_base
            )

            response = client.beta.chat.completions.parse(
                model="openai/gpt-4o-2024-11-20",
                messages=[
                    {
                        "role": "system",
                        "content": "Ты - помощник для учителя. Твоя задача сделать квиз на русском языке 3 вопроса и 4 варианта ответа по данному тексту. Время ответа на каждый вопрос: 15 секунд. Правильный ответ только один: "
                    },
                    {
                        "role": "user",
                        "content": lesson_text
                    }
                ],
                temperature=0.4,
                response_format=Quiz
            )

            # Get quiz data
            quiz_data = response.choices[0].message.parsed
            
            # Send text of the lesson
            await message.answer(f"📚 Текст урока:\n{lesson_text}\n\n")
            await message.answer("⏱️ На каждый вопрос у вас будет 15 секунд. Готовы? Начинаем!")
            
            # Wait a moment before starting the quiz
            await asyncio.sleep(2)
            
            # Store quiz data in state for the poll_answer handler
            await state.update_data(
                quiz_data=quiz_data.dict(),
                current_question=0,
                total_questions=len(quiz_data.questions),
                user_id=message.from_user.id,
                chat_id=message.chat.id,
                correct_answers=0
            )
            
            # Send the first question
            await send_next_question(message.chat.id, state, message.bot)

        except ValueError:
            await message.answer("❌ Урок не найден. Пожалуйста, проверьте ссылку.")
        except Exception as e:
            print(e)
            await message.answer("❌ Произошла ошибка при получении текста урока. Пожалуйста, попробуйте позже.")
    else:
        # This is a regular start - teacher mode
        await state.set_state(TeacherStates.waiting_for_lesson_text)
        await message.answer("👋 Добро пожаловать в режим учителя!\nПожалуйста, отправьте текст урока.")


async def send_next_question(chat_id: int, state: FSMContext, bot) -> None:
    """Send the next question in the quiz"""
    # Get the current state data
    data = await state.get_data()
    current_question = data.get("current_question", 0)
    total_questions = data.get("total_questions", 0)
    quiz_data = data.get("quiz_data", {})
    
    # Check if we've reached the end of the quiz
    if current_question >= total_questions:
        correct_answers = data.get("correct_answers", 0)
        await bot.send_message(
            chat_id=chat_id,
            text=f"🎉 Квиз завершен! Ваш результат: {correct_answers}/{total_questions}"
        )
        # Clear the state
        await state.clear()
        return
    
    # Get the current question data
    question = quiz_data.get("questions", [])[current_question]
    
    # Ensure correct_option_id is within valid range
    correct_option_id = min(max(0, question["correctAnswer"] - 1), len(question["options"]) - 1)
    
    # Send the question number
    await bot.send_message(
        chat_id=chat_id,
        text=f"❓ Вопрос {current_question + 1} из {total_questions}:"
    )
    
    # Send the poll
    sent_poll = await bot.send_poll(
        chat_id=chat_id,
        question=question["question"],
        options=question["options"],
        is_anonymous=False,
        type="quiz",
        correct_option_id=correct_option_id,
        explanation="Правильный ответ!",
        open_period=15  # 15 seconds time limit
    )
    
    # Store the poll ID in the active_polls dictionary
    active_polls[sent_poll.poll.id] = {
        "chat_id": chat_id,
        "user_id": data.get("user_id"),
        "state": state,
        "correct_option_id": correct_option_id,
        "bot": bot
    }
    
    # Update the state with the current poll ID
    await state.update_data(
        current_poll_id=sent_poll.poll.id,
        current_question=current_question
    )
    
    # Set a timeout to move to the next question if the user doesn't answer
    asyncio.create_task(handle_poll_timeout(sent_poll.poll.id, 16))  # 16 seconds (15 + 1 buffer)


async def handle_poll_timeout(poll_id: str, timeout: int) -> None:
    """Handle the timeout for a poll"""
    await asyncio.sleep(timeout)
    
    # Check if the poll is still active (user hasn't answered yet)
    if poll_id in active_polls:
        poll_data = active_polls.pop(poll_id)
        chat_id = poll_data.get("chat_id")
        state = poll_data.get("state")
        bot = poll_data.get("bot")
        
        # Get the current state data
        data = await state.get_data()
        current_question = data.get("current_question", 0)
        
        # Update the state to move to the next question
        await state.update_data(current_question=current_question + 1)
        
        # Send a message that time is up
        await bot.send_message(
            chat_id=chat_id,
            text="⏱️ Время вышло! Переходим к следующему вопросу..."
        )
        
        # Wait a moment before sending the next question
        await asyncio.sleep(1)
        
        # Send the next question
        await send_next_question(chat_id, state, bot)


async def process_poll_answer(poll_answer: PollAnswer, state: FSMContext) -> None:
    """Process a poll answer"""
    # Check if this poll is in our active polls
    poll_id = poll_answer.poll_id
    if poll_id not in active_polls:
        return
    
    # Get the poll data
    poll_data = active_polls.pop(poll_id)
    
    # Check if this answer is from the user who started the quiz
    if poll_answer.user.id != poll_data.get("user_id"):
        return
    
    # Get the state from the poll data
    user_state = poll_data.get("state")
    bot = poll_data.get("bot")
    
    # Get the current state data
    data = await user_state.get_data()
    current_question = data.get("current_question", 0)
    correct_answers = data.get("correct_answers", 0)
    chat_id = poll_data.get("chat_id")
    
    # Check if the answer is correct
    if poll_answer.option_ids and poll_answer.option_ids[0] == poll_data.get("correct_option_id"):
        # Increment the correct answers count
        correct_answers += 1
        await user_state.update_data(correct_answers=correct_answers)
    
    # Update the state to move to the next question
    await user_state.update_data(current_question=current_question + 1)
    
    # Wait a moment before sending the next question
    await asyncio.sleep(2)
    
    # Send the next question
    await send_next_question(chat_id, user_state, bot)


async def process_lesson_text(message: Message, state: FSMContext) -> None:
    try:
        # Get username from message
        
        # Store the lesson text in Supabase
        lesson_id = await store_lesson_text(
            text=message.text,
            author_id=float(message.from_user.id)
        )

        # print(message.from_user)
        # Generate student link
        # bot_username = message.b TODO: ОШИБка
        bot_username = 'teacherhelpercu_bot'
        student_link = f"https://t.me/{bot_username}?start={lesson_id}"
        
        await message.answer(
            "✅ Текст урока успешно сохранен!\n\n"
            f"🔗 Ссылка для учеников:\n{student_link}"
        )
    except Exception as e:
        print(e)
        await message.answer("❌ Произошла ошибка при сохранении текста урока. Пожалуйста, попробуйте позже.")
    finally:
        await state.clear()
        