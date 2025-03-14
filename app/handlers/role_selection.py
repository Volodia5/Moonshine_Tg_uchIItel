from aiogram.types import CallbackQuery
from ...main import supabase
from ..states import RegistrationStates
import uuid

async def process_role_selection(callback: CallbackQuery, state: FSMContext) -> None:
    role = callback.data.split('_')[1]
    await state.update_data(role=role)
    
    if role == "teacher":
        invite_code = str(uuid.uuid4())[:8]
        await state.update_data(invite_code=invite_code)
        
        supabase.table('users').insert({
            'user_id': callback.from_user.id,
            'username': callback.from_user.username,
            'role': 'teacher',
            'invite_code': invite_code
        }).execute()
        
        await callback.message.answer(
            f"Вы зарегистрированы как учитель!\nВаш код приглашения: {invite_code}\n"
            f"Отправьте этот код ученику, чтобы он мог присоединиться к вам."
        )
    else:
        await callback.message.answer("Пожалуйста, введите код приглашения от вашего учителя:")
        await state.set_state(RegistrationStates.waiting_for_invite_code)
    
    await callback.answer()