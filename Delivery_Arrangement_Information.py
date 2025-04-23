from token_generator import get_token
import requests


def deliverypoints(id, q):
    token = get_token(id)
    url = 'https://api.cdek.ru/v2/deliverypoints'
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    params = {
        'code': q
    }
    response = requests.get(url, headers=headers, params=params)
    return response.json()


def format_deliverypoint_info(info):
    phones = ", ".join([phone['number'] for phone in info.get('phones', [])])
    formatted_info = (
        f"Код: {info.get('code', 'N/A')}\n"
        f"Название: {info.get('name', 'N/A')}\n"
        # f"UUID: {info.get('uuid', 'N/A')}\n"
        f"Комментарий к адресу: {info.get('address_comment', 'N/A')}\n"
        f"Ближайшая станция: {info.get('nearest_station', 'N/A')}\n"
        f"Время работы: {info.get('work_time', 'N/A')}\n"
        f"Телефоны: {phones}\n"
        f"Электронная почта: {info.get('email', 'N/A')}\n"
        f"Примечание: {info.get('note', 'N/A')}\n"
        f"Тип: {info.get('type', 'N/A')}\n"
        # f"Код владельца: {info.get('owner_code', 'N/A')}\n"
        f"Только прием: {'Да' if info.get('take_only') else 'Нет'}\n"
        f"Пункт выдачи: {'Да' if info.get('is_handout') else 'Нет'}\n"
        f"Прием заказов: {'Да' if info.get('is_reception') else 'Нет'}\n"
        f"Примерочная: {'Да' if info.get('is_dressing_room') else 'Нет'}\n"
        f"LTL: {'Да' if info.get('is_ltl') else 'Нет'}\n"
        f"Безналичная оплата: {'Да' if info.get('have_cashless') else 'Нет'}\n"
        f"Наличная оплата: {'Да' if info.get('have_cash') else 'Нет'}\n"
        f"Система быстрых платежей: {'Да' if info.get('have_fast_payment_system') else 'Нет'}\n"
        f"Разрешен наложенный платеж: {'Да' if info.get('allowed_cod') else 'Нет'}\n"
        f"Минимальный вес: {info.get('weight_min', 'N/A')} кг\n"
        f"Максимальный вес: {info.get('weight_max', 'N/A')} кг\n"
        f"Адрес: {info.get('location', {}).get('address_full', 'N/A')}\n"
    )
    return formatted_info











def info(cdek_number):
    token = get_token()  # Fetch the token only once
    url = f'https://api.cdek.ru/v2/orders?cdek_number={cdek_number}'
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    response = requests.get(url, headers=headers)
    return response.json()

def get_uuid(cdek_number):
    order_info = info(cdek_number)
    return order_info['entity']['uuid']

def arrangement(cdek_number):
    token = get_token()  # Fetch the token only once
    uuid = get_uuid(cdek_number)
    url = f'http://api.cdek.ru/v2/delivery/{uuid}'
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    response = requests.get(url, headers=headers)
    return response.json()


