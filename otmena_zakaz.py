from token_generator import get_token
import requests


def otmena(uuid):

    url = f'https://api.cdek.ru/v2/orders/{uuid}/refusal'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {get_token()}'
    }
    response = requests.post(url=url, headers=headers)
    response_data = response.json()

    if 'requests' in response_data and response_data['requests'][0]['state'] == 'INVALID':
        error_message = response_data['requests'][0]['errors'][0]['message']
        raise ValueError(f'API Error: {error_message}')

    return response_data