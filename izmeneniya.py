from token_generator import get_token
import requests

def make_request(cdek_number, data):
    url = 'https://api.cdek.ru/v2/orders'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {get_token()}'
    }
    response = requests.patch(url=url, headers=headers, json={**{"uuid": cdek_number}, **data})
    response_data = response.json()

    if 'requests' in response_data and response_data['requests'][0]['state'] == 'INVALID':
        error_message = response_data['requests'][0]['errors'][0]['message']
        return ValueError(f'Ошибка API: аналогичный запрос v2 все еще обрабатывается {error_message}')
    print(response_data)

    return response_data

def fio(cdek_number, new_recipient_name):
    data = {
        "recipient": {
            "name": new_recipient_name
        }
    }
    return make_request(cdek_number, data)
# cdek_number = 10006324754
# new_recipient_name = "Шлипс Антон Александрович"
# print(fio(cdek_number, new_recipient_name))



def data_(cdek_number, new_recipient_name):
    data = {
    "requests": [
        {
            "date_time": new_recipient_name + "T12:00:00Z",
        }
    ]
}
    return make_request(cdek_number, data)

def fone(cdek_number, new_phone_number):
    data = {
        "recipient": {
            "phones": [
                {
                    "number": new_phone_number
                }
        ]
        }
    }
    return make_request(cdek_number, data)

def change_city(cdek_number, city, address):
    data = {
        "to_location": {
            "city": city,
            "address": address
        }
    }
    return make_request(cdek_number, data)

def adres(cdek_number, address):
    data = {
        "to_location": {
            "address": address
        }
    }
    return make_request(cdek_number, data)

def pwz(cdek_number, delivery_point):
    data = {
        "delivery_point": delivery_point
    }
    return make_request(cdek_number, data)

def nalozh_pay(cdek_number, value):
    data = {
        "uuid": cdek_number,
        "delivery_recipient_cost": {
            "value": value
        }
    }
    return make_request(cdek_number, data)

def nalozh_pay_dop_cbor(cdek_number, value):
    data = {
        "uuid": cdek_number,
        "delivery_recipient_cost": {
            "value": value
        }
    }
    rez = make_request(cdek_number, data)
    return rez

def nalozh_pay_otmena_vse(cdek_number):
    data = {
        "uuid": cdek_number,
        "delivery_recipient_cost": {
            "value": 0,  # Устанавливаем сумму наложенного платежа на ноль для отмены
        }
    }
    rez = make_request(cdek_number, data)
    return rez



def data_dostavki(cdek_number, address):
    data = {
        "to_location": {
            "address": address
        }
    }
    return make_request(cdek_number, data)