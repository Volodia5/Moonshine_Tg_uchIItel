from aiogram.fsm.state import State, StatesGroup

<<<<<<< Updated upstream
class RegistrationStates(StatesGroup):
    choosing_role = State()
    waiting_for_invite_code = State()

class ChatGptStates(StatesGroup):
    chat_gpt = State()
=======
class TeacherStates(StatesGroup):
    waiting_for_lesson_text = State()
>>>>>>> Stashed changes
