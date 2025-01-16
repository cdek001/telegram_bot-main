from token_generator import get_token
import requests
import json

def delivery_calc():
  global token
  # URL для получения информации об офисах
  url = f'https://api.cdek.ru/v2/delivery'

  # Заголовки для запросов к API с токеном
  headers = {
    'Authorization': f'Bearer {get_token()}',
    'Content-Type': 'application/json'
  }

  data = {
  "cdek_number": "1106207236",
  "order_uuid": "72753031-df04-44a4-bc60-11e8b5253b1d",
  "date": "2020-02-27",
  "time_from": "10:00",
  "time_to": "15:00",
  "comment": "Офис группы компаний Ланит ?",
  "delivery_point": "",
  "to_location": {
    "code": 137,
    "fias_guid": "c2deb16a-0330-4f05-821f-1d09c93331e6",
    "postal_code": "190000",
    "longitude": 30.3159,
    "latitude": 59.9391,
    "country_code": "RU",
    "region": "Санкт-Петербург",
    "region_code": 82,
    "sub_region": "Санкт-Петербург",
    "city": "Санкт-Петербург",
    "kladr_code": "78",
    "address": "г.Бердск ул.Ленина 16"
  }
}


  response = requests.post(url=url, headers=headers, json=data)
  return response.json()


print(delivery_calc())






















