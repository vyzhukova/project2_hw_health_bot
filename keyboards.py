from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_gender_keyboard():
    """Клавиатура для выбора пола"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Мужской", callback_data="gender_male"),
                InlineKeyboardButton(text="Женский", callback_data="gender_female")
            ]
        ]
    )

def get_activity_keyboard():
    """Клавиатура для выбора уровня активности"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Менее 30 мин", callback_data="activity_low"),
                InlineKeyboardButton(text="30-60 мин", callback_data="activity_medium")
            ],
            [
                InlineKeyboardButton(text="60-90 мин", callback_data="activity_high"),
                InlineKeyboardButton(text="Более 90 мин", callback_data="activity_very_high")
            ]
        ]
    )

def get_workout_types_keyboard():
    """Клавиатура для выбора типа тренировки"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Бег", callback_data="workout_бег"),
                InlineKeyboardButton(text="Ходьба", callback_data="workout_ходьба")
            ],
            [
                InlineKeyboardButton(text="Плавание", callback_data="workout_плавание"),
                InlineKeyboardButton(text="Велосипед", callback_data="workout_велосипед")
            ],
            [
                InlineKeyboardButton(text="Силовая", callback_data="workout_силовая"),
                InlineKeyboardButton(text="Йога", callback_data="workout_йога")
            ],
            [
                InlineKeyboardButton(text="Теннис", callback_data="workout_теннис"),
                InlineKeyboardButton(text="Футбол", callback_data="workout_футбол")
            ]
        ]
    )