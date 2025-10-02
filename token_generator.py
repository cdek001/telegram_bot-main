# import requests
# import time
# import sqlite3
#
#
# # Создание или подключение к базе данных
# conn = sqlite3.connect('users.db')
# c = conn.cursor()
#
# def get_api_credentials(id):
#     try:
#         # c.execute("SELECT username, password FROM users WHERE user_id = (SELECT MAX(user_id) FROM users)")
#         # c.execute("SELECT username, password FROM users ORDER BY user_id DESC LIMIT 1")
#         c.execute("SELECT username, password FROM users WHERE user_id = ?",
#                   (id,))  # Используем плейсхолдер и кортеж
#         print("get_api_credentials")
#         return c.fetchone()
#     except sqlite3.Error as e:
#         print(f"Ошибка при работе с базой данных: {e}")
#         return None
#
#
#
#
#
# auth_url = 'https://api.cdek.ru/v2/oauth/token?parameters'
#
# # Переменные для хранения токена и времени его истечения
# token = None
# token_expires_at = 0
#
#
# def get_new_token(id):
#     global token, token_expires_at
#     # URL для получения токена
#
#     # Инициализация учетных данных
#     api_credentials = get_api_credentials(id)
#     print("api_credentials", api_credentials)
#     if api_credentials:
#         account, secure_password = api_credentials
#     else:
#         print("Не удалось получить учетные данные из базы данных.")
#
#     auth_data = {
#         'grant_type': 'client_credentials',
#         'client_id': account,
#         'client_secret': secure_password
#     }
#
#     headers = {
#         'Content-Type': 'application/x-www-form-urlencoded'
#     }
#     response = requests.post(auth_url, data=auth_data, headers=headers)
#     if response.status_code == 200:
#         token_info = response.json()
#         token = token_info.get('access_token')
#         # Время истечения токена (текущие время + 3600 секунд)
#         token_expires_at = time.time() + token_info.get('expires_in', 3600)
#         print(token, token_expires_at)
#     else:
#         print('Ошибка авторизации:', response.json())
#         # exit()


# def get_token(id):
#     print("get_token")
#     if token is None or time.time() >= token_expires_at:
#         get_new_token(id)
#     return token



# def get_token_proverka(account, secure_password):
#     auth_data = {
#         'grant_type': 'client_credentials',
#         'client_id': account,
#         'client_secret': secure_password
#     }
#     headers = {
#         'Content-Type': 'application/x-www-form-urlencoded'
#     }
#     auth_url = 'https://api.cdek.ru/v2/oauth/token?parameters'
#     response = requests.post(auth_url, data=auth_data, headers=headers)
#     print(account, secure_password)
#     if response.status_code == 200:
#         token_info = response.json()
#         print(token_info)
#         return token_info
#     else:
#         print('Ошибка авторизации:', response.json())
#         return 'Ошибка авторизации'





import requests
import time
import sqlite3

# --- ИЗМЕНЕНИЕ 1: Заменяем глобальные переменные на словарь-кеш ---
# Ключом будет user_id, значением - словарь с токеном и временем истечения
token_cache = {}

# Подключение к базе данных
conn = sqlite3.connect('users.db')
c = conn.cursor()

def get_api_credentials(user_id):
    """Получает учетные данные для конкретного пользователя."""
    try:
        c.execute("SELECT username, password FROM users WHERE user_id = ?", (user_id,))
        return c.fetchone()
    except sqlite3.Error as e:
        print(f"Ошибка при работе с базой данных для user_id {user_id}: {e}")
        return None

def get_new_token(user_id):
    """Запрашивает и кеширует новый токен для конкретного пользователя."""
    global token_cache
    auth_url = 'https://api.cdek.ru/v2/oauth/token?parameters'

    api_credentials = get_api_credentials(user_id)
    if not api_credentials:
        print(f"Не удалось получить учетные данные из базы данных для user_id {user_id}.")
        return None

    account, secure_password = api_credentials
    auth_data = {
        'grant_type': 'client_credentials',
        'client_id': account,
        'client_secret': secure_password
    }
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}

    try:
        response = requests.post(auth_url, data=auth_data, headers=headers)
        response.raise_for_status()  # Вызовет ошибку для плохих статусов
        token_info = response.json()

        # --- ИЗМЕНЕНИЕ 2: Сохраняем токен в кеш по user_id ---
        token_cache[user_id] = {
            'token': token_info.get('access_token'),
            'expires_at': time.time() + token_info.get('expires_in', 3600)
        }
        print(f"Получен новый токен для user_id: {user_id}")
        return token_cache[user_id]['token']
    except requests.exceptions.RequestException as e:
        print(f'Ошибка авторизации для user_id {user_id}: {e}')
        if 'response' in locals():
            print(f'Ответ сервера: {response.text}')
        # Очищаем невалидные данные из кеша, если они там были
        if user_id in token_cache:
            del token_cache[user_id]
        return None


def get_token(user_id):
    """Получает токен для пользователя, используя кеш."""
    global token_cache
    print(f"Запрос токена для user_id: {user_id}")

    user_token_info = token_cache.get(user_id)

    # --- ИЗМЕНЕНИЕ 3: Проверяем кеш для конкретного пользователя ---
    if user_token_info is None or time.time() >= user_token_info['expires_at']:
        # Если для этого пользователя токена нет или он просрочен, получаем новый
        return get_new_token(user_id)

    # Иначе возвращаем токен из кеша
    print(f"Используется кешированный токен для user_id: {user_id}")
    return user_token_info['token']



# Функция для проверки логина/пароля остаётся без изменений
def get_token_proverka(account, secure_password):
    # ... (этот код не меняется)
    auth_data = {
        'grant_type': 'client_credentials',
        'client_id': account,
        'client_secret': secure_password
    }
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    auth_url = 'https://api.cdek.ru/v2/oauth/token?parameters'
    response = requests.post(auth_url, data=auth_data, headers=headers)
    print(account, secure_password)
    if response.status_code == 200:
        token_info = response.json()
        print(token_info)
        return token_info
    else:
        print('Ошибка авторизации:', response.json())
        return 'Ошибка авторизации'