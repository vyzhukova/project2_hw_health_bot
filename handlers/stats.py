from aiogram import Router, types
from aiogram.filters import Command
from aiogram.types import BufferedInputFile
import logging
import io
from datetime import datetime

from utils.storage import storage

logger = logging.getLogger(__name__)
router = Router()

@router.message(Command("stats"))
@router.message(Command("statistics"))
async def show_stats(message: types.Message):
    """Показать статистику и графики"""
    user_id = message.from_user.id
    user_data = storage.get_user(user_id)
    
    if not user_data:
        await message.answer("Сначала настройте профиль: /set_profile")
        return
    
    stats_text = _format_stats_text(user_data)
    await message.answer(stats_text)
    
    try:
        # График воды
        water_image = create_water_chart(user_data)
        if water_image and len(water_image) > 100:  
            await message.answer_photo(
                BufferedInputFile(water_image, filename="water.png"),
                caption="💧 Потребление воды"
            )
        else:
            logger.warning("Не удалось создать график воды")
        
        # График калорий
        calorie_image = create_calories_chart(user_data)
        if calorie_image and len(calorie_image) > 100:
            await message.answer_photo(
                BufferedInputFile(calorie_image, filename="calories.png"),
                caption="🔥 Потребление калорий"
            )
        else:
            logger.warning("Не удалось создать график калорий")
        
        # График макронутриентов (если есть данные)
        if user_data.get('food_log'):
            macro_image = create_macros_chart(user_data['food_log'])
            if macro_image and len(macro_image) > 100:
                await message.answer_photo(
                    BufferedInputFile(macro_image, filename="macros.png"),
                    caption="🍎 Макронутриенты"
                )
        
    except Exception as e:
        logger.error(f"Ошибка при создании графиков: {e}", exc_info=True)
        await message.answer("⚠️ Графики временно недоступны. Используйте текстовую статистику.")

def create_water_chart(user_data: dict) -> bytes:
    """Создать простой график воды"""
    try:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        
        fig, ax = plt.subplots(figsize=(8, 4))
        
        water_history = user_data.get('water_history', {})
        if isinstance(water_history, list):
            water_dict = {}
            for entry in water_history[-7:]:
                if isinstance(entry, dict):
                    water_dict[entry.get('date', '')] = entry.get('amount', 0)
            water_history = water_dict
        
        if water_history:
            dates = sorted(water_history.keys())[-7:]
            amounts = [water_history[date] for date in dates]
            
            simple_dates = []
            for date_str in dates:
                try:
                    date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                    simple_dates.append(date_obj.strftime('%d.%m'))
                except:
                    simple_dates.append(date_str[:5])
            
            ax.bar(simple_dates, amounts, color='lightblue')
            ax.set_xlabel('Дата')
            ax.set_ylabel('Вода (мл)')
            ax.set_title('Потребление воды')
            
            goal = user_data.get('water_goal')
            if goal:
                ax.axhline(y=goal, color='red', linestyle='--', alpha=0.5)
        
        else:
            ax.text(0.5, 0.5, 'Нет данных о воде', 
                   ha='center', va='center', fontsize=14)
        
        plt.tight_layout()
        
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=80, bbox_inches='tight')
        buf.seek(0)
        result = buf.getvalue()
        plt.close(fig)
        return result
        
    except Exception as e:
        print(f"Ошибка при создании графика воды: {e}")
        return b''

def create_calories_chart(user_data: dict) -> bytes:
    """Создать простой график калорий"""
    try:
        # Импорты внутри функции для изоляции
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        
        fig, ax = plt.subplots(figsize=(8, 4))
        
        calorie_history = user_data.get('calorie_history', {})
        processed_data = {}
        
        if isinstance(calorie_history, list):
            recent_entries = calorie_history[-7:] if calorie_history else []
            for entry in recent_entries:
                if isinstance(entry, dict):
                    date_val = entry.get('date', '')
                    calories_val = entry.get('calories', 0)
                    if date_val:
                        processed_data[date_val] = calories_val
        elif isinstance(calorie_history, dict):
            sorted_dates = sorted(calorie_history.keys())
            recent_dates = sorted_dates[-7:] if sorted_dates else []
            for date in recent_dates:
                processed_data[date] = calorie_history.get(date, 0)
        
        if processed_data:
            dates = sorted(processed_data.keys())
            calories = [processed_data[date] for date in dates]
            
            formatted_dates = []
            for date_str in dates:
                try:
                    date_obj = datetime.strptime(str(date_str), '%Y-%m-%d')
                    formatted_dates.append(date_obj.strftime('%d.%m'))
                except (ValueError, TypeError):
                    formatted_dates.append(str(date_str)[:5])
            
            ax.bar(formatted_dates, calories, color='orange', alpha=0.7)
            ax.set_xlabel('Дата')
            ax.set_ylabel('Калории (ккал)')
            ax.set_title('Потребление калорий')
            
            goal = user_data.get('calorie_goal')
            if goal and isinstance(goal, (int, float)):
                ax.axhline(y=goal, color='red', linestyle='--', alpha=0.5, 
                        label=f'Цель: {goal} ккал')
                ax.legend()
            
            plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
            
        else:
            # Нет данных
            ax.text(0.5, 0.5, 'Нет данных о калориях', 
                ha='center', va='center', fontsize=14, 
                transform=ax.transAxes)
            ax.set_xticks([])
            ax.set_yticks([])
        
        plt.tight_layout()
        
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=80, bbox_inches='tight')
        buf.seek(0)
        result = buf.getvalue()
        plt.close(fig)
        
        return result
    
    except Exception as e:
        print(f"Ошибка при создании графика калорий: {e}")
        import traceback
        traceback.print_exc()
        return b''

def create_macros_chart(food_log: list) -> bytes:
    """Создать простой график макронутриентов"""
    try:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        
        fig, ax = plt.subplots(figsize=(6, 6))
        
        if not food_log:
            ax.text(0.5, 0.5, 'Нет данных\nо питании', 
                   ha='center', va='center', fontsize=14)
            ax.axis('off')
        else:
            protein = sum(food.get('protein', 0) for food in food_log)
            carbs = sum(food.get('carbs', 0) for food in food_log)
            fat = sum(food.get('fat', 0) for food in food_log)
            
            labels = ['Белки', 'Углеводы', 'Жиры']
            sizes = [protein, carbs, fat]
            colors = ['lightgreen', 'gold', 'lightcoral']
            
            filtered_labels = []
            filtered_sizes = []
            filtered_colors = []
            
            for label, size, color in zip(labels, sizes, colors):
                if size > 0:
                    filtered_labels.append(label)
                    filtered_sizes.append(size)
                    filtered_colors.append(color)
            
            if filtered_sizes:
                ax.pie(filtered_sizes, labels=filtered_labels, colors=filtered_colors,
                      autopct='%1.1f%%', startangle=90)
                ax.set_title('Макронутриенты')
            else:
                ax.text(0.5, 0.5, 'Нет данных\nо макронутриентах', 
                       ha='center', va='center', fontsize=14)
                ax.axis('off')
        
        plt.tight_layout()
        
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=80, bbox_inches='tight')
        buf.seek(0)
        result = buf.getvalue()
        plt.close(fig)
        return result
        
    except Exception as e:
        print(f"Ошибка при создании графика макронутриентов: {e}")
        return b''

def _format_stats_text(user_data: dict) -> str:
    """Форматировать текстовую статистику"""
    # Базовые данные
    weight = user_data.get('weight', 'не указан')
    height = user_data.get('height', 'не указан')
    age = user_data.get('age', 'не указан')
    gender = user_data.get('gender', 'не указан')
    gender_text = "мужской" if gender == 'male' else ("женский" if gender == 'female' else "не указан")
    
    # Цели
    water_goal = user_data.get('water_goal', 0)
    calorie_goal = user_data.get('calorie_goal', 0)
    
    # Текущие показатели
    water_today = user_data.get('logged_water', 0)
    calories_today = user_data.get('logged_calories', 0)
    burned_today = user_data.get('burned_calories', 0)
    balance_today = calories_today - burned_today
    
    # Прогресс
    water_progress = (water_today / water_goal * 100) if water_goal > 0 else 0
    calorie_progress = (balance_today / calorie_goal * 100) if calorie_goal > 0 else 0
    
    # Логи еды и тренировок
    food_log = user_data.get('food_log', [])
    workout_log = user_data.get('workout_log', [])
    
    # Статистика питания
    food_stats = _calculate_food_stats(food_log)
    workout_stats = _calculate_workout_stats(workout_log)
    
    # История (последние 3 дня)
    history_text = _format_history(user_data)
    
    return f"""
📊 **ПОЛНАЯ СТАТИСТИКА**

👤 **Профиль:**
• Вес: {weight} кг
• Рост: {height} см
• Возраст: {age} лет
• Пол: {gender_text}

🎯 **Дневные цели:**
• Вода: {water_goal} мл
• Калории: {calorie_goal} ккал

📈 **Сегодня:**
💧 Вода: {water_today}/{water_goal} мл ({water_progress:.1f}%)
{'✅ Достигнута!' if water_today >= water_goal else '⏳ В процессе...'}

🔥 Калории:
• Потреблено: {calories_today} ккал
• Сожжено: {burned_today} ккал
• Баланс: {balance_today} ккал из {calorie_goal} ({calorie_progress:.1f}%)
{'⚠️ Превышение!' if balance_today > calorie_goal else '✅ В норме' if balance_today <= calorie_goal else ''}

🍎 **Питание:**
• Приемов пищи: {len(food_log)}
• Всего калорий: {food_stats['total_calories']:.0f} ккал
• Белки: {food_stats['total_protein']:.1f} г
• Углеводы: {food_stats['total_carbs']:.1f} г
• Жиры: {food_stats['total_fat']:.1f} г

🏃‍♂️ **Тренировки:**
• Количество: {len(workout_log)}
• Общее время: {workout_stats['total_minutes']} мин
• Сожжено калорий: {workout_stats['total_calories']:.0f} ккал

{history_text}

💡 **Рекомендации:**
{_get_recommendations(water_progress, calorie_progress, len(workout_log))}
"""

def _format_history(user_data: dict) -> str:
    """Форматировать историю"""
    water_history = user_data.get('water_history', {})
    calorie_history = user_data.get('calorie_history', {})
    
    if not water_history and not calorie_history:
        return "📅 **История:**\nНет данных за предыдущие дни."
    
    # Преобразуем историю воды
    water_items = []
    if isinstance(water_history, dict):
        for date, amount in list(water_history.items())[-3:]:  # Последние 3 дня
            water_items.append(f"  {date}: {amount} мл")
    elif isinstance(water_history, list):
        for entry in water_history[-3:]:
            if isinstance(entry, dict):
                water_items.append(f"  {entry.get('date', '')}: {entry.get('amount', 0)} мл")
    
    # Преобразуем историю калорий
    calorie_items = []
    if isinstance(calorie_history, dict):
        for date, calories in list(calorie_history.items())[-3:]:
            calorie_items.append(f"  {date}: {calories} ккал")
    elif isinstance(calorie_history, list):
        for entry in calorie_history[-3:]:
            if isinstance(entry, dict):
                calorie_items.append(f"  {entry.get('date', '')}: {entry.get('calories', 0)} ккал")
    
    history_text = "📅 **История (последние 3 дня):**\n"
    if water_items:
        history_text += "💧 Вода:\n" + "\n".join(water_items) + "\n"
    if calorie_items:
        history_text += "🔥 Калории:\n" + "\n".join(calorie_items)
    
    return history_text.strip()

def _get_recommendations(water_progress: float, calorie_progress: float, workouts_count: int) -> str:
    """Получить рекомендации"""
    recommendations = []
    
    if water_progress < 50:
        recommendations.append("• Пейте больше воды! Стакан каждый час.")
    elif water_progress < 80:
        recommendations.append("• Хороший темп по воде, продолжайте!")
    else:
        recommendations.append("• Отлично с водой!")
    
    if calorie_progress < 30:
        recommendations.append("• Можете позволить себе полноценный прием пищи.")
    elif calorie_progress < 70:
        recommendations.append("• Сбалансируйте следующие приемы пищи.")
    elif calorie_progress < 100:
        recommendations.append("• Близко к цели. Легкий ужин?")
    else:
        recommendations.append("• Вы достигли/превысили норму калорий.")
    
    if workouts_count == 0:
        recommendations.append("• Сегодня не было тренировок. 20-минутная прогулка?")
    elif workouts_count < 2:
        recommendations.append("• Отличная работа! Добавьте растяжку.")
    
    return "\n".join(recommendations) if recommendations else "• Продолжайте в том же духе!"

def _calculate_food_stats(food_log: list) -> dict:
    """Рассчитать статистику питания"""
    if not food_log:
        return {
            'total_calories': 0,
            'total_protein': 0,
            'total_carbs': 0,
            'total_fat': 0
        }
    
    total_calories = sum(food.get('calories', 0) for food in food_log)
    total_protein = sum(food.get('protein', 0) for food in food_log)
    total_carbs = sum(food.get('carbs', 0) for food in food_log)
    total_fat = sum(food.get('fat', 0) for food in food_log)
    
    return {
        'total_calories': total_calories,
        'total_protein': total_protein,
        'total_carbs': total_carbs,
        'total_fat': total_fat
    }

def _calculate_workout_stats(workout_log: list) -> dict:
    """Рассчитать статистику тренировок"""
    if not workout_log:
        return {
            'total_minutes': 0,
            'total_calories': 0
        }
    
    total_minutes = sum(workout.get('duration', 0) for workout in workout_log)
    total_calories = sum(workout.get('calories', 0) for workout in workout_log)
    
    return {
        'total_minutes': total_minutes,
        'total_calories': total_calories
    }