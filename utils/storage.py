import logging
from datetime import datetime, date
from typing import Dict, Optional

logger = logging.getLogger(__name__)

class UserStorage:
    """Класс для хранения данных пользователей"""
    
    def __init__(self):
        self.users: Dict[int, Dict] = {}
    
    def get_user(self, user_id: int) -> Optional[Dict]:
        """Получить данные пользователя"""
        return self.users.get(user_id)
    
    def create_user(self, user_id: int, user_data: Dict):
        """Создать нового пользователя"""
        self.users[user_id] = {
            **user_data,
            'logged_water': 0,
            'logged_calories': 0,
            'burned_calories': 0,
            'food_log': [],
            'workout_log': []
        }
    
    def update_user(self, user_id: int, updates: Dict):
        """Обновить данные пользователя"""
        if user_id in self.users:
            self.users[user_id].update(updates)
    
    def add_food(self, user_id: int, food_entry: Dict):
        """Добавить еду"""
        if user_id in self.users:
            today = date.today().isoformat()
            
            food_log = self.users[user_id].get('food_log', [])
            food_log.append(food_entry)
            
            current_calories = self.users[user_id].get('logged_calories', 0) + food_entry['calories']
            calorie_history = self.users[user_id].get('calorie_history', {})
            calorie_history[today] = current_calories
            
            self.update_user(user_id, {
                'logged_calories': current_calories,
                'food_log': food_log,
                'calorie_history': calorie_history
            })


    def update_water_goal_with_workouts(self, user_id: int, calculator):
        """Обновить норму воды с учетом всех тренировок за сегодня"""
        user_data = self.get_user(user_id)
        if not user_data:
            return
        
        # Рассчитываем базовую норму воды (без учета тренировок)
        base_activity = user_data.get('activity', 45)  
        temperature = user_data.get('temperature', 20.0)
        
        base_water_goal = calculator.calculate_water_norm(
            weight=user_data['weight'],
            activity_minutes=base_activity,
            temperature=temperature
        )
        
        # Суммируем дополнительную воду за все сегодняшние тренировки
        total_additional_water = 0
        today = datetime.now().strftime('%Y-%m-%d')
        
        for workout in user_data.get('workout_log', []):
            workout_date = workout.get('date', '')
            if today in workout_date:  
                total_additional_water += workout.get('additional_water', 0)
        
        new_water_goal = base_water_goal + total_additional_water
        
        self.update_user(user_id, {
            'water_goal': new_water_goal,
            'base_water_goal': base_water_goal  
        })
        
        return new_water_goal

    def add_workout(self, user_id: int, workout_entry: Dict):
        """Добавить тренировку"""
        if user_id in self.users:
            today = datetime.now().strftime('%Y-%m-%d')
            
            current_burned = self.users[user_id].get('burned_calories', 0) + workout_entry['calories']
            
            workout_log = self.users[user_id].get('workout_log', [])
            workout_log.append(workout_entry)
            
            burned_history = self.users[user_id].get('burned_history', [])
            
            found = False
            for entry in burned_history:
                if entry.get('date') == today:
                    entry['calories'] = current_burned
                    found = True
                    break
            
            if not found:
                burned_history.append({'date': today, 'calories': current_burned})
            
            self.update_user(user_id, {
                'burned_calories': current_burned,
                'workout_log': workout_log,
                'burned_history': burned_history
            })
        
    def get_daily_progress(self, user_id: int) -> Dict:
        """Получить дневной прогресс"""
        if user_id not in self.users:
            return {}
        
        user_data = self.users[user_id]
        
        water_goal = user_data.get('water_goal', 2000)
        calorie_goal = user_data.get('calorie_goal', 2000)
        
        water_logged = user_data.get('logged_water', 0)
        calorie_logged = user_data.get('logged_calories', 0)
        calorie_burned = user_data.get('burned_calories', 0)
        
        water_remaining = max(0, water_goal - water_logged)
        calorie_balance = calorie_logged - calorie_burned
        calorie_remaining = max(0, calorie_goal - calorie_balance)
        
        return {
            'water': {
                'logged': water_logged,
                'goal': water_goal,
                'remaining': water_remaining,
                'percentage': (water_logged / water_goal * 100) if water_goal > 0 else 0
            },
            'calories': {
                'logged': calorie_logged,
                'burned': calorie_burned,
                'balance': calorie_balance,
                'goal': calorie_goal,
                'remaining': calorie_remaining,
                'percentage': (calorie_balance / calorie_goal * 100) if calorie_goal > 0 else 0
            }
        }
    
    def reset_daily_data(self, user_id: int):
        """Сбросить дневные данные"""
        if user_id in self.users:
            # Сохраняем историю
            today = date.today().isoformat()
            
            self.users[user_id]['water_history'].append({
                'date': today,
                'amount': self.users[user_id]['logged_water']
            })
            
            self.users[user_id]['calorie_history'].append({
                'date': today,
                'calories': self.users[user_id]['logged_calories']
            })
            
            self.users[user_id]['burned_history'].append({
                'date': today,
                'calories': self.users[user_id]['burned_calories']
            })
            
            # Сбрасываем текущие значения
            self.users[user_id]['logged_water'] = 0
            self.users[user_id]['logged_calories'] = 0
            self.users[user_id]['burned_calories'] = 0
            self.users[user_id]['food_log'] = []
            self.users[user_id]['workout_log'] = []
            
            self.save_to_file()

storage = UserStorage()