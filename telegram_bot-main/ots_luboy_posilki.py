import requests
import hashlib


def get_auth_token(username, password):
    url = "https://auth.api.cdek.ru/web/simpleauth/authorize"

    # Подготовка данных для запроса
    payload = {
        "user": username,
        "hashedPass": password
    }

    # Отправка POST-запроса
    response = requests.post(url, json=payload)

    # Проверка статуса ответа
    if response.status_code == 200:
        data = response.json()
        return data.get("token")
    else:
        print(f"Ошибка: {response.status_code}")
        print(response.text)
        return None


# Пример использования
username = "apiuser-cdek.ru.net"
password = "8d55261707c5a20884b3cc44d6a3b313"


token = get_auth_token(username, password)

if token:
    print(f"Получен токен авторизации: {token}")
else:
    print("Не удалось получить токен авторизации")



def ots_l_p(orderNumber):
    # Step 2: Retrieve Order Tracking Information
    tracking_url = "https://tracing.api.cdek.ru/web/v2/order/find"
    headers = {
        "X-Auth-Token": token,
        "X-User-Lang": "rus",
        "Content-Type": "application/json"
    }

    tracking_payload = {
        "orderNumber": orderNumber # Replace with your order number   receiver
    }

    tracking_response = requests.post(tracking_url, headers=headers, json=tracking_payload)

    if tracking_response.status_code == 200:
        print("Информация об отслеживании заказа:", tracking_response.json())
        return tracking_response.json()
    else:
        print("Не удалось получить информацию об отслеживании:", tracking_response.text)
        return tracking_response.text


# orderNumber = 10024733562
# print(ots_l_p(orderNumber)) 10024733562 10024355398 10026313404