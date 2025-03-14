from aiogram.fsm.state import State, StatesGroup

class RegistrationStates(StatesGroup):
    choosing_role = State()
    waiting_for_invite_code = State()

class ChatGptStates(StatesGroup):
    chat_gpt = State()