from aiogram import Router, types
from aiogram.filters import Command

from utils.storage import storage

router = Router()

@router.message(Command("log_water"))
async def log_water(message: types.Message):
    """Логирование воды"""
    user_id = message.from_user.id
    user_data = storage.get_user(user_id)
    
    if not user_data:
        await message.answer("Сначала настройте профиль: /set_profile")
        return
    
    try:
        parts = message.text.split()
        if len(parts) < 2:
            await message.answer("Использование: /log_water количество в мл\nПример: /log_water 500")
            return
        
        amount = float(parts[1])
        if amount <= 0:
            await message.answer("Пожалуйста, введите положительное количество воды.")
            return
        
        storage.update_user(user_id, {'logged_water': user_data.get('logged_water', 0) + amount})
        
        user_data = storage.get_user(user_id)
        water_total = user_data.get('logged_water', 0)
        water_goal = user_data.get('water_goal', 2000)
        
        remaining = max(0, water_goal - water_total)
        response = f"""
        Вода залогирована: {amount} мл

        Прогресс по воде:
        Выпито: {water_total}/{water_goal} мл
        Осталось: {remaining} мл
        """
        
        await message.answer(response)
        
    except (ValueError, IndexError):
        await message.answer("Использование: /log_water <количество в мл>\nПример: /log_water 500")