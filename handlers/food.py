from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from datetime import datetime
import logging

from states import UserStates
from services.food_api import NutritionAPI
from utils.storage import storage

logger = logging.getLogger(__name__)
router = Router()

@router.message(Command("log_food"))
async def log_food(message: types.Message, state: FSMContext):
    """Логирование еды"""
    user_id = message.from_user.id
    
    if not storage.get_user(user_id):
        await message.answer("Сначала настройте профиль: /set_profile")
        return
    
    try:
        parts = message.text.split(maxsplit=1)
        if len(parts) < 2:
            await message.answer("Использование: /log_food название продукта\nПример: /log_food банан")
            return
        
        product_name = parts[1]
        
        nutrition_api = NutritionAPI()
        food_info = await nutrition_api.search_product(product_name)
        
        await state.update_data(
            current_food=food_info,
            product_name=product_name
        )
        await state.set_state(UserStates.food_amount)
        
        response = f"""
        Найден продукт: {food_info['name']}

        Пищевая ценность на 100г:
        • Калории: {food_info['calories']} ккал
        • Белки: {food_info['protein']} г
        • Углеводы: {food_info['carbs']} г
        • Жиры: {food_info['fat']} г

        Сколько грамм вы съели?
        """
        
        await message.answer(response)
        
    except Exception as e:
        logger.error(f"Ошибка при логировании еды: {e}")
        await message.answer("Произошла ошибка. Попробуйте еще раз.")

@router.message(UserStates.food_amount)
async def process_food_amount(message: types.Message, state: FSMContext):
    """Обработка количества еды"""
    try:
        amount = float(message.text)
        
        data = await state.get_data()
        food_info = data['current_food']
        
        calories = (food_info['calories'] * amount) / 100
        protein = (food_info['protein'] * amount) / 100
        carbs = (food_info['carbs'] * amount) / 100
        fat = (food_info['fat'] * amount) / 100
        
        food_entry = {
            'date': datetime.now().isoformat(),
            'name': food_info['name'],
            'amount': amount,
            'calories': calories,
            'protein': protein,
            'carbs': carbs,
            'fat': fat
        }
        
        storage.add_food(message.from_user.id, food_entry)
        await state.clear()
        
        user_data = storage.get_user(message.from_user.id)
        total_calories = user_data['logged_calories']
        
        response = f"""
        Записано: {food_info['name']} - {amount}г

        Пищевая ценность:
        • Калории: {calories:.1f} ккал
        • Белки: {protein:.1f} г
        • Углеводы: {carbs:.1f} г
        • Жиры: {fat:.1f} г

        Всего потреблено за день: {total_calories:.1f} ккал
        """
        
        await message.answer(response)
        
    except ValueError:
        await message.answer("Пожалуйста, введите число (например: 150):")