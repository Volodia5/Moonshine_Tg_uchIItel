from aiogram.fsm.state import State, StatesGroup

class RegistrationStates(StatesGroup):
    choosing_role = State()
    waiting_for_invite_code = State()

class UserState(StatesGroup):
    chat_gpt = State()

# Экспортируем состояния
__all__ = ['RegistrationStates', 'UserState']