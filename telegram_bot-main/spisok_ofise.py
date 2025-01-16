from token_generator import get_token
import requests
import json



def get_city_code(city):
    url = f'https://api.cdek.ru/v2/location/cities/?city={city}'
    headers = {
        'Authorization': f'Bearer {get_token()}',
        'Content-Type': 'application/json'
    }
    city = requests.get(url=url, headers=headers)
    city = json.dumps(city.json(), indent=4, ensure_ascii=False)
    city = json.loads(city)
    return city[0]['code']


def city_info(city):
    global token
    # URL для получения информации об офисах
    url = f'https://api.cdek.ru/v2/deliverypoints?city_code={get_city_code(city)}'

    # Заголовки для запросов к API с токеном
    headers = {
        'Authorization': f'Bearer {get_token()}',
        'Content-Type': 'application/json'
    }

    response = requests.get(url=url, headers=headers)

    return response.json()









def city_info1():
    # URL для получения информации об офисах
    url = 'https://api.cdek.ru/v2/deliverypoints'

    # Заголовки для запросов к API с токеном
    headers = {
        'Authorization': f'Bearer {get_token()}',
        'Content-Type': 'application/json'
    }

    response = requests.get(url=url, headers=headers)

    return response.json()

# Получим информацию и сохраним её в JSON-файл
data = city_info1()  # замените 'your_token_here' на свой токен

with open('city_info.json', 'w', encoding='utf-8') as file:
    json.dump(data, file, ensure_ascii=False, indent=4)

print("Данные сохранены в city_info.json")