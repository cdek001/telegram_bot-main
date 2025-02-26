
@dp.message_handler(state=Form.order_number)
async def process_order_number(message: types.Message, state: FSMContext):
    order_number = message.text
    from info import info
    order_info = info(order_number)
    if order_info:
        order_info_str = str(order_info)
        cursor.execute("INSERT INTO orders (user_id, cdek_number, order_info) VALUES (?, ?, ?)",
                       (message.from_user.id, order_number, order_info_str))
        conn.commit()
        await message.answer("Информация о заказе сохранена.")

        # Создаем меню с опциями
        inline_keyboard = InlineKeyboardMarkup(row_width=2)
        inline_keyboard.add(
            InlineKeyboardButton("Отследить посылку", callback_data='track_parcel'),
            InlineKeyboardButton("Данные по посылке", callback_data='parcel_data'),
            InlineKeyboardButton("Внести изменения в заказ (накладную)", callback_data='change_order'),
            InlineKeyboardButton("Отменить доставку", callback_data='cancel_delivery'),
            InlineKeyboardButton("Изменить дату доставки", callback_data='change_delivery_date'),
            InlineKeyboardButton("Редактировать сумму наложенного платежа", callback_data='edit_cod_amount'),
            InlineKeyboardButton("Продлить хранение", callback_data='extend_storage'),
            InlineKeyboardButton("Вернуться назад", callback_data='go_back')
        )

        await message.answer("Выберите действие:", reply_markup=inline_keyboard)
    else:
        await message.answer(
            "Не удалось получить информацию о заказе. Пожалуйста, проверьте номер заказа и попробуйте снова.")
    await state.finish()


@dp.message_handler(state=Form.order_number2)
async def process_order_number2(message: types.Message, state: FSMContext):
    order_number = message.text
    from info import info2
    print(order_number)
    order_info = info2(order_number)
    print(order_info)
    if order_info:
        order_info_str = str(order_info)
        cursor.execute("INSERT INTO orders (user_id, cdek_number, order_info) VALUES (?, ?, ?)",
                       (message.from_user.id, order_number, order_info_str))
        conn.commit()
        await message.answer("Информация о заказе сохранена.")

        # Создаем меню с опциями
        inline_keyboard = InlineKeyboardMarkup(row_width=2)
        inline_keyboard.add(
            InlineKeyboardButton("Отследить посылку", callback_data='track_parcel2'),
            InlineKeyboardButton("Данные по посылке", callback_data='parcel_data2'),
            InlineKeyboardButton("Внести изменения в заказ (накладную)", callback_data='change_order'),
            InlineKeyboardButton("Отменить доставку", callback_data='cancel_delivery2'),
            InlineKeyboardButton("Изменить дату доставки", callback_data='change_delivery_date2'),
            InlineKeyboardButton("Редактировать сумму наложенного платежа", callback_data='edit_cod_amount'),
            InlineKeyboardButton("Продлить хранение", callback_data='extend_storage2'),
            InlineKeyboardButton("Вернуться назад", callback_data='go_back2')
        )

        await message.answer("Выберите действие:", reply_markup=inline_keyboard)
    else:
        await message.answer(
            "Не удалось получить информацию о заказе. Пожалуйста, проверьте номер заказа и попробуйте снова.")
    await state.finish()

import tempfile
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
            # Save detailed information to a temporary file
            with tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8') as temp_file:
                temp_file.write(response_text + office_info)

            # Send the temporary file
            with open(temp_file.name, 'rb') as document:
                await message.answer_document(document)

            # Remove the temporary file
            os.remove(temp_file.name)
            os.unlink(temp_file.name)

    else:
        await message.answer("К сожалению, информация об офисах в данном городе отсутствует.")
    await state.finish()


@dp.message_handler(state=Form.fio)
async def process_entering_fullname(message: types.Message, state: FSMContext):
    entered_fullname = message.text
    # Performing an asynchronous query to retrieve order_info from the database for a specific user_id

    # Assuming you have already established a connection and cursor
    connection = sqlite3.connect('users.db')
    cursor = connection.cursor()

    cursor.execute('SELECT order_info FROM orders WHERE user_id = ?', (message.from_user.id,))
    order_info = cursor.fetchone()

    if order_info:
        order_info_str = order_info[0]
        try:
            order_info_dict = ast.literal_eval(order_info_str)  # Safely evaluate the string as a Python dictionary
            uuid = order_info_dict['entity']['uuid']
            from izmeneniya import fio
            fio = fio(uuid, entered_fullname)
            await bot.send_message(message.from_user.id, fio)

        except (ValueError, SyntaxError) as e:
            # Handle the exception if ast.literal_eval fails
            print(f"Failed to evaluate order_info_str as dictionary: {e}")
    else:
        print("No order_info found for the user")

    connection.close()
    await state.finish()


@dp.message_handler(state=Form.tel)
async def process_entering_tel(message: types.Message, state: FSMContext):
    entered_fullname = message.text
    # Performing an asynchronous query to retrieve order_info from the database for a specific user_id

    # Assuming you have already established a connection and cursor
    connection = sqlite3.connect('users.db')
    cursor = connection.cursor()

    cursor.execute('SELECT order_info FROM orders WHERE user_id = ?', (message.from_user.id,))
    order_info = cursor.fetchone()

    if order_info:
        order_info_str = order_info[0]
        try:
            order_info_dict = ast.literal_eval(order_info_str)  # Safely evaluate the string as a Python dictionary
            uuid = order_info_dict['entity']['uuid']
            from izmeneniya import fone
            fio = fone(uuid, entered_fullname)
            await bot.send_message(message.from_user.id, fio)

        except (ValueError, SyntaxError) as e:
            # Handle the exception if ast.literal_eval fails
            print(f"Failed to evaluate order_info_str as dictionary: {e}")
    else:
        print("No order_info found for the user")

    connection.close()
    await state.finish()

@dp.message_handler(state=Form.adr)
async def process_entering_adr(message: types.Message, state: FSMContext):
    entered_fullname = message.text
    # Performing an asynchronous query to retrieve order_info from the database for a specific user_id

    # Assuming you have already established a connection and cursor
    connection = sqlite3.connect('users.db')
    cursor = connection.cursor()

    cursor.execute('SELECT order_info FROM orders WHERE user_id = ?', (message.from_user.id,))
    order_info = cursor.fetchone()

    if order_info:
        order_info_str = order_info[0]
        try:
            order_info_dict = ast.literal_eval(order_info_str)  # Safely evaluate the string as a Python dictionary
            uuid = order_info_dict['entity']['uuid']
            from izmeneniya import adres
            fio = adres(uuid, entered_fullname)
            await bot.send_message(message.from_user.id, fio)

        except (ValueError, SyntaxError) as e:
            # Handle the exception if ast.literal_eval fails
            print(f"Failed to evaluate order_info_str as dictionary: {e}")
    else:
        print("No order_info found for the user")

    connection.close()
    await state.finish()

@dp.message_handler(state=Form.adr)
async def process_entering_cit(message: types.Message, state: FSMContext):
    entered_fullname = message.text
    # Performing an asynchronous query to retrieve order_info from the database for a specific user_id

    # Assuming you have already established a connection and cursor
    connection = sqlite3.connect('users.db')
    cursor = connection.cursor()

    cursor.execute('SELECT order_info FROM orders WHERE user_id = ?', (message.from_user.id,))
    order_info = cursor.fetchone()

    if order_info:
        order_info_str = order_info[0]
        try:
            order_info_dict = ast.literal_eval(order_info_str)  # Safely evaluate the string as a Python dictionary
            uuid = order_info_dict['entity']['uuid']
            from izmeneniya import change_city
            address_parts = entered_fullname.split(' ', 1)
            city = address_parts[0]  # Первая часть - город
            address = "улица " + address_parts[1]  # Вторая часть - адрес, добавляем "улица" обратно к адресу

            fio = change_city(uuid, city, address)
            await bot.send_message(message.from_user.id, fio)

        except (ValueError, SyntaxError) as e:
            # Handle the exception if ast.literal_eval fails
            print(f"Failed to evaluate order_info_str as dictionary: {e}")
    else:
        print("No order_info found for the user")

    connection.close()
    await state.finish()

@dp.message_handler(state=Form.adr)
async def process_entering_pwz(message: types.Message, state: FSMContext):
    entered_fullname = message.text
    # Performing an asynchronous query to retrieve order_info from the database for a specific user_id

    # Assuming you have already established a connection and cursor
    connection = sqlite3.connect('users.db')
    cursor = connection.cursor()

    cursor.execute('SELECT order_info FROM orders WHERE user_id = ?', (message.from_user.id,))
    order_info = cursor.fetchone()

    if order_info:
        order_info_str = order_info[0]
        try:
            order_info_dict = ast.literal_eval(order_info_str)  # Safely evaluate the string as a Python dictionary
            uuid = order_info_dict['entity']['uuid']
            from izmeneniya import pwz
            fio = pwz(uuid, entered_fullname)
            await bot.send_message(message.from_user.id, fio)

        except (ValueError, SyntaxError) as e:
            # Handle the exception if ast.literal_eval fails
            print(f"Failed to evaluate order_info_str as dictionary: {e}")
    else:
        print("No order_info found for the user")

    connection.close()
    await state.finish()