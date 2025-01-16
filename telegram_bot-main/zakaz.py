from token_generator import get_token
import time
import requests
import json
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(filename='cdek_api.log', level=logging.DEBUG, format='%(asctime)s %(levelname)s:%(message)s')


def zakaz1(
        type_, tariff_code, from_city, from_address, to_city, to_address,
        recipient_name, recipient_phone, sender_name, sender_company,
        sender_phone, package_number, package_weight, package_length,
        package_width, package_height, package_comment, item_names,
        ware_keys, costs, item_weights, amounts
):

    print(type_, tariff_code, from_city, from_address, to_city, to_address,
        recipient_name, recipient_phone, sender_name, sender_company,
        sender_phone, package_number, package_weight, package_length,
        package_width, package_height, package_comment, item_names,
        ware_keys, costs, item_weights, amounts)


    # Ensure all item lists have the same length
    if not (len(item_names) == len(ware_keys) == len(costs) == len(item_weights) == len(amounts)):
        logging.error("Item lists have different lengths")
        return "Ошибка: Длины списков предметов не совпадают"

    # Convert text values to numbers where necessary
    def convert_to_number(value):
        if isinstance(value, str):
            try:
                return float(value) if '.' in value else int(value)
            except ValueError:
                return value
        return value

    type_ = convert_to_number(type_)
    tariff_code = convert_to_number(tariff_code)
    package_weight = convert_to_number(package_weight)
    package_length = convert_to_number(package_length)
    package_width = convert_to_number(package_width)
    package_height = convert_to_number(package_height)
    costs = convert_to_number(costs)
    item_weights = convert_to_number(item_weights)
    amounts = convert_to_number(amounts)



    url = 'https://api.cdek.ru/v2/orders'

    headers = {
        'Authorization': f'Bearer {get_token()}',
        'Content-Type': 'application/json'
    }

    # Create call request data
    data = {
        "type": 1,
        "tariff_code": 137,
        "from_location": {
            "city": from_city,
            "address": from_address
        },
        "to_location": {
            "city": to_city,
            "address": to_address
        },
        "recipient": {
            "name": recipient_name,
            "phones": [{"number": recipient_phone}]
        },
        "packages": [
            {
                "number": package_number,
                "weight": package_weight,
                "length": package_length,
                "width": package_width,
                "height": package_height,
                "comment": package_comment,
                "items": [
                    {
                        "name": item_names[i],
                        "ware_key": ware_keys[i],
                        "payment": {
                            "value": 0,
                            "vat_sum": 0,
                            "vat_rate": 0
                        },
                        "cost": costs[i],
                        "weight": item_weights[i],
                        "amount": amounts[i]
                    } for i in range(len(item_names))
                ]
            }
        ],
        "sender": {
            "name": sender_name,
            "company": sender_company,
            "phones": [{
                "number": sender_phone
            }]
        }
    }


    response = requests.post(url, headers=headers, data=json.dumps(data))
    response_data = response.json()

    logging.debug(f"Request data: {json.dumps(data)}")
    logging.debug(f"Response data: {json.dumps(response_data)}")

    if response.status_code == 202:
        print(f"Заказ успешно создан. {response_data}")

        from info import info_uuid


        if response_data['entity']['uuid']:
            uuid = response_data['entity']['uuid']
            print(uuid)
            time.sleep(3)
            nomer = info_uuid(uuid)
            print("nomer", nomer)
            if 'cdek_number' in nomer['entity']:
                uuid = nomer['entity']['cdek_number']
                print(uuid)
                return "Заказ успешно создан", uuid
            else:
                uuid = nomer['entity']['sender']
                return "Заказ создан с ошибкой", nomer
        else:
            uuid = response_data['entity']['requests']
            return "Заказ создан с ошибкой", uuid
    else:
        error_code = response_data.get('errors', [{}])[0].get('code', 'unknown_error')
        error_message = response_data.get('errors', [{}])[0].get('message', 'No error message provided')
        logging.error(f"Error {error_code}: {error_message}")
        return "Ошибка при создании заказа", error_message



# zakaz1(
#     type_="1",
#     tariff_code="137",
#     from_city="Москва",
#     from_address="левши, 1",
#     to_city="Москва",
#     to_address="левши, 5",
#     recipient_name="Ivan Ivanov",
#     recipient_phone="+79991234567",
#     sender_name="Petr Petrov",
#     sender_company="Example Corp",
#     sender_phone="+79997654321",
#     package_number="1",
#     package_weight=1000,
#     package_length=10,
#     package_width=10,
#     package_height=10,
#     package_comment="Handle with care",
#     item_names="Item 1",
#     ware_keys="key1",
#     costs=100,
#     item_weights=500,
#     amounts=1
# )

