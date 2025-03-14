from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from supabase import Client, create_client

async def process_invite_code(message: Message, state: FSMContext) -> None:
    invite_code = message.text.strip()
    
    # Check if invite code exists and belongs to a teacher
    result = supabase.table('users').select('user_id').eq('invite_code', invite_code).eq('role', 'teacher').execute()
    
    if result.data:
        teacher_id = result.data[0]['user_id']
        # Save student to database with teacher reference
        supabase.table('users').insert({
            'user_id': message.from_user.id,
            'username': message.from_user.username,
            'role': 'student',
            'teacher_id': teacher_id
        }).execute()
        
        await message.answer("Вы успешно присоединились к учителю!")
    else:
        await message.answer("Неверный код приглашения. Пожалуйста, попробуйте еще раз:")
        return
    
    await state.clear()