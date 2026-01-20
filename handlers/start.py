from aiogram import Router, types
from aiogram.filters import Command, CommandStart

router = Router()

@router.message(CommandStart())
@router.message(Command("start"))
async def start_command(message: types.Message):
    welcome_text = """
    Здравствуйте! Я ваш персональный помощник по здоровью!

    Доступные команды:
    /set_profile - Настроить профиль
    /log_water [количество] - Записать выпитую воду (мл)
    /log_food [продукт] - Записать съеденный продукт
    /check_progress - Проверить прогресс
    /log_workout - Записать тренировку
    /help - Показать справку

    Начните с настройки профиля: /set_profile
    """
    await message.answer(welcome_text)

@router.message(Command("help"))
async def help_command(message: types.Message):
    help_text = """
    Список доступных команд:

    Профиль:
    /set_profile - Настроить профиль

    Вода:
    /log_water 500 - Записать 500 мл выпитой воды

    Питание:
    /log_food банан - Записать съеденный продукт

    Тренировки:
    /log_workout - Записать тренировку

    Прогресс:
    /check_progress - Показать текущий прогресс
    /stats - Показать статистику
    /recommend - Получить рекомендации

    Утилиты:
    /reset_day - Сбросить данные на день
    /help - Показать эту справку
    """
    await message.answer(help_text)