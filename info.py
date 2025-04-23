from token_generator import get_token
import requests


def info(cdek_number,user_id):
    global token
    # URL Запрос на получение информации о заказе
    url = f'https://api.cdek.ru/v2/orders?cdek_number={cdek_number}'
    headers = {
        'Authorization': f'Bearer {get_token(user_id)}',
        'Content-Type': 'application/json'
    }
    print(user_id)
    response = requests.get(url=url, headers=headers)

    return response.json()
# cdek_number = 10095311059   # 10004518564      # 10017486846   # 10006324754
# print(info(cdek_number))

def info2(cdek_number,user_id):
    global token
    cdek_number = int(cdek_number)
    # URL Запрос на получение информации о заказе
    url = f'https://api.cdek.ru/v2/orders?im_number={cdek_number}'
    headers = {
        'Authorization': f'Bearer {get_token(user_id)}',
        'Content-Type': 'application/json'
    }
    print(user_id)
    print(cdek_number)
    response = requests.get(url=url, headers=headers)
    return response.json()

# id = 6536870230
# cdek_number = 675715   #'72753034-5d75-4314-bb3f-4cfb96640321'
# print(info2(cdek_number, id))


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



def info_uuid_zayvka(uuid, user_id):
    global token
    # URL Запрос на получение информации о заказе
    url = f'https://api.cdek.ru/v2/intakes/{uuid}'
    headers = {
        'Authorization': f'Bearer {get_token(user_id)}',
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



# from token_generator import get_token
# import requests
# import sqlite3
#
# def get_user_id_by_cdek_number(cdek_number):
#     """Получает user_id из базы данных по cdek_number."""
#     conn = sqlite3.connect('users.db')  # Подключение к базе данных
#     cursor = conn.cursor()
#     print(cursor)
#     try:
#         # Важно использовать правильный запрос к базе данных.  Предполагается, что у вас есть таблица new_orders и в ней есть соответствие cdek_number и user_id
#         cursor.execute("SELECT user_id FROM new_orders WHERE cdek_number = ?", (cdek_number,))
#         result = cursor.fetchone()
#         if result:
#             return result[0]  # Возвращаем user_id
#         else:
#             return None  # Если cdek_number не найден
#     except sqlite3.Error as e:
#         print(f"Ошибка при работе с базой данных: {e}")
#         return None
#     finally:
#         conn.close()  # Обязательно закрываем соединение с базой данных
#
#
# def info(cdek_number, user_id):
#     print("info")
#     """Получает информацию о заказе по cdek_number."""
#     user_id = get_user_id_by_cdek_number(cdek_number)
#
#     if not user_id:
#         print(f"Не удалось найти user_id для cdek_number: {cdek_number}")
#         return None
#
#     headers = {
#         'Authorization': f'Bearer {get_token(user_id)}', # Передаем user_id в get_token
#         'Content-Type': 'application/json'
#     }
#     # URL Запрос на получение информации о заказе
#     url = f'https://api.cdek.ru/v2/orders?cdek_number={cdek_number}'
#     response = requests.get(url=url, headers=headers)
#
#     return response.json()
# # cdek_number = 10095311059   # 10004518564      # 10017486846   # 10006324754
# # print(info(cdek_number))
#
# def info2(cdek_number, state=None):
#     """Получает информацию о заказе по im_number."""
#     user_id = get_user_id_by_cdek_number(cdek_number)
#     if not user_id:
#         print(f"Не удалось найти user_id для cdek_number: {cdek_number}")
#         return None
#
#     headers = {
#         'Authorization': f'Bearer {get_token(user_id=user_id)}', # Передаем user_id в get_token
#         'Content-Type': 'application/json'
#     }
#     # URL Запрос на получение информации о заказе
#     url = f'https://api.cdek.ru/v2/orders?im_number={cdek_number}'
#     response = requests.get(url=url, headers=headers)
#     return response.json()
#
#
# # cdek_number = '72753034-a937-4b71-a861-ac07069309da'
# # print(info2(cdek_number))
#
#
# def get_uuid(cdek_number, state=None):
#     order_info = info(cdek_number, state)
#     if order_info and 'entity' in order_info:
#         return order_info['entity']['uuid']
#     else:
#         return None # Обработка случая, если order_info is None or doesn't have entity
#
#
#
# def info_uuid(uuid, state=None):
#     user_id = None  #  Невозможно получить user_id по uuid, его нужно передать!
#
#     # Если uuid был получен из state, то user_id должен быть там же
#     if state:
#         async with state.proxy() as data:
#             user_id = data.get('user_id')
#
#     if not user_id:
#         print("Не удалось получить user_id для вызова info_uuid")
#         return None
#
#     """Получает информацию о заказе по uuid."""
#     headers = {
#         'Authorization': f'Bearer {get_token(user_id=user_id)}', # Передаем user_id в get_token
#         'Content-Type': 'application/json'
#     }
#     # URL Запрос на получение информации о заказе
#     url = f'https://api.cdek.ru/v2/orders/{uuid}'
#     response = requests.get(url=url, headers=headers)
#     return response.json()
#
# # uuid = "a754cf16-f3e6-4791-8072-967749cb915c"
# # print(info_uuid(uuid))
#
#
#
# def info_uuid_zayvka(uuid, state=None):
#     user_id = None
#     if state:
#         async with state.proxy() as data:
#             user_id = data.get('user_id')
#
#     if not user_id:
#         print("Не удалось получить user_id для вызова info_uuid_zayvka")
#         return None
#
#     """Получает информацию о заявке по uuid."""
#     headers = {
#         'Authorization': f'Bearer {get_token(user_id=user_id)}', # Передаем user_id в get_token
#         'Content-Type': 'application/json'
#     }
#     # URL Запрос на получение информации о заказе
#     url = f'https://api.cdek.ru/v2/intakes/{uuid}'
#     response = requests.get(url=url, headers=headers)
#     return response.json()
#
# # uuid = "72753034-4b58-4f29-9319-3f742f8456f7"
# # print(info_uuid_zayvka(uuid))
#
#
# def udalenie_info_uuid_zayvka(uuid, state=None):
#     """Удаляет информацию о заявке по uuid."""
#     user_id = None
#     if state:
#         async with state.proxy() as data:
#             user_id = data.get('user_id')
#
#     if not user_id:
#         print("Не удалось получить user_id для вызова udalenie_info_uuid_zayvka")
#         return None
#     headers = {
#         'Authorization': f'Bearer {get_token(user_id=user_id)}', # Передаем user_id в get_token
#         'Content-Type': 'application/json'
#     }
#     # URL Запрос на получение информации о заказе
#     url = f'https://api.cdek.ru/v2/intakes/{uuid}'
#     response = requests.get(url=url, headers=headers)
#     return response.json()
#
#
#
# def info_delivery_problem(uuid, state=None):
#     """Получает информацию о проблеме доставки по uuid."""
#     user_id = None
#     if state:
#         async with state.proxy() as data:
#             user_id = data.get('user_id')
#
#     if not user_id:
#         print("Не удалось получить user_id для вызова info_delivery_problem")
#         return None
#     headers = {
#         'Authorization': f'Bearer {get_token(user_id=user_id)}', # Передаем user_id в get_token
#         'Content-Type': 'application/json'
#     }
#     url = f'https://api.cdek.ru/v2/orders/{uuid}'
#     response = requests.get(url=url, headers=headers)
#
#     if response.status_code != 200:
#         print(f"Ошибка запроса: {response.status_code} - {response.text}")
#         return None
#
#     res = response.json()
#
#     try:
#         delivery_problem = res['entity']['delivery_problem']
#     except KeyError:
#         return "Ключ 'delivery_problem' не найден в ответе."
#
#     return delivery_problem