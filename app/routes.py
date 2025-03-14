from app.handlers.start import start, process_lesson_text, process_poll_answer, process_student_name, show_teacher_links, show_quiz_results, back_to_links
from app.handlers.chatgpt import chatgpt, process_chatgpt
from app.states.state import TeacherStates, StudentStates, ChatGptStates
from aiogram.filters import Command

def register_handlers(dp):
    # Основные обработчики
    dp.message.register(start, Command("start"))
    dp.message.register(process_lesson_text, TeacherStates.waiting_for_lesson_text)
    dp.poll_answer.register(process_poll_answer)
    
    # Обработчик для имени пользователя
    dp.message.register(process_student_name, StudentStates.waiting_for_name)
    
    # Обработчики для ChatGPT
    dp.message.register(chatgpt, Command("chatgpt"))
    dp.message.register(process_chatgpt, ChatGptStates.chat_gpt)
    
    # Обработчики для учителя
    dp.message.register(show_teacher_links, Command("links"))
    dp.callback_query.register(show_quiz_results, lambda c: c.data.startswith("link_"))
    dp.callback_query.register(back_to_links, lambda c: c.data == "back_to_links")