# aiogram   2.23.1
import sqlite3
import os
import json
from datetime import timedelta, datetime

import requests
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.types import InputMediaPhoto
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram import types
from aiogram.types import WebAppInfo, ReplyKeyboardMarkup, KeyboardButton
from aiogram.dispatcher.filters import Text
from aiogram.types import Message
from aiohttp.web import Request, json_response
import logging
from aiogram.dispatcher.filters import Command
from aiogram.utils.markdown import escape_md
from datetime import datetime
from aiogram.utils.markdown import code
from aiogram.utils.exceptions import TelegramAPIError
# 10006324754 склад-дверь
# 10007168378 до пвз
# lYV0wvt14fYGgE7MoWosaIyvOavEqqUm
# 2ABI0GEJN5giKtlgHh2ZZ1rCsz2iWoHZ
# Настройка базового логирования
from token_generator import get_token
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from cedek_blizh_office import get_nearest_gdp_offices


MANAGER_ID = 6536870230

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    filename='bot_log.log')

# Получение логгера для aiogram
logger = logging.getLogger('aiogram')

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(console_formatter)

# Добавление обработчика к логгеру aiogram
logger.addHandler(console_handler)

# Initialize bot and dispatcher   7020285176:AAEr9NQt7m3pljwWAMfYANb1EjdMeQKmgVQ
# для теста 7207186878:AAGGEFlLavEBD0GXGTvRIgQZ7SLwHzlDHz8
bot = Bot(token="7351691962:AAGASpTq7J-uif9R7p0bphxbqs8gmx7oPP4")
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
dp.middleware.setup(LoggingMiddleware())

# Database setup

conn = sqlite3.connect('users.db')    #для деплоя докера

# conn = sqlite3.connect('users.db')
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                  id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  user_id INTEGER UNIQUE, 
                  username TEXT, 
                  password TEXT)''')  # Обновленная структура таблицы

cursor.execute('''CREATE TABLE IF NOT EXISTS new_orders
                  (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, cdek_number TEXT, order_info TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')

# Создание таблицы для хранения информации о пользователях и их заказах
cursor.execute('''CREATE TABLE IF NOT EXISTS user_zakaz (
                  id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  user_id INTEGER, 
                  weight INTEGER, 
                  name TEXT, 
                  comment TEXT, 
                  phone_number TEXT, 
                  city TEXT, 
                  address TEXT, 
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  FOREIGN KEY (user_id) REFERENCES new_orders(user_id))''')

class Form(StatesGroup):
    login = State()
    password = State()
    order_number = State()
    order_number2 = State()
    order_number3 = State()
    fio = State()
    tel = State()
    adr = State()
    pwz = State()
    cit = State()
    inpzt = State()
    npdc = State()
    dubl = State()
    call_request = State()
    kurier = State()
    address = State()
    konsalid = State()
    date = State()
    time = State()
    change_delivery_date_date = State()
    change_delivery_date_time_from = State()
    change_delivery_date_time_to = State()
    change_delivery_date_comment = State()
    waiting_for_city = State()  # Добавляем новое состояние
    address_confirmation = State()  # Define a new state in your Form class
    waiting_for_inn = State()  # Состояние ожидания ИНН


async def check_user(user_id):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result


# Функция для проверки наличия данных по user_id
def check_user_id_exists(user_id):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM users WHERE user_id = ?', (user_id,))
    count = cursor.fetchone()[0]
    # Закрытие соединения
    conn.close()
    return count > 0

@dp.message_handler(commands='start')
async def start(message: types.Message):
    # Создаем инлайн клавиатуру
    keyboard = InlineKeyboardMarkup(row_width=1)

    # Добавляем кнопки
    keyboard.add(
        # InlineKeyboardButton("🔑 Войти в личный кабинет", callback_data="register_1"),
        InlineKeyboardButton("📝 Заключить договор", callback_data="register_ek5"),
        InlineKeyboardButton("✅ Подключить бота к ЛК", callback_data="register_1"),
        InlineKeyboardButton("📦 Отслеживание посылки", callback_data="otsl"),
        InlineKeyboardButton("Документация", callback_data="docs")
    )

    await message.answer(
        "👋 Привет! Добро пожаловать в чат-бот СДЭК!\n\n"
        "🚚 Мы рады помочь вам с доставкой. Вот что вы можете сделать:\n\n"
        "Нажмите кнопку '📦 Отслеживание посылки' для того что бы отследить посылку.\n"
        "Для того чтобы воспользоваться всем функционалом Вам необходимо зарегестрироваться.\n"
        # "1️⃣2️ ️⃣  ️⃣ 3️⃣ Уже есть личный кабинет на сайте Сдек? Нажмите '🔑 Войти в личный кабинет'.\n"
        "1️⃣ Новый клиент? Нажмите '📝 Зарегистрироваться на сайте СДЭК'.\n"
        "2️⃣ Есть аккаунт, но бот еще не подключен? Нажмите '✅ Подключить бота к ЛК'.\n\n"
        "Так же вы можете ознакомиться со всем фугкционалом нажав на кнопку 'Документация'"
        "Выберите нужное действие, и давайте начнем! 😊",
        reply_markup=keyboard
    )


@dp.callback_query_handler(lambda c: c.data == 'register_1')
async def cmd_register(callback_query: types.CallbackQuery):
    user = await check_user(callback_query.from_user.id)
    if user:
        await bot.send_message(callback_query.from_user.id, "Здравствуйте! Вы вошли в личный кабинет.")
    else:
        # Путь к видео в вашем проекте
        video_path = os.path.join(os.getcwd(), 'video (video-converter.com).mp4')  # Замените на имя вашего видеофайла
        # Отправка видео
        with open(video_path, 'rb') as video:
            await bot.send_video(callback_query.from_user.id, video,
                                 caption="Видео: Для получения логина и пароля вам необходимо выполнить действия, которые показаны в видео.")
        await bot.send_message(callback_query.from_user.id,
                               "Вы не зарегистрированы. Пожалуйста, зарегистрируйтесь, нажав на кнопку 'Регистрация'.")

        keyboard = InlineKeyboardMarkup()
        registration_button = InlineKeyboardButton("Регистрация", callback_data="register")
        keyboard.add(registration_button)
        await bot.send_message(callback_query.from_user.id, "Нажмите для регистрации:", reply_markup=keyboard)





    await callback_query.answer()




@dp.callback_query_handler(lambda c: c.data =='register')
async def cmd_start(callback_query: types.CallbackQuery):  # Изменено на callback_query
    user = await check_user(callback_query.from_user.id)  # Используйте callback_query от колбэка
    if user:
        await bot.send_message(callback_query.from_user.id, f"Привет, {user[2]}! Вы вошли в личный кабинет.")  # Ответ через bot
    else:
        await bot.send_message(callback_query.from_user.id, "Вы не зарегистрированы. Пожалуйста, введите ваш идентификатор вашего ключа интеграции.")  # Ответ через bot
        await Form.login.set()

@dp.message_handler(state=Form.login)
async def process_login(message: types.Message, state: FSMContext):
    login = message.text
    # Проверка на минимальное и максимальное количество символов
    if 32 <= len(login):  # Например, от 1 до 32 символов
        await state.update_data(login=login)
        await message.answer("Теперь введите ваш Пароль ключа интеграции.")
        await Form.password.set()
    else:
        await message.answer("Логин должен содержать 32 символа. Пожалуйста, попробуйте снова.")
        # Завершаем состояние, чтобы прекратить ожидание ввода нового логина
        await state.finish()




@dp.message_handler(lambda message: message.text =='/main')
async def cmd_start1(message: types.Message, state: FSMContext):
    user = await check_user(message.from_user.id)

    if user:
        # Зарегистрированный пользователь
        keyboard = InlineKeyboardMarkup()
        keyboard.row(InlineKeyboardButton("Номер заказа (накладной) 📝", callback_data='enter_waybill'))
        keyboard.row(InlineKeyboardButton("Номер заказа Интернет-магазина 🛍️", callback_data='enter_webshop_order'))
        keyboard.row(InlineKeyboardButton("Что необходимо для получения посылки 📦",
                                          web_app=WebAppInfo(url='https://mobile.cdek.ru/packageto')))
        keyboard.row(InlineKeyboardButton("Заказать курьера (Забор груза) 🚪", callback_data='/zaborgruz'))
        keyboard.row(
            InlineKeyboardButton("Списки регионов/офисов/населенных пунктов 📍", callback_data='/lists'))
        keyboard.row(InlineKeyboardButton("Продублировать накладную если у вас дверь-склад 📝",
                                          callback_data='duplicate_waybill'))

        await message.answer("Ваше меню для юридических лиц:", reply_markup=keyboard)
    else:
        await message.answer("Для доступа к функционалу необходима регистрация. Введите /start для начала регистрации.")



# @dp.callback_query_handler(lambda c: c.data == 'register_ek5')
# async def process_register_ek5(callback_query: types.CallbackQuery):
#     await bot.send_message(callback_query.from_user.id, "Сайт для перехода и регистрации в ek5: https://cdek.ru.net/registration/ вы так же можете нажать /faq что бы ознакомиться как пройти регистрацию.")
@dp.callback_query_handler(lambda c: c.data == 'register_ek5', state=None) # Убедимся, что он не сработает, если пользователь уже в каком-то состоянии
async def process_register_ek5_start(callback_query: types.CallbackQuery, state: FSMContext):
    """
    Этот обработчик срабатывает при нажатии кнопки 'register_ek5'.
    Он запрашивает ИНН и переводит пользователя в состояние ожидания ввода.
    """
    await bot.answer_callback_query(callback_query.id) # Отвечаем на колбэк, чтобы убрать "часики" на кнопке
    await bot.send_message(
        callback_query.from_user.id,
        "Пожалуйста, введите ваш ИНН (Индивидуальный Номер Налогоплательщика):"
    )
    # Устанавливаем состояние ожидания ИНН для этого пользователя
    await Form.waiting_for_inn.set()
    # Можно сохранить user_id в данных состояния, если нужно будет передать дальше
    # await state.update_data(user_id_to_notify=callback_query.from_user.id)


# 3. Создаем обработчик для получения ИНН
@dp.message_handler(state=Form.waiting_for_inn)
async def process_inn_input(message: types.Message, state: FSMContext):
    """
    Этот обработчик ловит сообщение пользователя, когда он находится
    в состоянии waiting_for_inn.
    """
    user_inn = message.text
    user_id = message.from_user.id
    username = message.from_user.username # Получаем @username, если есть
    first_name = message.from_user.first_name # Имя пользователя

    # --- (Опционально) Валидация ИНН ---
    # Можно добавить проверку, что введенное значение похоже на ИНН
    # Например, состоит только из цифр и имеет длину 10 или 12
    if not user_inn.isdigit() or len(user_inn) not in [10, 12]:
        await message.reply("ИНН должен состоять из 10 или 12 цифр. Пожалуйста, попробуйте еще раз:")
        return # Остаемся в том же состоянии, ждем корректный ввод
    # --- /Валидация ---

    # Формируем сообщение для менеджера
    manager_message_text = (
        f"🔔 Новая заявка на регистрацию EK5!\n\n"
        f"👤 Пользователь: {first_name}\n"
        f"🆔 User ID: {user_id}\n"
        f"@{username if username else 'Нет username'}\n\n"
        f"  ИНН: `{user_inn}`" # Используем Markdown для выделения ИНН
    )

    try:
        # Отправляем сообщение менеджеру
        await bot.send_message(MANAGER_ID, manager_message_text)
        # Отправляем подтверждение пользователю
        await message.reply("✅ Спасибо! Ваш ИНН получен и отправлен менеджеру на рассмотрение.")

    except Exception as e:
        logging.error(f"Ошибка отправки сообщения менеджеру {MANAGER_ID}: {e}")
        # Сообщаем пользователю об ошибке
        await message.reply("❌ Произошла ошибка при отправке данных менеджеру. Пожалуйста, попробуйте позже или свяжитесь с поддержкой.")

    finally:
        # Сбрасываем состояние пользователя, чтобы он мог использовать бота дальше
        await state.finish()









@dp.callback_query_handler(lambda c: c.data == 'docs')
async def process_doc(callback_query: types.CallbackQuery):
    text = '''Команды Telegram бота для работы с API СДЭК:

/nomer
Получение информации по номеру заказа СДЭК.
Использует метод API: GET /orders
Пользователь должен ввести номер заказа после команды.
Бот возвращает текущий статус заказа, информацию о получателе, стоимость доставки и другие детали.

/im
Получение информации по номеру заказа интернет-магазина (ИМ).
Использует метод API: GET /orders
Пользователь должен ввести номер заказа ИМ после команды.
Бот возвращает информацию о заказе, связанную с данным номером ИМ.

/sklad_dver (ранее /zaborgruz)
Создание заказа по схеме "Склад-дверь".
Использует метод API: POST /orders
Бот запрашивает у пользователя необходимую информацию для создания заказа (адрес получателя, вес, габариты и т.д.).
После получения всех данных, создается заказ на доставку со склада СДЭК до двери получателя.

/zaborgruza
Заказ забора груза.
Использует метод API: POST /intakes
Бот запрашивает информацию о месте и времени забора груза, контактные данные отправителя.
Создается заявка на забор груза курьером СДЭК.

/doc
Получение документов (функционал в разработке).
В будущем может использовать методы API для получения различных документов (накладные, акты и т.д.).

/faq
Предоставление информации о сервисе.
Не требует обращения к API.
Выводит часто задаваемые вопросы и ответы на них.

/lists
Получение списков регионов, офисов, населенных пунктов.
Использует методы API: GET /location/regions, GET /deliverypoints, GET /location/cities
Позволяет пользователю запросить список регионов, офисов СДЭК или населенных пунктов.

/dan_zakaz
Добавление шаблона для забора груза.
Может использовать метод API: POST /intakes для сохранения шаблона
Бот запрашивает и сохраняет информацию о типичном заборе груза для быстрого создания заявок в будущем.

/zabor_konsalid
Забор консолидированного груза.
Использует метод API: POST /intakes с специфическими параметрами
Бот запрашивает информацию о нескольких грузах, которые нужно забрать одновременно.

/info_delivery_problem
Информация о проблеме доставки.
Использует метод API: GET /orders/{order_uuid}/statuses
Пользователь вводит номер проблемного заказа, бот возвращает детальную информацию о статусе и возможных проблемах.

/human_chat
Запрос на общение с поддержкой.
Не требует обращения к API СДЭК.
Ставит пользователя в очередь на общение с оператором поддержки.

/end_chat
Закрытие чата с поддержкой.
Не требует обращения к API СДЭК.
Завершает сессию общения с оператором поддержки.

/ypakovka
Заказ упаковки СДЭК.
Может использовать метод API: POST /orders с специфическими параметрами для заказа упаковки
Бот показывает доступные виды упаковки и позволяет пользователю заказать необходимую.'''
    await bot.send_message(callback_query.from_user.id, text)
@dp.callback_query_handler(lambda c: c.data == 'otsl')
async def process_register_ek5(callback_query: types.CallbackQuery):
    from ots_luboy_posilki import ots_l_p

    await bot.send_message(callback_query.from_user.id, "Введите номер посылки:")

    @dp.message_handler(lambda message: message.from_user.id == callback_query.from_user.id)
    async def handle_package_number(message: types.Message):
        package_number = message.text
        response = ots_l_p(package_number)  # Функция для получения данных о посылке
        try:
            if response:  # Проверяем, что ответ вообще есть
                if 'result' in response and response['result']:  # Проверяем наличие ключа result
                    result = response['result']
                    if 'order' in result and 'statuses' in result:  # Проверяем наличие заказа и статусов
                        order = result['order']
                        # pwz = result['updateInfo']['possibleDeliveryMode'] # Эта переменная не используется, можно убрать или использовать позже
                        sender = order['sender']
                        receiver = order['receiver']
                        sender_name_parts = sender['name'].split()
                        # Более надежное получение инициалов
                        sender_initials_list = [part[0].upper() for part in sender_name_parts if
                                                part and part[0].isalpha()]
                        sender_initials = '.'.join(sender_initials_list) + '.' if sender_initials_list else sender[
                            'name']  # Возвращаем имя если инициалы не получились

                        # Определение типа доставки
                        delivery_modes = {
                            "1": "дверь-дверь",
                            "2": "дверь-склад",
                            "3": "склад-дверь",
                            "4": "склад-склад",
                            "5": "терминал-терминал",
                            "6": "дверь-постамат",
                            "7": "склад-постамат",
                        }
                        delivery_mode = delivery_modes.get(order.get('trueDeliveryMode'), "неизвестный тип доставки")

                        message_text = (
                            "📦 *ДАННЫЕ ПОСЫЛКИ*\n"
                            "---\n"
                            f"🆔 *Номер заказа:* `{order.get('number', 'N/A')}`\n"
                            f"📦 *Количество мест:* {order.get('packagesCount', 'N/A')}\n"
                            f"📅 *Создан:* {order.get('creationTimestamp', 'N/A')[:10]}\n"
                            f"⚖️ *Вес:* {order.get('weight', 'N/A')} кг\n"
                            f"🚛 *Тип доставки:* {delivery_mode}\n\n"

                            "👤 *ОТПРАВИТЕЛЬ*\n"
                            "---\n"
                            f"├─ *Имя:* {sender_initials}\n"
                            f"└─ 🏙️ *Город:* {sender.get('address', {}).get('city', {}).get('name', 'N/A')}\n\n"  # Добавил .get для безопасности

                            "📬 *ПОЛУЧАТЕЛЬ*\n"
                            "---\n"
                            f"├─ *Инициалы:* {receiver.get('initials', 'N/A')}\n"
                            # Всегда выводим адрес получателя
                            f"└─ 🏠 *Адрес:* {receiver.get('address', {}).get('title', 'N/A')}, {receiver.get('address', {}).get('city', {}).get('name', 'N/A')}\n\n"
                        # Используем └─ здесь
                        )

                        # --- ИСТОРИЯ ДОСТАВКИ (теперь всегда выводится) ---
                        message_text += (
                            "📊 *ИСТОРИЯ ДОСТАВКИ*\n"
                            "---\n"
                        )
                        # Проверяем, что статусы существуют и это список
                        statuses = result.get('statuses', [])
                        if statuses:
                            for status in statuses:
                                city_info = f" {status['currentCity']['name']}" if 'currentCity' in status and status[
                                    'currentCity'] else ''
                                timestamp = status.get('timestamp', 'N/A')[:10]
                                message_text += f"├─ 🔄 *{status.get('name', 'Статус неизвестен')}*{city_info}  {timestamp}\n"
                        else:
                            message_text += "├─ История доставки недоступна.\n"
                        message_text += "\n"  # Добавляем пустую строку после истории

                        # --- ДЕТАЛИ ПВЗ/ОФИСА (только если есть ключ 'office') ---
                        if 'office' in receiver.get('address', {}):
                            office = receiver['address']['office']
                            message_text += f"🏢 *ИНФОРМАЦИЯ О ПУНКТЕ ВЫДАЧИ ({office.get('type', 'ПВЗ')})*\n"  # Используем тип офиса, если есть
                            message_text += "---\n"
                            # Можно переопределить адрес, если он отличается от основного адреса получателя
                            # message_text += f"├─ *Адрес ПВЗ:* {receiver['address']['title']}, {receiver['address']['city']['name']}\n"
                            if office.get('comment'):
                                message_text += f"├─ *Комментарий:* {office['comment']}\n"
                            if office.get('phones'):
                                message_text += f"├─ *Контакты:* {office['phones'][0]['number']}\n"  # Берем первый телефон



                            # Словарь для перевода дней недели на русский (короткие названия)
                            day_map_ru = {
                                "MONDAY": "Пн",
                                "TUESDAY": "Вт",
                                "WEDNESDAY": "Ср",
                                "THURSDAY": "Чт",
                                "FRIDAY": "Пт",
                                "SATURDAY": "Сб",
                                "SUNDAY": "Вс"
                            }

                            # Добавление графика работы
                            schedule_list = office.get('schedule', [])
                            if schedule_list:
                                message_text += "📅 *ГРАФИК РАБОТЫ ПВЗ*\n"
                                # message_text += "---\n" # Можно убрать дублирующий разделитель
                                for schedule in schedule_list:
                                    # Получаем английские названия дней
                                    startDay_en = schedule.get('startDay')
                                    endDay_en = schedule.get('endDay')

                                    # Переводим дни на русский, используя словарь
                                    # Если дня нет в словаре, оставляем английское название как запасной вариант
                                    startDay_ru = day_map_ru.get(startDay_en, startDay_en)
                                    endDay_ru = day_map_ru.get(endDay_en, endDay_en)

                                    # Формируем строку с русскими днями
                                    # Проверяем исходные английские дни для логики
                                    if startDay_en and endDay_en and startDay_en != endDay_en:
                                        days = f"{startDay_ru} - {endDay_ru}"
                                    elif startDay_en:  # Если дни совпадают или endDay отсутствует
                                        days = startDay_ru
                                    else:  # Если startDay отсутствует
                                        days = "N/A"  # Или другое значение по умолчанию

                                    # Формируем строку с часами работы (без изменений)
                                    working_hours = f"{schedule.get('startTime', 'N/A')[:5]} - {schedule.get('endTime', 'N/A')[:5]}"

                                    # Добавляем строку в сообщение
                                    message_text += f"├─ • *{days}:* {working_hours}\n"

                            message_text += "\n"  # Добавляем пустую строку после блока ПВЗ




                        # --- ИНФОРМАЦИЯ О СКЛАДЕ (по твоему условию) ---
                        # Если доставка НЕ дверь-дверь ("1") и НЕ склад-дверь ("3")
                        if order.get('trueDeliveryMode') not in ["1", "3"]:
                            if 'warehouse' in result:
                                warehouse = result['warehouse']
                                # Используем .get() для безопасного доступа
                                planned_end_date = warehouse.get('acceptance', {}).get('plannedEndDate', 'недоступно')

                                storage_days = 'недоступно'
                                if 'storage' in warehouse and 'days' in warehouse['storage']:
                                    storage_days = f"{warehouse['storage']['days']} дней"

                                message_text += (
                                    "🏭 *ИНФОРМАЦИЯ О СКЛАДЕ ПРИБЫТИЯ*\n"  # Немного уточнил заголовок
                                    "---\n"
                                    f"├─ 📆 *Планируемая дата поступления/выдачи:* {planned_end_date}\n"  # Уточнил текст
                                    f"└─ 🗄️ *Срок хранения:* {storage_days}\n\n"  # Добавил \n
                                )

                        # Можно добавить еще информацию, если нужно, например, о курьере
                        if 'deliveryAgreement' in result and result['deliveryAgreement']:
                            agreement = result['deliveryAgreement']
                            message_text += (
                                "🚚 *ИНФОРМАЦИЯ О ДОСТАВКЕ КУРЬЕРОМ*\n"
                                "---\n"
                                f"├─ *Согласованная дата:* {agreement.get('date', 'N/A')}\n"
                                f"└─ *Согласованное время:* {agreement.get('startTime', 'N/A')[:5]} - {agreement.get('endTime', 'N/A')[:5]}\n\n"
                            )

                        if 'courierProblem' in result and result['courierProblem']:
                            problem = result['courierProblem']
                            message_text += (
                                "⚠️ *ПРОБЛЕМА С ДОСТАВКОЙ*\n"
                                "---\n"
                                f"└─ *Причина:* {problem.get('reasonText', 'Не указана')}\n\n"
                            )
            # if response:
            #     order = response['result']['order']
            #     pwz = response['result']['updateInfo']['possibleDeliveryMode']
            #     sender = order['sender']
            #     receiver = order['receiver']
            #     sender_name_parts = sender['name'].split()
            #     sender_initials = ' '.join(
            #         [part[0] for part in sender_name_parts if part[0].isalpha()]) + '.' if sender_name_parts else ''
            #
            #     # Определение типа доставки
            #     delivery_modes = {
            #         "1": "дверь-дверь",
            #         "2": "дверь-склад",
            #         "3": "склад-дверь",
            #         "4": "склад-склад",
            #         "5": "терминал-терминал",
            #         "6": "дверь-постамат",
            #         "7": "склад-постамат",
            #     }
            #     delivery_mode = delivery_modes.get(order['trueDeliveryMode'], "неизвестный тип доставки")
            #
            #     message_text = (
            #         "📦 *ДАННЫЕ ПОСЫЛКИ*\n"
            #         "---\n"
            #         f"🆔 *Номер заказа:* `{order['number']}`\n"
            #         f"📦 *Количество мест:* {order['packagesCount']}\n"
            #         f"📅 *Создан:* {order['creationTimestamp'][:10]}\n"
            #         f"⚖️ *Вес:* {order['weight']} кг\n"
            #         f"🚛 *Тип доставки:* {delivery_mode}\n\n"
            #
            #         "👤 *ОТПРАВИТЕЛЬ*\n"
            #         "---\n"
            #         f"├─ *Имя:* {sender_initials}\n"
            #         f"└─ 🏙️ *Город:* {sender['address']['city']['name']}\n\n"
            #
            #         "📬 *ПОЛУЧАТЕЛЬ*\n"
            #         "---\n"
            #         f"├─ *Инициалы:* {receiver['initials']}\n"
            #     )
            #
            #     # Проверка на наличие офиса
            #     if 'office' in receiver['address']:
            #         office = receiver['address']['office']
            #         message_text += (
            #             f"├─ 🏢 *Адрес {office['type']}:* {receiver['address']['title']}, {receiver['address']['city']['name']}\n"
            #             f"├─ *Офис:* {office['type']}\n"
            #             f"├─ *Комментарий:* {office['comment']}\n"
            #             f"└─ *Контакты:* {office['phones'][0]['number']}\n\n"
            #
            #             "📊 *ИСТОРИЯ ДОСТАВКИ*\n"
            #             "---\n"
            #         )
            #
            #         for status in response['result']['statuses']:
            #             city_info = f" {status['currentCity']['name']}" if 'currentCity' in status else ''
            #             message_text += f"├─ 🔄 *{status['name']}*{city_info}  {status['timestamp'][:10]}\n"
            #
            #         message_text += "\n"
            #         # Добавление графика работы
            #         message_text += "📅 *ГРАФИК РАБОТЫ ПВЗ*\n"
            #         message_text += "---\n"
            #         for schedule in office['schedule']:
            #             days = f"{schedule['startDay'][:3]} - {schedule['endDay'][:3]}" if schedule['startDay'] != \
            #                                                                                schedule['endDay'] else \
            #             schedule['startDay'][:3]
            #             working_hours = f"{schedule['startTime'][:5]} - {schedule['endTime'][:5]}"
            #             message_text += f"├─ • *{days}:* {working_hours}\n"
            #
            #     # Проверка на необходимость отображения информации о складе
            #     if order['trueDeliveryMode'] not in ["1", "3"]:  # Если не двер-дверь и не склад-дверь
            #         if 'warehouse' in response['result']:
            #             warehouse = response['result']['warehouse']
            #             planned_end_date = warehouse.get('acceptance', {}).get('plannedEndDate', 'недоступно')
            #
            #             # Проверка наличия данных о хранении
            #             if 'storage' in warehouse and 'days' in warehouse['storage']:
            #                 storage_days = f"{warehouse['storage']['days']} дней"
            #             else:
            #                 storage_days = 'недоступно'
            #
            #             message_text += (
            #                 "\n🏭 *ИНФОРМАЦИЯ О СКЛАДЕ*\n"
            #                 "---\n"
            #                 f"├─ 📆 *Планируемая дата выдачи:* {planned_end_date}\n"
            #                 f"└─ 🗄️ *Срок хранения:* {storage_days}\n"
            #             )
            #     else:
            #         message_text += ""


                def inline_keyboard():
                    keyboard = types.InlineKeyboardMarkup()
                    button = types.InlineKeyboardButton(text="Отследить посылку", callback_data='otsl')
                    keyboard.add(button)
                    return keyboard

                await message.answer(message_text,
                                    reply_markup=inline_keyboard(),
    parse_mode='Markdown')

            else:
                await message.answer("Не удалось найти данные о посылке. Попробуйте снова.")
        except Exception as e:
            await message.answer("Произошла ошибка при обработке. Попробуйте еще раз.")
            print(f"Ошибка: {e}")  # Для отладки



@dp.message_handler(lambda message: message.text == '🗑️ Удалить аккаунт')
async def process_zamena(message: types.Message):
    print("Обработчик команды del вызван.")
    user = await check_user(message.from_user.id)
    if user:
        cursor.execute("DELETE FROM users WHERE id=?", (user[0],))
        conn.commit()
        await message.answer("Ваши данные удалены из базы данных. Пожалуйста, введите ваш логин.")
        await Form.login.set()
    else:
        await message.answer("Вы не зарегистрированы. Пожалуйста, введите ваш логин для регистрации.")
        await Form.login.set()


@dp.message_handler(state=Form.password)
async def process_password(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    login = user_data['login']
    password = message.text
    print(login, password)
    import requests
    import time

    def get_new_token(account, secure_password):
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
        if response.status_code == 200:
            token_info = response.json()
            print(token_info)
            return token_info
        else:
            print('Ошибка авторизации:', response.json())
            return 'Ошибка авторизации'


    tok = get_new_token(login, password)

    if tok == "Ошибка авторизации":
        await message.answer(f"Авторизация не удалась проверьте правильность введелнных данных!")
        await state.finish()
    else:
        cursor.execute("INSERT INTO users (user_id, username, password) VALUES (?, ?, ?)",
                       (message.from_user.id, login, password))
        conn.commit()

        await message.answer(f"Вы успешно зарегистрированы!")
        await state.finish()

@dp.message_handler(lambda message: message.text == '/faq')
async def process_zamena(message: types.Message):
    from aiogram.types import InputMediaVideo
    # Путь к видео в вашем проекте
    video_path = os.path.join(os.getcwd(), 'video.mp4')  # Замените на имя вашего видеофайла

    # Отправка одного видео и текста
    with open(video_path, 'rb') as video:
        media = InputMediaVideo(media=video, caption="Видео: Для получения логина и пароля вам необходимо выполнить действия, которые показаны в видео.")
        await message.answer_media_group([media])  # Пакетная отправка не требуется, просто используем send_video



# Define states for human operator chat
class HumanChatStates(StatesGroup):
    WAITING_FOR_OPERATOR = State()
    CHATTING_WITH_OPERATOR = State()


# List to store user IDs waiting for an operator
users_waiting_for_operator = []

# Dictionary to store active chats between users and operators
active_chats = {}

users_waiting_for_operator = []
operator_chat_id = 1252672778  # ID чата оператора

@dp.message_handler(Command("human_chat"))
async def request_human_chat(message: types.Message):
    user_id_to_check = message.from_user.id  # Используем user_id отправителя сообщения

    if check_user_id_exists(user_id_to_check):
        user_id = message.from_user.id
        user_name = message.from_user.full_name
        if user_id in users_waiting_for_operator:
            await message.answer(f"{user_name}, вы уже в очереди к человеку-оператору. Пожалуйста, подождите.")
        else:
            users_waiting_for_operator.append(user_id)
            await message.answer(
                f"{user_name}, вас добавили в очередь на оператора-человека. Пожалуйста, подождите. Оператор свяжется с вами напрямую.")
            await notify_operator(user_id, user_name)
    else:
        print(f'Данные для user_id {user_id_to_check} не найдены. ❌')
        await message.answer(f"Данный функционал доступен только договорным клиентам компании СДЭК. Чтобы воспользоваться данным функционалом вам необходимо войти в личный кабинет или заключить договор с группой компании СДЭК. Вы не зарегистрированы. Данные для user_id {user_id_to_check} не найдены. ❌")



async def notify_operator(user_id, user_name):
    keyboard = InlineKeyboardMarkup().add(
        InlineKeyboardButton("Начать чат", url=f"tg://user?id={user_id}")
    )
    try:
        await bot.send_message(
            operator_chat_id,
            f"Пользователь {user_name} (ID: {user_id}) ждет человеческой помощи. Нажмите кнопку ниже, чтобы начать чат напрямую.",
            reply_markup=keyboard
        )
    except Exception as e:
        logging.error(f"Не удалось уведомить оператора: {e}")

@dp.message_handler(Command("end_chat"))
async def end_wait(message: types.Message):
    user_id = message.from_user.id
    if user_id in users_waiting_for_operator:
        users_waiting_for_operator.remove(user_id)
        await message.answer("Вы были удалены из очереди ожидания оператора.")
    else:
        await message.answer("Вы не находитесь в очереди ожидания оператора.")

# Функция для оператора, чтобы отметить, что чат завершен
@dp.message_handler(Command("mark_completed"))
async def mark_chat_completed(message: types.Message):
    if message.from_user.id == operator_chat_id:
        # Предполагается, что оператор указывает ID пользователя после команды
        try:
            user_id = int(message.get_args())
            if user_id in users_waiting_for_operator:
                users_waiting_for_operator.remove(user_id)
                await message.answer(f"Чат с пользователем (ID: {user_id}) отмечен как завершенный.")
            else:
                await message.answer("Указанный пользователь не находится в очереди ожидания.")
        except ValueError:
            await message.answer("Пожалуйста, укажите корректный ID пользователя после команды.")
    else:
        await message.answer("Эта команда доступна только для операторов.")



# # Обработчик команды /dan_zakaz
# @dp.message_handler(commands=['dan_zakaz'])
# async def cmd_dan_zakaz(message: types.Message):
#     # Получаем user_id из сообщения
#     user_id_to_check = message.from_user.id  # Используем user_id отправителя сообщения
#
#     if check_user_id_exists(user_id_to_check):
#         await message.reply(
#             "Введите данные через запятую в формате: вес в кг (5), ФИО (Иванов Иван Иванович), комментарий (ввод коментария без запятых), номер телефона (7XXXXXXXXXX), город (Москва), улица (улица космическая 75)")
#         await Form.address.set()
#     else:
#         print(f'Данные для user_id {user_id_to_check} не найдены. ❌')
#         await message.answer(f"Данный функционал доступен только договорным клиентам компании СДЭК. Чтобы воспользоваться данным функционалом вам необходимо войти в личный кабинет или заключить договор с группой компании СДЭК. Вы не зарегистрированы. Данные для user_id {user_id_to_check} не найдены. ❌")
# Создаем инлайн-клавиатуру с кнопкой отмены
def get_cancel_inline_markup():
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("❌ Отменить ввод", callback_data="cancel_input"))
    return markup


# Обработчик команды /dan_zakaz
@dp.message_handler(commands=['dan_zakaz'])
async def cmd_dan_zakaz(message: types.Message):
    user_id_to_check = message.from_user.id

    if check_user_id_exists(user_id_to_check):
        await message.reply(
            "Введите данные через запятую в формате:\n"
            "вес в кг (5), ФИО (Иванов Иван Иванович), комментарий (ввод коментария без запятых), "
            "номер телефона (7XXXXXXXXXX), город (Москва), улица (улица космическая 75)\n\n"
            "Для отмены нажмите кнопку ниже:",
            reply_markup=get_cancel_inline_markup()
        )
        await Form.address.set()
    else:
        print(f'Данные для user_id {user_id_to_check} не найдены. ❌')
        await message.answer(
            "Данный функционал доступен только договорным клиентам компании СДЭК.\n"
            "Чтобы воспользоваться данным функционалом вам необходимо:\n"
            "1. Войти в личный кабинет\n"
            "2. Заключить договор с группой компании СДЭК\n\n"
            f"Вы не зарегистрированы. Данные для user_id {user_id_to_check} не найдены. ❌"
        )


# Обработчик отмены ввода (инлайн-кнопка)
@dp.callback_query_handler(lambda c: c.data == "cancel_input", state='*')
async def cancel_input(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    current_state = await state.get_state()
    if current_state is None:
        return

    await state.finish()
    await bot.send_message(
        callback_query.from_user.id,
        "Ввод отменен. Вы можете начать заново с помощью команды /dan_zakaz"
    )

@dp.message_handler(state=Form.address)
async def process_address(message: types.Message, state: FSMContext):
    await state.update_data(address=message.text)
    # Извлечение данных из сообщения
    user_id = message.from_user.id
    data = message.text.split(',')  # Используем запятую для разделения

    # Проверяем, достаточно ли данных
    if len(data) < 6:
        await message.reply("Некорректный ввод! Убедитесь, что ввели все данные в правильном формате.")
        return

    weight = data[0].strip()+"000" # Убираем пробелы
    name = data[1].strip()  # Фамилия Имя
    comment = data[2].strip()
    phone_number = data[3].strip()
    city = data[4].strip()
    # Объединяем все оставшиеся слова в адрес
    address = data[5].strip()  # Все слова после города

    # Запись данных в таблицу user_zakaz
    cursor.execute('''INSERT INTO user_zakaz (user_id, weight, name, comment, phone_number, city, address) 
                          VALUES (?, ?, ?, ?, ?, ?, ?)''',
                   (user_id, weight, name, comment, phone_number, city, address))
    conn.commit()

    await message.reply("Ваш заказ успешно создан! 🎉")
    # Завершение состояний
    await state.finish()

# Создаем кнопку для отмены
cancel_button = InlineKeyboardButton("❌ Отменить ввод", callback_data='cancel')
cancel_keyboard = InlineKeyboardMarkup().add(cancel_button)

# Обработчик для отмены ввода
@dp.callback_query_handler(lambda c: c.data == 'cancel', state='*')
async def cancel_input(callback_query: types.CallbackQuery, state: FSMContext):
    await state.finish()  # Завершаем состояние
    await callback_query.message.edit_text("✅ Ввод отменен. Вы можете начать заново.", reply_markup=None) # Отправляем сообщение
    await callback_query.answer() # Убираем "часики"

# def get_date_keyboard():
#     keyboard = InlineKeyboardMarkup(row_width=1)
#     today = datetime.now()
#     for i in range(1, 6):  # Next 5 days
#         date = today + timedelta(days=i)
#         date_str = date.strftime("%Y-%m-%d")
#         keyboard.add(InlineKeyboardButton(date_str, callback_data=f"date_{date_str}"))
#     return keyboard
#
#
# def get_time_keyboard():
#     keyboard = InlineKeyboardMarkup(row_width=1)
#     for hour in range(10, 14):  # From 10 to 13
#         time_str = f"{hour:02d}:00"
#         keyboard.add(InlineKeyboardButton(time_str, callback_data=f"time_{time_str}"))
#     return keyboard
#
#
# @dp.message_handler(commands=['zabor_konsalid'])
# async def zabor_konsalid(message: types.Message):
#     user_id_to_check = message.from_user.id
#     if check_user_id_exists(user_id_to_check):
#         await message.answer("Выберите дату:", reply_markup=get_date_keyboard())
#         await Form.date.set()
#     else:
#         await message.answer(f"Данный функционал доступен только договорным клиентам компании СДЭК. Чтобы воспользоваться данным функционалом вам необходимо войти в личный кабинет или заключить договор с группой компании СДЭК. Вы не зарегистрированы. Данные для user_id {user_id_to_check} не найдены. ❌")
#
#
# @dp.callback_query_handler(lambda c: c.data.startswith('date_'), state=Form.date)
# async def process_date(callback_query: types.CallbackQuery, state: FSMContext):
#     await bot.answer_callback_query(callback_query.id)
#     selected_date = callback_query.data.split('_')[1]
#     await state.update_data(date=selected_date)
#     await bot.send_message(callback_query.from_user.id, "Выберите время начала:", reply_markup=get_time_keyboard())
#     await Form.time.set()
#
#
# @dp.callback_query_handler(lambda c: c.data.startswith('time_'), state=Form.time)
# async def process_time(callback_query: types.CallbackQuery, state: FSMContext):
#     await bot.answer_callback_query(callback_query.id)
#     selected_time = callback_query.data.split('_')[1]
#     data = await state.get_data()
#     selected_date = data['date']
#
#     # Assume the duration is 5 hours
#     start_time = datetime.strptime(selected_time, "%H:%M")
#     end_time = (start_time + timedelta(hours=5)).strftime("%H:%M")
#
#     full_data = f"{selected_date} {selected_time} {end_time}"
#     await state.update_data(konsalid=full_data)
#     print("------")
#     await bot.send_message(
#         callback_query.from_user.id,
#         f"Вы выбрали следующие данные: {full_data}. Ожидайте, идет обработка данных"
#     )
#     print("------")
#     # Process the data
#     user_id = callback_query.from_user.id
#     cursor.execute("""
#         SELECT weight, name, comment, phone_number, city, address
#         FROM user_zakaz
#         WHERE user_id = ?
#         ORDER BY created_at DESC
#         LIMIT 1
#     """, (user_id,))
#     user_data = cursor.fetchone()
#     print("------")
#     if user_data:
#         from dublikat_zayavki import create_call_request_kurier_konsol
#         weight, name, comment, phone_number, city, address = user_data
#         konsol = create_call_request_kurier_konsol(weight, name, comment, phone_number, city, address, selected_date,
#                                                    selected_time, end_time, user_id)
#         await bot.send_message(callback_query.from_user.id, konsol)
#     else:
#         await bot.send_message(callback_query.from_user.id, f"Пользователь с ID {user_id} не найден в базе данных. Заполните форму /dan_zakaz и вернитесь в это меню")
#
#     await state.finish()
def get_date_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=2)
    today = datetime.now()
    for i in range(1, 6):  # Next 5 days
        date = today + timedelta(days=i)
        date_str = date.strftime("%Y-%m-%d")
        keyboard.add(InlineKeyboardButton(date_str, callback_data=f"date_{date_str}"))
    # Добавляем кнопку отмены
    keyboard.add(InlineKeyboardButton("❌ Отменить ввод", callback_data="cancel_input"))
    return keyboard


def get_time_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=2)
    for hour in range(10, 14):  # From 10 to 13
        time_str = f"{hour:02d}:00"
        keyboard.add(InlineKeyboardButton(time_str, callback_data=f"time_{time_str}"))
    # Добавляем кнопку отмены
    keyboard.add(InlineKeyboardButton("❌ Отменить ввод", callback_data="cancel_input"))
    return keyboard


# Обработчик отмены ввода
@dp.callback_query_handler(lambda c: c.data == "cancel_input", state='*')
async def cancel_input(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    await state.finish()
    await bot.send_message(
        callback_query.from_user.id,
        "❌ Ввод отменен. Для начала нового ввода используйте команду /zabor_konsalid"
    )


@dp.message_handler(commands=['zabor_konsalid'])
async def zabor_konsalid(message: types.Message):
    user_id_to_check = message.from_user.id
    if check_user_id_exists(user_id_to_check):
        await message.answer(
            "Выберите дату:",
            reply_markup=get_date_keyboard()
        )
        await Form.date.set()
    else:
        await message.answer(
            "Данный функционал доступен только договорным клиентам компании СДЭК. "
            "Чтобы воспользоваться данным функционалом вам необходимо войти в личный кабинет "
            "или заключить договор с группой компании СДЭК.\n\n"
            f"Вы не зарегистрированы. Данные для user_id {user_id_to_check} не найдены. ❌"
        )


@dp.callback_query_handler(lambda c: c.data.startswith('date_'), state=Form.date)
async def process_date(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    selected_date = callback_query.data.split('_')[1]
    await state.update_data(date=selected_date)
    await bot.send_message(
        callback_query.from_user.id,
        "Выберите время начала:",
        reply_markup=get_time_keyboard()
    )
    await Form.time.set()


@dp.callback_query_handler(lambda c: c.data.startswith('time_'), state=Form.time)
async def process_time(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    selected_time = callback_query.data.split('_')[1]
    data = await state.get_data()
    selected_date = data['date']

    # Assume the duration is 5 hours
    start_time = datetime.strptime(selected_time, "%H:%M")
    end_time = (start_time + timedelta(hours=3)).strftime("%H:%M")

    full_data = f"{selected_date} {selected_time} {end_time}"
    await state.update_data(konsalid=full_data)

    await bot.send_message(
        callback_query.from_user.id,
        f"Вы выбрали следующие данные: {full_data}. Ожидайте, идет обработка данных"
    )

    # Process the data
    user_id = callback_query.from_user.id
    cursor.execute("""
        SELECT weight, name, comment, phone_number, city, address 
        FROM user_zakaz 
        WHERE user_id = ? 
        ORDER BY created_at DESC 
        LIMIT 1
    """, (user_id,))
    user_data = cursor.fetchone()

    if user_data:
        from dublikat_zayavki import create_call_request_kurier_konsol
        weight, name, comment, phone_number, city, address = user_data
        konsol = create_call_request_kurier_konsol(
            weight, name, comment, phone_number,
            city, address, selected_date,
            selected_time, end_time, user_id
        )
        await bot.send_message(callback_query.from_user.id, konsol)
    else:
        await bot.send_message(
            callback_query.from_user.id,
            f"Пользователь с ID {user_id} не найден в базе данных. "
            "Заполните форму /dan_zakaz и вернитесь в это меню"
        )

    await state.finish()


@dp.message_handler(lambda message: message.text == '/nomer')
async def handle_enter_waybill(message: types.Message, state: FSMContext):
    user_id_to_check = message.from_user.id

    if check_user_id_exists(user_id_to_check):
        print(f'Данные для user_id {user_id_to_check} найдены! ✅')
        # Создаем кнопку отмены
        cancel_button = InlineKeyboardButton("Отмена", callback_data="cancel_order")
        keyboard = InlineKeyboardMarkup().add(cancel_button)


        await message.answer("Пожалуйста, введите номер заказа (накладной):", reply_markup=keyboard)
        await Form.order_number.set()
    else:
        print(f'Данные для user_id {user_id_to_check} не найдены. ❌')
        await message.answer(f"Данный функционал доступен только договорным клиентам компании СДЭК. Чтобы воспользоваться данным функционалом вам необходимо войти в личный кабинет или заключить договор с группой компании СДЭК. Вы не зарегистрированы. Данные для user_id {user_id_to_check} не найдены. ❌")


@dp.callback_query_handler(lambda c: c.data == 'cancel_order', state=Form.order_number)
async def cancel_order_number(callback_query: types.CallbackQuery, state: FSMContext):
    await state.finish()  # Завершаем текущее состояние
    await callback_query.answer()  # Убираем уведомление о нажатии
    await bot.send_message(callback_query.from_user.id, "Ввод отменен. Если нужно, вы можете начать снова.", reply_markup=types.ReplyKeyboardRemove())


@dp.message_handler(lambda message: message.text == '/im')
async def handle_enter_webshop_order(message: types.Message, state: FSMContext):
    user_id_to_check = message.from_user.id

    if check_user_id_exists(user_id_to_check):
        print(f'Данные для user_id {user_id_to_check} найдены! ✅')


        # Создаем инлайн кнопку отмены
        cancel_button = InlineKeyboardButton("Отмена", callback_data="cancel_order_im")
        keyboard = InlineKeyboardMarkup().add(cancel_button)

        await message.answer("Пожалуйста, введите номер заказа:", reply_markup=keyboard)
        await Form.order_number2.set()
    else:
        print(f'Данные для user_id {user_id_to_check} не найдены. ❌')
        await message.answer(f"Данный функционал доступен только договорным клиентам компании СДЭК. Чтобы воспользоваться данным функционалом вам необходимо войти в личный кабинет или заключить договор с группой компании СДЭК. Вы не зарегистрированы. Данные для user_id {user_id_to_check} не найдены. ❌")


@dp.callback_query_handler(lambda c: c.data == 'cancel_order_im', state=Form.order_number2)
async def cancel_order_webshop(callback_query: types.CallbackQuery, state: FSMContext):
    await state.finish()  # Завершаем текущее состояние
    await callback_query.answer()  # Убираем уведомление о нажатии
    await bot.send_message(callback_query.from_user.id, "Ввод отменен. Если нужно, вы можете начать снова.",
                           reply_markup=types.ReplyKeyboardRemove())

@dp.callback_query_handler(lambda c: c.data == 'list_offices')
async def handle_list_offices(message: types.Message, state: FSMContext):
    user_id_to_check = message.from_user.id  # Используем user_id отправителя сообщения
    if check_user_id_exists(user_id_to_check):
        print(f'Данные для user_id {user_id_to_check} найдены! ✅')
        await message.answer("Пожалуйста, введите название города:")
        await Form.order_number3.set()
    else:
        print(f'Данные для user_id {user_id_to_check} не найдены. ❌')
        await message.answer(f"Данный функционал доступен только договорным клиентам компании СДЭК. Чтобы воспользоваться данным функционалом вам необходимо войти в личный кабинет или заключить договор с группой компании СДЭК. Вы не зарегистрированы. Данные для user_id {user_id_to_check} не найдены. ❌")


# Создаем общую кнопку для отмены
cancel_button = InlineKeyboardButton("❌ Отменить ввод", callback_data='cancel_input')
cancel_keyboard = InlineKeyboardMarkup().add(cancel_button)

@dp.callback_query_handler(lambda c: c.data == 'change_fullname')
async def handle_change_fullname(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.send_message(callback_query.from_user.id, "Пожалуйста, введите ФИО:", reply_markup=cancel_keyboard)
    await Form.fio.set()

@dp.callback_query_handler(lambda c: c.data == 'change_phone')
async def handle_change_phone(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.send_message(callback_query.from_user.id, "Пожалуйста, введите номер телефона:", reply_markup=cancel_keyboard)
    await Form.tel.set()

@dp.callback_query_handler(lambda c: c.data == 'address')
async def handle_address(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.send_message(callback_query.from_user.id, "Введите желаемый адрес доставки. Обращаем ваше внимание что адрес доставки должен находиться в пределах конечного населенного пункта (города) доставки посылки. В  формате (Москва, улица Космонавтов 1):", reply_markup=cancel_keyboard)
    await Form.adr.set()

@dp.callback_query_handler(lambda c: c.data == 'change_city')
async def handle_change_city(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.send_message(callback_query.from_user.id, "Пожалуйста, введите город. Пример (Москва):", reply_markup=cancel_keyboard)
    await Form.cit.set()



@dp.callback_query_handler(lambda c: c.data == 'change_pickup_point', state='*')
async def handle_change_pickup_point(callback_query: types.CallbackQuery, state: FSMContext):
    # Достаем order_info из базы данных (как это делаете в других местах)
    connection = sqlite3.connect('users.db') #Создаем коннект
    cursor = connection.cursor() #Создаем курсор
    cursor.execute("SELECT order_info FROM new_orders WHERE user_id = ? ORDER BY id DESC LIMIT 1", (callback_query.from_user.id,)) #Делаем запрос в БД
    order_info = cursor.fetchone() #Получаем данные
    connection.close() #Закрываем соединение

    if order_info:
        order_info_str = order_info[0]
        try:
            order_info_dict = ast.literal_eval(order_info_str)
            uuid = order_info_dict['entity']['uuid']
            await state.update_data(uuid=uuid) #Сохраняем uuid в state
        except (ValueError, SyntaxError, KeyError) as e:
            await bot.send_message(callback_query.from_user.id, f"Ошибка при обработке данных заказа: {e}")
            await state.finish()
            return
        await bot.send_message(callback_query.from_user.id, "Пожалуйста, введите город в формате (Москва, улица Космонавтов 1):", reply_markup=cancel_keyboard)
        await Form.waiting_for_city.set()
    else:
        await bot.send_message(callback_query.from_user.id, "Информация о заказе не найдена.")
        await state.finish()



async def api_address(address):
    #  Replace with your actual Dadata token and secret
    token = "28f0c46ebf7a04748add3fc4f2990d2b2b979d44"  # Replace with your Dadata token
    secret = "576db248eb70b56c0f1649f1242cddeecabc9d92"

    #  Replace with your actual Dadata token and secret
    from dadata import Dadata  # Import here to avoid global scope issues if dadata is not always needed

    dadata = Dadata(token, secret)
    try:
        result = dadata.clean("address", address)
        return json.dumps(result, ensure_ascii=False, indent=2), result
    except Exception as e:
        print(f"Ошибка при стандартизации адреса '{address}': {e}")
        return None, None


@dp.message_handler(content_types=types.ContentType.TEXT, state=Form.waiting_for_city)
async def gdp_city(message: types.Message, state: FSMContext):
    """Handles the city input for GDP, using Dadata to standardize the address and offering confirmation buttons."""
    print(f"gdp_city called with state: {await state.get_state()}")
    address = message.text

    # Анимированный индикатор загрузки
    loading_symbols = ["\u25D0", "\u25D1", "\u25D2", "\u25D3"]
    loading_message = await bot.send_message(
        message.chat.id,
        "Идет стандартизация адреса...",
    )

    try:
        # Запускаем задачу для анимации индикатора
        async def animate_loading():
            index = 0
            while True:
                await asyncio.sleep(0.5)  # Меняем символ каждые 0.5 секунды
                index = (index + 1) % len(loading_symbols)
                new_text = "⏳ Идет стандартизация адреса..." + loading_symbols[index]
                try:
                    await bot.edit_message_text(
                        chat_id=message.chat.id,
                        message_id=loading_message.message_id,
                        text=new_text,
                    )
                except Exception as e:
                    logger.warning(f"Не удалось обновить сообщение: {e}")

        animation_task = asyncio.create_task(animate_loading())

        # Call Dadata API to standardize address
        api_response, api_result = await api_address(address)  # Use await here
        animation_task.cancel()

        try:
            await bot.delete_message(chat_id=message.chat.id, message_id=loading_message.message_id)
        except Exception as e:
            logger.warning(f"Не удалось удалить сообщение: {e}")

        if api_response:

            # Extract relevant information from the api_result
            city = api_result.get("settlement") or api_result.get("city") or api_result.get("region") or ""
            if api_result.get("settlement"):
                city_type = api_result.get("settlement_type_full") or "населенный пункт"
                city = f"{city}"
            elif api_result.get("city"):
                city_type = api_result.get("city_type_full") or "город"
                city = f"{city}"
            elif api_result.get("region"):
                city_type = api_result.get("region_type_full") or "регион"
                city = f"{api_result.get('region')}"
            street = api_result.get("street")
            house = api_result.get("house")

            formatted_address = f"{city}, ул {street}, д {house}" if house else f"г {city}, ул {street}"



            # Create inline keyboard for confirmation
            keyboard = InlineKeyboardMarkup()
            yes_button = InlineKeyboardButton(text="Да", callback_data="address_yes")
            no_button = InlineKeyboardButton(text="Нет", callback_data="address_no")
            cancel_button = InlineKeyboardButton(text="Отмена", callback_data="address_cancel")  # Add cancel button

            keyboard.add(yes_button, no_button, cancel_button)

            # Send the standardized address with confirmation buttons
            await bot.send_message(
                message.chat.id,
                f"Мы стандартизовали ваш адрес:\n\n{formatted_address}\n\nЭто верный адрес?",
                reply_markup=keyboard,
            )
            print(api_result)
            # Store the standardized address and original address in the state
            await state.update_data(standardized_address=api_result)
            await state.update_data(original_address=address)
            await Form.address_confirmation.set()  # Set state for address confirmation
            print(f"State set to Form.address_confirmation")

        else:
            await bot.send_message(
                message.chat.id, "Не удалось стандартизировать адрес. Пожалуйста, попробуйте еще раз."
            )
            await state.finish()

    except Exception as e:
        try:
            await bot.delete_message(chat_id=message.chat.id, message_id=loading_message.message_id)
        except Exception as e:
            logger.warning(f"Не удалось удалить сообщение: {e}")
        logger.exception("Ошибка при стандартизации адреса через Dadata:")
        await bot.send_message(
            message.chat.id, f"Произошла ошибка при стандартизации адреса: {e}. Пожалуйста, попробуйте еще раз."
        )
        await state.finish()
    print(f"gdp_city finished")


@dp.callback_query_handler(state=Form.address_confirmation)
async def address_confirmation_callback(query: types.CallbackQuery, state: FSMContext):
    """Обрабатывает обратный вызов после того, как пользователь подтвердит или отклонит стандартизированный адрес."""
    if query.data == "address_yes":
        # User confirmed the address
        data = await state.get_data()
        print(data.get("standardized_address"))
        standardized_address = data.get("standardized_address")
        if standardized_address:
            city = standardized_address.get("settlement") or standardized_address.get("city")
            if standardized_address.get("settlement"):
                city_type = standardized_address.get("settlement_type_full") or "населенный пункт"
                city = f"{city}"
            elif standardized_address.get("city"):
                city_type = standardized_address.get("city_type_full") or "город"
                city = f"{city}"
            elif standardized_address.get("region"):
                city_type = standardized_address.get("region_type_full") or "регион"
                city = f"{standardized_address.get('region')}"

            street = standardized_address.get("street") or ""  # get street
            house = standardized_address.get("house") or ""  # get house number
            # Combine street and house number (if available)
            full_street = f"{street} {house}" if street and house else street if street else ""

            print('===================', city, full_street)

            await state.update_data(city=city)
            await state.update_data(street=full_street)

            # Proceed with getting nearest offices
            await query.message.edit_text("Спасибо! Начинаю поиск ближайших ПВЗ...")  # Update the message
            await get_nearest_offices_and_display(query.message, state, city, full_street) # Call function to handle the rest
        else:
            await query.message.edit_text("Произошла ошибка. Стандартизованный адрес не найден.")
            await state.finish()


    elif query.data == "address_no":
        # User rejected the address
        await query.message.edit_text("Пожалуйста, введите адрес еще раз.")
        await Form.waiting_for_city.set()  # Go back to waiting for city input
        print(f"State set back to Form.waiting_for_city")



    elif query.data == "address_cancel":
        # User cancelled the operation
        await query.message.edit_text("Действие отменено.")
        await state.finish() #finish the state

    await query.answer()  # Acknowledge the callback


async def get_nearest_offices_and_display(message: types.Message, state: FSMContext, city: str, street: str):
    """Helper function to get nearest offices and display them."""
    id = message.from_user.id
    # Анимированный индикатор загрузки
    loading_symbols = ["\u25D0", "\u25D1", "\u25D2", "\u25D3"]  # ◰ ◱ ◲ ◳
    loading_message = await bot.send_message(
        message.chat.id,
        "Выполняется поиск ПВЗ. Пожалуйста, подождите. Это может занять от 5 секунд до 1 минуты, в зависимости от количества ПВЗ." + loading_symbols[0],  # Начальный символ
    )

    try:
        # Запускаем задачу для анимации индикатора
        async def animate_loading():
            index = 0
            while True:
                await asyncio.sleep(0.01)  # Меняем символ каждые 0.5 секунды
                index = (index + 1) % len(loading_symbols)
                new_text = "🔎 Ищем ПВЗ... Пожалуйста, подождите. Это может занять от 5 секунд до 1 минуты, в зависимости от количества ПВЗ." + loading_symbols[index]
                try:
                    await bot.edit_message_text(
                        chat_id=message.chat.id,
                        message_id=loading_message.message_id,
                        text=new_text,
                    )
                except Exception as e:
                    logger.warning(f"Не удалось обновить сообщение: {e}") #Логируем ошибку, если не удалось обновить

        animation_task = asyncio.create_task(animate_loading()) #Запускаем анимацию

        # Вызываем функцию для получения ближайших офисов CDEK
        nearest_offices = await get_nearest_gdp_offices(id, city, street)  # await тут
        animation_task.cancel() #Останавливаем анимацию после получения данных

        if nearest_offices:
            #Сохраняем nearest_offices в state
            await state.update_data(nearest_offices=nearest_offices)
            keyboard = types.InlineKeyboardMarkup(row_width=1)

            def extract_street_and_number(address_string):
                parts = address_string.split(',')
                # Проверяем, достаточно ли частей, чтобы улица и номер существовали
                if len(parts) >= 5:
                    # Извлекаем улицу и номер дома (они находятся в 4-м элементе)
                    street_part = parts[4].strip()  # Удаляем лишние пробелы

                    # Теперь разделяем street_part, чтобы отделить улицу от номера дома
                    street_parts = street_part.split(', ')  # Разделяем по запятой и пробелу

                    if len(street_parts) >= 1:
                        street = street_parts[0].strip()
                        number = None

                        # Если есть номер дома
                        if len(street_parts) > 1:
                            number = street_parts[1].strip()  # номер дома
                        elif len(parts) >= 6:
                            number = parts[5].strip()

                        return street, number
                    else:
                        return street_part, None
                else:
                    return None, None  # Или какое-то сообщение об ошибке, если структура адреса неверна


            for office in nearest_offices:
                office_code = office['code']
                print(office['address'][2:-1])
                city_code = office['city_code']
                button_text = f"{office['address']}"
                address = office['address']
                street, number = extract_street_and_number(address)  # Получаем и улицу, и номер дома

                if street and number:
                    button_text = f"{street}, д. {number}"  # Формируем текст для кнопки
                elif street:
                    button_text = street
                else:
                    button_text = "Адрес не найден"
                callback_data = f"gdp_office:{office_code}:{city_code}"
                keyboard.add(types.InlineKeyboardButton(text=button_text , callback_data=callback_data))

            try:
                await bot.delete_message(chat_id=message.chat.id, message_id=loading_message.message_id)
            except Exception as e:
                 logger.warning(f"Не удалось удалить сообщение: {e}")

            await bot.send_message(
                message.chat.id,
                "Выберите ближайшее ПВЗ:",
                reply_markup=keyboard
            )
            await Form.pwz.set()
            print(f"State set to Form.pwz")

        else:
            try:
                await bot.delete_message(chat_id=message.chat.id, message_id=loading_message.message_id)
            except Exception as e:
                 logger.warning(f"Не удалось удалить сообщение: {e}")
            await bot.send_message(message.chat.id, f"Не удалось найти офисы CDEK в городе {city}.")
            await state.finish()

    except Exception as e:
        try:
            await bot.delete_message(chat_id=message.chat.id, message_id=loading_message.message_id)
        except Exception as e:
             logger.warning(f"Не удалось удалить сообщение: {e}")
        logger.exception("Ошибка при получении офисов CDEK:")
        await bot.send_message(message.chat.id, f"Произошла ошибка при получении офисов CDEK: {e}")
        await state.finish()
    print(f"gdp_city finished")


@dp.callback_query_handler(lambda c: c.data.startswith('gdp_office:'), state=Form.pwz)
async def process_entering_pwz(callback_query: types.CallbackQuery, state: FSMContext):
    id = callback_query.from_user.id
    """Обрабатывает выбор ПВЗ и передает данные."""
    print(f"process_entering_pwz called with data: {callback_query.data} and state: {await state.get_state()}")
    try:
        office_data = callback_query.data.split(':')
        office_code = office_data[1]
        city_code = office_data[2]

        data = await state.get_data()
        city = data.get('city')
        street = data.get('street')

        # Получаем UUID из FSM
        uuid = data.get('uuid')  # Достать uuid из state
        if uuid is None:
            await bot.send_message(callback_query.from_user.id,
                                   "UUID не найден в FSM. Пожалуйста, начните заново.")
            await state.finish()
            return

        # Находим выбранный офис в nearest_offices
        nearest_offices = data.get('nearest_offices', [])

        logger.info(f"callback_query.data: {callback_query.data}")
        logger.info(f"office_code из callback_data: {office_code}")
        logger.info(f"city_code из callback_data: {city_code}")
        logger.info(f"nearest_offices из state: {nearest_offices}")

        selected_office = None
        for office in nearest_offices:
            logger.info(f"Сравнение: office['code'] == office_code: {office['code']} == {office_code}, office['city_code'] == city_code: {office['city_code']} == {city_code}")
            if office['code'] == office_code and str(office['city_code']) == city_code: #<----Преобразование в строку
                selected_office = office
                break


        if selected_office:
            # Save the selected office data to the state
            await state.update_data(selected_office=selected_office)

            # Extract address from selected_office
            full_address = selected_office.get('address', 'Адрес не найден')

            print(f"Calling change_delivery_point with uuid: {uuid}, office_code: {office_code}, city_code: {city_code}, street: {street}, city: {city}")  # Лог
            # Вызываем функцию изменения ПВЗ и передаем office_code и city_code
            api_response = await change_delivery_point(id, uuid, office_code, city_code, full_address)  # Вызываем функцию change_delivery_point и сохраняем ответ

            if api_response:  # Если запрос успешен
                #Извлекаем информацию из api_response
                #Пример (замените на реальную структуру ответа API)
                try:
                    new_pvz_code = api_response['entity']['delivery_point']
                    #full_address = api_response['entity']['to_location']['address'] #если адрес есть в ответе
                    #work_time = api_response['entity']['work_time'] #если есть время работы
                except (KeyError, TypeError):
                    new_pvz_code = office_code  #Если не удалось получить из ответа, берем office_code
                    #full_address = "Не удалось получить адрес"
                    #work_time = "Не удалось получить время работы"

                message_text = (
                    "ПВЗ успешно изменен!\n"
                    f"Новый ПВЗ: {new_pvz_code}\n"
                    f"Адрес: {full_address}\n" #  <----  Вот где вы используете адрес
                   # f"Время работы: {work_time}\n"

                )


                await bot.send_message(
                    callback_query.from_user.id,
                    message_text,
                    reply_markup=types.ReplyKeyboardRemove()
                )
                # здесь обрабатываем ответ от сервера с информацией об успешном изменении ПВЗ
            else:  # Если неуспешен
                await bot.send_message(
                    callback_query.from_user.id,
                    "Не удалось изменить ПВЗ. Попробуйте позже.",
                    reply_markup=types.ReplyKeyboardRemove()
                )
        else:
            await bot.send_message(callback_query.from_user.id,
                                   "Выбранный офис не найден. Пожалуйста, попробуйте заново.")
            await state.finish()
            return
        await state.finish()  # Завершаем состояние после выбора ПВЗ
    except Exception as e:  # Ловим ошибку
        print(f"Error in process_entering_pwz: {e}")  # Выводим сообщение об ошибке


import aiohttp
import json
import logging

logger = logging.getLogger(__name__)


async def change_delivery_point(id, uuid: str, delivery_point_code: str, city_code: str, new_address: str = None):
    token = get_token(id) #  Возвращаем await
    print('===========', uuid, delivery_point_code, city_code, new_address, "=================")
    """
    Асинхронно изменяет пункт выдачи заказов (ПВЗ) для существующего заказа,
    используя delivery_point и city_code.

    Args:
        uuid (str): UUID заказа, который нужно изменить.
        delivery_point_code (str): Код нового ПВЗ.
        city_code (str): Код города.

    Returns:
        dict: Ответ от API СДЭК (JSON). None в случае ошибки.
    """
    url = f"https://api.cdek.ru/v2/orders?im_number={uuid}"  # Замените на корректный URL
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }

    # Пример структуры payload (нужно адаптировать под реальный API СДЭК)
    payload = {
        "uuid": uuid,  # Добавляем UUID
        "type": 1, # Предполагаем, что у вас тип заказа 1
        "delivery_point": delivery_point_code, # Код ПВЗ
        "tariff_code": 136,
    }

    logger.debug(f"URL: {url}")
    logger.debug(f"Headers: {headers}")
    logger.debug(f"Payload: {payload}")


    async with (aiohttp.ClientSession() as session):
        try:
            async with session.patch(url, headers=headers, data=json.dumps(payload)) as response:
                response_text = await response.text()
                logger.debug(f"Response status: {response.status}")
                logger.debug(f"Response text: {response_text}")

                if response.status == 202:
                    pvz_response = await response.json()
                    print(pvz_response)
                    # Если указан новый адрес, отправляем второй запрос на изменение адреса
                    if new_address:
                        street = ""
                        house_number = ""
                        import re

                        match = new_address


                        if new_address:
                            street_and_house = new_address
                            print(street_and_house)
                        else:
                            print("Улица и дом не найдены")
                        await asyncio.sleep(3)  # Добавляем задержку в 2 секунды
                        address_payload = {
                            "uuid": uuid,  # Добавляем UUID
                            # "type": 1,  # Предполагаем, что у вас тип заказа 1
                            "to_location": {
                                "address": street_and_house,
                                # "code": city_code  # Обязательно нужно передавать city_code или city
                            },
                        }

                        logger.debug(f"URL (Адрес): {url}")
                        logger.debug(f"Payload (Адрес): {address_payload}")

                        async with session.patch(url, headers=headers,
                                                 data=json.dumps(address_payload)) as address_response:
                            address_response_text = await address_response.text()
                            logger.debug(f"Response status (Адрес): {address_response.status}")
                            logger.debug(f"Response text (Адрес): {address_response_text}")

                            if address_response.status == 202:
                                address_response_json = await address_response.json()
                                print(address_response_json)
                                return address_response_json  # Возвращаем ответ на запрос изменения адреса
                            else:
                                print(f"Ошибка при изменении адреса: {address_response.status}")
                                print(f"Response text (Адрес): {address_response_text}")
                                return None  # Или можно вернуть pvz_response, если изменение ПВЗ было успешным

                    return pvz_response  # Возвращаем ответ на запрос изменения ПВЗ

                else:
                    print(f"Ошибка при изменении ПВЗ: {response.status}")
                    print(f"Response text (ПВЗ): {response_text}")
                    return None
        except aiohttp.ClientError as e:
            print(f"Ошибка клиента aiohttp: {e}")
            return None
        except Exception as e:
            print(f"Произошла непредвиденная ошибка: {e}")
            return None





@dp.callback_query_handler(lambda c: c.data == 'izmenit_za_tovar')
async def handle_izmenit_za_tovar(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.send_message(callback_query.from_user.id, "Пожалуйста, введите через пробел Новая сумма наложенного платежа за товар:", reply_markup=cancel_keyboard)
    await Form.inpzt.set()

@dp.callback_query_handler(lambda c: c.data == 'izmenit_za_dop')
async def handle_izmenit_za_dop(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.send_message(callback_query.from_user.id, "Пожалуйста, введите сумму доп сбора товара (пример 1000):", reply_markup=cancel_keyboard)
    await Form.npdc.set()

@dp.callback_query_handler(lambda c: c.data == 'duplicate_waybill')
async def handle_duplicate_waybill(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.send_message(callback_query.from_user.id, "Пожалуйста, введите номер накладной CDEK:", reply_markup=cancel_keyboard)
    await Form.dubl.set()

@dp.callback_query_handler(lambda c: c.data == 'Заказать курьера')
async def handle_zakazati_kyriera(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.send_message(callback_query.from_user.id, "Пожалуйста, введите номер накладной CDEK, дату, время начала, время окончания и адрес. Например: 10006324754 2024-07-10 10:00 15:00 ул. Ленина, д. 1", reply_markup=cancel_keyboard)
    await Form.kurier.set()

# Обработчик для отмены ввода
@dp.callback_query_handler(lambda c: c.data == 'cancel_input')
async def cancel_input(callback_query: types.CallbackQuery, state: FSMContext):
    await state.finish()  # Завершаем состояние
    await bot.send_message(callback_query.from_user.id, "✅ Ввод отменен. Вы можете начать заново.")



async def process_order_info(message: types.Message, state: FSMContext, info_function, inline_buttons_data):
    order_number = message.text
    current_time = datetime.now()
    user_id = message.from_user.id

    # Проверка, что введенный текст состоит только из цифр
    if not order_number.isdigit():
        await message.answer("Неверный формат номера заказа. Пожалуйста, введите только цифры.")
        await state.finish()
        return  # Завершаем функцию, если формат неверный

    # Check if user has entered data within the last 15 minutes
    cursor.execute("SELECT * FROM new_orders WHERE user_id = ? AND created_at > ?",
                   (user_id, current_time - timedelta(minutes=15)))
    recent_order = cursor.fetchone()

    print(user_id)

    # Use recent order info if available, otherwise fetch new order info
    if recent_order:
        order_info = recent_order[2]
    else:
        order_info = info_function(order_number, user_id)

    if order_info:
        order_info_str = str(order_info)
        cursor.execute("INSERT INTO new_orders (user_id, cdek_number, order_info) VALUES (?, ?, ?)",
                       (message.from_user.id, order_number, order_info_str))
        conn.commit()

        # Создание меню с опциями
        inline_keyboard = InlineKeyboardMarkup(row_width=2)
        for button_text, callback_data in inline_buttons_data:
            inline_keyboard.add(InlineKeyboardButton(button_text, callback_data=callback_data))

        # Проверяем наличие проблем с доставкой и добавляем кнопку, если они есть
        if isinstance(order_info, dict) and order_info.get('entity', {}).get('delivery_problem'):
            inline_keyboard.add(InlineKeyboardButton("Проблемы доставки ⚠️", callback_data="delivery_problems"))

        await message.answer("Вы находитесь в меню по работе в накладной. Выберите действие:",
                             reply_markup=inline_keyboard)
    else:
        await message.answer("Не удалось получить информацию о заказе. Пожалуйста, проверьте номер заказа и попробуйте снова.")

    await state.finish()

@dp.message_handler(state=Form.order_number)
async def process_order_number(message: types.Message, state: FSMContext):
    from info import info
    await process_order_info(message, state, info, [
        ("Отследить посылку 📦", "track_parcel"),
        ("Данные по посылке 📝", "parcel_data"),
        ("Внести изменения в заказ (накладную) 📝", "change_order"),
        ("Удалить заказ 🗑️", "delete_order"),  # Добавлена кнопка "Удалить заказ"
        ("Отменить доставку ❌", "cancel_delivery"),
        ("Изменить дату доставки 📆", "change_delivery_date"),
        ("Редактировать сумму наложенного платежа 💸", "edit_cod_amount"),
    ])




@dp.message_handler(state=Form.order_number2)
async def process_order_number2(message: types.Message, state: FSMContext):
    from info import info2
    print(message)
    await process_order_info(message, state, info2, [
        ("Отследить посылку 📦", "track_parcel"),
        ("Данные по посылке 📝", "parcel_data"),
        ("Внести изменения в заказ (накладную) 📝", "change_order"),
        ("Удалить заказ 🗑️", "delete_order"),  # Добавлена кнопка "Удалить заказ"
        ("Отменить доставку ❌", "cancel_delivery"),
        ("Изменить дату доставки 📆", "change_delivery_date"),
        ("Редактировать сумму наложенного платежа 💸", "edit_cod_amount"),
    ])

# Обработчик callback-запроса для удаления заказа
@dp.callback_query_handler(lambda c: c.data == 'delete_order')
async def delete_order(callback_query: types.CallbackQuery):
    # Создаем inline клавиатуру с кнопками "Да" и "Нет"
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("Да", callback_data="confirm_delete_order"),
        InlineKeyboardButton("Нет", callback_data="cancel_delete_order")
    )
    await callback_query.message.answer("Вы уверены, что хотите удалить этот заказ? ⚠️ Условием возможности удаления заказа является отсутствие движения груза (статус заказа «Создан»).⚠️", reply_markup=keyboard)

# Обработчик подтверждения удаления
@dp.callback_query_handler(lambda c: c.data == 'confirm_delete_order')
async def confirm_delete_order(callback_query: types.CallbackQuery):
    from izmeneniya import delete_order
    id = callback_query.from_user.id
    connection = sqlite3.connect('users.db')
    cursor = connection.cursor()

    cursor.execute('SELECT cdek_number, order_info FROM new_orders WHERE user_id = ? ORDER BY id DESC LIMIT 1',
                   (callback_query.from_user.id,))
    order_data = cursor.fetchone()

    if order_data:
        order_number = order_data[0]
        order_info_str = order_data[1]

        try:
            order_info_dict = ast.literal_eval(order_info_str)
            order_uuid = order_info_dict['entity']['uuid']  # Получаем UUID заказа
            # Вызываем функцию удаления заказа через API СДЭК
            response = delete_order(id, order_uuid)
            if response and response.status_code == 202:  #Успешно удален
                # Удаляем заказ из базы данных, только если удаление через API прошло успешно
                cursor.execute("DELETE FROM new_orders WHERE user_id = ? AND cdek_number = ?",
                               (callback_query.from_user.id, order_number))
                conn.commit()
                await callback_query.message.answer(f"Заказ с номером {order_number} и UUID {order_uuid} был успешно удален.", reply_markup=types.ReplyKeyboardRemove())
            else:
                await callback_query.message.answer(f"Произошла ошибка при удалении заказа через API СДЭК.  Код ответа:{response.status_code}, текст:{response.text}", reply_markup=types.ReplyKeyboardRemove())


        except Exception as e:
            await callback_query.message.answer(f"Произошла ошибка: {e}", reply_markup=types.ReplyKeyboardRemove())
    else:
        await callback_query.message.answer("Информация о заказе не найдена.", reply_markup=types.ReplyKeyboardRemove())

    connection.close()

# Обработчик отмены удаления
@dp.callback_query_handler(lambda c: c.data == 'cancel_delete_order')
async def cancel_delete_order(callback_query: types.CallbackQuery):
    await callback_query.message.answer("Удаление заказа отменено.", reply_markup=types.ReplyKeyboardRemove())







@dp.callback_query_handler(lambda c: c.data == 'delivery_problems')
async def process_delivery_problems(callback_query: types.CallbackQuery, state: FSMContext):
    # Получаем сохраненную информацию о заказе
    async with state.proxy() as data:
        order_info = data.get('order_info')

    if order_info and 'entity' in order_info and 'delivery_problem' in order_info['entity']:
        delivery_problems = order_info['entity']['delivery_problem']
        if delivery_problems:
            problems_text = "\n".join([f"- {problem}" for problem in delivery_problems])
            await callback_query.message.answer(f"Обнаружены следующие проблемы с доставкой:\n{problems_text}")
        else:
            await callback_query.message.answer("В данный момент проблем с доставкой не обнаружено.")
    else:
        await callback_query.message.answer("Не удалось получить информацию о проблемах с доставкой.")

    # Отвечаем на callback, чтобы убрать "часики" на кнопке
    await callback_query.answer()




# dp.callback_query_handler(lambda c: c.data == 'cancel_delivery')
async def otmena_zakaza(callback_query: types.CallbackQuery):
    # Создаем кнопки подтверждения и отмены
    confirmation_keyboard = InlineKeyboardMarkup(row_width=2)
    confirm_button = InlineKeyboardButton("Подтвердить отмену", callback_data="confirm_cancel1")
    cancel_button = InlineKeyboardButton("Отмена", callback_data="decline_cancel1")
    confirmation_keyboard.add(confirm_button, cancel_button)

    # Отправляем сообщение с кнопками
    await callback_query.message.answer("Вы уверены, что хотите отменить заказ? ⚠️Обращаем ваше внимание что не рекомендуется использовать данную функцию для заказов, которые находятся в статусе 'Создан' и не планируются к отгрузке на склады СДЭК. Для отмены заказа в статусе 'Создан' воспользуйтесь функцией 'Удалить заказ'.⚠️", reply_markup=confirmation_keyboard)

    # Завершаем callback_query, чтобы убрать "часики"
    await callback_query.answer()


@dp.callback_query_handler(lambda c: c.data == 'confirm_cancel1')
async def confirm_otmena_zakaza(callback_query: types.CallbackQuery):
    from otmena_zakaz import otmena  # Импорт здесь, чтобы избежать циклического импорта
    id = callback_query.from_user.id
    connection = sqlite3.connect('users.db')
    cursor = connection.cursor()

    try:
        cursor.execute('SELECT order_info FROM new_orders WHERE user_id = ? ORDER BY id DESC LIMIT 1', (callback_query.from_user.id,))
        order_info = cursor.fetchone()

        if order_info:
            order_info_str = order_info[0]
            order_info_dict = ast.literal_eval(order_info_str)

            try:
                uuid = order_info_dict['entity']["statuses"][0]['code']
                if uuid == "CREATED":
                    await callback_query.message.answer(f"Ваш заказ в статусе Создан и пока не может быть отменен")
                else:
                    uuid = order_info_dict['entity']['uuid']
                    otmen = otmena(uuid, id)

                    if 'status' in otmen and otmen['status'] != 202:
                        print(otmen)
                        await callback_query.message.answer(f"Ошибка: {otmen['error']}")
                    else:
                        print(otmen)
                        await callback_query.message.answer(f"Ваш заказ отменен.")
            except KeyError as e:
                await callback_query.message.answer(f"Ошибка: Некорректная структура данных заказа. Отсутствует ключ: {e}")
            except Exception as e:
                await callback_query.message.answer(f"Произошла ошибка при отмене заказа: {e}")

        else:
            await callback_query.message.answer("Информация о заказе не найдена.")

    except Exception as e:
        print(f"Произошла ошибка: {e}")
        await callback_query.message.answer(f"Произошла непредвиденная ошибка: {e}")

    finally:
        connection.close()
        await callback_query.answer()


@dp.callback_query_handler(lambda c: c.data == 'decline_cancel1')
async def decline_otmena_zakaza(callback_query: types.CallbackQuery):
    await callback_query.message.answer("Отмена заказа отменена.")
    await callback_query.answer()  # Убираем "часики"


@dp.message_handler(Text(equals='/sklad_dver'))
async def zaborgruz(message: Message):
    # Получаем user_id из сообщения
    user_id_to_check = message.from_user.id  # Используем user_id отправителя сообщения
    if check_user_id_exists(user_id_to_check):
        print(f'Данные для user_id {user_id_to_check} найдены! ✅')
        keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
        web_app_info = WebAppInfo(url="https://mikforce.github.io/cdek.github.io/")
        keyboard.add(KeyboardButton(text="Открыть веб-приложение", web_app=web_app_info))
        await message.answer("Нажмите кнопку, чтобы открыть веб-приложение.", reply_markup=keyboard)
    else:
        print(f'Данные для user_id {user_id_to_check} не найдены. ❌')
        await message.answer(f"Данный функционал доступен только договорным клиентам компании СДЭК. Чтобы воспользоваться данным функционалом вам необходимо войти в личный кабинет или заключить договор с группой компании СДЭК. Вы не зарегистрированы. Данные для user_id {user_id_to_check} не найдены. ❌")


@dp.callback_query_handler(text='close_web_app')
async def close_web_app(callback_query: types.CallbackQuery):
    await callback_query.answer()
    await callback_query.message.edit_reply_markup(reply_markup=None)
    await callback_query.message.answer("Мини-приложение закрыто.")


logging.basicConfig(level=logging.INFO)
@dp.message_handler(content_types="web_app_data")
async def web_app_data_handler(request: Request):
    logging.info(f"Received data: {request}")
    # Извлекаем "web_app_data" и затем "data"
    web_app_data = request.web_app_data


    # Проверяем, что данные существуют
    if web_app_data and 'data' in web_app_data:
        # Извлекаем строку и распарсиваем ее
        data_str = web_app_data.data
        try:
            data = json.loads(data_str)
        except json.JSONDecodeError:
            data = {}  # Если не удалось распарсить, ставим пустой словарь

        data = json.loads(data_str)
        # Извлекаем только значения из словаря
        values = list(data.values())
        # Преобразуем все значения в строки для единообразия вывода
        values_str = [str(value) for value in values]
        # Соединяем все значения в одну строку, разделяя их запятыми
        output = ", ".join(values_str)
        await request.answer(f"Вы ввели: {output}")

        await request.answer(f"Ожидайте ответа от сервиса")
        # Здесь вы можете добавить функцию process_web_app_data, если она вам нужна
        await process_web_app_data(data_str, request)



async def process_web_app_data(web_app_data, message):
    from zakaz import zakaz1
    # Парсим данные из JSON строки в Python объект
    parsed_data = json.loads(web_app_data)
    print(parsed_data)
    # Извлечение переменных из распарсенных данных
    type_ = parsed_data.get('type_')
    tariff_code = parsed_data.get('tariff_code')
    from_city = parsed_data.get('from_city')
    from_address = parsed_data.get('from_address')
    to_city = parsed_data.get('to_city')
    to_address = parsed_data.get('to_address')
    recipient_name = parsed_data.get('recipient_name')
    recipient_phone = parsed_data.get('recipient_phone')
    sender_name = parsed_data.get('sender_name')
    sender_company = parsed_data.get('sender_company')
    sender_phone = parsed_data.get('sender_phone')
    package_number = parsed_data.get('package_number')
    package_weight = parsed_data.get('package_weight')
    package_length = parsed_data.get('package_length')
    package_width = parsed_data.get('package_width')
    package_height = parsed_data.get('package_height')
    package_comment = parsed_data.get('package_comment')
    items = parsed_data.get('items', [])

    # Validate and convert the items to the correct format if needed
    item_names = [item['name'] for item in items]
    ware_keys = [item['ware_key'] for item in items]
    costs = [item['cost'] for item in items]
    item_weights = [item['weight'] for item in items]
    amounts = [item['amount'] for item in items]

    print(type_, tariff_code, from_city, from_address, to_city, to_address,
          recipient_name, recipient_phone, sender_name, sender_company,
          sender_phone, package_number, package_weight, package_length,
          package_width, package_height, package_comment, item_names,
          ware_keys, costs, item_weights, amounts)
    zak, uuid = zakaz1(
        type_, tariff_code, from_city, from_address, to_city, to_address,
        recipient_name, recipient_phone, sender_name, sender_company,
        sender_phone, package_number, package_weight, package_length,
        package_width, package_height, package_comment, item_names,
        ware_keys,costs, item_weights,
        amounts
    )

    if zak == "Заказ успешно создан":
        print(zak)
        # Экранируем специальные символы в UUID и форматируем его как код
        escaped_uuid = escape_md(str(uuid))
        copyable_uuid = f'`{escaped_uuid}`'
        # Экранируем точку в сообщении
        escaped_message = escape_md("Заказ успешно создан.")
        # Отправляем сообщение с копируемым UUID
        await message.answer(
            f"Ваш СДЭК номер {copyable_uuid}\\. {escaped_message}\n\n"
            f"Нажмите на номер, чтобы скопировать его\\.",
            parse_mode="MarkdownV2"
        )
    else:
        if 'requests' in uuid:
            first_request = uuid['requests'][0]
            if 'errors' in first_request and first_request['errors']:
                error_message = first_request['errors'][0]['message']
                await message.answer(f"Ошибка: {error_message}", parse_mode=None)
            else:
                await message.answer("Запрос обработан, но ошибок не обнаружено.", parse_mode=None)
        else:
            await message.answer("Не удалось найти информацию об ошибках в ответе.", parse_mode=None)




# Создаем кнопку для отмены
cancel_button = InlineKeyboardButton("❌ Отменить ввод", callback_data='cancel')
cancel_keyboard = InlineKeyboardMarkup().add(cancel_button)

# Обработчик для отмены ввода
@dp.callback_query_handler(lambda c: c.data == 'cancel', state='*')
async def cancel_input(callback_query: types.CallbackQuery, state: FSMContext):
    await state.finish()  # Завершаем состояние
    await callback_query.message.edit_text("✅ Ввод отменен. Вы можете начать заново.", reply_markup=None) # Отправляем сообщение
    await callback_query.answer() # Убираем "часики"



@dp.message_handler(Text(equals='/zaborgruza'))
async def zaborgruz(message: types.Message):
        # Получаем user_id из сообщения
        user_id_to_check = message.from_user.id  # Используем user_id отправителя сообщения
        if check_user_id_exists(user_id_to_check):
            print(f'Данные для user_id {user_id_to_check} найдены! ✅')
            await message.answer(
                "Пожалуйста, введите номер накладной CDEK, дату, время начала, "
                "время окончания и адрес. Через пробел. Пример ввода (10006324754 2024-07-10 10:00 15:00 ул. Ленина, д. 1)",
                reply_markup=cancel_keyboard
            )
            await Form.kurier.set()
        else:
            print(f'Данные для user_id {user_id_to_check} не найдены. ❌')
            await message.answer(f"Данный функционал доступен только договорным клиентам компании СДЭК. Чтобы воспользоваться данным функционалом вам необходимо войти в личный кабинет или заключить договор с группой компании СДЭК. Вы не зарегистрированы. Данные для user_id {user_id_to_check} не найдены. ❌")


@dp.callback_query_handler(Text(equals='cancel'), state=Form.kurier)
async def cancel_input(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.answer()  # Убираем уведомление о нажатии
    await callback_query.message.answer("Ввод отменен. Вы можете начать заново, используя команду /zaborgruza.")
    await state.finish()

@dp.message_handler(state=Form.kurier)
async def process_kurier(message: types.Message, state: FSMContext):
    data = message.text.split()
    # Проверка на количество введенных элементов
    if len(data) < 5:
        await message.answer("Ошибка: Необходимо ввести номер, дату, время начала, время конца и адрес через пробел. Если вы желаете воспользоваться другой функцией нажмите кнопку Отмена")
        return

    nomer = data[0]
    date = data[1]
    time_begin = data[2]
    time_end = data[3]
    address = data[4]
    from dublikat_zayavki import create_call_request_kurier
    # kurier = create_call_request_kurier(nomer, date, time_begin, time_end, address)
    status_code, response_data, state1 = create_call_request_kurier(nomer, date, time_begin, time_end, address)


    if state1 == "SUCCESSFUL":
        await message.answer(f'Запрос на доставку успешно создан!{state1}')
    else:
        await message.answer(
            f'Ошибка при создании запроса на доставку. Код ошибки: {state1}.')
    await state.finish()


@dp.message_handler(state=Form.dubl)
async def process_dubl(message: types.Message, state: FSMContext):
    text = message.text
    from dublikat_zayavki import create_order
    uuid = create_order(text)
    await state.update_data(uuid=uuid)
    await Form.next()
    await message.answer('Введите дату, время начала, время окончания и адрес. Через пробел 2024-07-10 10:00 15:00 ул. Ленина, д. 1', reply_markup=types.ReplyKeyboardRemove())

@dp.message_handler(state=Form.call_request)
async def process_call_request(message: types.Message, state: FSMContext):
    data = message.text.split()
    date = data[0]
    time_begin = data[1]
    time_end = data[2]
    address = data[3]
    uuid = await state.get_data()
    from dublikat_zayavki import create_call_request
    import asyncio
    await asyncio.sleep(360)
    create = create_call_request(1, date, time_begin, time_end, address, uuid['uuid'])
    await message.answer(f'Запрос на доставку успешно создан! {create}')
    await state.finish()





@dp.callback_query_handler(lambda c: c.data == 'go_back_menu')
async def go_back_menu(callback_query: types.CallbackQuery, state: FSMContext):
    await cmd_start1(callback_query.message, state)


# @dp.message_handler(state=Form.npdc)
# async def process_izmenit_za_dop(message: types.Message, state: FSMContext):
#     try:
#         from izmeneniya import nalozh_pay_dop_cbor
#         text = message.text
#         if int(text) >= 0:
#             connection = sqlite3.connect('users.db')
#             cursor = connection.cursor()
#
#             cursor.execute('SELECT order_info FROM new_orders WHERE user_id = ? ORDER BY id DESC LIMIT 1', (message.from_user.id,))
#             order_info = cursor.fetchone()
#             order_info_str = order_info[0]
#
#             order_info_dict = ast.literal_eval(order_info_str)
#             uuid = order_info_dict['entity']['uuid']
#             result = nalozh_pay_dop_cbor(uuid, text)
#             keyboard = InlineKeyboardMarkup()
#             keyboard.add(
#                 InlineKeyboardButton("Назад", callback_data='go_back_menu')
#             )
#             print(result['requests'])
#             await bot.send_message(message.from_user.id, f"Операция выполнена успешно", reply_markup=keyboard)
#             await state.finish()
#         else:
#             await bot.send_message(message.from_user.id, f"Сумма не может быть отрицательной, введите корректное значение")
#
#
#     except Exception as e:
#         keyboard = InlineKeyboardMarkup()
#         keyboard.add(
#             InlineKeyboardButton("Назад", callback_data='go_back_menu')
#         )
#         await bot.send_message(message.from_user.id, f"Произошла ошибка при обработке запроса: {e}",
#                                reply_markup=keyboard)
#         await state.finish()

# Добавляем обработчик для callback_data 'cancel_input'
@dp.callback_query_handler(lambda c: c.data == 'cancel_input_1', state='*')
async def process_cancel_input(callback_query: types.CallbackQuery, state: FSMContext):
    """Обработчик для отмены ввода."""
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, "Ввод отменен.")
    await state.finish()


@dp.message_handler(state=Form.npdc)
async def process_izmenit_za_dop(message: types.Message, state: FSMContext):
    try:
        from izmeneniya import nalozh_pay_dop_cbor  # Под вопросом: лучше импортировать в начале файла

        text = message.text

        # Добавляем кнопку отмены
        keyboard = InlineKeyboardMarkup()
        keyboard.add(
            InlineKeyboardButton("Отмена", callback_data='cancel_input_1')
        )

        try:
            amount = int(text)  # Пытаемся преобразовать текст в число
        except ValueError:
            await bot.send_message(message.from_user.id, "Пожалуйста, введите корректное число.", reply_markup=keyboard)
            return  # Прерываем выполнение обработчика, если ввод некорректен.

        if amount >= 0:
            connection = sqlite3.connect('users.db')
            cursor = connection.cursor()

            cursor.execute('SELECT order_info FROM new_orders WHERE user_id = ? ORDER BY id DESC LIMIT 1', (message.from_user.id,))
            order_info = cursor.fetchone()

            if order_info:  # Проверяем, что order_info не None
                order_info_str = order_info[0]

                order_info_dict = ast.literal_eval(order_info_str)
                uuid = order_info_dict['entity']['uuid']
                result = nalozh_pay_dop_cbor(uuid, text) # Используется text, а не amount
                keyboard = InlineKeyboardMarkup()
                keyboard.add(
                    InlineKeyboardButton("Назад", callback_data='go_back_menu')
                )
                print(result['requests'])
                await bot.send_message(message.from_user.id, f"Операция выполнена успешно", reply_markup=keyboard)
                await state.finish()
            else:
                await bot.send_message(message.from_user.id, "Заказ не найден.", reply_markup=keyboard)
                await state.finish()


        else:
            await bot.send_message(message.from_user.id, f"Сумма не может быть отрицательной, введите корректное значение", reply_markup=keyboard)
    except Exception as e:
        keyboard = InlineKeyboardMarkup()
        keyboard.add(
            InlineKeyboardButton("Назад", callback_data='go_back_menu')
        )
        await bot.send_message(message.from_user.id, f"Произошла ошибка при обработке запроса: {e}",
            reply_markup=keyboard)
        await state.finish()




@dp.message_handler(state=Form.inpzt)
async def process_izmenit_za_tovar(message: types.Message, state: FSMContext):
    try:
        from izmeneniya import nalozh_pay
        text = message.text
        value = text

        connection = sqlite3.connect('users.db')
        cursor = connection.cursor()

        cursor.execute('SELECT order_info FROM new_orders WHERE user_id = ? ORDER BY id DESC LIMIT 1', (message.from_user.id,))
        order_info = cursor.fetchone()
        order_info_str = order_info[0]

        order_info_dict = ast.literal_eval(order_info_str)
        uuid = order_info_dict['entity']['uuid']
        result = nalozh_pay(uuid, value)
        keyboard = InlineKeyboardMarkup()
        keyboard.add(
            InlineKeyboardButton("Назад", callback_data='go_back_menu')
        )
        await bot.send_message(message.from_user.id, f"Операция выполнена успешно.{result}", reply_markup=keyboard)
        await state.finish()
    except Exception as e:
        keyboard = InlineKeyboardMarkup()
        keyboard.add(
            InlineKeyboardButton("Назад", callback_data='go_back_menu')
        )
        await bot.send_message(message.from_user.id, f"Произошла ошибка при обработке запроса: {e}",
                               reply_markup=keyboard)
        await state.finish()

@dp.message_handler(state=Form.order_number3)
async def process_list_offices(message: types.Message, state: FSMContext):
    city = message.text
    from spisok_ofise import city_info
    city_data = city_info(city)
    if city_data:
        response_text = f"Список офисов в городе {city}:\n\n"
        office_info = ""
        for office in city_data:
            office_info += f"🏢 Офис: {office['name']}\n"
            office_info += f"📞 Телефон: {office['phones'][0]['number']}\n"
            office_info += f"🕒 Часы работы: {office['work_time']}\n"
            if 'address_comment' in office:
                office_info += f"📍 Адрес: {office['address_comment']}\n"
            office_info += "--------------------------------------\n"

        if len(response_text + office_info) <= 4096:  # Telegram message character limit
            response_text += office_info
            await message.answer(response_text)
        else:
            from datetime import datetime
            # Create a meaningful filename for the temporary file
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            filename = f"office_info_{city}_{timestamp}.txt"

            # Save detailed information to the temporary file
            with open(filename, 'w', encoding='utf-8') as temp_file:
                temp_file.write(response_text + office_info)

            # Send the temporary file
            with open(filename, 'rb') as document:
                await message.answer_document(document)

            # Remove the temporary file
            os.remove(filename)
            # os.unlink(temp_file.name)

    else:
        await message.answer("К сожалению, информация об офисах в данном городе отсутствует.")
    await state.finish()

async def process_entering_info(message: types.Message, state: FSMContext, info_function):
    await bot.send_message(message.from_user.id, "Идет обработка... ⏳")
    id = message.from_user.id

    entered_text = message.text
    print("=-=-=-=-=-=")
    print(id, entered_text)
    connection = sqlite3.connect('users.db')
    cursor = connection.cursor()

    cursor.execute('SELECT order_info FROM new_orders WHERE user_id = ? ORDER BY id DESC LIMIT 1', (message.from_user.id,))
    order_info = cursor.fetchone()

    if order_info:
        order_info_str = order_info[0]
        try:
            order_info_dict = ast.literal_eval(order_info_str)
            uuid = order_info_dict['entity']['uuid']
            result = info_function(id, uuid, entered_text)

            # Проверка на успешный ответ от API
            if result and 'requests' in result and len(result['requests']) > 0:
                reez = result['requests'][0]['state']
                await bot.send_message(message.from_user.id, f"✅ Статус заказа: {reez}")
            else:
                await bot.send_message(message.from_user.id, "❌ Не удалось получить информацию от API. Попробуйте позже.")

        except (ValueError, SyntaxError) as e:
            print(f"Не удалось оценить order_info_str как словарь: {e}")
            await bot.send_message(message.from_user.id, "🚫 Ошибка обработки информации о заказе. Проверьте данные и попробуйте снова.")
        except Exception as e:
            print(f"Ошибка: {e}")
            await bot.send_message(message.from_user.id, "❌ Произошла ошибка при обращении к API. Попробуйте позже.")

    else:
        print("Для пользователя не найдено order_info")
        await bot.send_message(message.from_user.id, "📭 Не найдено информации о заказе. Пожалуйста, введите корректный номер заказа.")

    connection.close()
    await state.finish()
# SELECT order_info FROM new_orders WHERE user_id = ? ORDER BY id DESC LIMIT 1
@dp.message_handler(state=Form.fio)
async def process_entering_fullname(message: types.Message, state: FSMContext):
    from izmeneniya import fio
    await process_entering_info(message, state, fio)

@dp.message_handler(state=Form.tel)
async def process_entering_tel(message: types.Message, state: FSMContext):
    from izmeneniya import fone
    await process_entering_info(message, state, fone)

@dp.message_handler(state=Form.adr)
async def process_entering_adr(message: types.Message, state: FSMContext):
    from izmeneniya import adres
    print(adres,"++++++++++++++++++++++++++++")
    await process_entering_info(message, state, adres)

@dp.message_handler(state=Form.cit)
async def process_entering_cit(message: types.Message, state: FSMContext):
    print("----------------")
    entered_text = message.text
    id = message.from_user.id
    connection = sqlite3.connect('users.db')
    cursor = connection.cursor()

    cursor.execute('SELECT order_info FROM new_orders WHERE user_id = ? ORDER BY id DESC LIMIT 1', (message.from_user.id,))
    order_info = cursor.fetchone()
    print(order_info)
    if order_info:
        order_info_str = order_info[0]
        print("info")
        try:
            print('try')
            order_info_dict = ast.literal_eval(order_info_str)
            uuid = order_info_dict['entity']['uuid']
            address = order_info_dict['entity']['to_location']['address']
            print(address)
            from izmeneniya import change_city
            city = [entered_text, address]
            print(uuid, city)
            result = change_city(id, uuid, city)
            # Преобразуем JSON в красивый текст
            if result:
                try:
                    result_dict = json.loads(json.dumps(result))  # Преобразуем в словарь
                    formatted_result = format_json_response(result_dict)  # Форматируем
                    await bot.send_message(message.from_user.id, formatted_result, parse_mode=types.ParseMode.MARKDOWN)
                except (TypeError, json.JSONDecodeError) as e:
                    await bot.send_message(message.from_user.id, f"Ошибка при форматировании ответа: {e}\n{result}")
            else:
                await bot.send_message(message.from_user.id, "Не удалось изменить город.")

        except (ValueError, SyntaxError) as e:
            print(f"Failed to evaluate order_info_str as dictionary: {e}")
        else:
            print("No order_info found for the user")

        connection.close()
        await state.finish()

def format_json_response(data: dict) -> str:
    """Форматирует JSON-ответ для красивого отображения в Telegram."""
    output = ""
    if 'entity' in data:
        output += "*Entity:*\n"
        for key, value in data['entity'].items():
            output += f"  *{key}:* `{value}`\n"
    if 'requests' in data:
        output += "\n*Requests:*\n"
        for request in data['requests']:
            output += "  *Request:*\n"
            for key, value in request.items():
                output += f"    *{key}:* `{value}`\n"
            if 'warnings' in request:
                output += "    *Warnings:*\n"
                for warning in request['warnings']:
                    for key, value in warning.items():
                        output += f"      *{key}:* `{value}`\n"
    if 'related_entities' in data:
        output += "\n*Related Entities:*\n"
        output += "  (Информация отсутствует)\n"  # Или обработайте, если есть структура
    return output




@dp.message_handler(commands=['lists'])
async def cmd_lists(message: types.Message):
    inline_keyboard = InlineKeyboardMarkup(row_width=1)
    inline_keyboard.add(
        # InlineKeyboardButton("Списки регионов", callback_data='list_regions'),
        InlineKeyboardButton("Списки офисов", callback_data='list_offices')
        # InlineKeyboardButton("Списки населенных пунктов", callback_data='list_settlements')
    )
    await message.answer("Выберете из списка:", reply_markup=inline_keyboard)

from aiogram import types
import ast
from aiogram import types

@dp.callback_query_handler(lambda c: c.data)
async def process_callback(callback_query: types.CallbackQuery):
    id = callback_query.from_user.id
    # Добавляем константы для кодов статусов, которые нужно исключить
    EXCLUDED_STATUS_CODES = {"CREATED", "ACCEPTED"}
    connection = sqlite3.connect('users.db')
    cursor = connection.cursor()
    # ... (начало process_callback) ...
    print("начало process_callback")
    if callback_query.data == 'track_parcel':
        # Удаляем сообщение с кнопками (можно оставить, если хочешь)
        try:
            await callback_query.message.delete()
        except Exception as e:
            logger.warning(f"User {id}: Не удалось удалить сообщение при track_parcel: {e}")

        import datetime
        import pytz
        # import ast  # Убедись, что ast импортирован
        from collections import defaultdict
        print("запрос в бд")

        # Fetch order info from the database
        cursor.execute("SELECT order_info FROM new_orders WHERE user_id = ? ORDER BY id DESC LIMIT 1",
                       (callback_query.from_user.id,))
        order_info = cursor.fetchone()
        print(order_info)
        if order_info:
            order_info_str = order_info[0]
            logger.debug(
                f"User {id}: Fetched order info for tracking: {order_info_str[:200]}...")  # Логгируем начало строки

            try:
                order_info_dict = ast.literal_eval(
                    order_info_str)  # Безопаснее использовать json.loads, если храните JSON

                # --- Проверка наличия статусов ---
                # Используем .get() для безопасного доступа, по умолчанию пустой список
                statuses = order_info_dict.get('entity', {}).get('statuses', [])
                print(statuses)
                if not statuses:
                    # Если список статусов пуст или отсутствует
                    await bot.answer_callback_query(callback_query.id)
                    await bot.send_message(callback_query.from_user.id,
                                           "Информация о статусах пока отсутствует.")
                    logger.info(
                        f"User {id}: No statuses found for order {order_info_dict.get('entity', {}).get('cdek_number', 'N/A')}")

                else:
                    # --- Проверка, есть ли ТОЛЬКО CREATED/ACCEPTED ---
                    # Получаем коды всех статусов
                    status_codes = {status.get('code') for status in statuses if status.get('code')}  # Множество кодов

                    # Проверяем, что все имеющиеся коды входят в EXCLUDED_STATUS_CODES
                    # ИЛИ, проще, проверяем, что НЕТ кодов, НЕ входящих в EXCLUDED_STATUS_CODES
                    has_only_excluded = all(code in EXCLUDED_STATUS_CODES for code in status_codes)

                    if has_only_excluded:
                        # Если все статусы только CREATED или ACCEPTED
                        await bot.answer_callback_query(callback_query.id)
                        await bot.send_message(callback_query.from_user.id,
                                               "✅ Заказ создан, ожидает отправки.")
                        logger.info(
                            f"User {id}: Order {order_info_dict.get('entity', {}).get('cdek_number', 'N/A')} has only CREATED/ACCEPTED status.")

                    else:
                        # --- Если есть другие статусы, показываем историю ---
                        logger.info(
                            f"User {id}: Displaying tracking history for {order_info_dict.get('entity', {}).get('cdek_number', 'N/A')}")

                        # Фильтруем статусы для показа (убираем CREATED/ACCEPTED)
                        filtered_statuses = [
                            status for status in statuses if status.get('code') not in EXCLUDED_STATUS_CODES
                        ]

                        # Если после фильтрации что-то осталось (на всякий случай)
                        if filtered_statuses:
                            statuses_by_date = defaultdict(list)
                            moscow_tz = pytz.timezone('Europe/Moscow')

                            for status in reversed(filtered_statuses):  # Используем отфильтрованные статусы
                                # --- Твой существующий код парсинга даты и группировки ---
                                date_time_str = status.get('date_time')
                                if not date_time_str: continue  # Пропускаем статус без даты

                                city = status.get('city', 'Неизвестный город')  # Получаем город
                                status_name = status.get('name', 'Неизвестный статус')  # Получаем имя статуса

                                dt_format = None
                                if isinstance(date_time_str, str):
                                    if '+' in date_time_str:  # Проверяем наличие смещения
                                        try:  # Пробуем парсить с часовым поясом
                                            # Убираем ':' в смещении для Python < 3.7, если нужно
                                            if len(date_time_str) > 6 and date_time_str[-3] == ':':
                                                date_time_str = date_time_str[:-3] + date_time_str[-2:]
                                            dt_format = '%Y-%m-%dT%H:%M:%S%z'
                                            utc_time = datetime.datetime.strptime(date_time_str, dt_format)
                                        except ValueError:
                                            # Если не получилось, пробуем без микросекунд
                                            try:
                                                date_time_str_no_ms = date_time_str.split('.')[0] + date_time_str[-6:]
                                                if len(date_time_str_no_ms) > 6 and date_time_str_no_ms[-3] == ':':
                                                    date_time_str_no_ms = date_time_str_no_ms[
                                                                          :-3] + date_time_str_no_ms[-2:]
                                                utc_time = datetime.datetime.strptime(date_time_str_no_ms, dt_format)
                                            except ValueError:
                                                logger.warning(f"Could not parse date with timezone: {date_time_str}")
                                                continue  # Пропускаем этот статус
                                    else:  # Пробуем парсить как UTC (с 'Z' или без)
                                        try:
                                            if date_time_str.endswith('Z'):
                                                dt_format = '%Y-%m-%dT%H:%M:%SZ'
                                                utc_time = datetime.datetime.strptime(date_time_str, dt_format)
                                            else:  # Предполагаем UTC без 'Z' и без смещения
                                                dt_format = '%Y-%m-%dT%H:%M:%S'
                                                utc_time = datetime.datetime.strptime(date_time_str, dt_format)
                                            # Устанавливаем таймзону UTC явно
                                            utc_time = pytz.utc.localize(utc_time)
                                        except ValueError:
                                            logger.warning(f"Could not parse date as UTC: {date_time_str}")
                                            continue  # Пропускаем этот статус

                                else:  # Если формат даты неожиданный
                                    logger.warning(f"Unexpected date format: {date_time_str}")
                                    continue  # Пропускаем

                                # Переводим в московское время
                                moscow_time = utc_time.astimezone(moscow_tz)

                                # Форматируем строку статуса
                                # Используем escape_md для города и названия статуса
                                status_str = f"{moscow_time.strftime('%H:%M:%S')} {escape_md(status_name)} в {escape_md(city)}"

                                # Группируем статусы по дате
                                date_key = moscow_time.strftime('%d.%m.%Y')
                                statuses_by_date[date_key].append(status_str)
                                # --- /Конец твоего кода парсинга даты ---

                            # Формируем итоговый текст сообщения
                            output_lines = []
                            # Сортируем даты для вывода в хронологическом порядке
                            for date_key in sorted(statuses_by_date.keys()):
                                output_lines.append(f"*{date_key}*")  # ДАТА ЖИРНЫМ
                                for status_entry in statuses_by_date[date_key]:
                                    output_lines.append(f"  - {status_entry}")  # Отступ для элементов

                            status_text = "\n".join(output_lines)

                            await bot.answer_callback_query(callback_query.id)
                            # Используем parse_mode=types.ParseMode.MARKDOWN_V2 если используем escape_md
                            await bot.send_message(callback_query.from_user.id, status_text,
                                                    parse_mode="Markdown")
                            #                 await bot.answer_callback_query(callback_query.id)
                            #                 await bot.send_message(callback_query.from_user.id, status_text, parse_mode="Markdown")  # Отправляем сообщение
                            #             else:
                            #                 await bot.send_message(callback_query.from_user.id,
                            #                                        "Информация о статусе отсутствует. Пожалуйста введите номер посылки по своему договору.")
                        else:
                            # Если после фильтрации ничего не осталось (не должно случиться из-за проверки has_only_excluded)
                            await bot.answer_callback_query(callback_query.id)
                            await bot.send_message(callback_query.from_user.id, "Нет данных для отображения истории.")
                            logger.info(
                                f"User {id}: No statuses left after filtering for order {order_info_dict.get('entity', {}).get('cdek_number', 'N/A')}")
    # if callback_query.data == 'track_parcel':
    #     await callback_query.message.delete()
    #     import datetime
    #     import pytz
    #     # import ast
    #     from collections import defaultdict
    #     # Fetch order info from the database
    #     cursor.execute("SELECT order_info FROM new_orders WHERE user_id = ? ORDER BY id DESC LIMIT 1", (callback_query.from_user.id,))
    #     order_info = cursor.fetchone()
    #     if order_info:
    #         order_info_str = order_info[0]
    #         print(f"Debug: Fetched order info: {order_info_str}")  # Debugging line
    #
    #         try:
    #             order_info_dict = ast.literal_eval(order_info_str)  # Safely evaluate the string as a Python dictionary
    #             print(order_info_dict)
    #             if 'entity' in order_info_dict and 'statuses' in order_info_dict['entity']:
    #                 statuses = order_info_dict['entity']['statuses']
    #                 # Фильтруем статусы по коду.
    #                 filtered_statuses = [
    #                     status for status in statuses if status['code'] not in EXCLUDED_STATUS_CODES
    #                 ]
    #
    #                 statuses_by_date = defaultdict(list)
    #                 moscow_tz = pytz.timezone('Europe/Moscow')
    #                 print("---")
    #                 print(filtered_statuses)
    #                 for status in reversed(filtered_statuses):  # Используем отфильтрованные статусы
    #                     date_time_str = status['date_time']
    #                     print("222222222")
    #                     # Проверяем, есть ли смещение часового пояса в строке даты
    #                     if date_time_str.endswith('+0000'):
    #                         date_time_str = date_time_str[:-5]  # Удаляем смещение +0000
    #                         dt_format = '%Y-%m-%dT%H:%M:%S'
    #                         print("%Y-%m-%dT%H:%M:%S")
    #                     else:
    #                         dt_format = '%Y-%m-%dT%H:%M:%SZ'  # Изменено здесь!
    #                         print("%Y-%m-%dT%H:%M:%SZ")
    #
    #                     print("2222222")
    #
    #                     try:
    #                         # Парсим строку даты и времени
    #                         utc_time = datetime.datetime.strptime(date_time_str, dt_format)
    #
    #                         # Присваиваем UTC временную зону (если это необходимо)
    #                         if dt_format == '%Y-%m-%dT%H:%M:%S':
    #                             utc_time = pytz.utc.localize(utc_time)
    #
    #                         # Переводим в московское время
    #                         moscow_time = utc_time.astimezone(moscow_tz)
    #
    #                         # Форматируем строку статуса (только время)
    #                         status_str = f"{moscow_time.strftime('%H:%M:%S')} {status['name']} в {status['city']}"
    #
    #                         # Группируем статусы по дате
    #                         date_key = moscow_time.strftime('%d.%m.%Y')  # <<<=== ИЗМЕНЕН ФОРМАТ КЛЮЧА
    #                         statuses_by_date[date_key].append(status_str)
    #                         print("-------------------")
    #                     except ValueError as e:
    #                         print(f"Ошибка при парсинге даты: {e}")
    #                         await bot.send_message(callback_query.from_user.id,
    #                                                f"Ошибка при обработке даты статуса: {e}.  Обратитесь к администратору.")
    #                         return  # Прекращаем обработку, чтобы не вызвать дальнейшие ошибки
    #
    #                 # Формируем итоговый текст сообщения
    #                 output_lines = []
    #                 for date, status_list in statuses_by_date.items():
    #                     output_lines.append(f"*{date}*") # <<<=== ДАТА ЖИРНЫМ
    #                     for status in status_list:
    #                         output_lines.append(f"  - {status}")  # Добавляем отступ для элементов списка.
    #
    #                 status_text = "\n".join(output_lines)  # Объединяем все строки в один текст
    #
    #                 print(status_text)
    #                 await bot.answer_callback_query(callback_query.id)
    #                 await bot.send_message(callback_query.from_user.id, status_text, parse_mode="Markdown")  # Отправляем сообщение
    #             else:
    #                 await bot.send_message(callback_query.from_user.id,
    #                                        "Информация о статусе отсутствует. Пожалуйста введите номер посылки по своему договору.")
            except (ValueError, SyntaxError) as e:
                await bot.send_message(callback_query.from_user.id,
                                       "Error decoding order information. Please try again later.")
                print(f"Error: {e}")
        else:
            await bot.send_message(callback_query.from_user.id, "No order information found.")


    elif callback_query.data == 'track_parcel2':
        await callback_query.message.delete()
        # Fetch order info from the database
        cursor.execute("SELECT order_info FROM new_orders WHERE user_id = ? ORDER BY id DESC LIMIT 1", (callback_query.from_user.id,))
        order_info = cursor.fetchone()

        if order_info:
            order_info_str = order_info[0]
            print(f"Debug: Fetched order info: {order_info_str}")  # Debugging line

            try:
                order_info_dict = ast.literal_eval(order_info_str)  # Safely evaluate the string as a Python dictionary

                if 'entity' in order_info_dict and 'statuses' in order_info_dict['entity']:
                    statuses = order_info_dict['entity']['statuses']
                    status_text = "\n".join(f"{status['name']} в {status['city']}" for status in statuses)
                    await bot.send_message(callback_query.from_user.id, status_text)
                else:
                    await bot.send_message(callback_query.from_user.id, "No status information available.")
            except (ValueError, SyntaxError) as e:
                await bot.send_message(callback_query.from_user.id, "Error decoding order information. Please try again later.")
                print(f"Error: {e}")
        else:
            await bot.send_message(callback_query.from_user.id, "No order information found.")




    elif callback_query.data == 'parcel_data':
        await callback_query.message.delete()
        import datetime
        import pytz

        def calculate_overdue_days(planned_delivery_date, actual_delivery_date):
            """
            Рассчитывает количество дней просрочки доставки.

            Аргументы:
            planned_delivery_date (str или datetime): Планируемая дата доставки в формате строки ISO 8601 или объект datetime.
            actual_delivery_date (str или datetime): Фактическая дата доставки в формате строки ISO 8601 или объект datetime.

            Возвращает:
            int: Количество дней просрочки (положительное число, если доставка просрочена, 0 или отрицательное, если нет данных или доставка была вовремя).
            None: Если одна из дат не указана.
            """

            print(planned_delivery_date, actual_delivery_date)
            if not planned_delivery_date or not actual_delivery_date:
                return None  # Если нет данных о датах, то и просрочку не посчитать

            try:
                # Преобразование строк в datetime, если необходимо
                if isinstance(planned_delivery_date, str):
                    planned_delivery_date = datetime.datetime.strptime(planned_delivery_date, "%d.%m.%Y")
                if isinstance(actual_delivery_date, str):
                    actual_delivery_date = datetime.datetime.strptime(actual_delivery_date, "%d.%m.%Y")

                # Расчет разницы в днях
                overdue_days = (actual_delivery_date - planned_delivery_date).days

                return overdue_days if overdue_days > 0 else 0  # Возвращаем 0 если нет просрочки или доставка раньше срока

            except ValueError:
                print("Ошибка: Некорректный формат даты.  Убедитесь, что дата в формате ДД.ММ.ГГГГ")
                return None  # Если формат даты некорректный, возвращаем None

        def calculate_delivery_time(sender_city_code, recipient_city_code, weight, length, width, height,
                                    cost, id):  # Add cost
            """
            Функция для расчета срока доставки с использованием API СДЭК (tarifflist).
            """
            url = "https://api.cdek.ru/v2/calculator/tarifflist"
            headers = {
                "Content-Type": "application/json",
                'Authorization': f'Bearer {get_token(id)}'
            }

            # Get current date and time in the format required by the API
            current_time = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%S+0000')

            data = {
                "date": current_time,
                "type": 1,  # Тип заказа (интернет-магазин)
                "currency": 0,  # Валюта
                "lang": "rus",
                "from_location": {
                    "code": sender_city_code,
                },
                "to_location": {
                    "code": recipient_city_code
                },
                "packages": [
                    {
                        "weight": weight,  # Вес в граммах
                        "length": length,  # Длина в см
                        "width": width,  # Ширина в см
                        "height": height,  # Высота в см
                        "cost": cost  # Объявленная стоимость (для страховки)
                    }
                ]
            }

            print("Data being sent to API:", json.dumps(data))
            try:
                response = requests.post(url, headers=headers, data=json.dumps(data))
                response.raise_for_status()
                response_data = response.json()
                print("API Response:", json.dumps(response_data, indent=2))  # Pretty print

                # Extract the tariff codes and delivery periods
                tariff_codes = response_data.get("tariff_codes", [])
                if tariff_codes:
                    # Find the tariff with the same code as the original order
                    matching_tariff = next((t for t in tariff_codes if t['tariff_code'] == tariff_code),
                                           None)  # Find the matching tariff

                    if matching_tariff:
                        delivery_period_min = matching_tariff.get("period_min")
                        delivery_period_max = matching_tariff.get("period_max")
                        if delivery_period_min is not None and delivery_period_max is not None:
                            return f"{delivery_period_min}-{delivery_period_max} дней"
                        else:
                            return "Срок доставки не указан"
                    else:
                        return "Соответствующий тариф не найден"
                else:
                    return "Нет доступных тарифов"

            except requests.exceptions.RequestException as e:
                print(f"Ошибка при запросе к API СДЭК: {e}")
                if response is not None:
                    print(f"Response content: {response.text}")
                return "Ошибка API"
            except json.JSONDecodeError as e:
                print(f"Ошибка при обработке ответа API СДЭК: {e}")
                return "Ошибка формата ответа API"

        def get_delivery_dates(cdek_number, id):
            """
            Функция для получения планируемой и фактической даты доставки и информации о проблемах.
            """
            url = f"https://api.cdek.ru/v2/orders?cdek_number={cdek_number}"
            headers = {
                "Content-Type": "application/json",
                'Authorization': f'Bearer {get_token(id)}'
            }

            planned_delivery_date = "ожидается"
            actual_delivery_date = "ожидается"
            delivery_problem_reason = "Нет проблем"  # Значение по умолчанию

            try:
                response = requests.get(url, headers=headers)
                response.raise_for_status()
                response_data = response.json()
                print("==================================================================")
                print("Tracking API Response:", json.dumps(response_data, indent=2))

                #  Check if there are any errors
                if 'errors' in response_data and response_data['errors']:
                    print(f"Tracking API returned errors: {response_data['errors']}")
                    return planned_delivery_date, actual_delivery_date, delivery_problem_reason

                # Extract data from the 'entity'
                if 'entity' in response_data and response_data['entity']:
                    entity = response_data['entity']

                    # Extract planned delivery date
                    planned_delivery_date_str = entity.get('planned_delivery_date')
                    if planned_delivery_date_str:
                        try:
                            # Попытка преобразования с форматом даты и времени
                            planned_delivery_date = datetime.datetime.strptime(planned_delivery_date_str,
                                                                               "%Y-%m-%dT%H:%M:%S%z").strftime(
                                "%d.%m.%Y")
                        except ValueError:
                            try:
                                # Попытка преобразования только с форматом даты
                                planned_delivery_date = datetime.datetime.strptime(planned_delivery_date_str,
                                                                                   "%Y-%m-%d").strftime("%d.%m.%Y")
                            except ValueError:
                                print("Ошибка: Некорректный формат planned_delivery_date из API")
                                planned_delivery_date = "_ошибка формата_"

                    # Extract actual delivery date from statuses
                    statuses = entity.get('statuses', [])
                    for status in statuses:
                        if status.get('code') == 'DELIVERED':
                            actual_delivery_date_str = status.get('date_time')
                            if actual_delivery_date_str:
                                try:
                                    # Попытка преобразования с форматом даты и времени
                                    actual_delivery_date = datetime.datetime.strptime(actual_delivery_date_str,
                                                                                      "%Y-%m-%dT%H:%M:%S%z").strftime(
                                        "%d.%m.%Y")
                                except ValueError:
                                    try:
                                        # Попытка преобразования только с форматом даты
                                        actual_delivery_date = datetime.datetime.strptime(actual_delivery_date_str,
                                                                                          "%Y-%m-%d").strftime(
                                            "%d.%m.%Y")
                                    except ValueError:
                                        print("Ошибка: Некорректный формат actual_delivery_date из API")
                                        actual_delivery_date = "_ошибка формата_"
                                break  # Exit loop after finding delivered status
                        elif status.get('code') == 'NOT_DELIVERED':
                            # Get the reason for the delivery problem
                            delivery_problem_reason_code = status.get('status_reason_code')
                            if delivery_problem_reason_code:
                                delivery_problem_reason = f"Проблема с доставкой (код: {delivery_problem_reason_code})"
                            else:
                                delivery_problem_reason = "Проблема с доставкой (причина не указана)"

                else:
                    return planned_delivery_date, actual_delivery_date, delivery_problem_reason  # Or a message indicating no entity found

                return planned_delivery_date, actual_delivery_date, delivery_problem_reason

            except requests.exceptions.RequestException as e:
                print(f"Ошибка при запросе к Tracking API: {e}")
                return "_ожидается_", "_ожидается_", "Ошибка API"
            except json.JSONDecodeError as e:
                print(f"Ошибка при обработке ответа Tracking API: {e}")
                return "_ожидается_", "_ожидается_", "Ошибка формата API"

        # Функция для получения названия режима доставки
        def get_delivery_mode_text(delivery_mode):
            if delivery_mode == '1':
                return "Курьер заберет отправление у отправителя"
            elif delivery_mode == '2':
                return "Отправление будет доставлено курьером получателю"
            elif delivery_mode == '3':
                return "Отправление будет сдано в пункт выдачи СДЭК в городе отправителе"
            elif delivery_mode == '4':
                return "Отправление будет забрано получателем из ПВЗ СДЭК"
            elif delivery_mode == '5':
                return "Доставка в постамат"
            else:
                return "Неизвестен"

        # Функция для получения названия тарифа
        def get_tariff_name(tariff_code):
            """
            Возвращает название тарифа по его коду.

            Args:
                tariff_code (int): Код тарифа.

            Returns:
                str: Название тарифа или "Неизвестен", если код не найден.
            """
            tariff_names = {
                1: "Экспресс лайт",
                7: "Международный экспресс документы дверь-дверь",
                8: "Международный экспресс грузы дверь-дверь",
                10: "Экономичный экспресс",
                11: "Экспресс плюс",
                15: "Международный экспресс",
                16: "Импорт",
                17: "Международный экономичный",
                57: "Китайский экспресс",
                62: "СДЭК-Посылка",
                63: "CDEK Express",
                136: "Посылка склад-склад",
                137: "Посылка склад-дверь",
                138: "Посылка дверь-склад",
                139: "Посылка дверь-дверь",
                184: "E-com Standard дверь-дверь",
                185: "E-com Standard склад-склад",
                186: "E-com Standard склад-дверь",
                187: "E-com Standard дверь-склад",
                231: "Экономичная посылка дверь-дверь",
                232: "Экономичная посылка дверь-склад",
                233: "Экономичная посылка склад-дверь",
                234: "Экономичная посылка склад-склад",
                291: "E-com Express склад-склад",
                293: "E-com Express дверь-дверь",
                294: "E-com Express склад-дверь",
                295: "E-com Express дверь-склад",
                358: "Фулфилмент выдача",
                366: "Посылка дверь-постамат",
                368: "Посылка склад-постамат",
                378: "Экономичная посылка склад-постамат",
                497: "E-com Standard дверь-постамат",
                498: "E-com Standard склад-постамат",
                509: "E-com Express дверь-постамат",
                510: "E-com Express склад-постамат",
                2261: "Documents Express дверь-дверь",
                2262: "Documents Express дверь-склад",
                2263: "Documents Express склад-дверь",
                2264: "Documents Express склад-склад",
                2266: "Documents Express дверь-постамат",
                2267: "Documents Express склад-постамат",
                2321: "Экономичный экспресс дверь-склад",
                2322: "Экономичный экспресс склад-дверь",
                2323: "Экономичный экспресс склад-склад",
                2360: "Доставка день в день",
                2536: "Один офис (ИМ)"

            }
            return tariff_names.get(tariff_code, "Неизвестен")

        print(f"Debug: Callback query data: {callback_query.data}")

        cursor.execute("SELECT order_info FROM new_orders WHERE user_id = ? ORDER BY id DESC LIMIT 1",
                       (callback_query.from_user.id,))
        order_info = cursor.fetchone()
        id = callback_query.from_user.id
        if order_info:
            order_info_str = order_info[0]
            print(f"Debug: Fetched order info: {order_info_str}")

            try:
                order_info_dict = ast.literal_eval(order_info_str)
                if 'entity' in order_info_dict:
                    entity_info = order_info_dict['entity']

                    # Получаем режим доставки и название тарифа, используя функции
                    delivery_mode = entity_info.get('delivery_mode', 'N/A')
                    delivery_mode_text = get_delivery_mode_text(delivery_mode)
                    tariff_code = entity_info.get('tariff_code', 'N/A')
                    tariff_name = get_tariff_name(tariff_code)
                    print(tariff_name)

                    # Extract sender and recipient information, handling potential None values
                    sender_company = entity_info.get('sender', {}).get('company', 'N/A')
                    sender_name = entity_info.get('sender', {}).get('name', 'N/A')
                    recipient_company = entity_info.get('recipient', {}).get('company', 'N/A')

                    # Initialize recipient_name with a default value
                    recipient_name = 'N/A'
                    recipient_data = entity_info.get('recipient', {})
                    if recipient_data:  # Check if recipient data exists
                        recipient_name = recipient_data.get('name', 'N/A')

                    # Clean up company names (remove quotes and handle potential Unicode issues)
                    sender_company = sender_company.replace('"', '').encode('utf-8').decode('utf-8', 'replace')
                    sender_name = sender_name.replace('"', '').encode('utf-8').decode('utf-8', 'replace')
                    recipient_company = recipient_company.replace('"', '').encode('utf-8').decode('utf-8', 'replace')
                    recipient_name = recipient_name.replace('"', '').encode('utf-8').decode('utf-8', 'replace')

                    # Формируем текст для вывода
                    entity_text = "🔍 *Основная информация:*\n"
                    entity_text += f"- Номер отправления: {entity_info.get('cdek_number', 'N/A')}\n"
                    entity_text += f"- Пункт доставки: {entity_info.get('delivery_point', 'N/A')}\n"
                    entity_text += f"- Отправлено в Адрес получения доставки: {entity_info.get('to_location', {}).get('country', 'N/A')}, {entity_info.get('to_location', {}).get('city', 'N/A')}, {entity_info.get('to_location', {}).get('address', 'N/A')}\n"
                    entity_text += f"- Тариф: {tariff_name} (Код: {tariff_code})\n"
                    entity_text += f"- Итоговая стоимость заказа услуги (тариф + Дополнительный сбор за объявленную стоимость): {entity_info.get('delivery_detail', {}).get('total_sum', 'N/A')} руб.\n"
                    entity_text += f"- Оплата за товар: {entity_info.get('items_cost', 'N/A')} ₽\n"  # Предположил название ключа
                    entity_text += f"- Доп. сбор с получателя за доставку: 0,00 ₽\n"  # Нужно уточнить, где это хранится
                    entity_text += "- Сумма наложенного платежа, которую взяли с получателя:\n\n"  # Нужно уточнить, где это хранится

                    # entity_text += "✅Информация о вручении:\n\n"
                    entity_text += "👥 *Контакты отправителя:*\n"
                    entity_text += f"- Отправитель: {sender_company} - {sender_name}\n"
                    entity_text += f"- 📞 Телефон отправителя: {entity_info.get('sender', {}).get('phones', [{}])[0].get('number', 'N/A')}\n"

                    entity_text += "👥 *Контакты получателя:*\n"
                    entity_text += f"- Получатель: {recipient_company} - {recipient_name}\n"
                    entity_text += f"- 📞 Телефон получателя: {entity_info.get('recipient', {}).get('phones', [{}])[0].get('number', 'N/A')}\n\n"

                    entity_text += "🎁 *Содержимое посылки:*\n"
                    i = 1
                    for package in entity_info.get('packages', []):
                        entity_text += f"{i}) Номер места: {package.get('number', 'N/A')}, Вес: {package.get('weight', 'N/A')} г, Размеры: {package.get('length', 'N/A')}x{package.get('width', 'N/A')}x{package.get('height', 'N/A')} см\n"
                        for item in package.get('items', []):
                            item_name = item.get('name', 'N/A').replace('_', '\\_')  # Экранируем _
                            entity_text += f"- {item_name}: Вес: {item.get('weight', 'N/A')} г, Стоимость: {item.get('cost', 'N/A')} руб.\n"
                        i += 1

                    # Добавляем раздел о проблемах доставки
                    delivery_problems_section = ""
                    if 'statuses' in entity_info and len(entity_info['statuses']) > 0:
                        last_status = entity_info['statuses'][-1]
                        if 'delivery_detail' in last_status and last_status['delivery_detail']:
                            delivery_problems_section = (
                                "\n⚠️ *Проблемы доставки до двери (комментарий от курьера):*\n"
                                f"- {last_status['delivery_detail']}\n\n"
                            )
                        else:
                            delivery_problems_section = "\n✅ *Проблем с доставкой нет*\n\n"
                    else:
                        delivery_problems_section = "\nℹ️ *Информация о статусе доставки отсутствует*\n\n"

                    entity_text += delivery_problems_section

                    # def format_delivery_problems(entity_info):
                    #     """Форматирует информацию о проблемах доставки согласно спецификации СДЭК"""
                    #     problems = []
                    #     status_codes = {s['code']: s for s in entity_info.get('statuses', [])}
                    #
                    #     # 1. Проверка статусов, указывающих на проблемы
                    #     problem_statuses = {
                    #         'NOT_DELIVERED': '❌ Доставка не осуществлена',
                    #         'PARTIAL_DELIVERED': '⚠️ Частичная доставка',
                    #         'RETURNED': '↩️ Посылка возвращена',
                    #         'RETURNED_TO_SENDER_CITY_WAREHOUSE': '↩️ Возврат в город отправителя',
                    #         'RETURNED_TO_RECIPIENT_CITY_WAREHOUSE': '↩️ Возврат на склад доставки',
                    #         'LOST': '❗ Посылка утеряна',
                    #         'DAMAGED': '❗ Посылка повреждена'
                    #     }
                    #
                    #     for code, message in problem_statuses.items():
                    #         if code in status_codes:
                    #             status = status_codes[code]
                    #             problem_details = f"{message} ({status.get('city', '')})"
                    #             if 'reason' in status:
                    #                 problem_details += f"\n   - Причина: {status['reason']}"
                    #             if 'courier_comment' in status:
                    #                 problem_details += f"\n   -Комментарий курьера: {status['courier_comment']}"
                    #             problems.append(problem_details)
                    #
                    #     # 2. Проверка переносов доставки
                    #     if 'calls' in entity_info:
                    #         for call in entity_info['calls'].get('rescheduled_calls', []):
                    #             problems.append(
                    #                 f"⏱ Перенос доставки на {call.get('date_next', '?')}\n"
                    #                 f"   └─ Причина: {call.get('comment', 'не указана')}"
                    #             )
                    #     from datetime import datetime
                    #     # 3. Проверка задержки доставки
                    #     planned_date = entity_info.get('planned_delivery_date')
                    #     actual_date = entity_info.get('delivery_date')
                    #     if planned_date and actual_date and planned_date != actual_date:
                    #         try:
                    #             delta = (datetime.strptime(actual_date, "%Y-%m-%d") -
                    #                      datetime.strptime(planned_date, "%Y-%m-%d")).days
                    #             if delta > 0:
                    #                 problems.append(f"⌛ Задержка доставки: {delta} дней")
                    #         except ValueError:
                    #             pass
                    #
                    #     # 4. Форматирование результата
                    #     if problems:
                    #         problems_text = "\n".join([f"- {p}" for p in problems])
                    #         return (
                    #             "\n⚠️ *Проблемы с доставкой:*\n"
                    #             f"{problems_text}\n"
                    #             "ℹ️ *Рекомендация:* Уточните детали в службе поддержки СДЭК\n"
                    #         )
                    #     return "\n✅ *Проблем с доставкой не зафиксировано*\n"
                    #
                    # # Использование в основном коде:
                    # entity_text += format_delivery_problems(entity_info)
                    entity_text += f"\n"
















                    # entity_text += f"\n🚚 *Режим доставки:* {delivery_mode_text}\n"
                    # entity_text += f"📋 Тариф: {tariff_name} (Код: {tariff_code})\n\n"

                    # Extract data for delivery time calculation
                    sender_city_code = entity_info.get('from_location', {}).get('code', None)
                    recipient_city_code = entity_info.get('to_location', {}).get('code', None)
                    tariff_code = entity_info.get('tariff_code', None)
                    # Assuming all packages have the same dimensions; you might need to average or find the largest
                    if entity_info.get('packages'):
                        first_package = entity_info['packages'][0]
                        weight = first_package.get('weight', 1000)  # Default weight
                        length = first_package.get('length', 10)  # Default dimension
                        width = first_package.get('width', 10)  # Default dimension
                        height = first_package.get('height', 10)  # Default dimension
                        cost = first_package.get('cost', 10)  # Default dimension
                        print(cost)
                    else:
                        weight = 1000
                        length = 10
                        width = 10
                        height = 10
                        cost = 10

                    # Calculate delivery time (replace with actual API call)
                    if sender_city_code and recipient_city_code and tariff_code:
                        delivery_time = calculate_delivery_time(sender_city_code, recipient_city_code, weight, length,
                                                                width, height, cost, id)
                    else:
                        delivery_time = "Недостаточно данных для расчета"
                    print(delivery_time)
                    entity_text += "📅 *Сроки:*\n"
                    entity_text += f"- Прайсовый срок: {delivery_time}\n"
                    # Inside your main code, where you create entity_text
                    cdek_number = entity_info.get('cdek_number')  # Get the CDEK number
                    if cdek_number:
                        planned_delivery_date, actual_delivery_date, delivery_problem_reason = get_delivery_dates(
                            cdek_number, id)
                    else:
                        planned_delivery_date = "ожидается"  # Handle the case where cdek_number is missing
                        actual_delivery_date = "ожидается"
                        delivery_problem_reason = "Номер СДЭК отсутствует"  # Handle the case where cdek_number is missing





                    # Добавляем информацию о планируемой доставке
                    if planned_delivery_date and planned_delivery_date != "ожидается":
                        entity_text += f"- Планируемая дата доставки: {planned_delivery_date}\n"
                    else:
                        entity_text += "*Информация о планируемой доставке:* Отсутствует\n"
                    # Добавляем информацию о хранении на ПВЗ (если есть)
                    if 'warehouse' in entity_info and 'storage' in entity_info['warehouse']:
                        storage_date = entity_info['warehouse']['storage'].get('end_date')
                        if storage_date:
                            try:
                                storage_date = datetime.datetime.strptime(storage_date, "%Y-%m-%d").strftime("%d.%m.%Y")
                                entity_text += f"- Хранение на ПВЗ до: {storage_date}\n"
                            except ValueError:
                                entity_text += "- Хранение на ПВЗ до: не указано\n"
                        else:
                            entity_text += "- Хранение на ПВЗ до: не указано\n"
                    else:
                        entity_text += "- Хранение на ПВЗ до: не предусмотрено\n"







                    # Выводим информацию из related_entities текстом
                    related_entities = order_info_dict.get('related_entities', [])
                    if related_entities:
                        entity_text += "- Дата доставки :"
                        for delivery_info in related_entities:
                            delivery_date_str = delivery_info.get('date')
                            time_from_str = delivery_info.get('time_from')
                            time_to_str = delivery_info.get('time_to')

                            # Форматируем дату и время (если они есть)
                            formatted_delivery_date = ""
                            formatted_time_from = ""
                            formatted_time_to = ""

                            if delivery_date_str:
                                try:
                                    delivery_date = datetime.datetime.strptime(delivery_date_str, "%Y-%m-%d")
                                    formatted_delivery_date = delivery_date.strftime("%d.%m.%Y")
                                except ValueError:
                                    formatted_delivery_date = "Ошибка формата даты"

                            if time_from_str:
                                formatted_time_from = time_from_str  # Время уже в нужном формате

                            if time_to_str:
                                formatted_time_to = time_to_str  # Время уже в нужном формате

                            # Собираем строку информации
                            delivery_text = ""
                            if formatted_delivery_date:
                                delivery_text += f"  Дата: {formatted_delivery_date}, "
                            if formatted_time_from:
                                delivery_text += f"с {formatted_time_from} "
                            if formatted_time_to:
                                delivery_text += f"до {formatted_time_to}"

                            # Убираем последнюю запятую и пробел, если есть
                            delivery_text = delivery_text.rstrip(', ')

                            if delivery_text:
                                entity_text += f"{delivery_text}\n"
                            else:
                                entity_text += "- Нет данных о планируемой доставке\n"


                    else:
                        entity_text += "- Информация о планируемой доставке: Отсутствует\n"

                    entity_text += f"- Фактическая доставка: {actual_delivery_date}\n"

                    # Рассчитываем просрочку
                    overdue = calculate_overdue_days(planned_delivery_date, actual_delivery_date)

                    # if overdue is not None:  # Проверяем, что вернулось не None (значит, даты были валидны)
                    #     entity_text += f"- Просрочка: {overdue} дней\n"
                    # else:
                    #     entity_text += "- Просрочка: Нет данных (ожидается доставка или некорректные даты)\n"

                    # Добавляем информацию о проблеме с доставкой
                    # entity_text += f"- Проблемы с доставкой: {delivery_problem_reason}\n"
                    entity_text += f"💬 Комментарий: {entity_info.get('comment', 'N/A')}\n"

                    print(entity_text)

                    keyboard = InlineKeyboardMarkup()
                    keyboard.add(
                        InlineKeyboardButton("Телефон офиса ответственного за вручение посылки",
                                             callback_data='delivery_office_phone')
                    )
                    # Добавляем кнопку "Поделиться"
                    keyboard.add(
                        InlineKeyboardButton("↗️ Поделиться",
                                             switch_inline_query=f"Данные по посылке: {entity_text}")
                    )

                    max_length = 4000
                    if len(entity_text) > max_length:
                        split_index = entity_text.rfind('\n', 0, max_length)
                        if split_index == -1:
                            split_index = max_length

                        first_part = entity_text[:split_index]
                        second_part = entity_text[split_index:]

                        await bot.send_message(callback_query.from_user.id, first_part, parse_mode='Markdown')
                        await bot.send_message(callback_query.from_user.id, second_part, reply_markup=keyboard,
                                               parse_mode='Markdown')
                    else:
                        await bot.send_message(callback_query.from_user.id, entity_text, reply_markup=keyboard,
                                               parse_mode='Markdown')

                else:
                    await bot.send_message(callback_query.from_user.id,
                                           "Пожалуйста введите номер накладной по вашему договору.")

            except (ValueError, SyntaxError) as e:
                await bot.send_message(callback_query.from_user.id,
                                       "Ошибка декодирования информации о заказе. Попробуйте еще раз позже.")
                print(f"Error: {e}")
            except Exception as e:
                await bot.send_message(callback_query.from_user.id, f"Произошла непредвиденная ошибка: {e}")
                print(f"Unexpected error: {e}")
        else:
            await bot.send_message(callback_query.from_user.id, "Информация о заказе не найдена.")


    elif callback_query.data == 'parcel_data2':
        await callback_query.message.delete()
        # Fetch order info from the database
        cursor.execute("SELECT order_info FROM new_orders WHERE user_id = ? ORDER BY id DESC LIMIT 1",
                       (callback_query.from_user.id,))
        order_info = cursor.fetchone()
        if order_info:
            order_info_str = order_info[0]
            print(f"Debug: Fetched order info: {order_info_str}")  # Debugging line
            try:
                print("-----------------------------------------------------")
                order_info_dict = ast.literal_eval(order_info_str)  # Safely evaluate the string as a Python dictionary
                print("order_info_dict")
                if 'entity' in order_info_dict:
                    print("entity")
                    entity_info = order_info_dict['entity']
                    # Обработка статусов
                    statuses = entity_info.get('statuses', [])
                    status_text = ""
                    for status in statuses:
                        status_text += f"📌 *Статус:* {status['name']} ({status['code']}) - {status['date_time']} - {status['city']}\n"
                    print("status")
                    # Определяем способ доставки
                    delivery_mode = entity_info.get('delivery_mode', 'N/A')
                    delivery_mode_text = "Неизвестен"
                    if delivery_mode == '1':
                        delivery_mode_text = "Курьер заберет отправление у отправителя"
                    elif delivery_mode == '2':
                        delivery_mode_text = "Отправление будет доставлено курьером получателю"
                    elif delivery_mode == '3':
                        delivery_mode_text = "Отправление будет сдано в пункт выдачи СДЭК в городе отправителе"
                    elif delivery_mode == '4':
                        delivery_mode_text = "Отправление будет забрано получателем из ПВЗ СДЭК"
                    else:
                        delivery_mode_text = f""  # Для отладки
                    print(delivery_mode_text)
                    # Определяем тариф (по коду, требуется соответствие кодов и названий тарифов!)
                    tariff_code = entity_info.get('tariff_code', 'N/A')
                    tariff_name = "Неизвестен"  # Значение по умолчанию
                    if tariff_code == 1:
                        tariff_name = "Экспресс лайт"  # или "Express лайт" - уточните написание
                    elif tariff_code == 3:
                        tariff_name = "Супер-экспресс до 10:00"
                    elif tariff_code == 5:
                        tariff_name = "Супер-экспресс до 18:00"
                    elif tariff_code == 10:
                        tariff_name = "Экономичный экспресс"
                    elif tariff_code == 11:
                        tariff_name = "Экспресс плюс"
                    elif tariff_code == 15:
                        tariff_name = "Международный экспресс"
                    elif tariff_code == 16:
                        tariff_name = "Импорт"
                    elif tariff_code == 17:
                        tariff_name = "Международный экономичный"
                    elif tariff_code == 57:
                        tariff_name = "Китайский экспресс"
                    elif tariff_code == 62:
                        tariff_name = "СДЭК-Посылка"  # или "CDEK-Посылка"
                    elif tariff_code == 63:
                        tariff_name = "CDEK Express"
                    elif tariff_code == 136:
                        tariff_name = "Посылка дверь-дверь"  # Самый популярный для e-commerce
                    elif tariff_code == 137:
                        tariff_name = "Посылка склад-склад"
                    elif tariff_code == 139:
                        tariff_name = "Экономичная посылка склад-склад"
                    elif tariff_code == 233:
                        tariff_name = "Prime"
                    elif tariff_code == 291:
                        tariff_name = "LTL"
                    elif tariff_code == 292:
                        tariff_name = "FTL"
                    else:
                        tariff_name = f"Неизвестный тариф (код {tariff_code})"  # Для отладки

                    print(tariff_name)
                    entity_text = (
                        f"📦 *Информация об отправлении:*\n\n"
                        f"🔑 *UUID:* {entity_info.get('uuid', 'N/A')}\n"
                        f"📝 *Номер отправления:* {entity_info.get('cdek_number', 'N/A')}\n"
                        f"  💬 *Комментарий:* {entity_info.get('comment', 'N/A')}\n"
                        f"  📍 *Пункт доставки:* {entity_info.get('delivery_point', 'N/A')}\n"
                        f"  👥 *Отправитель:* {entity_info['sender'].get('company', 'N/A')} - {entity_info['sender'].get('name', 'N/A')}\n"
                        f"  👥 *Получатель:* {entity_info['recipient'].get('company', 'N/A')} - {entity_info['recipient'].get('name', 'N/A')}\n"
                        f"📋 *Тарифный код:* {entity_info.get('tariff_code', 'N/A')}\n"
                        f"📋 *Тариф:* {tariff_name} (Код: {tariff_code})\n"  # Добавлено название тарифа
                        f"🏢 *Пункт отправления:* {entity_info.get('shipment_point', 'N/A')}\n"
                        f"💵 *Стоимость товаров (в валюте):* {entity_info.get('items_cost_currency', 'N/A')}\n"
                        f"🚚 *Итоговая стоимость заказа:* {entity_info.get('delivery_recipient_cost', {}).get('value', 'N/A')}\n\n"
                        f"👤 *Отправитель:* {entity_info.get('sender', {}).get('name', 'N/A')}\n"
                        f"  📞 *Телефон отправителя:* {entity_info.get('sender', {}).get('phones', [{}])[0].get('number', 'N/A')}\n"
                            f"🏢 *Компания получателя:* {entity_info.get('recipient', {}).get('company', 'N/A')}\n\n"
                        f"👤 *Получатель:* {entity_info.get('recipient', {}).get('name', 'N/A')}\n"
                        f"  📞 *Телефон получателя:* {entity_info.get('recipient', {}).get('phones', [{}])[0].get('number', 'N/A')}\n"
                        f"📌 *Отправлено из:* {entity_info.get('from_location', {}).get('city', 'N/A')}, {entity_info.get('from_location', {}).get('country', 'N/A')}\n"
                        f"📌 *Отправлено в:* {entity_info.get('to_location', {}).get('city', 'N/A')}, {entity_info.get('to_location', {}).get('country', 'N/A')}\n"
                        f"🚚 *Режим доставки:* {delivery_mode_text}\n"  # Добавлено название режима доставки
                        # f"{status_text}"
                    )
                    print(entity_text)
                    # Add your code to process and send the entity information
                    keyboard = InlineKeyboardMarkup()
                    keyboard.add(
                        InlineKeyboardButton("Телефон офиса ответственного за вручение посылки",
                                             callback_data='delivery_office_phone'),
                        InlineKeyboardButton("Назад", callback_data='go_back')
                    )
                    max_length = 4000

                    if len(entity_text) > max_length:
                        # Находим последнее допустимое место для разрыва строки, чтобы не сломать Markdown
                        split_index = entity_text.rfind('\n', 0, max_length)  # Ищем последнюю новую строку

                        if split_index == -1:
                            split_index = max_length  # Если нет новой строки, просто обрезаем по максимальной длине

                        first_part = entity_text[:split_index]
                        second_part = entity_text[split_index:]

                        await bot.send_message(callback_query.from_user.id, first_part)
                        await bot.send_message(callback_query.from_user.id, second_part, reply_markup=keyboard)
                    else:
                        await bot.send_message(callback_query.from_user.id, entity_text, reply_markup=keyboard)
                else:
                    await bot.send_message(callback_query.from_user.id,
                                           "Пожалуйста введите номер накладной по вашему договору.")

            except (ValueError, SyntaxError) as e:
                await bot.send_message(callback_query.from_user.id, "Ошибка декодирования информации о заказе. Попробуйте еще раз позже.")
                print(f"Error: {e}")
        else:
            await bot.send_message(callback_query.from_user.id, "Информация о заказе не найдена.")



    elif callback_query.data == 'delivery_office_phone':
        await callback_query.message.delete()
        cursor.execute("SELECT order_info FROM new_orders WHERE user_id = ? ORDER BY id DESC LIMIT 1",
                       (callback_query.from_user.id,))
        order_info = cursor.fetchone()
        id = callback_query.from_user.id
        if order_info:
            order_info_str = order_info[0]
            print(f"Debug: Fetched order info: {order_info_str}")  # Debugging line
            try:
                order_info_dict = ast.literal_eval(order_info_str)  # Safely evaluate the string as a Python dictionary
                if 'entity' in order_info_dict:
                    entity_info = order_info_dict['entity']

                    delivery_point_code = entity_info.get('delivery_point')
                    print(delivery_point_code)
                    from Delivery_Arrangement_Information import deliverypoints, format_deliverypoint_info
                    if delivery_point_code:
                        response = deliverypoints(id, delivery_point_code)
                        if response:
                            formatted_info = format_deliverypoint_info(response[0])
                            await callback_query.message.answer(
                                f"{formatted_info}")
                        else:
                            await callback_query.message.answer("Информация о пункте выдачи не найдена.")
                    else:
                        await callback_query.message.answer("Код пункта выдачи не найден в данных заказа.")
            except (SyntaxError, ValueError) as e:
                print(f"Error parsing order info: {e}")  # Debugging line
                await callback_query.message.answer("Ошибка обработки данных заказа.")
        else:
            await callback_query.message.answer("Информация о заказе не найдена.")


    elif callback_query.data == 'go_back':

        await process_order_number(callback_query.message, state=None)










    elif callback_query.data == 'change_order':
        await callback_query.message.delete()
        keyboard_markup = types.InlineKeyboardMarkup(row_width=1)
        buttons = [
            types.InlineKeyboardButton(text="Изменить ФИО получателя", callback_data='change_fullname'),
            types.InlineKeyboardButton(text="Изменить телефон получателя", callback_data='change_phone'),
            types.InlineKeyboardButton(text="Изменить адрес\офис доставкиТариф", callback_data='change_address')
        ]
        keyboard_markup.add(*buttons)
        await bot.send_message(callback_query.from_user.id, "Выберите что хотите изменить",
                               reply_markup=keyboard_markup)
    elif callback_query.data == 'change_address':
        keyboard_markup = types.InlineKeyboardMarkup(row_width=1)
        buttons = [
            types.InlineKeyboardButton(text="Изменить адрес доставки (для режима «…до двери»)", callback_data='address'),
            types.InlineKeyboardButton(text="Изменить офис доставки (ПВЗ)", callback_data='change_pickup_point'),
            # types.InlineKeyboardButton(text="Изменить город получателя", callback_data='change_city')
        ]
        keyboard_markup.add(*buttons)
        await bot.send_message(callback_query.from_user.id, "Выберите что хотите изменить",
                               reply_markup=keyboard_markup)

    elif callback_query.data == 'cancel_delivery':
        await callback_query.message.delete()

        await otmena_zakaza(callback_query)
        # await bot.send_message(callback_query.from_user.id, "Функция отмены доставки в разработке.")
    elif callback_query.data == 'change_delivery_date':
        await callback_query.message.delete()
        # await bot.send_message(callback_query.from_user.id, "Функция изменения даты доставки в разработке.")
        await change_delivery_date(callback_query)




    elif callback_query.data == 'edit_cod_amount':
        await callback_query.message.delete()
        keyboard_markup = types.InlineKeyboardMarkup(row_width=1)
        buttons = [
            types.InlineKeyboardButton(text="Отменить все наложенные платежи", callback_data='otmena_vcex_plat'),
            # types.InlineKeyboardButton(text="Изменить наложенный платеж за товар", callback_data='izmenit_za_tovar'),
            types.InlineKeyboardButton(text="Изменить наложенный платеж за доп. сбор", callback_data='izmenit_za_dop')
        ]
        keyboard_markup.add(*buttons)
        await bot.send_message(callback_query.from_user.id, "Выберите что хотите изменить",
                               reply_markup=keyboard_markup)

    elif callback_query.data == 'otmena_vcex_plat':
        from izmeneniya import nalozh_pay_otmena_vse_3
        id = callback_query.from_user.id
        cursor.execute('SELECT order_info FROM new_orders WHERE user_id = ? ORDER BY id DESC LIMIT 1', (callback_query.from_user.id,))
        order_info = cursor.fetchone()
        print(order_info)
        if order_info:
            try:
                order_info_str = order_info[0]
                order_info_dict = ast.literal_eval(order_info_str)

                # Извлекаем необходимые поля из order_info_dict для передачи в nalozh_pay_otmena_vse
                uuid = order_info_dict['entity']['uuid']
                tariff_code = order_info_dict['entity'].get('tariff_code',
                                                            None)  # Используйте .get(), чтобы избежать ошибки, если ключ отсутствует
                sender_city_id = order_info_dict['entity'].get('sender_city_id', None)
                delivery_recipient_cost_value = order_info_dict['entity'].get('delivery_recipient_cost', {}).get('value',
                                                                                                                 None)  # извлекаем значение наложенного платежа
                # и другие поля, которые могут потребоваться для полного обновления заказа

                nalozh_pay_otmena = nalozh_pay_otmena_vse_3(
                    cdek_number=uuid,
                    tariff_code=tariff_code,
                    sender_city_id=sender_city_id,
                    delivery_recipient_cost_value=delivery_recipient_cost_value,
                    id = id,
                    # Передайте остальные необходимые поля
                )

                # Проверяем ответ от API и отправляем соответствующее сообщение
                if isinstance(nalozh_pay_otmena, dict) and 'entity' in nalozh_pay_otmena and nalozh_pay_otmena[
                    'entity'].get('uuid') == uuid and 'requests' in nalozh_pay_otmena and len(
                        nalozh_pay_otmena['requests']) > 0 and nalozh_pay_otmena['requests'][0]['state'] == 'ACCEPTED':
                    await callback_query.message.answer(
                        "Наложенный платеж успешно отменен!")  # или другое сообщение об успехе
                else:
                    await callback_query.message.answer(
                        f"Произошла ошибка при отмене наложенного платежа: {nalozh_pay_otmena}")  # Выводим ответ API для отладки

            except Exception as e:  # Ловим возможные ошибки при обработке или отмене
                await callback_query.message.answer(f"Произошла ошибка: {e}")

        else:
            await callback_query.message.answer("Информация о заказе не найдена.")









    elif callback_query.data == 'extend_storage':
        cursor.execute("SELECT order_info FROM new_orders WHERE user_id = ? ORDER BY id DESC LIMIT 1",
                       (callback_query.from_user.id,))
        order_info = cursor.fetchone()
        if order_info:
            order_info_str = order_info[0]
            print(f"Debug: Fetched order info: {order_info_str}")  # Debugging line
            try:
                order_info_dict = ast.literal_eval(order_info_str)  # Safely evaluate the string as a Python dictionary
                if 'entity' in order_info_dict:
                    entity_info = order_info_dict['entity']
                    delivery_point_code = entity_info.get('delivery_point')
                    print(delivery_point_code)
                    from Delivery_Arrangement_Information import deliverypoints, format_deliverypoint_info
                    if delivery_point_code:
                        response = deliverypoints(delivery_point_code)
                        if response:
                            formatted_info = format_deliverypoint_info(response[0])
                            await callback_query.message.answer(f"Обратитесь к закрепленному менеджеру:\n\n{formatted_info}")
                        else:
                            await callback_query.message.answer("Информация о пункте выдачи не найдена.")
                    else:
                        await callback_query.message.answer("Код пункта выдачи не найден в данных заказа.")
            except (SyntaxError, ValueError) as e:
                print(f"Error parsing order info: {e}")  # Debugging line
                await callback_query.message.answer("Ошибка обработки данных заказа.")
        else:
            await callback_query.message.answer("Информация о заказе не найдена.")



    elif callback_query.data == '/lists':
        # Create a new inline keyboard with three buttons
        inline_keyboard = InlineKeyboardMarkup(row_width=1)
        inline_keyboard.add(
            # InlineKeyboardButton("Списки регионов", callback_data='list_regions'),
            InlineKeyboardButton("Списки офисов", callback_data='list_offices')
            # InlineKeyboardButton("Списки населенных пунктов", callback_data='list_settlements')
        )
        # Send the "выберете из списка" message with the inline keyboard
        await bot.send_message(callback_query.from_user.id, "Выберете из списка:", reply_markup=inline_keyboard)


    # You can implement specific logic for each callback data here
    elif callback_query.data == 'list_regions':
        from regions import region_code
        region = region_code()
        message = "🌍 **Списки регионов 🏞️**:\n"
        for code, region in region.items():
            message += f"- {code}: '{region}'\n"

        await bot.send_message(callback_query.from_user.id, message)

    elif callback_query.data == 'list_offices':
        await bot.send_message(callback_query.from_user.id, "Списки офисов")


    elif callback_query.data == 'list_settlements':
        await bot.send_message(callback_query.from_user.id, "Списки населенных пунктов")



# # Клавиатура с датами
# def create_date_keyboard():
#     keyboard = InlineKeyboardMarkup(row_width=2)
#     # Начинаем с завтрашнего дня
#     today = datetime.now() + timedelta(days=1)
#     for i in range(5):
#         date = today + timedelta(days=i)
#         date_str = date.strftime('%Y-%m-%d')
#         keyboard.add(InlineKeyboardButton(text=date_str, callback_data=f"date_{date_str}"))
#     return keyboard
#
# # Функция для создания клавиатуры с временем
# def create_time_keyboard():
#     keyboard = InlineKeyboardMarkup(row_width=3)
#     keyboard.add(InlineKeyboardButton(text="09:00-14:00", callback_data="time_09:00-14:00"))
#     keyboard.add(InlineKeyboardButton(text="14:00-18:00", callback_data="time_14:00-18:00"))
#     keyboard.add(InlineKeyboardButton(text="09:00-18:00", callback_data="time_09:00-18:00"))
#     return keyboard
#
# # Обработчик выбора даты
# async def change_delivery_date(callback_query: types.CallbackQuery):
#     await bot.send_message(callback_query.from_user.id, "Выберите дату доставки:", reply_markup=create_date_keyboard())
#     await Form.change_delivery_date_date.set()
#
# # Обработчик выбора даты
# @dp.callback_query_handler(lambda c: c.data.startswith('date_'), state=Form.change_delivery_date_date)
# async def process_change_delivery_date_date(callback_query: types.CallbackQuery, state: FSMContext):
#     date = callback_query.data.split('_')[1]
#     await state.update_data(change_delivery_date_date=date)
#     await bot.send_message(callback_query.from_user.id, "Выберите время доставки:", reply_markup=create_time_keyboard())
#     await Form.change_delivery_date_time_from.set()
#
# # Обработчик выбора времени
# @dp.callback_query_handler(lambda c: c.data.startswith('time_'), state=Form.change_delivery_date_time_from)
# async def process_change_delivery_date_time_from(callback_query: types.CallbackQuery, state: FSMContext):
#     time_range = callback_query.data.split('_')[1]
#     time_from = time_range.split('-')[0]
#     time_to = time_range.split('-')[1]
#
#     await state.update_data(change_delivery_date_time_from=time_from)
#     await state.update_data(change_delivery_date_time_to=time_to) # Записываем time_to
#     await bot.send_message(callback_query.from_user.id, "Введите комментарий к изменению даты доставки:")
#     await Form.change_delivery_date_comment.set()
#
# # Обработчик ввода комментария
# @dp.message_handler(state=Form.change_delivery_date_comment)
# async def process_change_delivery_date_comment(message: types.Message, state: FSMContext):
#     print('-------------------------------------------------------')
#     comment = message.text
#     print(comment)
#     await state.update_data(change_delivery_date_comment=comment)
#
#     # Получаем все данные из FSM
#     data = await state.get_data()
#     print(data)
#     date = data['change_delivery_date_date']
#     time_from = data['change_delivery_date_time_from']
#     time_to = data['change_delivery_date_time_to']
#     comment = data['change_delivery_date_comment']
#
#
#     # Вызываем функцию для отправки запроса в API СДЭК
#     await send_delivery_date_change_request(message, state, date, time_from, time_to, comment)
# Клавиатура с датами
def create_date_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=2)
    # Начинаем с завтрашнего дня
    today = datetime.now() + timedelta(days=1)
    for i in range(5):
        date = today + timedelta(days=i)
        date_str = date.strftime('%Y-%m-%d')
        keyboard.add(InlineKeyboardButton(text=date_str, callback_data=f"date_{date_str}"))

    # Добавляем кнопку "Отмена"
    keyboard.add(InlineKeyboardButton(text="❌ Отменить ввод", callback_data="cancel_change_date"))
    return keyboard

# Функция для создания клавиатуры с временем
def create_time_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=3)
    keyboard.add(InlineKeyboardButton(text="09:00-14:00", callback_data="time_09:00-14:00"))
    keyboard.add(InlineKeyboardButton(text="14:00-18:00", callback_data="time_14:00-18:00"))
    keyboard.add(InlineKeyboardButton(text="09:00-18:00", callback_data="time_09:00-18:00"))

    # Добавляем кнопку "Отмена"
    keyboard.add(InlineKeyboardButton(text="❌ Отменить ввод", callback_data="cancel_change_time"))
    return keyboard

# Обработчик выбора даты
async def change_delivery_date(callback_query: types.CallbackQuery):
    await bot.send_message(callback_query.from_user.id, "Выберите дату доставки:", reply_markup=create_date_keyboard())
    await Form.change_delivery_date_date.set()

# Обработчик выбора даты
@dp.callback_query_handler(lambda c: c.data.startswith('date_'), state=Form.change_delivery_date_date)
async def process_change_delivery_date_date(callback_query: types.CallbackQuery, state: FSMContext):
    date = callback_query.data.split('_')[1]
    await state.update_data(change_delivery_date_date=date)
    await bot.send_message(callback_query.from_user.id, "Выберите время доставки:", reply_markup=create_time_keyboard())
    await Form.change_delivery_date_time_from.set()

# Обработчик выбора времени
@dp.callback_query_handler(lambda c: c.data.startswith('time_'), state=Form.change_delivery_date_time_from)
async def process_change_delivery_date_time_from(callback_query: types.CallbackQuery, state: FSMContext):
    time_range = callback_query.data.split('_')[1]
    time_from = time_range.split('-')[0]
    time_to = time_range.split('-')[1]

    await state.update_data(change_delivery_date_time_from=time_from)
    await state.update_data(change_delivery_date_time_to=time_to) # Записываем time_to
    await bot.send_message(callback_query.from_user.id, "Введите комментарий к изменению даты доставки:", reply_markup=cancel_keyboard) # cancel_keyboard already defined!
    await Form.change_delivery_date_comment.set()

# Обработчик ввода комментария
@dp.message_handler(state=Form.change_delivery_date_comment)
async def process_change_delivery_date_comment(message: types.Message, state: FSMContext):
    print('-------------------------------------------------------')
    comment = message.text
    print(comment)
    await state.update_data(change_delivery_date_comment=comment)

    # Получаем все данные из FSM
    data = await state.get_data()
    print(data)
    date = data['change_delivery_date_date']
    time_from = data['change_delivery_date_time_from']
    time_to = data['change_delivery_date_time_to']
    comment = data['change_delivery_date_comment']
    user_id = message.from_user.id


    # Вызываем функцию для отправки запроса в API СДЭК
    await send_delivery_date_change_request(message, state, date, time_from, time_to, comment, user_id)

# Обработчик отмены для выбора даты
@dp.callback_query_handler(lambda c: c.data == "cancel_change_date", state=Form.change_delivery_date_date)
async def cancel_change_date(callback_query: types.CallbackQuery, state: FSMContext):
    await state.finish()
    await bot.send_message(callback_query.from_user.id, "Ввод даты отменен.")

# Обработчик отмены для выбора времени
@dp.callback_query_handler(lambda c: c.data == "cancel_change_time", state=Form.change_delivery_date_time_from)
async def cancel_change_time(callback_query: types.CallbackQuery, state: FSMContext):
    await state.reset_state(with_data=False) # or state.finish()
    await bot.send_message(callback_query.from_user.id, "Ввод времени отменен.")

# Обработчик отмены для комментария
@dp.callback_query_handler(lambda c: c.data == 'cancel', state=Form.change_delivery_date_comment)
async def cancel_comment(callback_query: types.CallbackQuery, state: FSMContext):
    await state.finish()
    await bot.send_message(callback_query.from_user.id, "Ввод комментария отменен.")





#Функция запроса к API
async def send_delivery_date_change_request(message: types.Message, state: FSMContext, date, time_from, time_to, comment, user_id):
    import requests
    import json
    from info import get_token

    token = get_token(user_id)
    print(token)

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}',
    }

    connection = sqlite3.connect('users.db')
    cursor = connection.cursor()

    cursor.execute('SELECT order_info FROM new_orders WHERE user_id = ? ORDER BY id DESC LIMIT 1', (message.from_user.id,))
    order_info = cursor.fetchone()
    print(order_info)
    if order_info:
        order_info_str = order_info[0]
        try:
            order_info_dict = ast.literal_eval(order_info_str)
            order_uuid = order_info_dict['entity']['uuid']

            url = 'https://api.cdek.ru/v2/delivery' #Замените на актуальный URL API

            payload = json.dumps({
                "order_uuid": order_uuid,
                "date": date,
                "time_from": time_from,
                "time_to": time_to,
                "comment": comment
            })

            try:
                response = requests.post(url, headers=headers, data=payload)
                response.raise_for_status()  # Raises HTTPError for bad responses (4xx or 5xx)
                data = response.json()

                # Получаем request_uuid
                request_uuid = data['requests'][0]['request_uuid']
                from aiogram.utils.markdown import text, bold, italic, link  # Импортируем функции для форматирования

                # Формируем красивое сообщение
                success_message = text(
                    bold("✅ Дата доставки успешно изменена!"),
                    "",  # Пустая строка для разделения
                    bold("Новая дата:"), date,
                    bold("Время доставки:"), f"{time_from} - {time_to}",
                    bold("Комментарий:"), comment,
                    bold("UUID запроса:"), request_uuid,  # Добавляем UUID запроса
                    sep="\n"  # Разделитель строк
                )

                await message.answer(success_message, parse_mode="Markdown")  # Отправляем сообщение с Markdown
                logging.info(f"Успешный ответ от API: {data}")

            except requests.exceptions.HTTPError as e:
                # Обработка ошибок HTTP
                await message.answer(f"Произошла ошибка при запросе к API: {e}")
            except requests.exceptions.RequestException as e:
                # Обработка других ошибок, связанных с запросом
                await message.answer(f"Произошла ошибка при выполнении запроса: {e}")

        except (ValueError, SyntaxError) as e:
            print(f"Не удалось оценить order_info_str как словарь: {e}")
            await message.answer(f"Произошла ошибка при обработке информации о заказе. Пожалуйста, попробуйте позже.")

        finally:
            connection.close()
    else:
        await message.answer("Для пользователя не найдено order_info")
    await state.finish()



























@dp.message_handler(commands='docs')
async def process_doc(callback_query: types.CallbackQuery):
    text = '''Команды Telegram бота для работы с API СДЭК:

/nomer
Получение информации по номеру заказа СДЭК.
Использует метод API: GET /orders
Пользователь должен ввести номер заказа после команды.
Бот возвращает текущий статус заказа, информацию о получателе, стоимость доставки и другие детали.

/im
Получение информации по номеру заказа интернет-магазина (ИМ).
Использует метод API: GET /orders
Пользователь должен ввести номер заказа ИМ после команды.
Бот возвращает информацию о заказе, связанную с данным номером ИМ.

/sklad_dver (ранее /zaborgruz)
Создание заказа по схеме "Склад-дверь".
Использует метод API: POST /orders
Бот запрашивает у пользователя необходимую информацию для создания заказа (адрес получателя, вес, габариты и т.д.).
После получения всех данных, создается заказ на доставку со склада СДЭК до двери получателя.

/zaborgruza
Заказ забора груза.
Использует метод API: POST /intakes
Бот запрашивает информацию о месте и времени забора груза, контактные данные отправителя.
Создается заявка на забор груза курьером СДЭК.

/doc
Получение документов (функционал в разработке).
В будущем может использовать методы API для получения различных документов (накладные, акты и т.д.).

/faq
Предоставление информации о сервисе.
Не требует обращения к API.
Выводит часто задаваемые вопросы и ответы на них.

/lists
Получение списков регионов, офисов, населенных пунктов.
Использует методы API: GET /location/regions, GET /deliverypoints, GET /location/cities
Позволяет пользователю запросить список регионов, офисов СДЭК или населенных пунктов.

/dan_zakaz
Добавление шаблона для забора груза.
Может использовать метод API: POST /intakes для сохранения шаблона
Бот запрашивает и сохраняет информацию о типичном заборе груза для быстрого создания заявок в будущем.

/zabor_konsalid
Забор консолидированного груза.
Использует метод API: POST /intakes с специфическими параметрами
Бот запрашивает информацию о нескольких грузах, которые нужно забрать одновременно.

/info_delivery_problem
Информация о проблеме доставки.
Использует метод API: GET /orders/{order_uuid}/statuses
Пользователь вводит номер проблемного заказа, бот возвращает детальную информацию о статусе и возможных проблемах.

/human_chat
Запрос на общение с поддержкой.
Не требует обращения к API СДЭК.
Ставит пользователя в очередь на общение с оператором поддержки.

/end_chat
Закрытие чата с поддержкой.
Не требует обращения к API СДЭК.
Завершает сессию общения с оператором поддержки.

/ypakovka
Заказ упаковки СДЭК.
Может использовать метод API: POST /orders с специфическими параметрами для заказа упаковки
Бот показывает доступные виды упаковки и позволяет пользователю заказать необходимую.'''
    await bot.send_message(callback_query.from_user.id, text)









@dp.message_handler(lambda message: message.text == '/del')
async def process_zamena(message: types.Message):
    print("Обработчик команды del вызван.")
    user = await check_user(message.from_user.id)
    if user:
        cursor.execute("DELETE FROM users WHERE id=?", (user[0],))
        conn.commit()
        await message.answer("Вы вышли из аккаунта.")

    else:
        await message.answer("Вы не зарегистрированы.")


@dp.message_handler(Text(equals='/podderzhka'))
async def podderzhka(message: types.Message):
    support_links = {
        "Whatsapp": "https://api.whatsapp.com/send?phone=74993506695&text=%D0%9F%D0%BE%D0%B6%D0%B0%D0%BB%D1%83%D0%B9%D1%81%D1%82%D0%B0,%20%D0%BE%D1%82%D0%BF%D1%80%D0%B0%D0%B2%D1%8C%D1%82%D0%B5%20%D1%8D%D1%82%D0%BE%20%D1%81%D0%BE%D0%BE%D0%B1%D1%89%D0%B5%D0%BD%D0%B8%D0%B5%20%D0%B8%D0%B7%20%D0%BF%D1%80%D0%B8%D0%BB%D0%BE%D0%B6%D0%B5%D0%BD%D0%B8%D1%8F%20WhatsApp%20%F0%9F%93%B2%20gR8EtNy5ngX281wJU8Msr",
        "Телеграм": "https://t.me/edostavkabot?start=ZlhWWMLFNSpGbGQm4CrIZ",
        "ВКонтакте": "https://vk.com/write-142153191?ref=gJOzB7aTuWdPgbfA8rQHZ",
        "Вайбер": "https://invite.viber.com/?g2=AQASBGNDxA4MbEyOd1G4WZ7oQDqr6Svy5w6hCG4ZV2MbLE7u70HHy8ilo7yV4uRz&lang=ru"
    }

    response = "Наши каналы поддержки:\n\n" + "\n".join(
        [f"{platform}: {link}" for platform, link in support_links.items()])

    await message.answer(response)


@dp.message_handler(lambda message: message.text == '/ypakovka')
async def ypakovka(message: types.Message):

    await message.answer("Функция в разработке")

if __name__ == '__main__':
    import asyncio
    from aiogram import executor
    from aiohttp import web

    app = web.Application()
    app.router.add_post('/webapp-data', web_app_data_handler)

    loop = asyncio.get_event_loop()
    # loop.create_task(web._run_app(app, host='localhost', port=8080))

    executor.start_polling(dp, skip_updates=True)


# start - ВХОД В ЛИЧНЫЙ КАБИНЕТ
# nomer - ВВЕДИТЕ НОМЕР ЗАКАЗА (НАКЛАДНОЙ)
# im - ВВЕДИТЕ НОМЕР ЗАКАЗА ИНТЕРНЕТ-МАГАЗИНА (ИМ)
# dan_zakaz - СОЗДАНИЕ ШАБЛОНА УСЛУГИ "ЗАБОР ГРУЗА"
# zabor_konsalid - ЗАБОР КОНСОЛИДИРОВАННОГО ГРУЗА
# ypakovka - МАГАЗИН УПАКОВКИ
# human_chat - ОБЩЕНИЕ С ПОДДЕРЖКОЙ
# end_chat - ЗАКРЫТЬ ЧАТ С ПОДДЕРЖКОЙ
# docs - ИНСТРУКЦИЯ ПО ЧАТ-БОТУ
# lists - СПИСКИ ОФИСОВ
# info_delivery_problem - информация о проблеме доставки
# faq - FAQ
# del - Выйти из аккаунта