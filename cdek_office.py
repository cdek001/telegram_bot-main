# delivery_points.py
import requests
import json
import asyncio
from token_generator import get_token  # Импортируем функцию get_token
from cdek_cod_city import get_city  # Импортируем функцию get_city


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
        region_code (int, optional): Код региона СДЭК.
        have_cashless (bool, optional): Наличие терминала оплаты.
        have_cash (bool, optional): Есть прием наличных.
        allowed_cod (bool, optional): Разрешен наложенный платеж.
        is_dressing_room (bool, optional): Наличие примерочной.
        weight_max (int, optional): Максимальный вес в кг, который может принять офис.
        weight_min (int, optional): Минимальный вес в кг, который принимает офис.
        lang (str, optional): Локализация офиса.
        take_only (bool, optional): Является ли офис только пунктом выдачи.
        is_handout (bool, optional): Является пунктом выдачи.
        is_reception (bool, optional): Есть ли в офисе приём заказов.
        is_marketplace (bool, optional): Офис для доставки "До маркетплейса".
        is_ltl (bool, optional): Работает ли офис с LTL (сборный груз).
        fulfillment (bool, optional): Офис с зоной фулфилмента.
        fias_guid (str, optional): Код города ФИАС.
        size (int, optional): Ограничение выборки результата (размер страницы).
        page (int, optional): Номер страницы выборки результата.

    Returns:
        list: Список офисов (словарь) или None в случае ошибки.
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

# --- Пример использования ---
if __name__ == "__main__":
    async def main():
        city_name = "Москва"  # Название города для поиска
        country_code = "RU"

        city = await get_city(city_name, country_code)  # Получаем информацию о городе

        if city:
            city_code = city.get("code")  # Получаем код города
            print(f"Код города '{city_name}': {city_code}")

            # Пример запроса с параметрами, используя полученный city_code
            delivery_points = await get_delivery_points(city_code=city_code, have_cashless=True, size=10)  # Краснодар с терминалом оплаты, размер страницы 2

            if delivery_points:
                print("Офисы:")
                for point in delivery_points:
                    print(f"  Код: {point.get('code')}")
                    print(f"  Адрес: {point.get('location', {}).get('address_full')}") # Обращаемся к вложенному словарю безопасно
                    print("-" * 20)
            else:
                print("Не удалось получить список офисов.")
        else:
            print(f"Не удалось найти город '{city_name}'.")

    asyncio.run(main())