import io
import matplotlib
matplotlib.use('Agg') 
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

class Charts:
    """Простой класс для создания графиков без сложных настроек"""
    
    @staticmethod
    def create_water_chart(user_data: dict) -> bytes:
        """Создать простой график воды"""
        try:
            fig, ax = plt.subplots(figsize=(8, 4))
            
            # Получаем историю воды
            water_history = user_data.get('water_history', {})
            if isinstance(water_history, list):
                # Конвертируем список в словарь
                water_dict = {}
                for entry in water_history[-7:]:
                    if isinstance(entry, dict):
                        water_dict[entry.get('date', '')] = entry.get('amount', 0)
                water_history = water_dict
            
            if water_history:
                dates = sorted(water_history.keys())[-7:]
                amounts = [water_history[date] for date in dates]
                
                # Создаем простые метки (только день)
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
                
                # Целевая линия
                goal = user_data.get('water_goal')
                if goal:
                    ax.axhline(y=goal, color='red', linestyle='--', alpha=0.5)
            
            else:
                ax.text(0.5, 0.5, 'Нет данных о воде', 
                       ha='center', va='center', fontsize=14)
            
            plt.tight_layout()
            
            buf = io.BytesIO()
            plt.savefig(buf, format='png', dpi=80)
            buf.seek(0)
            plt.close(fig)
            return buf.getvalue()
            
        except Exception as e:
            print(f"Ошибка при создании графика воды: {e}")
            return b''
    
    @staticmethod
    def create_calories_chart(user_data: dict) -> bytes:
        """Создать простой график калорий"""
        try:
            plt.close('all')  
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
                
                bars = ax.bar(formatted_dates, calories, color='orange', alpha=0.7)
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
                ax.text(0.5, 0.5, 'Нет данных о калориях', 
                    ha='center', va='center', fontsize=14, 
                    transform=ax.transAxes)
                ax.set_xticks([])
                ax.set_yticks([])
            
            fig.tight_layout()
            
            buf = io.BytesIO()
            fig.savefig(buf, format='png', dpi=80, bbox_inches='tight')
            buf.seek(0)
            
            plt.close(fig)
            
            return buf.getvalue()
        
        except Exception as e:
            print(f"Ошибка при создании графика калорий: {e}")
            import traceback
            traceback.print_exc()
            return b''
    
    @staticmethod
    def create_macros_chart(food_log: list) -> bytes:
        """Создать простой график макронутриентов"""
        try:
            fig, ax = plt.subplots(figsize=(6, 6))
            
            if not food_log:
                ax.text(0.5, 0.5, 'Нет данных\nо питании', 
                       ha='center', va='center', fontsize=14)
                ax.axis('off')
            else:
                # Считаем макронутриенты
                protein = sum(food.get('protein', 0) for food in food_log)
                carbs = sum(food.get('carbs', 0) for food in food_log)
                fat = sum(food.get('fat', 0) for food in food_log)
                
                # Создаем данные для круговой диаграммы
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
            plt.savefig(buf, format='png', dpi=80)
            buf.seek(0)
            plt.close(fig)
            return buf.getvalue()
            
        except Exception as e:
            print(f"Ошибка при создании графика макронутриентов: {e}")
            return b''