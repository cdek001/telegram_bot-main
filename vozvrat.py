import aiohttp
import json
import logging
from typing import Optional, Dict, Any # Для type hinting
# Убедитесь, что у вас есть доступ к функции get_token
# Если она не асинхронная, ее вызов будет блокировать цикл событий!
from token_generator import get_token

# Настройка логгера (если еще не настроен глобально)
logger = logging.getLogger(__name__)
# logging.basicConfig(level=logging.INFO) # Раскомментируйте, если логгер не настроен

CDEK_API_BASE_URL = "https://api.cdek.ru/v2"

async def register_client_return(
    user_id: int,
    original_order_uuid: str,
    return_tariff_code: int
) -> Optional[Dict[str, Any]]:
    """
    Регистрирует клиентский возврат для указанного заказа СДЭК.

    Args:
        user_id: ID пользователя Telegram для получения токена авторизации.
        original_order_uuid: UUID оригинального заказа, по которому оформляется возврат.
        return_tariff_code: Код тарифа СДЭК для возврата.

    Returns:
        Словарь с ответом от API СДЭК в случае успеха (статус 202),
        иначе None. Ответ содержит статус обработки запроса и информацию
        о связанных сущностях (включая созданный возвратный заказ).
    """
    # Получаем токен авторизации.
    # ВАЖНО: Если get_token - синхронная функция, она будет блокировать asyncio!
    # В идеале она должна быть асинхронной и вызываться с await.
    # Если она синхронная, рассмотрите запуск в executor: loop.run_in_executor(None, get_token, user_id)
    token = get_token(user_id)
    if not token or token == "Ошибка авторизации":
        logger.error(f"Не удалось получить токен для пользователя {user_id}")
        return None

    # Формируем URL и заголовки
    url = f"{CDEK_API_BASE_URL}/orders/{original_order_uuid}/client_return"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }

    # Формируем тело запроса
    payload = {
        "tariff_code": return_tariff_code
    }

    logger.info(f"Регистрация клиентского возврата для заказа {original_order_uuid} с тарифом {return_tariff_code}")
    logger.debug(f"URL: POST {url}")
    logger.debug(f"Headers: {headers}")
    logger.debug(f"Payload: {json.dumps(payload)}")

    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(url, headers=headers, json=payload) as response:
                try:
                    response_data = await response.json()
                    logger.debug(f"Статус ответа API: {response.status}")
                    logger.debug(f"Тело ответа API: {response_data}")
                except aiohttp.ContentTypeError:
                    # Если ответ не JSON
                    response_text = await response.text()
                    logger.error(f"Ошибка регистрации клиентского возврата для {original_order_uuid}. API вернул не JSON. Статус: {response.status}. Текст: {response_text}")
                    return None
                except json.JSONDecodeError:
                    # Если JSON невалидный
                    response_text = await response.text()
                    logger.error(f"Ошибка декодирования JSON ответа API для {original_order_uuid}. Статус: {response.status}. Текст: {response_text}")
                    return None


                if response.status == 202:
                    logger.info(f"Запрос на регистрацию клиентского возврата для {original_order_uuid} принят (202). Ответ: {response_data}")
                    # Проверяем наличие ошибок или предупреждений в ответе API
                    if 'requests' in response_data:
                       for req in response_data['requests']:
                           if req.get('errors'):
                               logger.warning(f"API вернул ошибки при регистрации возврата для {original_order_uuid}: {req['errors']}")
                           if req.get('warnings'):
                               logger.warning(f"API вернул предупреждения при регистрации возврата для {original_order_uuid}: {req['warnings']}")
                    return response_data
                else:
                    logger.error(f"Ошибка API при регистрации клиентского возврата для {original_order_uuid}. Статус: {response.status}. Ответ: {response_data}")
                    return None # Можно вернуть response_data, чтобы вызывающий код видел ошибку

        except aiohttp.ClientError as e:
            logger.error(f"Ошибка сети/клиента при регистрации клиентского возврата для {original_order_uuid}: {e}", exc_info=True)
            return None
        except Exception as e:
            logger.exception(f"Неожиданная ошибка при регистрации клиентского возврата для {original_order_uuid}: {e}")
            return None