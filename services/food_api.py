import requests
import logging
from typing import Optional, Dict

logger = logging.getLogger(__name__)

class NutritionAPI:
    """Класс для работы с API пищевых продуктов"""
    
    @staticmethod
    async def search_product(product_name: str) -> Optional[Dict]:
        """Поиск информации о продукте через OpenFoodFacts"""
        url = f"https://world.openfoodfacts.org/cgi/search.pl?action=process&search_terms={product_name}&json=true"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            products = data.get('products', [])
            if products:  
                product = products[0]
                nutriments = product.get('nutriments', {})
                calories = nutriments.get('energy-kcal_100g', 0)
                return {
                    'name': product.get('product_name', product_name),
                    'calories': round(float(calories), 2),
                    'protein': nutriments.get('proteins_100g', 0),
                    'carbs': nutriments.get('carbohydrates_100g', 0),
                    'fat': nutriments.get('fat_100g', 0)
                }
            return None
        print(f"Ошибка: {response.status_code}")
        return None                    