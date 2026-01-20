import aiohttp
import logging
from typing import Dict, Optional
from config import config

logger = logging.getLogger(__name__)

class WeatherAPI:
    
    @staticmethod
    async def get_temperature(city: str) -> Optional[float]:
        """Получение температуры для города"""
        try:
            api_key = config.OPENWEATHER_API_KEY
            if not api_key:
                logger.warning("OPENWEATHER_API_KEY не установлен")
                return config.DEFAULT_TEMPERATURE
            
            url = "http://api.openweathermap.org/data/2.5/weather"
            params = {
                'q': city,
                'appid': api_key,
                'units': 'metric',
                'lang': 'ru'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, timeout=10) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data['main']['temp']
                    else:
                        logger.warning(f"Не удалось получить погоду: {response.status}")
                        return config.DEFAULT_TEMPERATURE
        except Exception as e:
            logger.error(f"Ошибка при получении погоды: {e}")
            return config.DEFAULT_TEMPERATURE
    
    @staticmethod
    async def get_weather_info(city: str) -> Optional[Dict]:
        """Получение полной информации о погоде"""
        try:
            api_key = config.OPENWEATHER_API_KEY
            if not api_key:
                return None
            
            url = "http://api.openweathermap.org/data/2.5/weather"
            params = {
                'q': city,
                'appid': api_key,
                'units': 'metric',
                'lang': 'ru'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, timeout=10) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {
                            'temperature': data['main']['temp'],
                            'feels_like': data['main']['feels_like'],
                            'humidity': data['main']['humidity'],
                            'description': data['weather'][0]['description'],
                            'city': data['name']
                        }
            return None
        except Exception as e:
            logger.error(f"Ошибка при получении погоды: {e}")
            return None