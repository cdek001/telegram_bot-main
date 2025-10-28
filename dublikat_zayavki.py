import time
import logging
from token_generator import get_token
import requests
import json


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/telegram_bot_api.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)




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





def create_call_request_kurier_konsol(weight, name, comment, phone_number, city, address, date, start_time, end_time, user_id):
    # Set API endpoint and authentication
    # Логируем начало создания запроса
    logger.info(f"🚚 Создание заявки на вызов курьера для user_id: {user_id}")
    logger.info(f"📦 Данные: вес={weight}кг, город={city}, адрес={address}")
    logger.info(f"📅 Дата: {date}, время: {start_time}-{end_time}")
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

    # Логируем отправляемый payload
    logger.debug(f"📤 Payload для API: {payload}")

    # Sending the request
    logger.info("📡 Отправка запроса к API CDEK...")
    response = requests.post(url, json=payload, headers=headers)

    # Логируем ответ API
    logger.info(f"📥 Ответ API: статус {response.status_code}")
    logger.debug(f"Тело ответа: {response.text}")

    # Checking the response
    if response.status_code == 202:
        # Successful response
        response_data = response.json()
        uuid = response_data['entity']['uuid']  # Получаем uuid из ответа
        logger.info(f"✅ Запрос принят API. UUID: {uuid}")

        print(response)
        # Задержка на 3 секунды
        logger.info("⏳ Ожидание 3 секунды перед проверкой статуса...")
        time.sleep(3)
        from info import info_uuid_zayvka
        uuid_zayvka = info_uuid_zayvka(uuid, user_id)
        requests_list = uuid_zayvka['requests']  # Получаем список requests
        logger.info(f"📋 Получено запросов: {len(requests_list)}")
        print(requests_list)
        # Проверяем состояние каждого запроса
        for request in requests_list:
            request_uuid = request['request_uuid']
            state = request['state']

            if request['state'] == 'SUCCESSFUL':
                logger.info(f"🎉 Запрос УСПЕШЕН! UUID: {request_uuid}")
                print("Все прошло хорошо! UUID запроса:", request['request_uuid'])
                success_message = f"Создана заявка на забор груза с адреса {address} {date} в промежутке с {start_time} {end_time}! Необходимо подготовить груз для отправления до приезда курьера. Время ожидания более 15 мин. оплачивается дополнительно"
                logger.info(f"📝 Сообщение для пользователя: {success_message}")

                return f"Создана заявка на забор груза с адреса {address} {date} в промежутке с {start_time} {end_time}! Необходимо подготовить груз для отправления до приезда курьера. Время ожидания более 15 мин. оплачивается дополнительно"
            else:
                logger.error(f"❌ Запрос НЕУСПЕШЕН! Состояние: {state}, UUID: {request_uuid}")
                print(f"Ошибка: состояние запроса - {request['state']}. UUID: {request['request_uuid']}")
                error_message = f"Ошибка: состояние запроса - {request['state']}. UUID: {request['request_uuid']}"
                logger.error(f"💥 Ошибка создания заявки: {error_message}")
                return f"Ошибка: состояние запроса - {request['state']}. UUID: {request['request_uuid']}"
    else:
        # Обработка ошибок
        error_data = response.json()
        logger.error(f"💥 Критическая ошибка в create_call_request_kurier_konsol: {str(e)}")
        logger.exception("Полный traceback ошибки:")
        print(f"Error: {error_data}")  # Логирование ошибки (при необходимости)
        return None  # Возвращаем None при ошибке
