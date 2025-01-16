# import requests
# from token_generator import get_token
#
# def kurier(intake_date, intake_time_from, intake_time_to, company, name, phone_number, address):
#     global token
#
#     # Set the sender's data
#     sender = {
#         "company": company,
#         "name": name,
#         "phones": [{"number": phone_number}]
#     }
#
#     # Set the from location
#     from_location = {
#         "code": "44",
#         "fias_guid": "0c5b2444-70a0-4932-980c-b4dc0d3f02b5",
#         "postal_code": "109004",
#         "longitude": 37.6204,
#         "latitude": 55.754,
#         "country_code": "RU",
#         "region": "Москва",
#         "sub_region": "Москва",
#         "city": "Москва",
#         "kladr_code": "7700000000000",
#         "address": address
#     }
#
#     # Set the recipient's data
#     recipient = {
#         "name": "Иванов Иван",
#         "phones": [{"number": "+79589441654"}]
#     }
#
#     # Set the request data
#     data = {
#         "intake_date": intake_date,
#         "intake_time_from": intake_time_from,
#         "intake_time_to": intake_time_to,
#         "name": "Консолидированный груз",
#         "weight": 1000,
#         "length": 10,
#         "width": 10,
#         "height": 10,
#         "comment": "Комментарий курьеру",
#         "sender": sender,
#         "from_location": from_location,
#         "tariff_code": "133",  # Add a valid tariff code
#         "recipient": recipient,  # Add a recipient
#         "packages": [{  # Add a valid package
#             "weight": 1000,
#             "length": 10,
#             "width": 10,
#             "height": 10,
#             "number": "PKG123",  # Add a package number
#             "items": [{  # Add package items
#                 "weight": 500,
#                 "name": "Item 1",
#                 "ware_key": "WARE123",  # Add a ware key
#                 "payment": {  # Update the payment field
#                     "type": "cash",
#                     "sum": 1000,
#                     "value": 1000  # Add a payment value
#                 },
#                 "cost": 1000,  # Add a cost
#                 "amount": 1  # Add an amount
#             }]
#         }],
#         "need_call": False
#     }
#
#     # Send the request
#     url = "https://api.cdek.ru/v2/orders"
#     headers = {
#         'Authorization': f'Bearer {get_token()}',
#         'Content-Type': 'application/json'
#     }
#     response = requests.post(url, headers=headers, json=data)
#     if response.status_code == 200:
#         response_data = response.json()
#         uuid = response_data["entity"]["uuid"]
#         return f"Заявка создана успешно! UUID: {uuid} {response.json()}"
#     else:
#         return f"Ошибка при создании заявки {response.json()}"
#
# # Set the pickup date and time
# intake_date = "2024-07-10"  # Today's date
# intake_time_from = "10:00"
# intake_time_to = "17:00"
# company = "Иванов Иван"
# name = "Компания"
# phone_number = "+79589441654"
# address = "ул. Блюхера, 32"
# print(kurier(intake_date, intake_time_from, intake_time_to, company, name, phone_number, address))

from token_generator import get_token
import requests


def info(uid):
    global token
    # URL Запрос на получение информации о заказе
    url = f'https://api.cdek.ru/v2/orders?cdek_number={uid}'
    headers = {
        'Authorization': f'Bearer {get_token()}',
        'Content-Type': 'application/json'
    }
    response = requests.get(url=url, headers=headers)

    return response.json()
# uid = '10009081118'
# print(info(uid))