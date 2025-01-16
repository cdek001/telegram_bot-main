from token_generator import get_token
import requests
import json


def region_code():
    url = f'https://api.cdek.ru/v2/location/regions?country_codes=RU,TR'
    headers = {
        'Authorization': f'Bearer {get_token()}',
        'Content-Type': 'application/json'
    }
    response = requests.get(url=url, headers=headers)

    regions = response.json()
    region_dict = {}

    for region in regions:
        region_code = region['region_code']
        region_name = region['region']
        region_dict[region_code] = region_name

    return region_dict


