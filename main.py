# aiogram   2.23.1
import sqlite3
import os
import json
from datetime import timedelta, datetime
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
from aiogram.utils.markdown import code
from aiogram.utils.exceptions import TelegramAPIError
# 10006324754 склад-дверь
# 10007168378 до пвз
# lYV0wvt14fYGgE7MoWosaIyvOavEqqUm
# 2ABI0GEJN5giKtlgHh2ZZ1rCsz2iWoHZ
# Настройка базового логирования
from token_generator import get_token  # Импортируем функцию get_token



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



@dp.callback_query_handler(lambda c: c.data == 'register_ek5')
async def process_register_ek5(callback_query: types.CallbackQuery):
    await bot.send_message(callback_query.from_user.id, "Сайт для перехода и регистрации в ek5: https://cdek.ru.net/registration/ вы так же можете нажать /faq что бы ознакомиться как пройти регистрацию.")

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
            if response:
                order = response['result']['order']
                pwz = response['result']['updateInfo']['possibleDeliveryMode']
                sender = order['sender']
                receiver = order['receiver']
                sender_name_parts = sender['name'].split()
                sender_initials = ' '.join(
                    [part[0] for part in sender_name_parts if part[0].isalpha()]) + '.' if sender_name_parts else ''

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
                delivery_mode = delivery_modes.get(order['trueDeliveryMode'], "неизвестный тип доставки")

                message_text = (
                    "📦 *Данные о посылке:*\n\n"
                    f"🆔 *Номер заказа:* ` {order['number']} `\n"
                    f"📦 *Количество мест:* {order['packagesCount']}\n"
                    f"📅 *Дата создания:* {order['creationTimestamp'][:10]}\n"
                    f"⚖️ *Расчетный вес:* {order['weight']} кг\n"
                    f"🚛 *Тип доставки:* {delivery_mode}\n\n"

                    "👤 *Отправитель:*\n"
                    f"  *Имя:* {sender_initials}\n"
                    f"  🏙️ *Город:* {sender['address']['city']['name']}\n\n"

                    "📬 *Получатель:*\n"
                    f"  *Инициалы:* {receiver['initials']}\n"
                )

                # Проверка на наличие офиса
                if 'office' in receiver['address']:
                    office = receiver['address']['office']
                    message_text += (
                        f"  🏢 *Адрес {office['type']}:* {receiver['address']['title']}, {receiver['address']['city']['name']}\n"
                        f"  *Офис:* {office['type']}\n"
                        f"  *Комментарий:* {office['comment']}\n"
                        f"  *По вопросам доставки звоните:* {office['phones'][0]['number']}\n\n"
                    )

                    # Добавление графика работы
                    message_text += "📅 *График работы:*\n"
                    for schedule in office['schedule']:
                        days = f"{schedule['startDay'][:3]} - {schedule['endDay'][:3]}" if schedule['startDay'] != \
                                                                                           schedule['endDay'] else \
                        schedule['startDay'][:3]
                        working_hours = f"{schedule['startTime'][:5]} - {schedule['endTime'][:5]}"
                        message_text += f"  • *{days}:* {working_hours}\n"

                message_text += "📊 *Статусы доставки:*\n"

                for status in response['result']['statuses']:
                    city_info = f" {status['currentCity']['name']}" if 'currentCity' in status else ''
                    message_text += f"  🔄 *{status['name']}*{city_info}  {status['timestamp'][:10]}\n"

                message_text += "\n"

                # Проверка на необходимость отображения информации о складе
                if order['trueDeliveryMode'] not in ["1", "3"]:  # Если не двер-дверь и не склад-дверь
                    if 'warehouse' in response['result']:
                        warehouse = response['result']['warehouse']
                        planned_end_date = warehouse.get('acceptance', {}).get('plannedEndDate', 'недоступно')

                        # Проверка наличия данных о хранении
                        if 'storage' in warehouse and 'days' in warehouse['storage']:
                            storage_days =f"{warehouse['storage']['days']} дней"
                        else:
                            storage_days = 'недоступно'  # Указываем по умолчанию, если данные отсутствуют

                        message_text += (
                            f"  📆 *Планируемая дата поступления в пункт выдачи:* {planned_end_date}\n"
                            f"  🗄️ *Хранение:* {storage_days}\n"
                        )
                else:
                    message_text += ""


                def inline_keyboard():
                    keyboard = types.InlineKeyboardMarkup()
                    button = types.InlineKeyboardButton(text="Отследить посылку", callback_data='otsl')
                    keyboard.add(button)
                    return keyboard

                await message.answer(message_text,
                                    reply_markup=inline_keyboard())

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



# Обработчик команды /dan_zakaz
@dp.message_handler(commands=['dan_zakaz'])
async def cmd_dan_zakaz(message: types.Message):
    # Получаем user_id из сообщения
    user_id_to_check = message.from_user.id  # Используем user_id отправителя сообщения

    if check_user_id_exists(user_id_to_check):
        await message.reply(
            "Введите данные через запятую в формате: вес в кг (5), ФИО (Иванов Иван Иванович), комментарий (ввод коментария без запятых), номер телефона (7XXXXXXXXXX), город (Москва), улица (улица космическая 75)")
        await Form.address.set()
    else:
        print(f'Данные для user_id {user_id_to_check} не найдены. ❌')
        await message.answer(f"Данный функционал доступен только договорным клиентам компании СДЭК. Чтобы воспользоваться данным функционалом вам необходимо войти в личный кабинет или заключить договор с группой компании СДЭК. Вы не зарегистрированы. Данные для user_id {user_id_to_check} не найдены. ❌")


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

def get_date_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=1)
    today = datetime.now()
    for i in range(1, 6):  # Next 5 days
        date = today + timedelta(days=i)
        date_str = date.strftime("%Y-%m-%d")
        keyboard.add(InlineKeyboardButton(date_str, callback_data=f"date_{date_str}"))
    return keyboard


def get_time_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=1)
    for hour in range(10, 14):  # From 10 to 13
        time_str = f"{hour:02d}:00"
        keyboard.add(InlineKeyboardButton(time_str, callback_data=f"time_{time_str}"))
    return keyboard


@dp.message_handler(commands=['zabor_konsalid'])
async def zabor_konsalid(message: types.Message):
    user_id_to_check = message.from_user.id
    if check_user_id_exists(user_id_to_check):
        await message.answer("Выберите дату:", reply_markup=get_date_keyboard())
        await Form.date.set()
    else:
        await message.answer(f"Данный функционал доступен только договорным клиентам компании СДЭК. Чтобы воспользоваться данным функционалом вам необходимо войти в личный кабинет или заключить договор с группой компании СДЭК. Вы не зарегистрированы. Данные для user_id {user_id_to_check} не найдены. ❌")


@dp.callback_query_handler(lambda c: c.data.startswith('date_'), state=Form.date)
async def process_date(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    selected_date = callback_query.data.split('_')[1]
    await state.update_data(date=selected_date)
    await bot.send_message(callback_query.from_user.id, "Выберите время начала:", reply_markup=get_time_keyboard())
    await Form.time.set()


@dp.callback_query_handler(lambda c: c.data.startswith('time_'), state=Form.time)
async def process_time(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    selected_time = callback_query.data.split('_')[1]
    data = await state.get_data()
    selected_date = data['date']

    # Assume the duration is 5 hours
    start_time = datetime.strptime(selected_time, "%H:%M")
    end_time = (start_time + timedelta(hours=5)).strftime("%H:%M")

    full_data = f"{selected_date} {selected_time} {end_time}"
    await state.update_data(konsalid=full_data)
    print("------")
    await bot.send_message(
        callback_query.from_user.id,
        f"Вы выбрали следующие данные: {full_data}. Ожидайте, идет обработка данных"
    )
    print("------")
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
    print("------")
    if user_data:
        from dublikat_zayavki import create_call_request_kurier_konsol
        weight, name, comment, phone_number, city, address = user_data
        konsol = create_call_request_kurier_konsol(weight, name, comment, phone_number, city, address, selected_date,
                                                   selected_time, end_time)
        await bot.send_message(callback_query.from_user.id, konsol)
    else:
        await bot.send_message(callback_query.from_user.id, f"Пользователь с ID {user_id} не найден в базе данных. Заполните форму /dan_zakaz и вернитесь в это меню")

    await state.finish()

# @dp.message_handler(Text(equals='/zabor_konsalid'))
# async def zabor_konsalid(message: types.Message):
#         # Получаем user_id из сообщения
#         user_id_to_check = message.from_user.id  # Используем user_id отправителя сообщения
#
#         if check_user_id_exists(user_id_to_check):
#             await message.answer(
#                 "Убедитесь что вы заполнили шаблон /dan_zakaz. Пожалуйста, введите через пробел дату(год-месяц-день), время начала, время конца (2024-07-10 10:00 15:00)",
#                 reply_markup=cancel_keyboard
#             )
#             await Form.konsalid.set()
#         else:
#             print(f'Данные для user_id {user_id_to_check} не найдены. ❌')
#             await message.answer(f"Вы не зарегистрированы. Данные для user_id {user_id_to_check} не найдены. ❌")
#
#
# @dp.callback_query_handler(text="cancel", state="*")
# async def cancel_handler(call: types.CallbackQuery, state: FSMContext):
#     await state.finish()
#     await call.message.answer("Ввод отменен.")
#     await call.answer()



# @dp.message_handler(state=Form.konsalid)
# async def process_zabor_konsalid(message: types.Message, state: FSMContext):
#     await state.update_data(konsalid=message.text)
#
#
#     data = message.text.split()
#
#     await message.answer(f"Вы ввели следующие данные {data}. Ожидайте идет обработка данных")
#     if len(data) < 3:
#         await message.reply("Некорректный ввод! Убедитесь, что ввели дату, время и адрес.")
#         return
#
#     user_id = message.from_user.id
#     date = data[0]
#     start_time = data[1]
#     end_time = data[2]
#
#     # Получение данных пользователя из базы данных
#     cursor.execute("""
#         SELECT weight, name, comment, phone_number, city, address
#         FROM user_zakaz
#         WHERE user_id = ?
#         ORDER BY created_at DESC
#         LIMIT 1
#     """, (user_id,))
#     user_data = cursor.fetchone()
#
#     if user_data:
#         from dublikat_zayavki import create_call_request_kurier_konsol
#         weight, name, comment, phone_number, city, address = user_data
#         konsol = create_call_request_kurier_konsol(weight, name, comment, phone_number, city, address, date, start_time, end_time)
#
#         await message.reply(konsol)
#     else:
#         await message.reply(f"Пользователь с ID {user_id} не найден в базе данных.")
#
#     # Завершение состояний
#     await state.finish()


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

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

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
    await bot.send_message(callback_query.from_user.id, "Пожалуйста, введите адрес:", reply_markup=cancel_keyboard)
    await Form.adr.set()

@dp.callback_query_handler(lambda c: c.data == 'change_city')
async def handle_change_city(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.send_message(callback_query.from_user.id, "Пожалуйста, введите город через пробел адрес (Москва улица Комарова, 2):", reply_markup=cancel_keyboard)
    await Form.cit.set()





from cedek_blizh_office import get_nearest_gdp_offices

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




# Меняем фильтр, чтобы он проверял состояние
@dp.message_handler(content_types=types.ContentType.TEXT, state=Form.waiting_for_city)
async def gdp_city(message: types.Message, state: FSMContext):
    """Обрабатывает ввод города для GDP."""
    print(f"gdp_city called with state: {await state.get_state()}")
    city = message.text
    def split_address(address: str):
        """Пытается разделить адрес на город и улицу по запятой."""
        parts = address.split(',')
        if len(parts) == 1:
            # Нет запятой, считаем, что это только город или только улица
            return parts[0].strip(), ""  # Возвращаем город, улица пустая
        else:
            city = parts[0].strip()
            street = ','.join(parts[1:]).strip()  # Соединяем остаток обратно, если запятых несколько
            return city, street

    city, street = split_address(city)
    await state.update_data(city=city)
    await state.update_data(street=street)  #Сохраняем улицу для дальнейшего использования
    data = await state.get_data()
    product_id = data.get('product_id')
    print(city, "------", street)

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
        nearest_offices = await get_nearest_gdp_offices(city, street)  # await тут
        animation_task.cancel() #Останавливаем анимацию после получения данных

        if nearest_offices:
            keyboard = types.InlineKeyboardMarkup(row_width=1)

            def extract_street_and_number(address_string):
                parts = address_string.split(',')
                # Проверяем, достаточно ли частей, чтобы улица и номер существовали
                if len(parts) >= 5:
                    # Извлекаем улицу и номер дома (они находятся в 4-м элементе)
                    street_part = parts[4].strip()  # Удаляем лишние пробелы

                    return street_part
                else:
                    return None  # Или какое-то сообщение об ошибке, если структура адреса неверн


            for office in nearest_offices:
                office_code = office['code']
                print(office['address'][2:-1])
                city_code = office['city_code']
                button_text = f"{office['address']}"
                street1 = extract_street_and_number(button_text)
                callback_data = f"gdp_office:{office_code}:{city_code}"
                keyboard.add(types.InlineKeyboardButton(text=street1, callback_data=callback_data))

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

        print(f"Calling change_delivery_point with uuid: {uuid}, office_code: {office_code}, city_code: {city_code}, {street}")  # Лог
        # Вызываем функцию изменения ПВЗ и передаем office_code и city_code
        api_response = await change_delivery_point(uuid, office_code, city_code, street)  # Вызываем функцию change_delivery_point и сохраняем ответ

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
               # f"Полный адрес: {full_address}\n"
               # f"Время работы: {work_time}\n"
                f"Город: {city}\n"
                f"Улица: {street}\n"
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

        await state.finish()  # Завершаем состояние после выбора ПВЗ
    except Exception as e:  # Ловим ошибку
        print(f"Error in process_entering_pwz: {e}")  # Выводим сообщение об ошибке

import aiohttp
import json
import logging

logger = logging.getLogger(__name__)


async def change_delivery_point(uuid: str, delivery_point_code: str, city_code: str, new_address: str = None):
    token = get_token() #  Возвращаем await
    print('===========', uuid, delivery_point_code, city_code, "=================")
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
    }

    logger.debug(f"URL: {url}")
    logger.debug(f"Headers: {headers}")
    logger.debug(f"Payload: {payload}")


    async with aiohttp.ClientSession() as session:
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
                        await asyncio.sleep(3)  # Добавляем задержку в 2 секунды
                        address_payload = {
                            "uuid": uuid,  # Добавляем UUID
                            "type": 1,  # Предполагаем, что у вас тип заказа 1
                            "to_location": {
                                "address": new_address,
                                "city_code": city_code  # Обязательно нужно передавать city_code или city
                            }
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




# здесь был код из obrabotka.py

# Функция для обработки ввода информации о заказе
async def process_order_info(message: types.Message, state: FSMContext, info_function, inline_buttons_data):
    order_number = message.text
    current_time = datetime.now()
    user_id = message.from_user.id



    # Check if user has entered data within the last 15 minutes
    cursor.execute("SELECT * FROM new_orders WHERE user_id = ? AND created_at > ?", (user_id, current_time - timedelta(minutes=15)))
    recent_order = cursor.fetchone()
    print(recent_order)

    # Use recent order info if available, otherwise fetch new order info
    if recent_order:
        order_info = recent_order[2]
    else:
        order_info = info_function(order_number)

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
    ])

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

@dp.callback_query_handler(lambda c: c.data == 'cancel_delivery')
async def otmena_zakaza(callback_query: types.CallbackQuery):
    from otmena_zakaz import otmena

    connection = sqlite3.connect('users.db')
    cursor = connection.cursor()

    cursor.execute('SELECT order_info FROM new_orders WHERE user_id = ? ORDER BY id DESC LIMIT 1', (callback_query.from_user.id,))
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
@dp.message_handler(state=Form.npdc)
async def process_izmenit_za_dop(message: types.Message, state: FSMContext):
    try:
        from izmeneniya import nalozh_pay_dop_cbor
        text = message.text
        if int(text) >= 0:
            connection = sqlite3.connect('users.db')
            cursor = connection.cursor()

            cursor.execute('SELECT order_info FROM new_orders WHERE user_id = ? ORDER BY id DESC LIMIT 1', (message.from_user.id,))
            order_info = cursor.fetchone()
            order_info_str = order_info[0]

            order_info_dict = ast.literal_eval(order_info_str)
            uuid = order_info_dict['entity']['uuid']
            result = nalozh_pay_dop_cbor(uuid, text)
            keyboard = InlineKeyboardMarkup()
            keyboard.add(
                InlineKeyboardButton("Назад", callback_data='go_back_menu')
            )
            await bot.send_message(message.from_user.id, f"Операция выполнена успешно.{result['requests']}", reply_markup=keyboard)
            await state.finish()
        else:
            await bot.send_message(message.from_user.id, f"Сумма не может быть отрицательной, введите корректное значение")


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
    entered_text = message.text
    connection = sqlite3.connect('users.db')
    cursor = connection.cursor()

    cursor.execute('SELECT order_info FROM new_orders WHERE user_id = ? ORDER BY id DESC LIMIT 1', (message.from_user.id,))
    order_info = cursor.fetchone()

    if order_info:
        order_info_str = order_info[0]
        try:
            order_info_dict = ast.literal_eval(order_info_str)
            uuid = order_info_dict['entity']['uuid']
            result = info_function(uuid, entered_text)

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
            address_parts = address_parts[1:]
            address = ' '.join(address_parts)
            print(city, address)
            result = change_city(uuid, city, address)

    #         await bot.send_message(message.from_user.id, result)
    #
    #     except (ValueError, SyntaxError) as e:
    #         print(f"Failed to evaluate order_info_str as dictionary: {e}")
    # else:
    #     print("No order_info found for the user")
    #
    # connection.close()
    # await state.finish()
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
                    import pytz
                    moscow_tz = pytz.timezone('Europe/Moscow')
                    #
                    # for status in reversed(statuses):
                    #     date_time_str = status['date_time']
                    #     # Убираем смещение +0000
                    #     date_time_str = date_time_str[:-5]  # Удаляем последние 5 символов
                    #     # Парсим строку даты и времени
                    #     utc_time = datetime.strptime(date_time_str, '%Y-%m-%dT%H:%M:%S')
                    #     # Присваиваем UTC временную зону
                    #     utc_time = pytz.utc.localize(utc_time)
                    #     # Переводим в московское время
                    #     moscow_time = utc_time.astimezone(moscow_tz)
                    #     # Форматируем строку
                    #     status_str = f"{status['name']} в {status['city']} {moscow_time.strftime('%Y-%m-%d %H:%M:%S')}"
                    #     statuses_reversed.append(status_str)
                    # status_text = "\n".join(statuses_reversed)
                    # await bot.send_message(callback_query.from_user.id, status_text)
                    from collections import defaultdict
                    from datetime import datetime
                    import pytz
                    statuses_by_date = defaultdict(list)
                    for status in reversed(statuses):
                        date_time_str = status['date_time']
                        date_time_str = date_time_str[:-5]  # Удаляем смещение +0000

                        # Парсим строку даты и времени
                        utc_time = datetime.strptime(date_time_str, '%Y-%m-%dT%H:%M:%S')

                        # Присваиваем UTC временную зону
                        utc_time = pytz.utc.localize(utc_time)

                        # Переводим в московское время
                        moscow_time = utc_time.astimezone(moscow_tz)

                        # Форматируем строку статуса (только время)
                        status_str = f"{status['name']} в {status['city']} {moscow_time.strftime('%H:%M:%S')}"

                        # Группируем статусы по дате
                        date_key = moscow_time.strftime('%Y-%m-%d')  # Используем дату как ключ
                        statuses_by_date[date_key].append(status_str)

                    # Формируем итоговый текст сообщения
                    output_lines = []
                    for date, status_list in statuses_by_date.items():
                        output_lines.append(date)  # Добавляем дату как заголовок
                        for status in status_list:
                            output_lines.append(f"  - {status}")  # Добавляем отступ для элементов списка.

                    status_text = "\n".join(output_lines)  # Объединяем все строки в один текст

                    await bot.send_message(callback_query.from_user.id, status_text)  # Отправляем сообщение
                else:
                    await bot.send_message(callback_query.from_user.id, "Информация о статусе отсутствует. Пожалуйста введите номер посылки по своему договору.")
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
                import pytz
                order_info_dict = ast.literal_eval(order_info_str)  # Safely evaluate the string as a Python dictionary
                if 'entity' in order_info_dict:
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
                        f"📦 *Данные о поссылки:*\n"
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
                else:
                    await bot.send_message(callback_query.from_user.id, "Пожалуйста введите номер накладной по вашему договору.")
            except (ValueError, SyntaxError) as e:
                await bot.send_message(callback_query.from_user.id, "Ошибка декодирования информации о заказе. Попробуйте еще раз позже.")
                print(f"Error: {e}")
        else:
            await bot.send_message(callback_query.from_user.id, "Информация о заказе не найдена.")

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
                    # Обработка статусов
                    statuses = entity_info.get('statuses', [])
                    status_text = ""
                    for status in statuses:
                        status_text += f"📌 *Стус:* {status['name']} ({status['code']}) - {status['date_time']} - {status['city']}\n"

                    # Format the output
                    entity_text = (
                        f"📦 *Информация об отправлении:*\n\n"
                        f"🔑 *UUID:* {entity_info.get('uuid', 'N/A')}\n"
                        f"📝 *Номер отправления:* {entity_info.get('cdek_number', 'N/A')}\n"
                        f"  💬 *Комментарий:* {entity_info.get('comment', 'N/A')}\n"
                        f"  📍 *Пункт доставки:* {entity_info.get('delivery_point', 'N/A')}\n"
                        f"  👥 *Отправитель:* {entity_info['sender'].get('company', 'N/A')} - {entity_info['sender'].get('name', 'N/A')}\n"
                        f"  👥 *Получатель:* {entity_info['recipient'].get('company', 'N/A')} - {entity_info['recipient'].get('name', 'N/A')}\n"
                        f"📋 *Тарифный код:* {entity_info.get('tariff_code', 'N/A')}\n"
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
                        f"{status_text}"
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
                    await bot.send_message(callback_query.from_user.id, "Пожалуйста введите номер накладжной по вашему договору.")
            except (ValueError, SyntaxError) as e:
                await bot.send_message(callback_query.from_user.id, "Ошибка декодирования информации о заказе. Попробуйте еще раз позже.")
                print(f"Error: {e}")
        else:
            await bot.send_message(callback_query.from_user.id, "Информация о заказе не найдена.")



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
            types.InlineKeyboardButton(text="Изменить город получателя (город назначения + адрес получателя)", callback_data='change_city')
        ]
        keyboard_markup.add(*buttons)
        await bot.send_message(callback_query.from_user.id, "Выберите что хотите изменить",
                               reply_markup=keyboard_markup)

    elif callback_query.data == 'cancel_delivery':
        await bot.send_message(callback_query.from_user.id, "Функция отмены доставки в разработке.")
    elif callback_query.data == 'change_delivery_date':

        # await bot.send_message(callback_query.from_user.id, "Функция изменения даты доставки в разработке.")
        await change_delivery_date(callback_query)




    elif callback_query.data == 'edit_cod_amount':
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



# Клавиатура с датами
def create_date_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=2)
    # Начинаем с завтрашнего дня
    today = datetime.now() + timedelta(days=1)
    for i in range(5):
        date = today + timedelta(days=i)
        date_str = date.strftime('%Y-%m-%d')
        keyboard.add(InlineKeyboardButton(text=date_str, callback_data=f"date_{date_str}"))
    return keyboard

# Функция для создания клавиатуры с временем
def create_time_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=3)
    keyboard.add(InlineKeyboardButton(text="09:00-14:00", callback_data="time_09:00-14:00"))
    keyboard.add(InlineKeyboardButton(text="14:00-18:00", callback_data="time_14:00-18:00"))
    keyboard.add(InlineKeyboardButton(text="09:00-18:00", callback_data="time_09:00-18:00"))
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
    await bot.send_message(callback_query.from_user.id, "Введите комментарий к изменению даты доставки:")
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


    # Вызываем функцию для отправки запроса в API СДЭК
    await send_delivery_date_change_request(message, state, date, time_from, time_to, comment)






#Функция запроса к API
async def send_delivery_date_change_request(message: types.Message, state: FSMContext, date, time_from, time_to, comment):
    import requests
    import json
    from info import get_token

    token = get_token()
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