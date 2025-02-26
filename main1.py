import ast
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor
import sqlite3
from datetime import datetime, timedelta
import os

# Initialize bot and dispatcher
bot = Bot(token="7020285176:AAEr9NQt7m3pljwWAMfYANb1EjdMeQKmgVQ")
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
dp.middleware.setup(LoggingMiddleware())

# Database setup
conn = sqlite3.connect('users.db')
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS users
                  (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, username TEXT, password TEXT)''')
cursor.execute('''CREATE TABLE IF NOT EXISTS new_orders
                  (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, cdek_number TEXT, order_info TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')

# Define states
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
        await message.answer(f"Привет, {user[2]}! Вы уже зарегистрированы.")
    else:
        await message.answer("Вы не зарегистрированы. Пожалуйста, введите ваш логин.")
        await Form.login.set()

@dp.message_handler(state=Form.login)
async def process_login(message: types.Message, state: FSMContext):
    await state.update_data(login=message.text)
    await message.answer("Теперь введите ваш пароль.")
    await Form.password.set()

@dp.message_handler(state=Form.password)
async def process_password(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    login = user_data['login']
    password = message.text

    cursor.execute("INSERT INTO users (user_id, username, password) VALUES (?, ?, ?)",
                   (message.from_user.id, login, password))
    conn.commit()

    await message.answer(f"Вы успешно зарегистрированы как {login}!")
    await state.finish()

@dp.message_handler(commands='nomer')
async def cmd_nomer(message: types.Message):
    await Form.order_number.set()
    await message.answer("Пожалуйста, введите номер заказа (накладной):")

async def process_order_info(message: types.Message, state: FSMContext, order_number):
    current_time = datetime.now()
    user_id = message.from_user.id

    # Check if user has entered data within the last 15 minutes
    cursor.execute("SELECT * FROM new_orders WHERE user_id = ? AND created_at > ?", (user_id, current_time - timedelta(minutes=15)))
    recent_order = cursor.fetchone()

    if recent_order:
        order_info = recent_order[2]
    else:
        # Simulate order info retrieval
        order_info = f"Информация о заказе {order_number}"
        cursor.execute("INSERT INTO new_orders (user_id, cdek_number, order_info) VALUES (?, ?, ?)",
                       (user_id, order_number, order_info))
        conn.commit()

    # Creating inline keyboard for options
    inline_keyboard = InlineKeyboardMarkup(row_width=2)
    buttons = [
        ("Отследить посылку 📦", "track_parcel"),
        ("Данные по посылке 📝", "parcel_data"),
        ("Внести изменения в заказ (накладную) 📝", "change_order"),
        ("Отменить доставку ❌", "cancel_delivery"),
        ("Изменить дату доставки 📆", "change_delivery_date"),
        ("Редактировать сумму наложенного платежа 💸", "edit_cod_amount"),
        ("Продлить хранение ⏰", "extend_storage")
    ]
    for button_text, callback_data in buttons:
        inline_keyboard.add(InlineKeyboardButton(button_text, callback_data=callback_data))

    await message.answer("Вы находитесь в меню по работе в накладной. Выберите действие:", reply_markup=inline_keyboard)
    await state.finish()

@dp.message_handler(state=Form.order_number)
async def process_order_number(message: types.Message, state: FSMContext):
    order_number = message.text
    await process_order_info(message, state, order_number)

@dp.callback_query_handler(lambda c: c.data)
async def process_callback(callback_query: types.CallbackQuery):
    connection = sqlite3.connect('users.db')
    cursor = connection.cursor()

    if callback_query.data == 'track_parcel':
        cursor.execute("SELECT order_info FROM new_orders WHERE user_id = ? ORDER BY id DESC LIMIT 1", (callback_query.from_user.id,))
        order_info = cursor.fetchone()

        if order_info:
            order_info_str = order_info[0]
            try:
                order_info_dict = ast.literal_eval(order_info_str)
                if 'entity' in order_info_dict and 'statuses' in order_info_dict['entity']:
                    statuses = order_info_dict['entity']['statuses']
                    statuses_reversed = [f"{status['name']} в {status['city']} {status['date_time']}" for status in reversed(statuses)]
                    status_text = "\n".join(statuses_reversed)
                    await bot.send_message(callback_query.from_user.id, status_text)
                else:
                    await bot.send_message(callback_query.from_user.id, "No status information available.")
            except (ValueError, SyntaxError) as e:
                await bot.send_message(callback_query.from_user.id, "Error decoding order information. Please try again later.")
                print(f"Error: {e}")
        else:
            await bot.send_message(callback_query.from_user.id, "No order information found.")

    elif callback_query.data == 'parcel_data':
        cursor.execute("SELECT order_info FROM new_orders WHERE user_id = ? ORDER BY id DESC LIMIT 1", (callback_query.from_user.id,))
        order_info = cursor.fetchone()
        if order_info:
            order_info_str = order_info[0]
            try:
                order_info_dict = ast.literal_eval(order_info_str)
                if 'entity' in order_info_dict:
                    entity_info = order_info_dict['entity']
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
                    keyboard = InlineKeyboardMarkup().add(
                        InlineKeyboardButton("Телефон офиса ответственного за вручение посылки", callback_data='delivery_office_phone'),
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
        cursor.execute("SELECT order_info FROM new_orders WHERE user_id = ? ORDER BY id DESC LIMIT 1", (callback_query.from_user.id,))
        order_info = cursor.fetchone()
        if order_info:
            order_info_str = order_info[0]
            try:
                order_info_dict = ast.literal_eval(order_info_str)
                if 'entity' in order_info_dict:
                    entity_info = order_info_dict['entity']
                    delivery_point_code = entity_info.get('delivery_point')
                    if delivery_point_code:
                        from Delivery_Arrangement_Information import deliverypoints, format_deliverypoint_info
                        response = deliverypoints(delivery_point_code)
                        if response:
                            formatted_info = format_deliverypoint_info(response[0])
                            await callback_query.message.answer(f"Обратитесь к закрепленному менеджеру:\n\n{formatted_info}")
                        else:
                            await callback_query.message.answer("Информация о пункте выдачи не найдена.")
                    else:
                        await callback_query.message.answer("Код пункта выдачи не найден в данных заказа.")
            except (SyntaxError, ValueError) as e:
                print(f"Error parsing order info: {e}")
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
        await bot.send_message(callback_query.from_user.id, "Выберите что хотите изменить", reply_markup=keyboard_markup)

    elif callback_query.data == 'change_address':
        keyboard_markup = types.InlineKeyboardMarkup(row_width=1)
        buttons = [
            types.InlineKeyboardButton(text="Изменить адрес получателя", callback_data='address'),
            types.InlineKeyboardButton(text="Изменить ПВЗ в городе получателе", callback_data='change_pickup_point'),
            types.InlineKeyboardButton(text="Изменить город получателя", callback_data='change_city')
        ]
        keyboard_markup.add(*buttons)
        await bot.send_message(callback_query.from_user.id, "Выберите что хотите изменить", reply_markup=keyboard_markup)

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
        await bot.send_message(callback_query.from_user.id, "Выберите что хотите изменить", reply_markup=keyboard_markup)

    elif callback_query.data == 'otmena_vcex_plat':
        from izmeneniya import nalozh_pay_otmena_vse
        cursor.execute('SELECT order_info FROM new_orders WHERE user_id = ?', (callback_query.from_user.id,))
        order_info = cursor.fetchone()
        if order_info:
            order_info_str = order_info[0]
            order_info_dict = ast.literal_eval(order_info_str)
            uuid = order_info_dict['entity']['uuid']
            nalozh_pay_otmena = nalozh_pay_otmena_vse(uuid)
            await callback_query.message.answer(f"Отменены все наложенные платежи:\n\n{nalozh_pay_otmena}")

    elif callback_query.data == 'extend_storage':
        cursor.execute("SELECT order_info FROM new_orders WHERE user_id = ? ORDER BY id DESC LIMIT 1", (callback_query.from_user.id,))
        order_info = cursor.fetchone()
        if order_info:
            order_info_str = order_info[0]
            try:
                order_info_dict = ast.literal_eval(order_info_str)
                if 'entity' in order_info_dict:
                    entity_info = order_info_dict['entity']
                    delivery_point_code = entity_info.get('delivery_point')
                    if delivery_point_code:
                        from Delivery_Arrangement_Information import deliverypoints, format_deliverypoint_info
                        response = deliverypoints(delivery_point_code)
                        if response:
                            formatted_info = format_deliverypoint_info(response[0])
                            await callback_query.message.answer(f"Обратитесь к закрепленному менеджеру:\n\n{formatted_info}")
                        else:
                            await callback_query.message.answer("Информация о пункте выдачи не найдена.")
                    else:
                        await callback_query.message.answer("Код пункта выдачи не найден в данных заказа.")
            except (SyntaxError, ValueError) as e:
                print(f"Error parsing order info: {e}")
                await callback_query.message.answer("Ошибка обработки данных заказа.")
        else:
            await callback_query.message.answer("Информация о заказе не найдена.")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
