# aiogram   2.23.1
import sqlite3
import os
import json
from datetime import timedelta, datetime

import requests
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.types import ParseMode, ReplyKeyboardMarkup, KeyboardButton, InputMediaPhoto, WebAppInfo
from aiogram.utils import executor
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import tempfile

from token_generator import get_token

# 10006324754 склад-дверь
# 10007168378 до пвз

# Initialize bot and dispatcher
bot = Bot(token="7020285176:AAEr9NQt7m3pljwWAMfYANb1EjdMeQKmgVQ")
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
dp.middleware.setup(LoggingMiddleware())

# Database setup

conn = sqlite3.connect('users.db')
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS new_orders
                  (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, cdek_number TEXT, order_info TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')

# cursor.execute('''INSERT INTO new_orders (id, user_id, cdek_number, order_info)
#                   SELECT id, user_id, cdek_number, order_info FROM orders''')
#
# cursor.execute('''DROP TABLE orders''')
#
# cursor.execute('''ALTER TABLE new_orders RENAME TO orders''')

# Keyboard markup
keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
keyboard.add(KeyboardButton('📋 Основное меню'))
keyboard.add(KeyboardButton('ℹ️ Информация'))
# keyboard.add(KeyboardButton('🛒 Меню заказа'))
keyboard.add(KeyboardButton('🗑️ Удалить аккаунт'))
def get_main_keyboard():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    keyboard.add(KeyboardButton('📋 Основное меню'))
    keyboard.add(KeyboardButton('ℹ️ Информация'))
    # keyboard.add(KeyboardButton('🛒 Меню заказа'))
    keyboard.add(KeyboardButton('🗑️ Удалить аккаунт'))
    return keyboard
@dp.message_handler(lambda message: message.text == '🛒 Меню заказа')
async def handle_get_order_info(message: types.Message, state: FSMContext):
    user = await check_user(message.from_user.id)

    if user:
        await process_order_number(message, state)
    else:
        await message.answer(
            "Для доступа к информации о заказе необходима регистрация. Введите /start для начала регистрации.")


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


async def check_user(user_id):
    cursor.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    return cursor.fetchone()


@dp.message_handler(commands='start')
async def cmd_start(message: types.Message):
    user = await check_user(message.from_user.id)
    if user:
        await message.answer(f"Привет, {user[2]}! Вы уже зарегистрированы.", reply_markup=keyboard)
    else:
        await message.answer("Вы не зарегистрированы. Пожалуйста, введите ваш логин. Логиин и пароль ван необходимо получить в личном кабинете, как это сделать вы можете узнать нажав на кнопку info.", reply_markup=keyboard)
        await Form.login.set()


@dp.message_handler(lambda message: message.text =='📋 Основное меню')
async def cmd_start1(message: types.Message, state: FSMContext):
    user = await check_user(message.from_user.id)

    if user:
        # Зарегистрированный пользователь
        keyboard = InlineKeyboardMarkup()
        # keyboard.row(InlineKeyboardButton("Внесение изменений в заказ", callback_data='change_order'))
        # keyboard.row(InlineKeyboardButton("Отследить заказ", callback_data='track_order'))
        keyboard.row(InlineKeyboardButton("Номер заказа (накладной) 📝", callback_data='enter_waybill'))
        keyboard.row(InlineKeyboardButton("Номер заказа Интернет-магазина 🛍️", callback_data='enter_webshop_order'))
        # keyboard.row(InlineKeyboardButton("Рассчитать стоимость 💸", callback_data='calculate_cost'))
        keyboard.row(InlineKeyboardButton("Что необходимо для получения посылки 📦",
                                          web_app=WebAppInfo(url='https://mobile.cdek.ru/packageto')))
        keyboard.row(InlineKeyboardButton("Заказать курьера (Забор груза) 🚪", callback_data='order_courier'))
        keyboard.row(
            InlineKeyboardButton("Списки регионов/офисов/населенных пунктов 📍", callback_data='list_regions_offices'))
        keyboard.row(InlineKeyboardButton("Продублировать накладную если у вас склад-дверь 📝",
                                          callback_data='duplicate_waybill'))

        await message.answer("Ваше меню для юридических лиц:", reply_markup=keyboard)
    else:
        await message.answer("Для доступа к функционалу необходима регистрация. Введите /start для начала регистрации.")


@dp.message_handler(state=Form.login)
async def process_login(message: types.Message, state: FSMContext):
    await state.update_data(login=message.text)
    await message.answer("Теперь введите ваш пароль.")
    await Form.password.set()

@dp.message_handler(lambda message: message.text == '🗑️ Удалить аккаунт')
async def process_zamena(message: types.Message):
    print("Обработчик команды del вызван.")
    user = await check_user(message.from_user.id)
    if user:
        cursor.execute("DELETE FROM users WHERE id=?", (user[0],))
        conn.commit()
        await message.answer("Ваши данные удалены из базы данных. Пожалуйста, введите ваш логин.", reply_markup=keyboard)
        await Form.login.set()
    else:
        await message.answer("Вы не зарегистрированы. Пожалуйста, введите ваш логин для регистрации.", reply_markup=keyboard)
        await Form.login.set()

@dp.message_handler(state=Form.password)
async def process_password(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    login = user_data['login']
    password = message.text

    cursor.execute("INSERT INTO users (user_id, username, password) VALUES (?, ?, ?)",
                   (message.from_user.id, login, password))
    conn.commit()

    await message.answer(f"Вы успешно зарегистрированы как {login}!", reply_markup=keyboard)
    await state.finish()

@dp.message_handler(lambda message: message.text == 'ℹ️ Информация')
async def process_zamena(message: types.Message):
    # Paths to images in your project directory
    image1_path = os.path.join(os.getcwd(), 'a.jpg')
    image2_path = os.path.join(os.getcwd(), 'b.jpg')
    # Sending two images and text
    with open(image1_path, 'rb') as image1, open(image2_path, 'rb') as image2:
        media = [
            InputMediaPhoto(media=image1, caption="Первое изображение: Для получения логина и пароля вам необходимо выполнить действия, которые показаны в скриншотах."),
            InputMediaPhoto(media=image2)
        ]
        await message.answer_media_group(media)


# здесь был код из proces.py


async def process_callback_query(callback_query: types.CallbackQuery, message: str, state):
    await bot.send_message(callback_query.from_user.id, message)
    await state.set()

# Словарь для сопоставления callback_data с сообщениями и состояниями форм
callback_data_mapping = {
    'enter_waybill': ("Пожалуйста, введите номер заказа (накладной):", Form.order_number),
    'enter_webshop_order': ("Пожалуйста, введите номер заказа:", Form.order_number2),
    'list_offices': ("Пожалуйста, введите название города:", Form.order_number3),
    'change_fullname': ("Пожалуйста, введите ФИО:", Form.fio),
    'change_phone': ("Пожалуйста, введите номер телефона:", Form.tel),
    'address': ("Пожалуйста, введите адрес:", Form.adr),
    'change_city': ("Пожалуйста, введите город через пробел адрес (Москва проспект московский строение 20):", Form.cit),
    'change_pickup_point': ("Пожалуйста, введите адрес:", Form.pwz),
    'izmenit_za_tovar': ("Пожалуйста, введите через пробел Новая сумма наложенного платежа, Сумма НДС, Ставка НДС:", Form.inpzt),
    'izmenit_za_dop': (
    "Пожалуйста, введите через пробел Порог стоимости товара, Сумма дополнительного сбора, Сумма НДС, Ставка НДС:", Form.inpzt),
    'duplicate_waybill': (
        "Пожалуйста, введите номер накладной CDEK",
        Form.dubl),
    'Заказать курьера': (
        "Пожалуйста, введите номер накладной CDEK, дату, время начала, время окончания и адрес. Через пробел 10006324754 2024-07-10 10:00 15:00 ул. Ленина, д. 1",
        Form.kurier),
}

# Обработчик callback_query с использованием общей функции и словаря
@dp.callback_query_handler(lambda c: c.data in callback_data_mapping)
async def process_any_callback_query(callback_query: types.CallbackQuery):
    data = callback_data_mapping[callback_query.data]
    await process_callback_query(callback_query, data[0], data[1])




# здесь был код из obrabotka.py

# Функция для обработки ввода информации о заказе
async def process_order_info(message: types.Message, state: FSMContext, info_function, inline_buttons_data):
    order_number = message.text
    current_time = datetime.now()
    user_id = message.from_user.id

    # Check if user has entered data within the last 15 minutes
    cursor.execute("SELECT * FROM new_orders WHERE user_id = ? AND created_at > ?", (user_id, current_time - timedelta(minutes=15)))
    recent_order = cursor.fetchone()
#new_orders
    if recent_order:
        # Use the recent order info
        order_info = recent_order[2]
    else:
        # Get new order info
        order_info = info_function(order_number)

    if order_info:
        order_info_str = str(order_info)
        cursor.execute("INSERT INTO new_orders (user_id, cdek_number, order_info) VALUES (?, ?, ?)",
                       (message.from_user.id, order_number, order_info_str))
        conn.commit()
        # await message.answer("Вы находитесь в меню по работе в накладной.")

        # Создание меню с опциями
        inline_keyboard = InlineKeyboardMarkup(row_width=2)
        for button_text, callback_data in inline_buttons_data:
            inline_keyboard.add(InlineKeyboardButton(button_text, callback_data=callback_data))

        await message.answer("Вы находитесь в меню по работе в накладной. Выберите действие:", reply_markup=inline_keyboard)
    else:
        await message.answer("Не удалось получить информацию о заказе. Пожалуйста, проверьте номер заказа и попробуйте снова.")
    await state.finish()

# Обработчики сообщений
@dp.message_handler(state=Form.order_number)
async def process_order_number(message: types.Message, state: FSMContext):
    from info import info
    await process_order_info(message, state, info, [
        ("Отследить посылку 📦", "track_parcel"),
        ("Данные по посылке 📝", "parcel_data"),
        ("Внести изменения в заказ (накладную) 📝", "change_order"),
        ("Отменить доставку ❌", "cancel_delivery"),
        ("Изменить дату доставки 📆", "change_delivery_date"),
        ("Редактировать сумму наложенного платежа 💸", "edit_cod_amount"),
        ("Продлить хранение ⏰", "extend_storage")
        # ("Вернуться назад 🔙", "go_back")
    ])

@dp.message_handler(state=Form.order_number2)
async def process_order_number2(message: types.Message, state: FSMContext):
    from info import info2
    await process_order_info(message, state, info2, [
        ("Отследить посылку 📦", "track_parcel"),
        ("Данные по посылке 📝", "parcel_data"),
        ("Внести изменения в заказ (накладную) 📝", "change_order"),
        ("Отменить доставку ❌", "cancel_delivery"),
        ("Изменить дату доставки 📆", "change_delivery_date"),
        ("Редактировать сумму наложенного платежа 💸", "edit_cod_amount"),
        ("Продлить хранение ⏰", "extend_storage")
        # ("Вернуться назад 🔙", "go_back")
    ])


from aiogram import types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, WebAppInfo
from aiogram.dispatcher.filters import Text


@dp.callback_query_handler(lambda c: c.data == 'cancel_delivery')
async def otmena_zakaza(callback_query: types.CallbackQuery):
    from otmena_zakaz import otmena

    connection = sqlite3.connect('users.db')
    cursor = connection.cursor()

    cursor.execute('SELECT order_info FROM new_orders WHERE user_id = ?', (callback_query.from_user.id,))
    order_info = cursor.fetchone()
    order_info_str = order_info[0]

    order_info_dict = ast.literal_eval(order_info_str)
    uuid = order_info_dict['entity']["statuses"][0]['code']
    if uuid == "CREATED":
        await callback_query.message.answer(f"Ваш заказ в статусе CREATED и пока не может быть отменен")
    else:
        uuid = order_info_dict['entity']['uuid']
        otmen = otmena(uuid)
        if 'status' in otmen and otmen['status'] != 202:
            print(otmen)
            await callback_query.message.answer(f"Ошибка: {otmen['error']}")
        else:
            print(otmen)
            await callback_query.message.answer(f"Ваш заказ отменен {otmen}")


@dp.callback_query_handler(lambda c: c.data == 'order_courier')
async def zakaz(callback_query: types.CallbackQuery):
    # URL вашего мини-приложения
    web_app_url = 'https://cdek01.github.io/cdekhtml.github.io/'

    # Создаем кнопку для открытия мини-приложения
    web_app_button = InlineKeyboardButton(text='Открыть заказ', web_app=WebAppInfo(url=web_app_url))
    close_button = InlineKeyboardButton(text='Закрыть', callback_data='close_web_app')

    # Создаем клавиатуру с двумя кнопками
    keyboard = InlineKeyboardMarkup().add(web_app_button).add(close_button)

    # Отправляем сообщение с кнопкой пользователю
    await callback_query.message.answer("Пожалуйста, оформите заказ через мини-приложение:", reply_markup=keyboard)

# @dp.callback_query_handler(Text(equals='close_web_app'))
# async def close_web_app(callback_query: types.CallbackQuery):
#     # Удаляем сообщение с кнопками
#     await callback_query.message.delete()
#     await callback_query.answer("Мини-приложение закрыто")
@dp.callback_query_handler(lambda c: c.data == 'close_web_app')
async def close_web_app(callback_query: types.CallbackQuery):
    # Удаляем клавиатуру и отправляем сообщение о закрытии
    await callback_query.message.edit_reply_markup(reply_markup=None)
    await callback_query.message.answer("Мини-приложение закрыто. Если у вас есть еще вопросы, пожалуйста, дайте знать.")



@dp.message_handler(content_types=['web_app_data'])
async def web_app(message: types.Message):
    # Получение данных от мини-приложения
    web_app_data = message.web_app_data.data

    # Возвращение данных пользователю
    await message.answer(f"Вы ввели следующие данные: {web_app_data}")
    # Убираем кнопку после нажатия, отправив сообщение с пустой клавиатурой
    await message.answer("Кнопка убрана", reply_markup=get_main_keyboard())
    # Вызываем функцию process_web_app_data для создания заказа
    await process_web_app_data(web_app_data, message)

async def process_web_app_data(data, message):
    from zakaz import zakaz1
    # Парсим данные из JSON строки в Python объект
    parsed_data = json.loads(data)

    # Извлечение переменных из распарсенных данных
    type_ = parsed_data.get('type')
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
    item_names = parsed_data.get('item_name[]', [])
    ware_keys = parsed_data.get('ware_key[]', [])
    payment_values = parsed_data.get('payment_value[]', [])
    vat_sums = parsed_data.get('vat_sum[]', [])
    vat_rates = parsed_data.get('vat_rate[]', [])
    costs = parsed_data.get('cost[]', [])
    item_weights = parsed_data.get('item_weight[]', [])
    amounts = parsed_data.get('amount[]', [])
    items = parsed_data.get('items', [])
    zak = zakaz1(
        type_, tariff_code, from_city, from_address, to_city, to_address,
        recipient_name, recipient_phone, sender_name, sender_company,
        sender_phone, package_number, package_weight, package_length,
        package_width, package_height, package_comment, item_names,
        ware_keys, payment_values, vat_sums, vat_rates, costs, item_weights,
        amounts, items
    )
    if zak == "Заказ успешно создан":


        # Отправляем сообщение с кнопкой
        await message.answer("Заказ успешно создан. Пожалуйста, введите номер накладной CDEK, дату, время начала, время окончания и адрес. Через пробел 10006324754 2024-07-10 10:00 15:00 ул. Ленина, д. 1")
        await Form.kurier.set()
    else:
        await message.answer("Повторите попытку", str(zak))


@dp.message_handler(state=Form.kurier)
async def process_kurier(message: types.Message, state: FSMContext):
    data = message.text.split()
    nomer = data[0]
    date = data[1]
    time_begin = data[2]
    time_end = data[3]
    address = data[4]
    from dublikat_zayavki import create_call_request_kurier
    # kurier = create_call_request_kurier(nomer, date, time_begin, time_end, address)
    status_code, response_data = create_call_request_kurier(nomer, date, time_begin, time_end, address)

    if status_code == 202:
        await message.answer(f'Запрос на доставку успешно создан!')
    else:
        await message.answer(
            f'Ошибка при создании запроса на доставку. Код ошибки: {status_code}, Ответ сервера: {response_data}')

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
async def go_back_menu(callback_query: types.CallbackQuery):
    await cmd_start1(callback_query.message)
@dp.message_handler(state=Form.npdc)
async def process_izmenit_za_dop(message: types.Message, state: FSMContext):
    try:
        from izmeneniya import nalozh_pay_dop_cbor
        text = message.text
        threshold, value, vat_sum, vat_rate = text[0], text[1], text[2], text[3]

        connection = sqlite3.connect('users.db')
        cursor = connection.cursor()

        cursor.execute('SELECT order_info FROM new_orders WHERE user_id = ?', (message.from_user.id,))
        order_info = cursor.fetchone()
        order_info_str = order_info[0]

        order_info_dict = ast.literal_eval(order_info_str)
        uuid = order_info_dict['entity']['uuid']
        result = nalozh_pay_dop_cbor(uuid, threshold, value, vat_sum, vat_rate)
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
@dp.message_handler(state=Form.inpzt)
async def process_izmenit_za_tovar(message: types.Message, state: FSMContext):
    try:
        from izmeneniya import nalozh_pay
        text = message.text
        value, vat_sum, vat_rate = text[0], text[1], text[2]

        connection = sqlite3.connect('users.db')
        cursor = connection.cursor()

        cursor.execute('SELECT order_info FROM new_orders WHERE user_id = ?', (message.from_user.id,))
        order_info = cursor.fetchone()
        order_info_str = order_info[0]

        order_info_dict = ast.literal_eval(order_info_str)
        uuid = order_info_dict['entity']['uuid']
        result = nalozh_pay(uuid, value, vat_sum, vat_rate)
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
    entered_text = message.text
    connection = sqlite3.connect('users.db')
    cursor = connection.cursor()

    cursor.execute('SELECT order_info FROM new_orders WHERE user_id = ?', (message.from_user.id,))
    order_info = cursor.fetchone()

    if order_info:
        order_info_str = order_info[0]
        try:
            order_info_dict = ast.literal_eval(order_info_str)
            uuid = order_info_dict['entity']['uuid']
            result = info_function(uuid, entered_text)
            await bot.send_message(message.from_user.id, result)

        except (ValueError, SyntaxError) as e:
            print(f"Failed to evaluate order_info_str as dictionary: {e}")
    else:
        print("No order_info found for the user")

    connection.close()
    await state.finish()

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
    await process_entering_info(message, state, adres)

@dp.message_handler(state=Form.cit)
async def process_entering_cit(message: types.Message, state: FSMContext):
    entered_text = message.text
    connection = sqlite3.connect('users.db')
    cursor = connection.cursor()

    cursor.execute('SELECT order_info FROM new_orders WHERE user_id = ?', (message.from_user.id,))
    order_info = cursor.fetchone()

    if order_info:
        order_info_str = order_info[0]
        try:
            order_info_dict = ast.literal_eval(order_info_str)
            uuid = order_info_dict['entity']['uuid']
            from izmeneniya import change_city
            address_parts = entered_text.split(' ', 1)
            city = address_parts[0]
            address = "улица " + address_parts[1]

            result = change_city(uuid, city, address)
            await bot.send_message(message.from_user.id, result)

        except (ValueError, SyntaxError) as e:
            print(f"Failed to evaluate order_info_str as dictionary: {e}")
    else:
        print("No order_info found for the user")

    connection.close()
    await state.finish()

@dp.message_handler(state=Form.pwz)
async def process_entering_pwz(message: types.Message, state: FSMContext):
    # from izmeneniya import pwz
    # await process_entering_info(message, state, pwz)
    await message.answer("Извините, этот функционал находится в разработке. Пожалуйста, попробуйте позже.")
    await Form.next()




from aiogram import types
import ast
from aiogram import types

@dp.callback_query_handler(lambda c: c.data)
async def process_callback(callback_query: types.CallbackQuery):

    connection = sqlite3.connect('users.db')
    cursor = connection.cursor()
    if callback_query.data == 'track_parcel':
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
                    statuses_reversed = []
                    for status in reversed(statuses):
                        date_time_str = status['date_time']
                        date_str, time_str = date_time_str.split('T')
                        time_str = time_str[:-5]  # remove the +0000 timezone offset
                        status_str = f"{status['name']} в {status['city']} {date_str} {time_str}"
                        statuses_reversed.append(status_str)
                    status_text = "\n".join(statuses_reversed)
                    await bot.send_message(callback_query.from_user.id, status_text)
                else:
                    await bot.send_message(callback_query.from_user.id, "No status information available.")
            except (ValueError, SyntaxError) as e:
                await bot.send_message(callback_query.from_user.id, "Error decoding order information. Please try again later.")
                print(f"Error: {e}")
        else:
            await bot.send_message(callback_query.from_user.id, "No order information found.")


    elif callback_query.data == 'track_parcel2':
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
        # Fetch order info from the database
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

                    # Format the output
                    entity_text = (
                        f"📦 *Информация об отправлении:*\n"
                        f"🔑 *UUID:* {entity_info.get('uuid', 'N/A')}\n"
                        f"📝 *Номер отправления:* {entity_info.get('cdek_number', 'N/A')}\n"
                        f"💬 *Комментарий:* {entity_info.get('comment', 'N/A')}\n"
                        f"📍 *Пункт доставки:* {entity_info.get('delivery_point', 'N/A')}\n"
                        f"👥 *Отправитель:* {entity_info['sender'].get('company', 'N/A')} - {entity_info['sender'].get('name', 'N/A')}\n"
                        f"👥 *Получатель:* {entity_info['recipient'].get('company', 'N/A')} - {entity_info['recipient'].get('name', 'N/A')}\n"
                        f"🏠 *Адрес отправителя:* {entity_info['from_location'].get('address', 'N/A')}, {entity_info['from_location'].get('city', 'N/A')}\n"
                        f"🏠 *Адрес получателя:* {entity_info['to_location'].get('city', 'N/A')}, {entity_info['to_location'].get('region', 'N/A')}\n"
                    )
                    # Add your code to process and send the entity information
                    keyboard = InlineKeyboardMarkup()
                    keyboard.add(
                        InlineKeyboardButton("Телефон офиса ответственного за вручение посылки",
                                             callback_data='delivery_office_phone'),
                        InlineKeyboardButton("Назад", callback_data='go_back')
                    )
                    await bot.send_message(callback_query.from_user.id, entity_text, reply_markup=keyboard)
                else:
                    await bot.send_message(callback_query.from_user.id, "No entity information found in order data.")
            except (ValueError, SyntaxError) as e:
                await bot.send_message(callback_query.from_user.id, "Error decoding order information. Please try again later.")
                print(f"Error: {e}")
        else:
            await bot.send_message(callback_query.from_user.id, "No order information found.")

    elif callback_query.data == 'parcel_data2':
        # Fetch order info from the database
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

                    # Format the output
                    entity_text = (
                        f"📦 *Информация об отправлении:*\n"
                        f"🔑 *UUID:* {entity_info.get('uuid', 'N/A')}\n"
                        f"📝 *Номер отправления:* {entity_info.get('cdek_number', 'N/A')}\n"
                        f"💬 *Комментарий:* {entity_info.get('comment', 'N/A')}\n"
                        f"📍 *Пункт доставки:* {entity_info.get('delivery_point', 'N/A')}\n"
                        f"👥 *Отправитель:* {entity_info['sender'].get('company', 'N/A')} - {entity_info['sender'].get('name', 'N/A')}\n"
                        f"👥 *Получатель:* {entity_info['recipient'].get('company', 'N/A')} - {entity_info['recipient'].get('name', 'N/A')}\n"
                        f"🏠 *Адрес отправителя:* {entity_info['from_location'].get('address', 'N/A')}, {entity_info['from_location'].get('city', 'N/A')}\n"
                        f"🏠 *Адрес получателя:* {entity_info['to_location'].get('city', 'N/A')}, {entity_info['to_location'].get('region', 'N/A')}\n"
                    )
                    # Add your code to process and send the entity information
                    keyboard = InlineKeyboardMarkup()
                    keyboard.add(
                        InlineKeyboardButton("Телефон офиса ответственного за вручение посылки",
                                             callback_data='delivery_office_phone'),
                        InlineKeyboardButton("Назад", callback_data='go_back')
                    )
                    await bot.send_message(callback_query.from_user.id, entity_text, reply_markup=keyboard)
                else:
                    await bot.send_message(callback_query.from_user.id, "No entity information found in order data.")
            except (ValueError, SyntaxError) as e:
                await bot.send_message(callback_query.from_user.id, "Error decoding order information. Please try again later.")
                print(f"Error: {e}")
        else:
            await bot.send_message(callback_query.from_user.id, "No order information found.")








    elif callback_query.data == 'delivery_office_phone':
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
                            await callback_query.message.answer(
                                f"Обратитесь к закрепленному менеджеру:\n\n{formatted_info}")
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
        keyboard_markup = types.InlineKeyboardMarkup(row_width=1)
        buttons = [
            types.InlineKeyboardButton(text="Изменить ФИО получателя", callback_data='change_fullname'),
            types.InlineKeyboardButton(text="Изменить телефон получателя", callback_data='change_phone'),
            types.InlineKeyboardButton(text="Изменить адрес получателя", callback_data='change_address')
        ]
        keyboard_markup.add(*buttons)
        await bot.send_message(callback_query.from_user.id, "Выберите что хотите изменить",
                               reply_markup=keyboard_markup)
    elif callback_query.data == 'change_address':
        keyboard_markup = types.InlineKeyboardMarkup(row_width=1)
        buttons = [
            types.InlineKeyboardButton(text="Изменить адрес получателя", callback_data='address'),
            types.InlineKeyboardButton(text="Изменить ПВЗ в городе получателе", callback_data='change_pickup_point'),
            types.InlineKeyboardButton(text="Изменить город получателя", callback_data='change_city')
        ]
        keyboard_markup.add(*buttons)
        await bot.send_message(callback_query.from_user.id, "Выберите что хотите изменить",
                               reply_markup=keyboard_markup)

    elif callback_query.data == 'cancel_delivery':
        await bot.send_message(callback_query.from_user.id, "Функция отмены доставки в разработке.")
    elif callback_query.data == 'change_delivery_date':
        await bot.send_message(callback_query.from_user.id, "Функция изменения даты доставки в разработке.")


    elif callback_query.data == 'edit_cod_amount':
        keyboard_markup = types.InlineKeyboardMarkup(row_width=1)
        buttons = [
            types.InlineKeyboardButton(text="Отменить все наложенные платежи", callback_data='otmena_vcex_plat'),
            types.InlineKeyboardButton(text="Изменить наложенный платеж за товар", callback_data='izmenit_za_tovar'),
            types.InlineKeyboardButton(text="Изменить наложенный платеж за доп. сбор", callback_data='izmenit_za_dop')
        ]
        keyboard_markup.add(*buttons)
        await bot.send_message(callback_query.from_user.id, "Выберите что хотите изменить",
                               reply_markup=keyboard_markup)

    elif callback_query.data == 'otmena_vcex_plat':
        from izmeneniya import nalozh_pay_otmena_vse
        cursor.execute('SELECT order_info FROM new_orders WHERE user_id = ?', (callback_query.from_user.id,))
        order_info = cursor.fetchone()

        if order_info:
            order_info_str = order_info[0]

            order_info_dict = ast.literal_eval(order_info_str)
            uuid = order_info_dict['entity']['uuid']
            nalozh_pay_otmena = nalozh_pay_otmena_vse(uuid)
            await callback_query.message.answer(
                f"Отменены все наложенные платежи:\n\n{nalozh_pay_otmena}")




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



    elif callback_query.data == 'list_regions_offices':
        # Create a new inline keyboard with three buttons
        inline_keyboard = InlineKeyboardMarkup(row_width=1)
        inline_keyboard.add(
            InlineKeyboardButton("Списки регионов", callback_data='list_regions'),
            InlineKeyboardButton("Списки офисов", callback_data='list_offices'),
            InlineKeyboardButton("Списки населенных пунктов", callback_data='list_settlements')
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


# async def process_order_number(user_id, state):
#     # Add logic to open the cmd_start1 menu
#     await cmd_start1(user_id)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
