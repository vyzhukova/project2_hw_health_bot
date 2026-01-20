from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from datetime import datetime
import logging

from states import UserStates
from keyboards import get_workout_types_keyboard
from services.calculator import Calculator
from utils.storage import storage

logger = logging.getLogger(__name__)
router = Router()

@router.message(Command("log_workout"))
async def log_workout_start(message: types.Message, state: FSMContext):
    """Начало логирования тренировки"""
    user_id = message.from_user.id
    
    if not storage.get_user(user_id):
        await message.answer("Сначала настройте профиль: /set_profile")
        return
    
    keyboard = get_workout_types_keyboard()
    await message.answer("Выберите тип тренировки:", reply_markup=keyboard)
    await state.set_state(UserStates.workout_type)

@router.callback_query(UserStates.workout_type, F.data.startswith("workout_"))
async def process_workout_type(callback: types.CallbackQuery, state: FSMContext):
    """Обработка типа тренировки"""
    workout_type = callback.data.replace('workout_', '')
    await state.update_data(workout_type=workout_type)
    
    await callback.message.edit_text(f"Тип тренировки: {workout_type}")
    await callback.answer()
    
    await state.set_state(UserStates.workout_duration)
    await callback.message.answer("Введите продолжительность тренировки в минутах:")

@router.message(UserStates.workout_duration)
async def process_workout_duration(message: types.Message, state: FSMContext):
    """Обработка продолжительности тренировки"""
    try:
        duration = int(message.text)
    
        data = await state.get_data()
        workout_type = data['workout_type']
        
        user_id = message.from_user.id
        user_data = storage.get_user(user_id)
        
        if not user_data:
            await message.answer("Сначала настройте профиль: /set_profile")
            return
        
        calculator = Calculator()
        burned_calories = calculator.calculate_workout_calories(
            workout_type, duration, user_data['weight']
        )
        
        additional_water = calculator.calculate_workout_water(duration)
        water_recommendation = calculator.get_workout_water_recommendation(duration)
        
        workout_entry = {
            'date': datetime.now().isoformat(),
            'type': workout_type,
            'duration': duration,
            'calories': burned_calories,
            'additional_water': additional_water
        }
        
        storage.add_workout(user_id, workout_entry)
        
        # Обновляем норму воды с учетом тренировки
        if additional_water > 0:
            current_water_goal = user_data.get('water_goal', 2000)
            base_activity = user_data.get('activity', 45) 
            
            # Рассчитываем базовую норму воды
            temperature = user_data.get('temperature', 20.0)
            base_water_goal = calculator.calculate_water_norm(
                weight=user_data['weight'],
                activity_minutes=base_activity,
                temperature=temperature
            )
            
            # Суммируем дополнительную воду за все сегодняшние тренировки
            total_additional_water = 0
            today = datetime.now().strftime('%Y-%m-%d')
            
            # Все тренировки за сегодня
            for workout in storage.get_user(user_id).get('workout_log', []):
                workout_date = workout.get('date', '')
                if today in workout_date:  
                    total_additional_water += workout.get('additional_water', 0)
            
            new_water_goal = base_water_goal + total_additional_water
            
            storage.update_user(user_id, {'water_goal': new_water_goal})
            
            logger.info(f"Обновлена норма воды: {current_water_goal} -> {new_water_goal} мл (+{additional_water} мл за тренировку)")
        
        await state.clear()
        
        user_data = storage.get_user(user_id)
        total_burned = user_data['burned_calories']
        response = f"""
        Тренировка добавлена!

        Детали:
        • Тип: {workout_type}
        • Продолжительность: {duration} минут
        • Сожжено калорий: {burned_calories} ккал

        {water_recommendation}

        Всего сожжено за день: {total_burned} ккал
        """
        
        await message.answer(response)
        
    except ValueError:
        await message.answer("Пожалуйста, введите целое число (например: 30):")