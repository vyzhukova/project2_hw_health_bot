from typing import Dict, List

class Helpers:
    
    @staticmethod
    def create_progress_bar(current: float, goal: float, width: int = 20) -> str:
        """Создать прогресс-бар"""
        if goal == 0:
            return "[" + " " * width + "]"
        
        progress = min(current / goal, 1.0)
        filled = int(width * progress)
        bar = "█" * filled + "░" * (width - filled)
        percentage = int(progress * 100)
        
        return f"[{bar}] {percentage}%"
    
    @staticmethod
    def format_water_response(amount: float, total: float, goal: float) -> str:
        """Форматировать ответ о воде"""
        remaining = max(0, goal - total)
        percentage = (total / goal * 100) if goal > 0 else 0
        
        return f"""
        Добавлено: {amount} мл

        Общий прогресс:
        Выпито: {total:.0f}/{goal:.0f} мл ({percentage:.1f}%)
        Осталось: {remaining:.0f} мл

        {Helpers.create_progress_bar(total, goal)}
        """
    
    @staticmethod
    def format_calorie_response(food_info: Dict, amount: float, calories: float, total: float) -> str:
        """Форматировать ответ о калориях"""
        return f"""
        Записано: {food_info['name']} - {amount}г

        Пищевая ценность:
        • Калории: {calories:.1f} ккал
        • Белки: {((food_info['protein'] * amount) / 100):.1f} г
        • Углеводы: {((food_info['carbs'] * amount) / 100):.1f} г
        • Жиры: {((food_info['fat'] * amount) / 100):.1f} г

        Всего потреблено за день: {total:.1f} ккал
        """
    
    @staticmethod
    def get_recommendations(water_percentage: float, calorie_percentage: float, has_workout: bool) -> List[str]:
        """Получить рекомендации на основе прогресса"""
        recommendations = []
        
        # Рекомендации по воде
        if water_percentage < 30:
            recommendations.append("Вы выпили меньше 30% от нормы. Старайтесь пить по стакану воды каждый час.")
        elif water_percentage < 60:
            recommendations.append("Хороший темп! Продолжайте пить воду равномерно в течение дня.")
        elif water_percentage < 90:
            recommendations.append("Отлично! Вы близки к достижению цели по воде.")
        else:
            recommendations.append("Поздравляем! Вы достигли дневной нормы воды!")
        
        # Рекомендации по калориям
        if calorie_percentage < 30:
            recommendations.append("У вас еще много калорий в запасе. Не пропускайте приемы пищи.")
        elif calorie_percentage < 60:
            recommendations.append("Вы в хорошем темпе. Следующий прием пищи может быть полноценным.")
        elif calorie_percentage < 90:
            recommendations.append("Вы близки к цели. Рассмотрите легкий ужин.")
        else:
            recommendations.append("Вы достигли или превысили дневную норму калорий.")
        
        # Рекомендации по тренировкам
        if not has_workout:
            recommendations.append("Сегодня еще не было тренировок. 30 минут ходьбы помогут улучшить метаболизм.")
        
        return recommendations