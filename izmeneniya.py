import json
from token_generator import get_token
import requests
import time


def make_request_5(id, cdek_number, data):
    url = 'https://api.cdek.ru/v2/orders'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {get_token(id)}'
    }
    response = requests.patch(url=url, headers=headers, json={**{"uuid": cdek_number}, **data})
    response_data = response.json()

    if 'requests' in response_data and response_data['requests'][0]['state'] == 'INVALID':
        error_message = response_data['requests'][0]['errors'][0]['message']
        print(error_message)
        return ValueError(f'Ошибка API: аналогичный запрос все еще обрабатывается, пожалуйста попробуйте позже.')
    print(response_data)

    return response_data

def fio(id, cdek_number, new_recipient_name):
    data = {
        "recipient": {
            "name": new_recipient_name
        }
    }
    return make_request(id, cdek_number, data)
# cdek_number = 10006324754
# new_recipient_name = "Шлипс Антон Александрович"
# print(fio(cdek_number, new_recipient_name))


def make_request(id, cdek_number, data, max_retries=3, initial_delay=1):  # Добавим параметры повторных попыток
    url = 'https://api.cdek.ru/v2/orders'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {get_token(id)}'
    }
    print("make_request", id, cdek_number, data)
    for attempt in range(max_retries):
        try:
            response = requests.patch(url=url, headers=headers, json={**{"uuid": cdek_number}, **data})
            response_data = response.json()

            if 'requests' in response_data and response_data['requests'][0]['state'] == 'INVALID':
                error_message = response_data['requests'][0]['errors'][0]['message']
                if "аналогичный запрос все еще обрабатывается" in error_message:
                    print(f"Попытка {attempt+1}: {error_message}.  Повторная попытка через {initial_delay * (2**attempt)} секунд.")
                    time.sleep(initial_delay * (2**attempt))  # Экспоненциальная задержка
                    continue  # Перейти к следующей попытке
                else:
                    raise ValueError(f'Ошибка API: {error_message}')  # Другая ошибка - выбрасываем исключение
            print(response_data)
            return response_data  # Успешно - возвращаем результат

        except requests.exceptions.RequestException as e:
            print(f"Ошибка соединения (попытка {attempt+1}): {e}. Повторная попытка через {initial_delay * (2**attempt)} секунд.")
            time.sleep(initial_delay * (2**attempt)) # Задержка при ошибке соединения

    raise Exception(f"Не удалось выполнить запрос после {max_retries} попыток.") # Если все попытки неудачны, выбрасываем исключение

def data_(id, cdek_number, new_recipient_name):
    data = {
    "requests": [
        {
            "date_time": new_recipient_name + "T12:00:00Z",
        }
    ]
}
    return make_request(id, cdek_number, data)

def fone(id, cdek_number, new_phone_number):
    data = {
        "recipient": {
            "phones": [
                {
                    "number": new_phone_number
                }
        ]
        }
    }
    return make_request(id, cdek_number, data)

def change_city(id, cdek_number, adres):
    city = adres[0]
    address = adres[1]
    print("change_city", city, address)
    data = {
        "to_location": {
            "city": city,
            "address": address
        }
    }

    rez = make_request_5(id, cdek_number, data)
    print(rez)
    return rez

def adres(id, cdek_number, address):
    data = {
        "to_location": {
            "address": address
        }
    }
    print(id, cdek_number, address)
    return make_request(id, cdek_number, data)

def pwz(id, cdek_number, delivery_point):
    data = {
        "delivery_point": delivery_point
    }
    return make_request(id, cdek_number, data)

def nalozh_pay(id, cdek_number, value):
    data = {
        "uuid": cdek_number,
        "delivery_recipient_cost": {
            "value": value
        }
    }
    return make_request(id, cdek_number, data)

def nalozh_pay_dop_cbor(id, cdek_number, value):
    data = {
        "uuid": cdek_number,
        "delivery_recipient_cost": {
            "value": value
        }
    }
    rez = make_request(id, cdek_number, data)
    return rez



def data_dostavki(id, cdek_number, address):
    data = {
        "to_location": {
            "address": address
        }
    }
    return make_request(id, cdek_number, data)

def fio(id, cdek_number, new_recipient_name):
    data = {
        "recipient": {
            "name": new_recipient_name
        }
    }
    return make_request(id, cdek_number, data)



# Отмена наложенного платежа
def nalozh_pay_otmena_vse(cdek_number, tariff_code=None, sender_city_id=None, delivery_recipient_cost_value=None):
    """
    Функция для отмены наложенного платежа в заказе СДЭК.

    Args:
        cdek_number (str): UUID заказа в СДЭК.
        tariff_code (int, optional): Тарифный код. Defaults to None.
        sender_city_id (int, optional): ID города отправителя. Defaults to None.
        delivery_recipient_cost_value (float, optional): Сумма наложенного платежа
    """
    print(f"Отмена наложенного платежа для заказа с UUID: {cdek_number}")

    data = {
        "uuid": cdek_number,
        "tariff_code": tariff_code,
        "sender_city_id": sender_city_id,
        "delivery_recipient_cost": {  # Отменяем наложенный платеж
            "value": 0,
            "vat_sum": 0,
            "vat_rate": 0
        }
        # Здесь можно добавить и другие поля заказа, которые необходимо передавать
    }

    # Удаляем None значения, чтобы не отправлять их в запросе
    data = {k: v for k, v in data.items() if v is not None}
    if "delivery_recipient_cost" in data and data["delivery_recipient_cost"] is None:
        del data["delivery_recipient_cost"]

    url = f'https://api.cdek.ru/v2/orders'  # Endpoint для изменения заказа
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {get_token()}'
    }
    print(f"Данные, отправляемые в запросе: {data}")  # Для отладки
    response = requests.patch(url=url, headers=headers, json={**{"uuid": cdek_number}, **data})
    print(f"Ответ от API: {response.json()}")
    response.raise_for_status()  # Raises HTTPError for bad responses (4XX, 5XX)
    return response.json()



def nalozh_pay_otmena_vse_3(cdek_number, tariff_code=None, sender_city_id=None, delivery_recipient_cost_value=None, id = None):
    """
    Функция для отмены наложенного платежа и установки payment value в 0 для всех items в packages в заказе СДЭК.

    Args:
        cdek_number (str): UUID заказа в СДЭК.
        tariff_code (int, optional): Тарифный код. Defaults to None.
        sender_city_id (int, optional): ID города отправителя. Defaults to None.
        delivery_recipient_cost_value (float, optional): Сумма наложенного платежа (устаревший параметр)
    """
    print(f"Отмена наложенного платежа и установка payment value в 0 для заказа с UUID: {cdek_number}")

    # 1. Получаем текущую информацию о заказе
    url_get = f'https://api.cdek.ru/v2/orders/{cdek_number}'  # Endpoint для получения информации о заказе
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {get_token(id)}'
    }
    response_get = requests.get(url=url_get, headers=headers)
    response_get.raise_for_status()
    order_data = response_get.json()

    # 2. Модифицируем данные, обнуляя payment.value в каждом item каждого package
    for package in order_data['entity']['packages']:
        for item in package['items']:
            item['payment']['value'] = 0

    # 3. Подготавливаем данные для PATCH запроса
    data = {
        "uuid": cdek_number,
        "tariff_code": tariff_code,
        "sender_city_id": sender_city_id,
        "delivery_recipient_cost": {  # Отменяем наложенный платеж
            "value": 0.0,
            "vat_sum": 0,
            "vat_rate": 0
        },
        "packages": order_data['entity']['packages']  # Добавляем модифицированный packages
        # Здесь можно добавить и другие поля заказа, которые необходимо передавать
    }

    # Удаляем None значения, чтобы не отправлять их в запросе
    data = {k: v for k, v in data.items() if v is not None}
    if "delivery_recipient_cost" in data and data["delivery_recipient_cost"] is None:
        del data["delivery_recipient_cost"]

    url_patch = 'https://api.cdek.ru/v2/orders'  # Endpoint для изменения заказа (ИСПРАВЛЕНО)
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {get_token(id)}'
    }
    print(
        f"Данные, отправляемые в PATCH запросе: {json.dumps(data, indent=2, ensure_ascii=False)}")  # Для отладки, вывод JSON с отступами
    response_patch = requests.patch(url=url_patch, headers=headers, json=data)

    print(f"Ответ от API: {response_patch.json()}")
    response_patch.raise_for_status()
    return response_patch.json()













# Удаление заказа

def delete_order(id, uuid: str) -> requests.Response:
    """
    Метод для удаления заказа СДЭК через API v2.

    Args:
        uuid: Идентификатор заказа в ИС СДЭК (UUID), который необходимо удалить.
        bearer_token: Bearer токен для авторизации.

    Returns:
        requests.Response: Объект ответа от API. Содержит статус код, заголовки и тело ответа.
                          Возвращает None в случае ошибки.
    """

    url = f"https://api.cdek.ru/v2/orders/{uuid}"  # Замените на актуальный URL, если отличается

    headers = {
        "Authorization": f'Bearer {get_token(id)}'
    }

    try:
        response = requests.delete(url, headers=headers)
        response.raise_for_status()  # Поднимает исключение для статус кодов 4XX и 5XX
        return response

    except requests.exceptions.RequestException as e:
        print(f"Ошибка при выполнении запроса удаления заказа: {e}")
        return None

# # Пример использования
# if __name__ == '__main__':
#     order_uuid = "72753034-96b7-43f3-a555-6c660fed6020"  # Замените на реальный UUID заказа, который хотите удалить
#
#
#     response = delete_order(order_uuid)
#
#     if response:
#         print(f"Статус код: {response.status_code}")
#         print(f"Ответ API: {response.json()}")
#     else:
#         print("Не удалось выполнить запрос удаления заказа.")