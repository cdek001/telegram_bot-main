import json
import logging

import requests

from token_generator import get_token
#
# from telegram import KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove, Update, WebAppInfo
# from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
#
# # Enable logging
# logging.basicConfig(
#     format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
# )
# # set higher logging level for httpx to avoid all GET and POST requests being logged
# logging.getLogger("httpx").setLevel(logging.WARNING)
#
# logger = logging.getLogger(__name__)
#
#
# # Define a `/start` command handler.
# async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
#     """Send a message with a button that opens a the web app."""
#     await update.message.reply_text(
#         "Please press the button below to choose a color via the WebApp.",
#         reply_markup=ReplyKeyboardMarkup.from_button(
#             KeyboardButton(
#                 text="Open the color picker!",
#                 web_app=WebAppInfo(url="https://mikforce.github.io/cdek.github.io/"),
#             )
#         ),
#     )
#
#
# # Handle incoming WebAppData
# async def web_app_data(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
#     """Print the received data and remove the button."""
#     # Here we use `json.loads`, since the WebApp sends the data JSON serialized string
#     # (see webappbot.html)
#     data = json.loads(update.effective_message.web_app_data.data)
#     await update.message.reply_html(
#         text=(
#             f"You selected the color with the HEX value <code>{data}</code>. The "
#             f"corresponding RGB value is <code>{tuple(data.values())}</code>."
#         ),
#         reply_markup=ReplyKeyboardRemove(),
#     )
#
#
# def main() -> None:
#     """Start the bot."""
#     # Create the Application and pass it your bot's token.
#     application = Application.builder().token("7020285176:AAEr9NQt7m3pljwWAMfYANb1EjdMeQKmgVQ").build()
#
#     application.add_handler(CommandHandler("start", start))
#     application.add_handler(MessageHandler(filters.StatusUpdate.WEB_APP_DATA, web_app_data))
#
#     # Run the bot until the user presses Ctrl-C
#     application.run_polling(allowed_updates=Update.ALL_TYPES)
#
#
# if __name__ == "__main__":
#     main()


# import asyncio
# import logging
# from aiogram import Bot, Dispatcher
# from aiogram.types import Message, WebAppInfo, ReplyKeyboardMarkup, KeyboardButton
# from aiogram.utils.web_app import safe_parse_webapp_init_data
# from aiohttp.web import Request, json_response
#
#
# logging.basicConfig(level=logging.INFO)
# API_TOKEN = '7020285176:AAEr9NQt7m3pljwWAMfYANb1EjdMeQKmgVQ'
#
# # Define a handler to start the bot and send the web app
# bot = Bot(token=API_TOKEN)
# dp = Dispatcher(bot)
#
#
# # Define a handler to start the bot and send the web app
# @dp.message_handler(commands=['start'])
# async def send_welcome(message: Message):
#     keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
#     web_app_info = WebAppInfo(url="https://mikforce.github.io/cdek.github.io/")
#     keyboard.add(KeyboardButton(text="Open Web App", web_app=web_app_info))
#     await message.answer("Click the button to open the Web App", reply_markup=keyboard)
#
#
# # Define a handler to process WebApp data
# @dp.message_handler(content_types="web_app_data")
# async def check_data_handler(request: Request):
#
#     logging.info(f"Received data: {request}")
#
#     await request.answer(request)
#
#
#
# import asyncio
# # Run the bot
# if __name__ == '__main__':
#     from aiogram import executor
#     from aiohttp import web
#
#     app = web.Application()
#     app.router.add_post('/webapp-data', check_data_handler)
#
#     loop = asyncio.get_event_loop()
#     # loop.create_task(web._run_app(app, host='localhost', port=8080))
#
#     executor.start_polling(dp, skip_updates=True)

# API_KEY = "e76077adb79ecf5925910c5a7f856f514f04429e"
# secret = "9ef0e08714737f6d36ced0170e0c17d3a10a78f3"
#
# import requests
# import json
#
# # Базовый URL API для поиска компаний
# url = "https://suggestions.dadata.ru/suggestions/api/4_1/rs/findById/party"
#
# # Данные для поиска (например, ИНН компании)
# data = {
#     "query": "5040142770",  # Замените на нужный ИНН, ОГРН или название
#     "count": 1  # Максимальное количество возвращаемых результатов
# }
#
# # Заголовки для авторизации
# headers = {
#     "Content-Type": "application/json",
#     "Accept": "application/json",
#     "Authorization": f"$Token {API_KEY}"
# }
#
# # Выполнение POST-запроса к API
# try:
#     response = requests.post(url, json=data, headers=headers, timeout=1000)  # Увеличено время ожидания до 10 секунд
#
#     # Проверка статуса ответа
#     if response.status_code == 200:
#         # Обработка данных ответа
#         result = response.json()
#         print("Информация о компании:", result)
#     elif response.status_code == 403:
#         print("Ошибка 403: Доступ запрещен. Проверьте ваши API-ключи и права доступа.")
#     else:
#         print(f"Ошибка {response.status_code}: {response.text}")
# except requests.exceptions.Timeout:
#     print("Ошибка: время ожидания ответа от сервера истекло.")

# import sqlite3
# import os
#
# # Убедитесь, что путь к базе данных корректен.
# db_path = './data/users.db'  # Замените на ваш путь к базе данных
#
# # Проверяем, существует ли файл базы данных
# if not os.path.exists(db_path):
#     print(f"Database file '{db_path}' does not exist.")
# else:
#     # Подключаемся к базе данных
#     conn = sqlite3.connect(db_path)
#     cursor = conn.cursor()
#
#     # Выводим список всех таблиц в базе данных
#     cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
#     tables = cursor.fetchall()
#
#     if tables:
#         print("Tables in the database:")
#         for table_name in tables:
#             print(f"- {table_name[0]}")
#
#             # Выводим все данные из текущей таблицы
#             cursor.execute(f"SELECT * FROM {table_name[0]};")
#             rows = cursor.fetchall()
#
#             # Печатаем строки таблицы
#             for row in rows:
#                 print(row)
#
#             print("\n")
#     else:
#         print("No tables found in the database.")
#
#     # Закрываем соединение
#     conn.close()


entity_info = order_info_dict['entity']
# Обработка статусов
statuses = entity_info.get('statuses', [])
status_text = ""
moscow_tz = pytz.timezone('Europe/Moscow')

for status in statuses:
    # Убираем смещение +0000
    date_time_str = status['date_time'][:-5]  # Удаляем последние 5 символов
    # Парсим строку даты и времени
    utc_time = datetime.strptime(date_time_str, '%Y-%m-%dT%H:%M:%S')
    # Присваиваем UTC временную зону
    utc_time = pytz.utc.localize(utc_time)
    # Переводим в московское время
    moscow_time = utc_time.astimezone(moscow_tz)

    # Форматируем строку
    status_text += f"📌 *Стус:* {status['name']} ({status['code']}) - {moscow_time.strftime('%Y-%m-%d %H:%M:%S')} - {status['city']}\n"

# Format the output
entity_text = (
    f"📦 *Информация об отправлении:*\n\n"
    f"📝 *Номер отправления:* {entity_info.get('cdek_number', 'N/A')}\n\n"
    f"  💬 *Комментарий:* {entity_info.get('comment', 'N/A')}\n\n"
    f"📍 *Пункт доставки:* {entity_info.get('delivery_point', 'N/A')}\n"
    f"  👥 *Отправитель:* {entity_info['sender'].get('company', 'N/A')} - {entity_info['sender'].get('name', 'N/A')}\n"
    f"  👥 *Получатель:* {entity_info['recipient'].get('company', 'N/A')} - {entity_info['recipient'].get('name', 'N/A')}\n"
    f"  🚚 *Итоговая стоимость заказа: {entity_info.get('delivery_detail', {}).get('total_sum', 'N/A')} руб.\n\n"
    f"👤 *Отправитель:* {entity_info.get('sender', {}).get('name', 'N/A')}\n"
    f"  📞 *Телефон отправителя:* {entity_info.get('sender', {}).get('phones', [{}])[0].get('number', 'N/A')}\n\n"
    # f"🏢 *Компания получателя:* {entity_info.get('recipient', {}).get('company', 'N/A')}\n"
    f"👤 *Получатель:* {entity_info.get('recipient', {}).get('name', 'N/A')}\n"
    f"  📞 *Телефон получателя:* {entity_info.get('recipient', {}).get('phones', [{}])[0].get('number', 'N/A')}\n\n"
    f"📌 *Отправлено из:* {entity_info.get('from_location', {}).get('country', 'N/A')}, {entity_info.get('from_location', {}).get('city', 'N/A')}, {entity_info.get('from_location', {}).get('address', 'N/A')}\n"
    f"📌 *Отправлено в:* {entity_info.get('to_location', {}).get('country', 'N/A')}, {entity_info.get('to_location', {}).get('city', 'N/A')}, {entity_info.get('to_location', {}).get('address', 'N/A')}\n\n"
    f"📦 *Данные о посылки:*\n"
)

# Добавление информации о пакетах
for package in entity_info.get('packages', []):
    entity_text += (
        f"    - 📦 Номер место: {package.get('number', 'N/A')}, "
        f"Вес: {package.get('weight', 'N/A')} г, "
        f"Размеры: {package.get('length', 'N/A')}x{package.get('width', 'N/A')}x{package.get('height', 'N/A')} см\n"
        f"      *Содержимое:*\n"
    )
    for item in package.get('items', []):
        entity_text += (
            f"        - 🎁 {item.get('name', 'N/A')}: "
            f"Вес: {item.get('weight', 'N/A')} г, "
            f"Стоимость: {item.get('cost', 'N/A')} руб.\n"
        )

# entity_text += "🔚 *Конец информации.*"                    # Add your code to process and send the entity information
keyboard = InlineKeyboardMarkup()
keyboard.add(
    InlineKeyboardButton("Телефон офиса ответственного за вручение посылки",
                         callback_data='delivery_office_phone'),
    InlineKeyboardButton("Назад", callback_data='go_back')
)
await bot.send_message(callback_query.from_user.id, entity_text, reply_markup=keyboard)




















