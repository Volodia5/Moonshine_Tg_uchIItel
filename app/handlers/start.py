from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, Poll, PollAnswer
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from app.utils.database import store_lesson_text, get_lesson_text, check_user_exists, save_user, get_user_name, store_quiz_result, get_teacher_links, get_quiz_results_by_link
from app.utils.language import get_text, get_user_language, get_user_text
from app.states.state import TeacherStates, StudentStates
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
    explanation: str  # Add explanation field to the model

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
            
            # Check if user exists in the database
            user_id = float(message.from_user.id)
            user_exists = await check_user_exists(user_id)
            
            
            if not user_exists:
                # User doesn't exist, ask for name
                await state.set_state(StudentStates.waiting_for_name)
                await state.update_data(lesson_id=lesson_id)
                await message.answer(
                    get_text("welcome_student", "ru")  # Default to Russian for new users
                )
                return
            
            lesson_text = await get_lesson_text(lesson_id)
            name = await get_user_name(user_id)
            language = await get_user_language(user_id)
            
            # Send welcome message with lesson text
            await message.answer(
                get_text("welcome_back_student", language, name)
            )

            # Generate quiz using ChatGPT
            api_key = os.getenv("API_CHATGPT")
            api_base = os.getenv("API_BASE")
            
            if not api_key:
                await message.answer(get_text("api_key_error", language))
                return

            client = OpenAI(
                api_key=api_key,
                base_url=api_base
            )

            response = client.beta.chat.completions.parse(
                model="openai/gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": get_text("quiz_system_prompt", language)
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
            await message.answer(get_text("lesson_text", language, lesson_text))
            await message.answer(get_text("quiz_start", language))
            
            # Wait a moment before starting the quiz
            await asyncio.sleep(2)
            
            # Store quiz data in state for the poll_answer handler
            await state.update_data(
                quiz_data=quiz_data.dict(),
                current_question=0,
                total_questions=len(quiz_data.questions),
                user_id=message.from_user.id,
                chat_id=message.chat.id,
                correct_answers=0,
                lesson_id=lesson_id,
                language=language
            )
            
            # Send the first question
            await send_next_question(message.chat.id, state, message.bot)

        except ValueError:
            language = await get_user_language(float(message.from_user.id)) if await check_user_exists(float(message.from_user.id)) else "ru"
            await message.answer(get_text("lesson_not_found", language))
        except Exception as e:
            print(e)
            language = await get_user_language(float(message.from_user.id)) if await check_user_exists(float(message.from_user.id)) else "ru"
            await message.answer(get_text("general_error", language))
    else:
        # This is a regular start - teacher mode
        user_id = float(message.from_user.id)
        language = await get_user_language(user_id) if await check_user_exists(user_id) else "ru"
        
        await state.set_state(TeacherStates.waiting_for_lesson_text)
        await message.answer(get_text("welcome_teacher", language))


async def send_next_question(chat_id: int, state: FSMContext, bot) -> None:
    """Send the next question in the quiz"""
    # Get the current state data
    data = await state.get_data()
    current_question = data.get("current_question", 0)
    total_questions = data.get("total_questions", 0)
    quiz_data = data.get("quiz_data", {})
    language = data.get("language", "ru")
    
    # Check if we've reached the end of the quiz
    if current_question >= total_questions:
        correct_answers = data.get("correct_answers", 0)
        # Calculate score from 0 to 100
        average_score = int((correct_answers / total_questions) * 100) if total_questions > 0 else 0
        
        # Get user_id and lesson_id from state
        user_id = data.get("user_id")
        link_id = data.get("lesson_id")
        
        # Store the result in the database
        try:
            await store_quiz_result(float(user_id), link_id, correct_answers, total_questions)
            await bot.send_message(
                chat_id=chat_id,
                text=get_text("quiz_completed", language, correct_answers, total_questions, average_score)
            )
        except Exception as e:
            print(f"Error storing quiz result: {e}")
            await bot.send_message(
                chat_id=chat_id,
                text=get_text("quiz_completed", language, correct_answers, total_questions, average_score)
            )
        
        # Clear the state
        await state.clear()
        return
    
    # Get the current question data
    question = quiz_data.get("questions", [])[current_question]
    
    # Ensure correct_option_id is within valid range (assuming 0-indexed)
    correct_option_id = min(max(0, question["correctAnswer"]), len(question["options"]) - 1)
    
    # Get the explanation for this question
    explanation = question.get("explanation", "Правильный ответ!")
    
    # Send the question number
    await bot.send_message(
        chat_id=chat_id,
        text=get_text("question_number", language, current_question + 1, total_questions)
    )
    
    # Send the poll
    sent_poll = await bot.send_poll(
        chat_id=chat_id,
        question=question["question"],
        options=question["options"],
        is_anonymous=False,
        type="quiz",
        correct_option_id=correct_option_id,
        explanation=explanation,
        open_period=15  # 15 seconds time limit
    )
    
    # Store the poll ID in the active_polls dictionary
    active_polls[sent_poll.poll.id] = {
        "chat_id": chat_id,
        "user_id": data.get("user_id"),
        "state": state,
        "correct_option_id": correct_option_id,
        "bot": bot,
        "language": language
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
        language = poll_data.get("language", "ru")
        
        # Get the current state data
        data = await state.get_data()
        current_question = data.get("current_question", 0)
        quiz_data = data.get("quiz_data", {})
        
        # Get the current question data
        question = quiz_data.get("questions", [])[current_question]
        
        # Ensure correct_option_id is within valid range (assuming 0-indexed)
        correct_option_id = min(max(0, question["correctAnswer"]), len(question["options"]) - 1)
        correct_answer = question["options"][correct_option_id]
        
        # Update the state to move to the next question
        await state.update_data(current_question=current_question + 1)
        
        # Send a message that time is up with the correct answer
        await bot.send_message(
            chat_id=chat_id,
            text=get_text("time_up", language, correct_answer)
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
        user_id = float(message.from_user.id)
        language = await get_user_language(user_id)
        
        # Store the lesson text in Supabase
        lesson_id = await store_lesson_text(
            text=message.text,
            author_id=user_id
        )

        # Generate student link
        bot_username = 'teacherhelpercu_bot'
        student_link = f"https://t.me/{bot_username}?start={lesson_id}"
        
        await message.answer(
            get_text("lesson_saved", language, student_link)
        )
    except Exception as e:
        print(e)
        user_id = float(message.from_user.id)
        language = await get_user_language(user_id)
        await message.answer(get_text("lesson_save_error", language))
    finally:
        await state.clear()


async def process_student_name(message: Message, state: FSMContext) -> None:
    """Process the student's name and save it to the database"""
    try:
        # Get the student's name from the message
        student_name = message.text.strip()
        
        # Get the user ID
        user_id = float(message.from_user.id)
        
        # Default language is Russian for new users
        language = "ru"
        
        # Save the user to the database
        await save_user(user_id, student_name, language)
        
        # Get the lesson ID from the state
        data = await state.get_data()
        lesson_id = data.get("lesson_id")
        
        # Get the lesson text
        lesson_text = await get_lesson_text(lesson_id)
        
        # Send welcome message
        await message.answer(
            get_text("name_saved", language, student_name)
        )
        
        # Generate quiz using ChatGPT
        api_key = os.getenv("API_CHATGPT")
        api_base = os.getenv("API_BASE")
        
        if not api_key:
            await message.answer(get_text("api_key_error", language))
            return

        client = OpenAI(
            api_key=api_key,
            base_url=api_base
        )

        response = client.beta.chat.completions.parse(
            model="openai/gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": get_text("quiz_system_prompt", language)
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
        await message.answer(get_text("lesson_text", language, lesson_text))
        await message.answer(get_text("quiz_start", language))
        
        # Wait a moment before starting the quiz
        await asyncio.sleep(2)
        
        # Store quiz data in state for the poll_answer handler
        await state.update_data(
            quiz_data=quiz_data.dict(),
            current_question=0,
            total_questions=len(quiz_data.questions),
            user_id=message.from_user.id,
            chat_id=message.chat.id,
            correct_answers=0,
            lesson_id=lesson_id,
            language=language
        )
        
        # Send the first question
        await send_next_question(message.chat.id, state, message.bot)
        
    except Exception as e:
        print(e)
        await message.answer(get_text("name_save_error", "ru"))  # Default to Russian for new users
        # Only clear state on error
        await state.clear()


async def show_teacher_links(message: Message, state: FSMContext) -> None:
    """Show all links created by the teacher"""
    try:
        teacher_id = float(message.from_user.id)
        language = await get_user_language(teacher_id)
        links = await get_teacher_links(teacher_id)
        
        if not links:
            await message.answer(get_text("no_links", language))
            return
        
        # Create inline keyboard with links
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=f"{get_text('link_prefix', language, link['id'])}: {link['text'][:30]}...", callback_data=f"link_{link['id']}")] 
            for link in links
        ])
        
        await message.answer(get_text("choose_link", language), reply_markup=keyboard)
    except Exception as e:
        print(e)
        teacher_id = float(message.from_user.id)
        language = await get_user_language(teacher_id)
        await message.answer(get_text("links_error", language))


async def show_quiz_results(callback: CallbackQuery, state: FSMContext) -> None:
    """Show quiz results for a specific link"""
    try:
        # Extract link ID from callback data
        link_id = int(callback.data.split('_')[1])
        user_id = float(callback.from_user.id)
        language = await get_user_language(user_id)
        
        # Get quiz results for this link
        results = await get_quiz_results_by_link(link_id)
        
        if not results:
            await callback.message.answer(get_text("no_results", language, link_id))
            await callback.answer()
            return
        
        # Format results as a message
        message_text = get_text("results_title", language, link_id) + "\n\n"
        
        for i, result in enumerate(results, 1):
            message_text += (
                f"{i}. {result['name']}: {result['correct_answers']}/{result['total_questions']} "
                f"({result['average_score']}%)\n"
            )
        
        # Add back button
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=get_text("back_button", language), callback_data="back_to_links")]
        ])
        
        await callback.message.answer(message_text, reply_markup=keyboard)
        await callback.answer()
    except Exception as e:
        print(e)
        user_id = float(callback.from_user.id)
        language = await get_user_language(user_id)
        await callback.message.answer(get_text("results_error", language))
        await callback.answer()


async def back_to_links(callback: CallbackQuery, state: FSMContext) -> None:
    """Handle back button to return to links list"""
    try:
        user_id = float(callback.from_user.id)
        language = await get_user_language(user_id)
        
        # Сначала получаем новое сообщение, затем удаляем старое
        new_message = await callback.message.answer(get_text("loading_links", language))
        await callback.message.delete()
        
        # Используем новое сообщение для показа списка ссылок
        teacher_id = float(callback.from_user.id)
        links = await get_teacher_links(teacher_id)
        
        if not links:
            await new_message.edit_text(get_text("no_links", language))
            await callback.answer()
            return
        
        # Создаем клавиатуру с ссылками
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=f"{get_text('link_prefix', language, link['id'])}: {link['text'][:30]}...", callback_data=f"link_{link['id']}")] 
            for link in links
        ])
        
        await new_message.edit_text(get_text("choose_link", language), reply_markup=keyboard)
        await callback.answer()
    except Exception as e:
        print(f"Ошибка в back_to_links: {e}")
        user_id = float(callback.from_user.id)
        language = await get_user_language(user_id)
        await callback.answer(get_text("general_error", language))
        