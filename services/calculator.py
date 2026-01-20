class Calculator:
    """Класс для расчета норм"""
    
    @staticmethod
    def calculate_water_norm(weight: float, activity_minutes: int, temperature: float = 20.0) -> float:
        """Расчет базовой нормы воды в мл"""
        base_norm = weight * 30
        
        # Добавка за общую дневную активность
        activity_add = (activity_minutes / 30) * 500
        
        # Добавка за жаркую погоду
        weather_add = 0
        if temperature > 25:
            weather_add = 500 + (temperature - 25) * 100
            weather_add = min(weather_add, 1000) 
        
        total = base_norm + activity_add + weather_add
        return round(total)
    
    @staticmethod
    def calculate_calorie_norm(weight: float, height: float, age: int, 
                               activity_minutes: int, gender: str = 'male') -> float:
        """Расчет нормы калорий по формуле"""
        if gender.lower() == 'female':
            bmr = 10 * weight + 6.25 * height - 5 * age - 161
        else:
            bmr = 10 * weight + 6.25 * height - 5 * age + 5
        
        if activity_minutes < 30:
            activity_factor = 1.2
        elif activity_minutes < 60:
            activity_factor = 1.375
        elif activity_minutes < 90:
            activity_factor = 1.55
        else:
            activity_factor = 1.725
        
        workout_calories = activity_minutes * 7
        total_calories = (bmr * activity_factor) + workout_calories
        
        return round(total_calories)
    
    @staticmethod
    def calculate_workout_calories(workout_type: str, duration: int, weight: float) -> float:
        """Расчет сожженных калорий за тренировку"""
        calories_per_minute = {
            'бег': 10,
            'ходьба': 5,
            'плавание': 8,
            'велосипед': 7,
            'силовая': 6,
            'йога': 4,
            'аэробика': 8,
            'теннис': 9,
            'футбол': 10,
            'баскетбол': 9
        }
        
        base_rate = calories_per_minute.get(workout_type.lower(), 5)
        weight_factor = weight / 70
        
        return round(base_rate * duration * weight_factor)
    
    @staticmethod
    def calculate_workout_water(duration: int) -> int:
        """Расчет дополнительной воды для тренировки (200 мл за каждые 30 минут)"""
        periods = duration // 30
        return periods * 200
    
    @staticmethod
    def get_workout_water_recommendation(duration: int) -> str:
        """Получить рекомендацию по воде для тренировки"""
        additional_water = Calculator.calculate_workout_water(duration)
        if additional_water > 0:
            return f"Во время/после тренировки выпейте дополнительно {additional_water} мл воды"
        return "Не забывайте пить воду во время тренировки"