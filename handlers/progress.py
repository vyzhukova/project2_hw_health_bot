from aiogram import Router, types
from aiogram.filters import Command
import logging

from utils.storage import storage
from utils.helpers import Helpers

logger = logging.getLogger(__name__)
router = Router()

@router.message(Command("check_progress"))
async def check_progress(message: types.Message):
    """Проверка прогресса"""
    user_id = message.from_user.id
    user_data = storage.get_user(user_id)
    
    if not user_data:
        await message.answer("Сначала настройте профиль: /set_profile")
        return
    
    progress = storage.get_daily_progress(user_id)
    
    if not progress:
        await message.answer("Нет данных о прогрессе.")
        return
    
    water = progress['water']
    calories = progress['calories']
    
    water_bar = Helpers.create_progress_bar(water['logged'], water['goal'])
    calorie_bar = Helpers.create_progress_bar(calories['balance'], calories['goal'])
    
    response = f"""
    Ваш прогресс на сегодня:

    Вода:
    {water_bar}
    Выпито: {water['logged']:.0f}/{water['goal']:.0f} мл ({water['percentage']:.1f}%)
    Осталось: {water['remaining']:.0f} мл

    Калории:
    {calorie_bar}
    Потреблено: {calories['logged']:.1f} ккал
    Сожжено: {calories['burned']:.1f} ккал
    Баланс: {calories['balance']:.1f} ккал
    Цель: {calories['goal']:.0f} ккал ({calories['percentage']:.1f}%)
    Осталось: {calories['remaining']:.1f} ккал

    Статистика:
    • Приемов пищи: {len(user_data['food_log'])}
    • Тренировок: {len(user_data['workout_log'])}
    """
    
    await message.answer(response)

@router.message(Command("reset_day"))
async def reset_day(message: types.Message):
    """Сбросить данные на день"""
    user_id = message.from_user.id
    
    if not storage.get_user(user_id):
        await message.answer("Сначала настройте профиль: /set_profile")
        return
    
    storage.reset_daily_data(user_id)
    await message.answer("Данные за день сброшены. Начинаем новый день!")

@router.message(Command("recommend"))
async def get_recommendations(message: types.Message):
    """Получить рекомендации"""
    user_id = message.from_user.id
    user_data = storage.get_user(user_id)
    
    if not user_data:
        await message.answer("Сначала настройте профиль: /set_profile")
        return
    
    progress = storage.get_daily_progress(user_id)
    
    if not progress:
        await message.answer("Нет данных для рекомендаций.")
        return
    
    water_percentage = progress['water']['percentage']
    calorie_percentage = progress['calories']['percentage']
    has_workout = len(user_data['workout_log']) > 0
    
    recommendations = Helpers.get_recommendations(water_percentage, calorie_percentage, has_workout)
    
    response = "Рекомендации на сегодня:\n\n" + "\n".join(f"• {rec}" for rec in recommendations)
    
    await message.answer(response)