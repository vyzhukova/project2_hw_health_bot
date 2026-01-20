from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from states import UserStates
from keyboards import get_activity_keyboard, get_gender_keyboard
from utils.storage import storage

router = Router()

@router.message(Command("set_profile"))
async def set_profile_start(message: types.Message, state: FSMContext):
    """Начало настройки профиля"""
    user_id = message.from_user.id
    
    if storage.get_user(user_id):
        await message.answer(
            "У вас уже есть профиль. Чтобы изменить его, сначала сбросьте данные командой /reset_day"
        )
        return
    
    await state.set_state(UserStates.weight)
    await message.answer("Давайте настроим ваш профиль!\n\nВведите ваш вес (в кг):")

@router.message(UserStates.weight)
async def process_weight(message: types.Message, state: FSMContext):
    """Обработка веса"""
    try:
        weight = float(message.text)
        await state.update_data(weight=weight)
        await state.set_state(UserStates.height)
        await message.answer("Теперь введите ваш рост (в см):")
    except ValueError:
        await message.answer("Пожалуйста, введите число (например: 70):")

@router.message(UserStates.height)
async def process_height(message: types.Message, state: FSMContext):
    """Обработка роста"""
    try:
        height = float(message.text)
        await state.update_data(height=height)
        await state.set_state(UserStates.age)
        await message.answer("Хорошо! Теперь введите ваш возраст:")
    except ValueError:
        await message.answer("Пожалуйста, введите число (например: 180):")

@router.message(UserStates.age)
async def process_age(message: types.Message, state: FSMContext):
    """Обработка возраста"""
    try:
        age = int(message.text)
        await state.update_data(age=age)
        await state.set_state(UserStates.activity)
        
        keyboard = get_activity_keyboard()
        await message.answer(
            "Сколько минут активности у вас в день?",
            reply_markup=keyboard
        )
        
    except ValueError:
        await message.answer("Пожалуйста, введите целое число (например: 25):")

@router.callback_query(UserStates.activity, F.data.startswith("activity_"))
async def process_activity_callback(callback: types.CallbackQuery, state: FSMContext):
    """Обработка выбора уровня активности"""
    activity_map = {
        'activity_low': 15,
        'activity_medium': 45,
        'activity_high': 75,
        'activity_very_high': 120
    }
    
    activity_minutes = activity_map.get(callback.data, 45)
    await state.update_data(activity=activity_minutes)
    
    await callback.message.edit_text(f"Уровень активности: {activity_minutes} мин/день")
    await callback.answer()
    
    await state.set_state(UserStates.city)
    await callback.message.answer("В каком городе вы находитесь? (для учета погоды)")

@router.message(UserStates.city)
async def process_city(message: types.Message, state: FSMContext):
    """Обработка города"""
    city = message.text
    await state.update_data(city=city)
    await state.set_state(UserStates.gender)
    
    keyboard = get_gender_keyboard()
    await message.answer("Выберите ваш пол:", reply_markup=keyboard)

@router.callback_query(UserStates.gender)
async def process_gender_callback(callback: types.CallbackQuery, state: FSMContext):
    """Обработка выбора пола"""
    from services.calculator import Calculator
    from services.weather_api import WeatherAPI
    
    gender = "male" if callback.data == "gender_male" else "female"
    gender_text = "мужской" if gender == "male" else "женский"
    
    await state.update_data(gender=gender)
    await callback.message.edit_text(f"Пол: {gender_text}")
    await callback.answer()
    
    data = await state.get_data()
    calculator = Calculator()
    
    temperature = await WeatherAPI.get_temperature(data.get('city', 'Moscow'))
    
    water_goal = calculator.calculate_water_norm(
        weight=data['weight'],
        activity_minutes=data['activity'],
        temperature=temperature
    )
    
    calorie_goal = calculator.calculate_calorie_norm(
        weight=data['weight'],
        height=data['height'],
        age=data['age'],
        activity_minutes=data['activity'],
        gender=gender
    )
    
    user_id = callback.from_user.id
    storage.create_user(user_id, {
        **data,
        'water_goal': water_goal,
        'base_water_goal': water_goal,  
        'calorie_goal': calorie_goal,
        'temperature': temperature
    })
    
    await state.clear()
    
    summary = f"""
    Профиль успешно создан!

    Ваши данные:
    • Вес: {data['weight']} кг
    • Рост: {data['height']} см
    • Возраст: {data['age']} лет
    • Активность: {data['activity']} мин/день
    • Город: {data.get('city', 'не указан')}
    • Пол: {gender_text}
    • Температура: {temperature:.1f}°C

    Ваши дневные нормы:
    • Вода: {water_goal} мл (базовая норма)
    • Калории: {calorie_goal} ккал

    Примечание: Норма воды будет увеличиваться при добавлении тренировок
    (+200 мл за каждые 30 минут тренировки)

    Теперь вы можете использовать команды:
    /log_water - записать воду
    /log_food - записать питание
    /log_workout - записать тренировку
    /check_progress - проверить прогресс
    """
    
    await callback.message.answer(summary)