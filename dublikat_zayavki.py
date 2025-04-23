import time

from token_generator import get_token
import requests
import json


# def create_order(cdek_number):
#     # Set API endpoint and authentication
#     url_get_order = f"https://api.cdek.ru/v2/orders?cdek_number={cdek_number}"
#     url_create_order = "https://api.cdek.ru/v2/orders"
#
#     headers = {
#         'Authorization': f'Bearer {get_token()}',
#         'Content-Type': 'application/json'
#     }
#
#     # Make GET request to retrieve order data
#     response_get_order = requests.get(url_get_order, headers=headers)
#
#     if response_get_order.status_code == 200:
#         # Parse response data as JSON
#         order_data = response_get_order.json()
#         print(order_data["entity"]["packages"])
#         # Extract relevant data from response
#         order_data_extracted = {
#             "type": 1,  # default type is "интернет-магазин"
#             "number": order_data["entity"]["cdek_number"],
#             'tariff_code': order_data["entity"]["tariff_code"],
#             "from_location": order_data["entity"]["from_location"],
#             'recipient': order_data["entity"]["recipient"],
#             "to_location": order_data["entity"]["to_location"],
#             "packages": [
#                 {
#                     "number": order_data["entity"]["packages"][0]["number"],
#                     "weight": order_data["entity"]["packages"][0]["weight"],
#                     "length": order_data["entity"]["packages"][0]["length"],
#                     "width": order_data["entity"]["packages"][0]["width"],
#                     "height": order_data["entity"]["packages"][0]["height"],
#                     "items": [
#                         {
#                             "ware_key": "WARE_KEY_123",  # example ware key
#                             "payment": {
#                                 "value": 3000
#                             },
#                             "name": "Товар",
#                             "cost": 300,
#                             "amount": 2,
#                             "weight": 700,
#                             "url": "www.item.ru"
#                         }
#                     ]
#                 }
#             ]
#         }
#
#         # Convert extracted data to JSON
#         order_json = json.dumps(order_data_extracted)
#
#         # Send POST request to create new order
#         response_create_order = requests.post(url_create_order, headers=headers, data=order_json)
#
#         if response_create_order.status_code == 201:
#             print("Order created successfully!")
#         else:
#             print("Error creating order:", response_create_order.text)
#     else:
#         print("Error retrieving order data:", response_get_order.text)


# cdek_number = 10006324754
# create_order(cdek_number)

def create_order(cdek_number):
    # Set API endpoint and authentication
    url_get_order = f"https://api.cdek.ru/v2/orders?cdek_number={cdek_number}"
    url_create_order = "https://api.cdek.ru/v2/orders"

    headers = {
        'Authorization': f'Bearer {get_token()}',
        'Content-Type': 'application/json'
    }

    # Make GET request to retrieve order data
    response_get_order = requests.get(url_get_order, headers=headers)
    print(response_get_order)

    if response_get_order.status_code:
        # Parse response data as JSON
        order_data = response_get_order.json()
        order_data_extracted = {
            "type": 1,  # Default type is "интернет-магазин"
            "number": order_data["entity"]["cdek_number"],
            'tariff_code': order_data["entity"]["tariff_code"],
            "packages": [
                    {
                        "number": order_data["entity"]["packages"][0]["number"],
                        "weight": order_data["entity"]["packages"][0]["weight"],
                        "length": order_data["entity"]["packages"][0]["length"],
                        "width": order_data["entity"]["packages"][0]["width"],
                        "height": order_data["entity"]["packages"][0]["height"],
                        "items": [
                            {
                                "ware_key": "WARE_KEY_123",  # Example ware key
                                "payment": {
                                    "value": 3000
                                },
                                "name": "Товар",
                                "cost": 300,
                                "amount": 2,
                                "weight": 700,
                                "url": "www.item.ru"
                            }
                        ]
                    }
                ]
            # Include other relevant data based on your requirements
            # ... Add more fields based on your specific needs

        }
        # Extract relevant data from response
        # order_data_extracted = {
        #     "type": 1,  # Default type is "интернет-магазин"
        #     "number": order_data["entity"]["cdek_number"],
        #     'tariff_code': order_data["entity"]["tariff_code"],
        #     'recipient': order_data["entity"]["recipient"],
        #     "to_location": order_data["entity"]["to_location"],
        #     "from_location": order_data["entity"]["from_location"],
        #     "packages": [
        #         {
        #             "number": order_data["entity"]["packages"][0]["number"],
        #             "weight": order_data["entity"]["packages"][0]["weight"],
        #             "length": order_data["entity"]["packages"][0]["length"],
        #             "width": order_data["entity"]["packages"][0]["width"],
        #             "height": order_data["entity"]["packages"][0]["height"],
        #             "items": [
        #                 {
        #                     "ware_key": "WARE_KEY_123",  # Example ware key
        #                     "payment": {
        #                         "value": 3000
        #                     },
        #                     "name": "Товар",
        #                     "cost": 300,
        #                     "amount": 2,
        #                     "weight": 700,
        #                     "url": "www.item.ru"
        #                 }
        #             ]
        #         }
        #     ]
        # }

        # Check if delivery_recipient_cost_adv is present
        if "delivery_recipient_cost_adv" in order_data["entity"]:
            # If present, add threshold field
            order_data_extracted["delivery_recipient_cost_adv"] = {
                "threshold": 1000  # example threshold value
            }

        # Convert extracted data to JSON
        order_json = json.dumps(order_data_extracted)

        # Send POST request to create new order
        response_create_order = requests.post(url_create_order, headers=headers, data=order_json)
        response_create_order = response_create_order.json()
        print(response_create_order)
        return response_create_order



def create_call_request(call_type, date, time_begin, time_end, address, order_uuid):
    # Set API endpoint and authentication
    url_create_call_request = "	https://api.cdek.ru/v2/intakes"

    headers = {
        'Authorization': f'Bearer {get_token()}',
        'Content-Type': 'application/json'
    }

    # Create call request data
    call_request_data = {
        "type": call_type,
        "intake_date": date,
        "intake_time_from": time_begin,
        "intake_time_to": time_end,
        "address": address,
        "order_uuid": order_uuid
    }

    # Convert call request data to JSON
    call_request_json = json.dumps(call_request_data)

    # Send POST request to create call request
    response_create_call_request = requests.post(url_create_call_request, headers=headers, data=call_request_json)

    print(response_create_call_request)
    return response_create_call_request


# call_type = 1  # 1 - для вызова курьера для оформления заказа
# date = "2024-07-10"
# time_begin = "10:00"
# time_end = "15:00"
# address = "ул. Ленина, д. 1"
# order_uuid = "72753034-80dc-4704-ba58-f2556149aa5a"
#
#
#
# create_call_request(call_type, date, time_begin, time_end, address, order_uuid)





def create_call_request_kurier(nom, date, time_begin, time_end, address):
    # Set API endpoint and authentication
    url_create_call_request = "	https://api.cdek.ru/v2/intakes"

    headers = {
        'Authorization': f'Bearer {get_token()}',
        'Content-Type': 'application/json'
    }
    call_type = 1
    # Create call request data
    call_request_data = {
        "type": call_type,
        "intake_date": date,
        "intake_time_from": time_begin,
        "intake_time_to": time_end,
        "address": address,
        "cdek_number": nom
    }

    # Convert call request data to JSON
    call_request_json = json.dumps(call_request_data)

    # Send POST request to create call request
    response_create_call_request = requests.post(url_create_call_request, headers=headers, data=call_request_json)
    response = response_create_call_request.json()
    print(response)
    # Проверяем, есть ли ключ 'entity' в ответе
    if 'entity' in response:
        uuid = response['entity']['uuid']
        if uuid:
            from info import info_uuid_zayvka
            time.sleep(3)
            state = info_uuid_zayvka(uuid)

            # Проверяем, есть ли запросы
            if 'requests' in state and state['requests']:
                # Получаем состояние первого запроса
                state1 = state['requests'][0]['state']  # Используем индекс 0 для доступа к первому элементу
                print(state1)
                return response_create_call_request.status_code, response_create_call_request.json(), state1
            else:
                print("Запросы отсутствуют.")
                # Если запросов нет, безопасно возвращаем None
                return response_create_call_request.status_code, response_create_call_request.json(), None
        else:
            print("UUID отсутствует.")
            return response_create_call_request.status_code, response_create_call_request.json(), None
    else:
        print("Ошибка в ответе:", response)
        return response_create_call_request.status_code, response_create_call_request.json(), None



# call_type = 1  # 1 - для вызова курьера для оформления заказа
# date = "2024-07-10"
# time_begin = "10:00"
# time_end = "15:00"
# address = "ул. Ленина, д. 1"
# nom = 10006324754
#
#
#
# create_call_request(call_type, date, time_begin, time_end, address, nom)



import requests
def create_call_request_kurier_konsol(weight, name, comment, phone_number, city, address, date, start_time, end_time, user_id):
    # Set API endpoint and authentication
    print("Creating call request")
    print(user_id)
    url = "	https://api.cdek.ru/v2/intakes"

    headers = {
        'Authorization': f'Bearer {get_token(user_id)}',
        'Content-Type': 'application/json'
    }
    payload = {
        "intake_date": date,
        "intake_time_from": start_time,
        "intake_time_to": end_time,
        "weight": weight,
        "name": "Консолидированный груз",
        "comment": comment,
        "sender": {
            "name": name,
            "phones": [
                {
                    "number": phone_number
                }
            ]
        },
        "from_location": {
            "city": city,
            "address": address
        },
        "need_call": False
}


    # Sending the request
    response = requests.post(url, json=payload, headers=headers)
    # Checking the response
    if response.status_code == 202:
        # Successful response
        response_data = response.json()
        uuid = response_data['entity']['uuid']  # Получаем uuid из ответа
        print(response)
        # Задержка на 3 секунды
        time.sleep(3)
        from info import info_uuid_zayvka
        uuid_zayvka = info_uuid_zayvka(uuid, user_id)
        requests_list = uuid_zayvka['requests']  # Получаем список requests
        print(requests_list)
        # Проверяем состояние каждого запроса
        for request in requests_list:
            if request['state'] == 'SUCCESSFUL':
                print("Все прошло хорошо! UUID запроса:", request['request_uuid'])
                return f"Создана заявка на забор груза с адреса {address} {date} в промежутке с {start_time} {end_time}! Необходимо подготовить груз для отправления до приезда курьера. Время ожидания более 15 мин. оплачивается дополнительно"
            else:
                print(f"Ошибка: состояние запроса - {request['state']}. UUID: {request['request_uuid']}")
                return f"Ошибка: состояние запроса - {request['state']}. UUID: {request['request_uuid']}"
    else:
        # Обработка ошибок
        error_data = response.json()
        print(f"Error: {error_data}")  # Логирование ошибки (при необходимости)
        return None  # Возвращаем None при ошибке
# print(create_call_request_kurier_konsol())