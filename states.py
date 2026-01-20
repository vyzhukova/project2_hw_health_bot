from aiogram.fsm.state import State, StatesGroup

class UserStates(StatesGroup):
    weight = State()
    height = State()
    age = State()
    activity = State()
    city = State()
    gender = State()
    calorie_goal = State()
    food_amount = State()
    workout_type = State()
    workout_duration = State()