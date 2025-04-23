# import requests
# import json
# from token_generator import get_token
#
# def calculate_cdek_tariff(tariff_code, from_location_code, to_location_code, package_weight, type=1, currency=1):
#     """
#     Рассчитывает стоимость доставки СДЭК на основе указанных параметров.
#
#     Args:
#         tariff_code (int): Код тарифа СДЭК.
#         from_location_code (int): Код города отправителя.
#         to_location_code (int): Код города получателя.
#         package_weight (int): Вес посылки в граммах.
#         type (int): Тип тарифа (по умолчанию 1).
#         currency (int): Код валюты (по умолчанию 1 - рубли).
#
#     Returns:
#         dict: Ответ от API СДЭК в формате JSON или None в случае ошибки.
#     """
#
#     url = "https://api.cdek.ru/v2/calculator/tariff"
#     headers = {
#         'Authorization': f'Bearer {get_token()}',
#         'Content-Type': 'application/json'
#     }
#     payload = {
#         "type": type,
#         "currency": currency,
#         "tariff_code": tariff_code,
#         "from_location": {
#             "code": from_location_code
#         },
#         "to_location": {
#             "code": str(to_location_code) # Преобразуем в строку, как в примере
#         },
#         "packages": [
#             {
#                 "weight": package_weight,
#                 "length": 1,
#                 "width": 1,
#                 "height": 1
#             }
#         ]
#     }
#
#
#     try:
#         response = requests.post(url, data=json.dumps(payload), headers=headers)
#         response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
#         return response.json()
#     except requests.exceptions.RequestException as e:
#         print(f"Error during API request: {e}")
#         return None
#     except json.JSONDecodeError as e:
#         print(f"Error decoding JSON response: {e}")
#         return None
#
#
# # Пример использования
# tariff_code = 234
# from_location_code = 44
# to_location_code = 2526
# package_weight = 1000
#
# result = calculate_cdek_tariff(tariff_code, from_location_code, to_location_code, package_weight)
#
# if result:
#     print(json.dumps(result, indent=4, ensure_ascii=False))  # Красивый вывод JSON
# else:
#     print("Failed to calculate tariff.")
import requests
import json
from token_generator import get_token

# def calculate_cdek_tariff(tariff_code, from_location_code, to_location_code, package_weight, type=1, currency=1):
#     """
#     Рассчитывает стоимость доставки СДЭК на основе указанных параметров.
#
#     Args:
#         tariff_code (int): Код тарифа СДЭК.
#         from_location_code (int): Код города отправителя.
#         to_location_code (int): Код города получателя.
#         package_weight (int): Вес посылки в граммах.
#         type (int): Тип тарифа (по умолчанию 1).
#         currency (int): Код валюты (по умолчанию 1 - рубли).
#
#     Returns:
#         dict: Ответ от API СДЭК в формате JSON или None в случае ошибки.
#     """
#
#     url = "https://api.cdek.ru/v2/calculator/tariff"
#     headers = {
#         'Authorization': f'Bearer {get_token()}',
#         'Content-Type': 'application/json'
#     }
#     payload = {
#         "type": type,
#         "currency": currency,
#         "tariff_code": tariff_code,
#         "from_location": {
#             "code": from_location_code
#         },
#         "to_location": {
#             "code": str(to_location_code) # Преобразуем в строку, как в примере
#         },
#         "packages": [
#             {
#                 "weight": package_weight,
#                 "length": 1,
#                 "width": 1,
#                 "height": 1
#             }
#         ]
#     }
#
#     # Выводим тело запроса в JSON-формате
#     print("Тело запроса (JSON):")
#     print(json.dumps(payload, indent=4, ensure_ascii=False))
#
#     try:
#         response = requests.post(url, data=json.dumps(payload), headers=headers)
#         response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
#         return response.json()
#     except requests.exceptions.RequestException as e:
#         print(f"Error during API request: {e}")
#         return None
#     except json.JSONDecodeError as e:
#         print(f"Error decoding JSON response: {e}")
#         return None
#
#
# # Пример использования
# tariff_code = 234
# from_location_code = 44
# to_location_code = 2526
# package_weight = 1000
#
# result = calculate_cdek_tariff(tariff_code, from_location_code, to_location_code, package_weight)
#
# if result:
#     print(json.dumps(result, indent=4, ensure_ascii=False))  # Красивый вывод JSON
# else:
#     print("Failed to calculate tariff.")

# import requests
# import json
#
# import requests
# import json
#
# # Параметры запроса (замените на свои значения)
# token = get_token()  # Замените на ваш токен
# cdek_number = "10091646452"  # Или используйте cdek_number
#
# url = "https://api.cdek.ru/v2/check"  # URL эндпоинта
#
# # Формируем параметры запроса (query parameters)
# params = {}
# if cdek_number:
#     params["cdek_number"] = cdek_number
#
# headers = {
#     'Authorization': f'Bearer {token}',
#     'Content-Type': 'application/json'
# }
#
# response = requests.get(url, headers=headers, params=params)  # Отправляем GET-запрос с параметрами
# response.raise_for_status()  # Проверяем на ошибки HTTP
# check_info = response.json() # Получаем JSON
#
# # Извлекаем информацию о чеке из ответа
# if check_info and 'check_info' in check_info and check_info['check_info']:
#     check_data = check_info['check_info'][0]  # Берем первый элемент из списка check_info
#
#     order_uuid = check_data.get('order_uuid')
#     cdek_number_from_response = check_data.get('cdek_number')
#     date = check_data.get('date')
#     fiscal_storage_number = check_data.get('fiscal_storage_number')
#     document_number = check_data.get('document_number')
#     fiscal_sign = check_data.get('fiscal_sign')
#     type = check_data.get('type')
#     payment_info = check_data.get('payment_info') # Уже является списком
#
#     # Выводим извлеченные данные
#     print(f"order_uuid: {order_uuid}")
#     print(f"cdek_number: {cdek_number_from_response}")
#     print(f"date: {date}")
#     print(f"fiscal_storage_number: {fiscal_storage_number}")
#     print(f"document_number: {document_number}")
#     print(f"fiscal_sign: {fiscal_sign}")
#     print(f"type: {type}")
#     print(f"payment_info: {payment_info}") # Выводим список payment_info целиком
#
#     # Если нужно вывести информацию из payment_info более детально
#     if payment_info:
#         for payment in payment_info:
#             payment_sum = payment.get('sum')
#             payment_type = payment.get('type')
#             print(f"  Сумма платежа: {payment_sum}")
#             print(f"  Тип платежа: {payment_type}")
#
#
# else:
#     print("Информация о чеке не найдена.")

import json
import asyncio
from unittest.mock import patch  # Используем unittest.mock для patch






# token = get_token()
# url = f"https://api.cdek.ru/v2/orders"  #  Более корректный URL для обновления адреса
# uuid = "72753034-f692-4af7-b43e-5d919cf4d509"
# headers = {
#     "Content-Type": "application/json",
#     "Authorization": f"Bearer {token}"
# }
#
# data = {
#     "uuid": uuid,  # UUID  уже в URL, не нужен в payload
#     "type": 1,  # Предполагаем, что у вас тип заказа 1
#     "to_location": {
#         "address": "ш. Варшавское, 160, корп. 2",
#         "code": 44  # Обязательно нужно передавать city_code или city. Лучше city_code
#     },
#     "sender": {
#         "name": "\"ОБЪЕДИНЕННАЯ КОНДИТЕРСКАЯ СЕТЬ\""
#     },
#     "recipient": {
#         "name": "тест",
#     }
# }
#
# response = requests.patch(url=url, headers=headers, json={**{"uuid": uuid}, **data})
# response_data = response.json()
# print(response_data)











