import requests
import json
from token_generator import get_token  # Импортируем функцию get_token
from cdek_cod_city import get_city  # Импортируем функцию get_city
from geopy.distance import geodesic
import asyncio
import time
from geopy.geocoders import Nominatim

BASE_URL = "https://api.cdek.ru/v2"  # Или тестовый URL

async def get_delivery_points(
    code: str = None,
    type: str = None,
    postal_code: str = None,
    city_code: int = None,
    country_code: str = None,
    region_code: int = None,
    have_cashless: bool = None,
    have_cash: bool = None,
    allowed_cod: bool = None,
    is_dressing_room: bool = None,
    weight_max: int = None,
    weight_min: int = None,
    lang: str = None,
    take_only: bool = None,
    is_handout: bool = None,
    is_reception: bool = None,
    is_marketplace: bool = None,
    is_ltl: bool = None,
    fulfillment: bool = None,
    fias_guid: str = None,
    size: int = None,
    page: int = None
):
    """
    Получает список офисов СДЭК, используя указанные параметры.

    Args:
        code (str, optional): Код ПВЗ.
        type (str, optional): Тип офиса ("POSTAMAT", "PVZ", "ALL"). Defaults to "ALL" if None.
        postal_code (str, optional): Почтовый индекс города.
        city_code (int, optional): Код населенного пункта СДЭК.
        country_code (str, optional): Код страны в формате ISO_3166-1_alpha-2.
        region_code: bool = None
        weight_max: bool = None
        weight_min: bool = None
        lang: bool = None
        take_only: bool = None
        is_handout: bool = None
        is_reception: bool = None
        is_marketplace: bool = None
        is_ltl: bool = None
        fulfillment: bool = None
        fias_guid: bool = None
        size: int = None
        page: bool = None
    """
    auth_token = get_token()
    url = f"{BASE_URL}/deliverypoints"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {auth_token}"
    }

    params = {}
    if code is not None:
        params["code"] = code
    if type is not None:
        params["type"] = type
    if postal_code is not None:
        params["postal_code"] = postal_code
    if city_code is not None:
        params["city_code"] = city_code
    if country_code is not None:
        params["country_code"] = country_code
    if region_code is not None:
        params["region_code"] = region_code
    if have_cashless is not None:
        params["have_cashless"] = "true" if have_cashless else "false"
    if have_cash is not None:
        params["have_cash"] = "true" if have_cash else "false"
    if allowed_cod is not None:
        params["allowed_cod"] = "true" if allowed_cod else "false"
    if is_dressing_room is not None:
        params["is_dressing_room"] = "true" if is_dressing_room else "false"
    if weight_max is not None:
        params["weight_max"] = weight_max
    if weight_min is not None:
        params["weight_min"] = weight_min
    if lang is not None:
        params["lang"] = lang
    if take_only is not None:
        params["take_only"] = "true" if take_only else "false"
    if is_handout is not None:
        params["is_handout"] = "true" if is_handout else "false"
    if is_reception is not None:
        params["is_reception"] = "true" if is_reception else "false"
    if is_marketplace is not None:
        params["is_marketplace"] = "true" if is_marketplace else "false"
    if is_ltl is not None:
        params["is_ltl"] = "true" if is_ltl else "false"
    if fulfillment is not None:
        params["fulfillment"] = "true" if fulfillment else "false"
    if fias_guid is not None:
        params["fias_guid"] = fias_guid
    if size is not None:
        params["size"] = size
    if page is not None:
        params["page"] = page

    try:
        response = requests.get(url, headers=headers, params=params, timeout=10000)
        response.raise_for_status()  # Проверка на ошибки HTTP
        delivery_points = response.json()  # Предполагаем, что возвращается список
        return delivery_points
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при получении списка офисов: {e}")
        if response is not None:
            print(f"Response status code: {response.status_code}")
            print(f"Response text: {response.text}")
        return None
    except json.JSONDecodeError as e:
        print(f"Ошибка при разборе ответа JSON: {e}")
        return None


async def get_coordinates(city, address):
    geolocator = Nominatim(user_agent="MyCdekOfficeLocator/1.0")
    full_address = f"{city}, {address}"
    try:
        location = await asyncio.to_thread(geolocator.geocode, full_address, timeout=10000)
        if location:
            print(location.address)
            print((location.latitude, location.longitude))
            return (location.latitude, location.longitude)
        else:
            print(f"Не удалось найти координаты для адреса: {full_address}")
            return None
    except Exception as e:
        print(f"Ошибка при геокодировании: {e}")
        return None
    finally:
        time.sleep(1)  # Задержка в 1 секунду между запросами

async def get_nearest_gdp_offices(city_name: str, my_address: str, max_offices: int = 5):
    """
    Получает список ближайших офисов GDP.

    Args:
        city_name: Название города.
        my_address: Адрес пользователя.
        max_offices: Максимальное количество офисов для возврата.

    Returns:
        Список словарей с информацией о ближайших офисах GDP.
    """

    country_code = "RU"

    city = await get_city(city_name, country_code)  # Получаем информацию о городе

    if not city:
        print(f"Не удалось найти город '{city_name}'.")
        return None

    city_code = city.get("code")  # Получаем код города
    print(f"Код города '{city_name}': {city_code}")

    # Получаем координаты моего адреса
    my_coordinates = await get_coordinates(city_name, my_address)

    if not my_coordinates:
        print("Не удалось получить координаты вашего адреса.")
        return None

    # Получаем все офисы в городе
    delivery_points = await get_delivery_points(city_code=city_code, size=1000)  # Больше офисов для поиска

    if not delivery_points:
        print("Не удалось получить список офисов.")
        return None

    print("Всего найдено офисов:", len(delivery_points))

    # Рассчитываем расстояние до каждого офиса
    office_distances = []
    for point in delivery_points:
        office_address_full = point.get('location', {}).get('address_full')
        office_code = point.get('code') # Получаем код офиса
        if office_address_full:
            # Разделяем адрес на город и улицу с номером дома
            parts = office_address_full.split(', ')
            if len(parts) >= 3:
                office_city = parts[2]  # Город
                office_address = parts[3]  # Улица и номер дома
            else:
                print(f"Некорректный формат адреса для офиса {point.get('code')}: {office_address_full}")
                continue

            office_coordinates = await get_coordinates(office_city, office_address)
            if office_coordinates:
                distance = geodesic(my_coordinates, office_coordinates).km  # Расстояние в километрах
                office_distances.append((point, distance))
            else:
                print(f"Не удалось получить координаты для офиса: {point.get('code')}")
        else:
            print(f"У офиса {point.get('code')} нет адреса")

    # Сортируем офисы по расстоянию
    office_distances.sort(key=lambda x: x[1])

    # Возвращаем N ближайших офисов
    nearest_offices = []
    for i in range(min(max_offices, len(office_distances))):
        point = office_distances[i][0]
        distance = office_distances[i][1]
        nearest_offices.append({
            "code": point.get('code'), # office_code
            "address": point.get('location', {}).get('address_full'),
            "distance": distance,
            "city_code": city_code, # Передаем code города
            "kode": city_code
        })

    return nearest_offices

# --- Пример использования ---
# if __name__ == "__main__":
#     async def main():
#         city_name = "Ленинградская"  # Название города для поиска
#         my_address = "Западная , 1"  # Твой адрес, сука
#
#         nearest_offices = await get_nearest_gdp_offices(city_name, my_address)
#         print(nearest_offices)
#         if nearest_offices:
#             print("Ближайшие офисы GDP:")
#             for office in nearest_offices:
#                 print(f"  Код: {office['code']}")
#                 print(f"  Адрес: {office['address']}")
#                 print(f"  Расстояние: {office['distance']:.2f} км")
#                 print(f"  Код города: {office['city_code']}")
#                 print(f"  Код : {office['kode']}")
#                 print("-" * 20)
#         else:
#             print("Не удалось получить список ближайших офисов GDP.")
#
#     asyncio.run(main())