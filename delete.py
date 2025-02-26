from token_generator import get_token
from info import get_uuid
import requests
import json



def delete(uuid):
    global token
    # URL Запрос на получение информации о заказе
    url = f'https://api.cdek.ru/v2/orders/{uuid}'


    headers = {
        'Authorization': f'Bearer {get_token()}',
        'Content-Type': 'application/json'
    }

    response = requests.get(url=url, headers=headers)

    return response


# cdek_number = 10004518564
# uuid = get_uuid(cdek_number)