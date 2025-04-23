import requests
import json
import asyncio
from token_generator import get_token  # Импортируем функцию get_token

# --- Константы (замени на свои значения) ---
BASE_URL = "https://api.cdek.ru/v2"  # Или тестовый URL

async def get_city(id, city_name, country_code="RU", region_code=None):
    """
    Получает информацию о конкретном населенном пункте по его наименованию.
    Возвращает только первый результат, если он есть.

    Args:
        city_name (str): Название города для поиска.
        country_code (str, optional): Код страны в формате ISO_3166-1_alpha-2. Defaults to "RU".
        region_code (str, optional): Код региона. Defaults to None.

    Returns:
        dict: Информация о городе (словарь) или None, если город не найден.
    """
    auth_token = get_token(id)
    url = f"{BASE_URL}/location/suggest/cities"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {auth_token}"
    }
    params = {
        "name": city_name,  # Параметр для поиска по названию города (обязательный)
        "country_code": country_code  # Обязательный параметр (если знаем страну)
    }

    if region_code:
        params["region_code"] = region_code

    try:
        response = requests.get(url, headers=headers, params=params, timeout=10000)
        response.raise_for_status()  # Проверка на ошибки HTTP
        cities = response.json()
        if cities and len(cities) > 0:
            return cities[0]  # Возвращаем первый город
        else:
            print(f"Город '{city_name}' не найден.")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при подборе города: {e}")
        if response is not None:
            print(f"Response status code: {response.status_code}")
            print(f"Response text: {response.text}")
        return None
    except json.JSONDecodeError as e:
        print(f"Ошибка при разборе ответа JSON: {e}")
        return None

# # --- Пример использования ---
# if __name__ == "__main__":
#     async def main():
#         city_name = "Краснодар"
#         country_code = "RU"  # Код России
#
#         city = await get_city(city_name, country_code)
#
#         if city:
#             print(f"Найден город '{city_name}':")
#             print(json.dumps(city, indent=4, ensure_ascii=False))
#         else:
#             print("Не удалось найти город.")
#
#     asyncio.run(main())