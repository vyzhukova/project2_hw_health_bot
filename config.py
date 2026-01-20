import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "")
    
    PARSE_MODE = "HTML"
    
    NUTRITION_API_TIMEOUT = 10
    WEATHER_API_TIMEOUT = 10
    
config = Config()