import sqlite3
import os
import json
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.types import ParseMode, ReplyKeyboardMarkup, KeyboardButton, InputMediaPhoto
from aiogram.utils import executor
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def proces(*args, **kwargs):
    bot = Bot(token="7020285176:AAEr9NQt7m3pljwWAMfYANb1EjdMeQKmgVQ")
    storage = MemoryStorage()
    dp = Dispatcher(bot, storage=storage)
    dp.middleware.setup(LoggingMiddleware())


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

    # процесс для накланой номера сдек
    @dp.callback_query_handler(lambda c: c.data == 'enter_waybill')
    async def process_enter_waybill(callback_query: types.CallbackQuery):
        await bot.send_message(callback_query.from_user.id, "Пожалуйста, введите номер заказа (накладной):")
        await Form.order_number.set()


    # процесс для онлайн магазина
    @dp.callback_query_handler(lambda c: c.data == 'enter_webshop_order')
    async def process_enter_webshop_order(callback_query: types.CallbackQuery):
        await bot.send_message(callback_query.from_user.id, "Пожалуйста, введите номер заказа:")
        await Form.order_number2.set()


    # процесс для ввода города
    @dp.callback_query_handler(lambda c: c.data == 'list_offices')
    async def process_list_offices(callback_query: types.CallbackQuery):
        await bot.send_message(callback_query.from_user.id, "Пожалуйста, введите название города:")
        await Form.order_number3.set()

    @dp.callback_query_handler(lambda c: c.data == 'change_fullname')
    async def process_fio(callback_query: types.CallbackQuery):
        await bot.send_message(callback_query.from_user.id, "Пожалуйста, введите ФИО:")
        await Form.fio.set()

    @dp.callback_query_handler(lambda c: c.data == 'change_phone')
    async def process_tel(callback_query: types.CallbackQuery):
        await bot.send_message(callback_query.from_user.id, "Пожалуйста, введите номер телефона:")
        await Form.tel.set()

    @dp.callback_query_handler(lambda c: c.data == 'address')
    async def process_adress(callback_query: types.CallbackQuery):
        await bot.send_message(callback_query.from_user.id, "Пожалуйста, введите адрес:")
        await Form.adr.set()

    @dp.callback_query_handler(lambda c: c.data == 'change_city')
    async def process_city(callback_query: types.CallbackQuery):
        await bot.send_message(callback_query.from_user.id, "Пожалуйста, введите город через пробел адрес (Москва проспект московский строение 20):")
        await Form.cit.set()

    @dp.callback_query_handler(lambda c: c.data == 'change_pickup_point')
    async def process_pwz(callback_query: types.CallbackQuery):
        await bot.send_message(callback_query.from_user.id, "Пожалуйста, введите адрес:")
        await Form.pwz.set()