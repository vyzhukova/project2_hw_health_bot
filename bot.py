import os
import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from dotenv import load_dotenv

from handlers.start import router as start_router
from handlers.profile import router as profile_router
from handlers.water import router as water_router
from handlers.food import router as food_router
from handlers.workout import router as workout_router
from handlers.progress import router as progress_router
from handlers.stats import router as stats_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

async def main():
    """Основная функция запуска бота"""
    load_dotenv()
    
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    if not BOT_TOKEN:
        logger.error("BOT_TOKEN не установлен в переменных окружения")
        print("Установите переменную окружения BOT_TOKEN")
        return
    
    bot = Bot(
        token=BOT_TOKEN, 
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    
    dp = Dispatcher()
    dp.include_router(start_router)
    dp.include_router(profile_router)
    dp.include_router(water_router)
    dp.include_router(food_router)
    dp.include_router(workout_router)
    dp.include_router(progress_router)
    dp.include_router(stats_router)
    
    logger.info("Бот запущен")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Бот остановлен")