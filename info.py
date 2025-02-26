from token_generator import get_token
import requests


def info(cdek_number):
    global token
    # URL Запрос на получение информации о заказе
    url = f'https://api.cdek.ru/v2/orders?cdek_number={cdek_number}'
    headers = {
        'Authorization': f'Bearer {get_token()}',
        'Content-Type': 'application/json'
    }
    response = requests.get(url=url, headers=headers)

    return response.json()
# cdek_number = 100211   # 10004518564      # 10017486846   # 10006324754
# print(info(cdek_number))

def info2(cdek_number):
    global token
    # URL Запрос на получение информации о заказе
    url = f'https://api.cdek.ru/v2/orders?im_number={cdek_number}'
    headers = {
        'Authorization': f'Bearer {get_token()}',
        'Content-Type': 'application/json'
    }
    response = requests.get(url=url, headers=headers)
    return response.json()


# cdek_number = 10006324754
# print(info(cdek_number))


def get_uuid(cdek_number):
    order_info = info(cdek_number)
    return order_info['entity']['uuid']



def info_uuid(uuid):
    global token
    # URL Запрос на получение информации о заказе
    url = f'https://api.cdek.ru/v2/orders/{uuid}'
    headers = {
        'Authorization': f'Bearer {get_token()}',
        'Content-Type': 'application/json'
    }
    response = requests.get(url=url, headers=headers)
    return response.json()

# uuid = "a754cf16-f3e6-4791-8072-967749cb915c"
# print(info_uuid(uuid))



def info_uuid_zayvka(uuid):
    global token
    # URL Запрос на получение информации о заказе
    url = f'https://api.cdek.ru/v2/intakes/{uuid}'
    headers = {
        'Authorization': f'Bearer {get_token()}',
        'Content-Type': 'application/json'
    }
    response = requests.get(url=url, headers=headers)
    return response.json()

# uuid = "72753034-4b58-4f29-9319-3f742f8456f7"
# print(info_uuid_zayvka(uuid))


def udalenie_info_uuid_zayvka(uuid):
    global token
    # URL Запрос на получение информации о заказе
    url = f'https://api.cdek.ru/v2/intakes/{uuid}'
    headers = {
        'Authorization': f'Bearer {get_token()}',
        'Content-Type': 'application/json'
    }
    response = requests.get(url=url, headers=headers)
    return response.json()



def info_delivery_problem(uuid):
    global token
    url = f'https://api.cdek.ru/v2/orders/{uuid}'
    headers = {
        'Authorization': f'Bearer {get_token()}',
        'Content-Type': 'application/json'
    }
    response = requests.get(url=url, headers=headers)

    if response.status_code != 200:
        print(f"Ошибка запроса: {response.status_code} - {response.text}")
        return None

    res = response.json()

    try:
        delivery_problem = res['entity']['delivery_problem']
    except KeyError:
        return "Ключ 'delivery_problem' не найден в ответе."

    return delivery_problem


# uuid = "a754cf16-f3e6-4791-8072-967749cb915c"
# print(info_delivery_problem(uuid))