import requests
import json


def create_sbp_invoice(api_key, account_id, amount, description):
    url = "https://enter.tochka.com/api/v2/sbp/invoices"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "account_id": account_id,
        "amount": {
            "value": str(amount),
            "currency": "RUB"
        },
        "description": description,
        "notification_url": "https://your-callback-url.com/webhook",
        "ttl": 24 * 60 * 60  # Время жизни счета в секундах (24 часа)
    }

    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()  # Вызовет исключение для неуспешных статус-кодов
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при отправке запроса: {e}")
        return None


# Пример использования
api_key = "ваш_api_ключ"
account_id = "ид_вашего_счета"
amount = 1000.00  # Сумма в рублях
description = "Оплата заказа #12345"

result = create_sbp_invoice(api_key, account_id, amount, description)

if result:
    print("Счет успешно выставлен:")
    print(json.dumps(result, indent=2))
else:
    print("Не удалось выставить счет.")












import requests

# Replace with your access token
access_token = "YOUR_ACCESS_TOKEN"

# Define the headers and endpoint
headers = {
    "Authorization": f"Bearer {access_token}",
    "Content-Type": "application/json"
}
url = "https://enter.tochka.com/sandbox/v2/invoice/v1.0/bills"

# Define the payload for creating the invoice
payload = {
    "Data": {
        "accountId": "40817810802000000008/044525104",
        "customerCode": "300000092",
            "SecondSide": {
            "accountId": "40817810802000000008/044525104",
            "legalAddress": "624205, РОССИЯ, СВЕРДЛОВСКАЯ обл, ЛЕСНОЙ г, ЛЕНИНА ул, ДОМ 96, офис КВ. 19",
            "kpp": "668101001",
            "bankName": "ООО БАНК ТОЧКА",
            "bankCorrAccount": "30101810745374525104",
            "taxCode": "660000000000",
            "type": "company",
            "secondSideName": "ООО Студия дизайна М-АРТ"
            },
        "Content": {
            "Invoice": {
                "Positions": [],
                "date": "2010-10-29",
                "totalAmount": "1234.56",
                "totalNds": "1234.56",
                "number": "1",
                "basedOn": "Основание платежа",
                "comment": "Комментарий к платежу",
                "paymentExpiryDate": "2020-01-20"
            }
        }
    }
}

# Make the request to create the invoice
response = requests.post(url, json=payload, headers=headers)

# Check the response
if response.status_code == 201:
    print("Invoice created successfully:", response.json())
else:
    print("Failed to create invoice:", response.status_code, response.text)