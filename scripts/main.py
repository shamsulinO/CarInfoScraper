import re
import string
import sqlite3
import json
import random

import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor
from aiogram.utils.callback_data import CallbackData

import chromedriver_binary
from selenium import webdriver
from selenium.webdriver.common.by import By

from datetime import datetime, timedelta
from time import sleep

import emoji
from yoomoney import Quickpay, Client
import urllib.request
import configparser
import requests
import Gibdd_Parsing

settings = configparser.ConfigParser()
settings.read(r"data\settings.ini", encoding='utf-8-sig')

token_p2p = settings["settings"]["yoo_token"]
cb = CallbackData('btn', 'action')

show_print = True
print = print if show_print else str

options = webdriver.ChromeOptions()
options.add_argument('ignore-certificate-errors')
options.add_argument('headless')
browser = webdriver.Chrome(chrome_options=options)

loop = asyncio.new_event_loop()
bot = Bot(token=settings["settings"]["telegram_token"], parse_mode='HTML')
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage, loop=loop)

checking_files_status = False

months = {i +1:x for i, x in enumerate(["января", "февраля", "марта", "апреля", "мая", "июня", "июля", "августа", "сентября", "окрября", "ноября", "декабрь"])}
red_mark = ":red_circle:"
yellow_mark = ":yellow_circle:"
green_mark = ":green_circle:"
blue_mark = ":blue_circle:"

emoji_list = [":otter:",":cat_with_wry_smile:",":grinning_cat_with_smiling_eyes:",
              ":grinning_cat:",":alien:",":alien_monster:",":smiling_face_with_sunglasses:",
              ":nerd_face:",":face_with_monocle:",":cowboy_hat_face:",":disguised_face:",
              ":smiling_face_with_open_hands:",":smiling_face:",":star_struck:",
              ":winking_face:",":grinning_face_with_smiling_eyes:"]

@dp.message_handler(commands=['start','help'])
async def cmd_start(message: types.Message):
    markup = types.InlineKeyboardMarkup()
    avitobutton = types.InlineKeyboardButton("Перейти в Авито", url="https://www.avito.ru/")
    markup.add(avitobutton)
    await message.answer(f'''*Avito Parser*\n\n*Привет, {message.chat.first_name}!* {emoji.emojize(random.choice(emoji_list))}\nДля работы парсера необходима ссылка для поиска, получить её можно используя видео-инструкцию под этим сообщением. *(*_Если нет инструкции нужно подождать_*)*
    \n*Вот список того что я умею делать*\n\t- Парсить объвления :D\n\t- Получить гос. номер и вин номер машины (под всеми объявлениями есть для этого кнопка)
\t- Если в чат скинуть ссылку на определенную машину то можно получить её гос. номер и вин номер\n\t- Если скинуть Vin номер то можно получить отчет об авто ГИБДД''',parse_mode="Markdown",reply_markup=markup)
    await message.answer_chat_action("upload_video")
    await bot.send_video(message.chat.id, open(r'data\data_photo/instruction.mp4', "rb"),caption="*Полученую ссылку нужно скинуть суда в чат, после нажать на кнопку старт.*\n\n*Изменять ссылку можно в любой момент для этого нужно просто отправить её в этот чат.*", parse_mode="Markdown")
    save_new_user(message.chat.id, message.from_user.first_name)

async def checking_files():
    while True:
            for user in sqlite3_query("SELECT id, name, search_status, message, second_message, subscribe_date FROM user"):
                try:
                    log_print(user[0], user[1], green_mark, "Check file")
                    if user[2] == 1 and not user[3] == user[4]:
                        follow_time = user[5].split("-")
                        if not (datetime(int(follow_time[0]), int(follow_time[1]),int(follow_time[2])) - datetime.now()).total_seconds() < 0:
                            show = "\n\n".join(user[3].split("~")).split("&")
                            name_ad_for_get_vin = user[3].split("~")
                            markup = types.InlineKeyboardMarkup()
                            button1 = types.InlineKeyboardButton("Ссылка на объявление", url= show[1])
                            markup.add(button1)
                            index_vin = 0 if "Название" in name_ad_for_get_vin[0] else 1
                            split_link_for_vin = f'{name_ad_for_get_vin[index_vin].replace(" ","/").replace("*Название*:","")}&{show[1].split("_")[-1]}'
                            markup.add(types.InlineKeyboardButton(text="Получить номер и VIN", callback_data=f"ad_id={split_link_for_vin}"))
                            await bot.send_photo(user[0], types.InputFile(fr'data\data_photo/{user[0]}.jpg') , caption= emoji.emojize(f"{show[0]}"), parse_mode='Markdown', reply_markup=markup, disable_notification=False)
                            log_print(user[0], user[1], green_mark, f"New ad. Link: {show[1]}")
                            sqlite3_query(f"UPDATE user SET second_message = '{user[3]}' WHERE id = '{user[0]}'")
                        else:
                            await bot.send_message(user[0], "*Найдено объявление но у вас отсутствует подписка! Поиск объявлений остановлен.*", parse_mode="Markdown")
                            log_print(user[0], user[1], yellow_mark, f"No subscribe")
                            sqlite3_query(f"UPDATE user SET search_status = 0 WHERE id = '{user[0]}'")
                            await buy_subscribe(user[0])
                except Exception as e:
                    log_print(user[0], user[1], red_mark, f"Error in Check file")
            await asyncio.sleep(0.5)

@dp.message_handler()
async def main(message: types.Message):
    global checking_files_status
    if not checking_files_status:
        checking_files_status = True
        await checking_files()

    save_new_user(message.chat.id, message.from_user.first_name)
    user = sqlite3_query(f"SELECT id, name, search_status, subscribe_date FROM user WHERE id = {message.chat.id}")
    start, stop, information = types.KeyboardButton(emoji.emojize(":chequered_flag: Старт :chequered_flag:")), types.KeyboardButton(emoji.emojize(":no_entry: Стоп :no_entry:")), types.KeyboardButton(emoji.emojize(":bar_chart: Информация :bar_chart:"))
    greet_kb = ReplyKeyboardMarkup(resize_keyboard=True)
    follow_time = user[0][3].split("-")
    if not (datetime(int(follow_time[0]), int(follow_time[1]), int(follow_time[2])) - datetime.now()).total_seconds() < 0:
        check_len = len(message.text.split("?")[0].split("_")[-1]) if "?" in message.text else len(message.text.split("_")[-1]) if '_' in message.text else 0
        if "https://" in message.text and "avito.ru/" in message.text and "_" in message.text and check_len <= 12:
            await get_vin_number_car(message)
        elif "https://" in message.text and "avito.ru/" in message.text:
            await parsing_get_link(message)
        elif any(x in message.text.lower() for x in ["стоп", "stop"]):
            await parsing_stop(message)
        elif any(x in message.text.lower() for x in ["старт", "start"]):
            await parsing_start(message)
        elif any(x in message.text.lower() for x in ["инф", "inf"]):
            await user_information(message)
        elif message.text.isdigit() and len(message.text) == 5:
            await get_infomation_from_gibdd(message)
        elif len(message.text) == 17:
            await gibdd_captcha(message)
        else:
            log_print(user[0][0], user[0][1], yellow_mark, f"Unknown text: {message.text}")
            greet_kb.add(stop, information) if user[0][2] == 1 else greet_kb.add(start, information)
            await message.answer("Неизвесная команда",reply_markup=greet_kb)
    else:
        log_print(user[0][0], user[0][1], yellow_mark, f"No subscribe")
        sqlite3_query(f"UPDATE user SET search_status = 0 WHERE id = {user[0][0]}")
        await buy_subscribe(message.chat.id)

async def parsing_get_link(message: types.Message):
    start, stop, information = types.KeyboardButton(emoji.emojize(":chequered_flag: Старт :chequered_flag:")), types.KeyboardButton(emoji.emojize(":no_entry: Стоп :no_entry:")), types.KeyboardButton(emoji.emojize(":bar_chart: Информация :bar_chart:"))
    greet_kb = ReplyKeyboardMarkup(resize_keyboard=True)
    user = sqlite3_query(f"SELECT id, name, search_status FROM user WHERE id = {message.chat.id}")
    try:
        if not "%" in message.text and "&s=104" in message.text and "avtomobili" in message.text:
            new_link = re.sub(r'^.*(http.*&s=104).*', r'\1', message.text)
            sqlite3_query(f"UPDATE user SET search_status = 0, search_link = '{new_link}' WHERE id = '{user[0][0]}'")
            greet_kb.add(stop, information) if user[0][2] == "True" else greet_kb.add(start, information)
            log_print(user[0][0], user[0][1], green_mark, f"Link save successfully")
            await message.answer(emoji.emojize(f'*Ссылка успешно сохранена!* :check_mark_button:\n\nДля запуска поиска нужно нажать кнопку "*Старт*"!'),reply_markup=greet_kb, parse_mode="Markdown")
        else:
            error_message = 'Ссылка не должна иметь знак "%", попробуйте сделать ссылку по новой.' if "%" in message.text else \
            'У вас отсутствует фильтр "По дате"!\nДобавьте фильтр и отправьте обновленную ссылку.' if not "&s=104" in message.text else "У вас ссылка не для поиска автомобилей!"
            await message.answer(emoji.emojize(f'*Ссылка не сохранена!* :warning:\n\n{error_message}'),reply_markup=greet_kb, parse_mode="Markdown")
            log_print(user[0][0], user[0][1], red_mark, f"Error in Save link")
    except Exception as e:
        await message.answer("Повторите попытку.")

async def parsing_start(message: types.Message):
    start, stop, information = types.KeyboardButton(emoji.emojize(":chequered_flag: Старт :chequered_flag:")), types.KeyboardButton(emoji.emojize(":no_entry: Стоп :no_entry:")), types.KeyboardButton(emoji.emojize(":bar_chart: Информация :bar_chart:"))
    greet_kb = ReplyKeyboardMarkup(resize_keyboard=True)
    user = sqlite3_query(f"SELECT id, name, search_status, search_link FROM user WHERE id = '{message.chat.id}'")
    try:
        if user[0][3] != "0":
            sqlite3_query(f"UPDATE user SET search_status = 1 WHERE id = '{user[0][0]}'")
            log_print(user[0][0], user[0][1], blue_mark, f"Finding started")
            greet_kb.add(stop, information) if user[0][2] == 1 else greet_kb.add(start, information)
            await message.answer(emoji.emojize(f':chequered_flag: *Поиск запущен!*\nДля завершения поиска нажмите *Стоп*!'),reply_markup=greet_kb, parse_mode="Markdown")
        else:
            await message.answer(emoji.emojize("*Ошибка запуска* :warning:\nУ вас не указана ссылка на поиск!"),parse_mode="Markdown")
    except Exception as e:
        await message.answer(emoji.emojize(":warning: *Ошибка* повторите попытку."),parse_mode="Markdown")

async def parsing_stop(message: types.Message):
    start, stop, information = types.KeyboardButton(emoji.emojize(":chequered_flag: Старт :chequered_flag:")), types.KeyboardButton(emoji.emojize(":no_entry: Стоп :no_entry:")), types.KeyboardButton(emoji.emojize(":bar_chart: Информация :bar_chart:"))
    greet_kb = ReplyKeyboardMarkup(resize_keyboard=True)
    user = sqlite3_query(f"SELECT id, name, search_status, search_link FROM user WHERE id = '{message.chat.id}'")
    try:
        sqlite3_query(f"UPDATE user SET search_status = 0 WHERE id = '{user[0][0]}'")
        log_print(user[0][0], user[0][1], blue_mark, f"Finding Stoped")
        greet_kb.add(stop, information) if user[0][2] == 1 else greet_kb.add(start, information)
        await message.answer(emoji.emojize(f":no_entry: *Поиск остановлен!*\nДля запуска нажмите кнопку *Старт*!"), reply_markup=greet_kb, parse_mode="Markdown")
    except Exception as e:
        await message.answer("Повторите попытку.")

@dp.callback_query_handler(lambda c: c.data.startswith('ad_id='))
async def handle_callback_query(query: types.CallbackQuery):
    user = sqlite3_query(f"SELECT id, name, subscribe_date FROM user WHERE id = '{query.message.chat.id}'")
    follow_time = user[0][2].split("-")
    if not (datetime(int(follow_time[0]), int(follow_time[1]),int(follow_time[2])) - datetime.now()).total_seconds() < 0:
        msg = await query.message.answer(emoji.emojize(f":hourglass_not_done: *Загрузка...*"), parse_mode="Markdown")
        try:
            link_for_get_vin = query.data.split("=")[1].replace("/"," ").split("&")
            browser.get(f'https://www.avito.ru/shops/157799769/blockForItem?baseItemId={link_for_get_vin[1]}')
            information_car = browser.find_element(By.XPATH,f"//pre[@style='word-wrap: break-word; white-space: pre-wrap;']").text
            number = re.search(r'"110427":"(.+?)","110907"', information_car)
            number = f"`{number.group(1)}`" if number else "Не найдено"
            vin = re.search(r'"836":"(.+?)"},"', information_car)
            vin = f"`{vin.group(1)}`" if vin else "Не найдено"
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton(text=emoji.emojize(":oncoming_automobile: Информация об авто :oncoming_automobile:"), callback_data=f"gibdd_captcha={vin}"))
            await bot.delete_message(query.message.chat.id, msg.message_id)
            await query.message.answer(f"*{link_for_get_vin[0]}*\n\n*Номер*: {number}\n*Vin*: {vin}", parse_mode="Markdown",reply_markup=markup)
        except Exception:
            await bot.delete_message(query.message.chat.id, msg.message_id)
            await query.message.answer(f"*Ошибка, повторите попытку позже*", parse_mode="Markdown")
    else:
        log_print(user[0][0], user[0][1], yellow_mark, f"No subscribe")
        await buy_subscribe(query.message.chat.id)
    await bot.answer_callback_query(query.id)

async def get_vin_number_car(message: types.Message):
    msg = await message.answer(emoji.emojize(f":hourglass_not_done: *Загрузка...*"), parse_mode="Markdown")
    try:
        ad_id = message.text.split("?")[0].split("_")[-1] if "?" in message.text else message.text.split("_")[-1]
        browser.get(f'https://www.avito.ru/shops/157799769/blockForItem?baseItemId={ad_id}')
        information_car = browser.find_element(By.XPATH,f"//pre[@style='word-wrap: break-word; white-space: pre-wrap;']").text
        number = re.search(r'"110427":"(.+?)","110907"', information_car)
        number = f"`{number.group(1)}`" if number else "Не найдено"
        vin = re.search(r'"836":"(.+?)"},"', information_car)
        vin = f"`{vin.group(1)}`" if vin else "Не найдено"
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton(text=emoji.emojize(":oncoming_automobile: Информация об авто :oncoming_automobile:"),callback_data=f"gibdd_captcha={vin}"))
        await bot.delete_message(message.chat.id, msg.message_id)
        await message.answer(f"*Номер*: {number}\n*Vin*: {vin}", parse_mode="Markdown", reply_markup=markup)
    except Exception:
        await bot.delete_message(message.chat.id, msg.message_id)
        await message.answer(f"*Ошибка, повторите попытку позже*", parse_mode="Markdown")

async def user_information(message: types.Message):
    user = sqlite3_query(f"SELECT id, name, search_link, search_status, subscribe_date, count_ads FROM user WHERE id = '{message.chat.id}'")
    try:
        data_score = int(user[0][5])
        adword = "Объявление" if data_score == 1 else "Объявления" if data_score >= 2 and data_score <= 4 else "Объявлений"
        user_link = "У вас нет ссылки для поиска." if user[0][2] == "0" else f'[Ссылка]({user[0][2]})'
        user_status = "Включен :green_square:" if user[0][3] == "True" else "Выключен :red_square:"
        subscribe = user[0][4].split("-")
        await message.answer(f'''{emoji.emojize(":bar_chart:") } *Список вашей информации*\n\n*Подписка активна до*: {subscribe[2]} {months[int(subscribe[1])%12]} {subscribe[0]}г.\n\n*Ваша ссылка для поиска*: {user_link}\n\n*Статус поиска*: {emoji.emojize(user_status)}\n\n*Интерестный факт!* {emoji.emojize(random.choice(emoji_list))}\nЗа всё время вам было отправленно *{user[0][5]}* {adword}.''',disable_web_page_preview=True, parse_mode="Markdown")
    except Exception as e:
        log_print(user[0][0], user[0][1], red_mark, f"Error in user_information")
        await message.answer(f'*Ошибка. Повторите попытку.*', parse_mode="Markdown")

async def buy_subscribe(user_id):
    letters_and_digits = string.ascii_lowercase + string.digits
    rand_string = ''.join(random.sample(letters_and_digits, 20))
    quickpay = Quickpay(
        receiver = settings["settings"]["card_receiver"],
        quickpay_form = 'shop',
        targets = 'Avito Parser',
        paymentType = 'SB',
        sum = int(settings["settings"]["subscribe_price"]),
        label = rand_string
    )
    claim_keyboard = InlineKeyboardMarkup(inline_keyboard=[[]])
    claim_keyboard.add(InlineKeyboardButton(text=emoji.emojize(':credit_card: Перейти к оплате! :credit_card:'),url=quickpay.redirected_url, callback_data='pay_button'))
    claim_keyboard.add(InlineKeyboardButton(text=emoji.emojize(':shopping_cart: Получить товар! :shopping_cart:'),callback_data=f'code:{rand_string}'))
    await bot.send_photo(user_id, types.InputFile(fr'data\data_photo/buysubscribe.jpg'),caption=emoji.emojize(f'*Avito Parser*\n\n*У вас отсутствует подписка!*\n*Avito Parser на месяц* - _299₽_\n\nВы можете купить её нажав на кнопку "Перейти к оплате!" а после оплаты нажать на кнопку "Получить товар!" для того чтобы получить товар.\n\n[Телеграм для техподдержки](https://t.me/r_shmsln)'), parse_mode='Markdown', reply_markup=claim_keyboard)

@dp.callback_query_handler(lambda c: c.data.startswith('code:'))
async def check_payment(call: types.CallbackQuery):
    label = call.data.replace('code:','')
    client = Client(token_p2p)
    history = client.operation_history(label=label)
    user = sqlite3_query(f"SELECT id, name, search_status, subscribe_date FROM user WHERE id = '{call.message.chat.id}'")
    try:
        operation = history.operations[-1]
        if operation.status == 'success':
            await bot.delete_message(call.message.chat.id, call.message.message_id)
            start, stop, information = types.KeyboardButton(emoji.emojize(":chequered_flag: Старт :chequered_flag:")), types.KeyboardButton(emoji.emojize(":no_entry: Стоп :no_entry:")), types.KeyboardButton(emoji.emojize(":bar_chart: Информация :bar_chart:"))
            greet_kb = ReplyKeyboardMarkup(resize_keyboard=True)
            greet_kb.add(stop, information) if user[0][2] == 1 else greet_kb.add(start,information)
            sqlite3_query(f"UPDATE user SET subscribe_date = '{(datetime.now() + timedelta(days=31)).strftime('%Y-%m-%d')}' WHERE id = '{call.message.chat.id}'")
            log_print(user[0][0], user[0][1], blue_mark, f"Seccessful buying mounth subscribe!")
            await bot.send_message(call.message.chat.id,f'*Avito Parser | Успешно! {emoji.emojize(":star-struck:")}*\n\n*Подписка успешно оформлена!*\nВам была выдана подписка на месяц. Узнать когда подписка закончиться можно нажав на кнопку "Информация"',reply_markup=greet_kb, parse_mode="Markdown")
            file = open(fr"data\data_payment_log/{label}.txt", "w+")
            file.write(f"USER_NAME: {emoji.demojize(call.from_user.first_name)} | USER_ID: {call.message.chat.id} | GETTING_TIME: {datetime.now()}\n")
            file.write(f"Operation: {operation.operation_id}\n\tStatus     --> {operation.status}\n\tDatetime   --> {operation.datetime}\n\tTitle      --> {operation.title}\n")
            file.write(f"\tPattern id --> {operation.pattern_id}\n\tDirection  --> {operation.direction}\n\tAmount     --> {operation.amount}\n\tLabel      --> {operation.label}\n\tType       --> {operation.type}")
            file.close()
        else:
            log_print(user[0][0], user[0][1], red_mark, f"Error in payment. Type: 1")
            await call.message.answer(f"*Avito Parser | Товар не выдан!*\n\nОшибка! Оплаты еще нет, если вы уже оплатили то повторите попытку, если всё равно не получилось то напишите нам по ссылке ниже.\n\n*ВАЖНО! Получать товар нужно из того сообщения из которого оплатили!*\n\n[Телеграм для техподдержки](https://t.me/r_shmsln)\nКод оплаты: `{label}`",parse_mode="Markdown", disable_web_page_preview=True)
    except Exception as e:
        log_print(user[0][0], user[0][1], red_mark, f"Error in payment. Type: 2")
        await call.message.answer(f"*Avito Parser | Товар не выдан!*\n\nОшибка! Оплаты еще нет, если вы уже оплатили то повторите попытку, если всё равно не получилось то напишите нам по ссылке ниже.\n\n*ВАЖНО! Получать товар нужно из того сообщения из которого оплатили!*\n\n[Телеграм для техподдержки](https://t.me/r_shmsln)\nКод оплаты: `{label}`", parse_mode="Markdown",disable_web_page_preview=True)
    await bot.answer_callback_query(call.id)

async def gibdd_captcha(message: types.Message):
    try:
        captcha = requests.get('https://check.gibdd.ru/captcha')
        captcha = json.loads(captcha.text)
        urllib.request.urlretrieve(f'data:image/png;base64,{captcha["base64jpg"]}', fr'data\data_photo/captcha{message.chat.id}.jpg')
        sqlite3_query(f"UPDATE user SET captcha = '{captcha['token']}&{message.text}' WHERE id = '{message.chat.id}'")
        await bot.send_photo(message.chat.id, types.InputFile(fr'data\data_photo/captcha{message.chat.id}.jpg'),caption=f"*Введите текст с картинки*", parse_mode='Markdown')
    except Exception:
        await message.answer(emoji.emojize(f":prohibited: *Не удалось получить капчу :(*"), parse_mode="Markdown")

@dp.callback_query_handler(lambda c: c.data.startswith('gibdd_captcha='))
async def handle_captcha(call: types.CallbackQuery):
    user = sqlite3_query(f"SELECT id, name, subscribe_date FROM user WHERE id = '{call.message.chat.id}'")
    follow_time = user[0][2].split("-")
    if not (datetime(int(follow_time[0]), int(follow_time[1]),int(follow_time[2])) - datetime.now()).total_seconds() < 0:
        call.message.text, call.message.chat.id = call.data.split("=")[1].replace("`",""), call.from_user.id
        if len(call.message.text) == 17:
            await gibdd_captcha(call.message)
        else:
            await call.message.answer("*Ошибка!*\nК сожалению бот может проверить такой vin номер :(", parse_mode="Markdown")
        await bot.answer_callback_query(call.id)
    else:
        log_print(user[0][0], user[0][1], yellow_mark, f"No subscribe")
        await buy_subscribe(call.message.chat.id)

async def get_infomation_from_gibdd(message: types.Message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(text=emoji.emojize("Закрыть :cross_mark:"), callback_data=f"close_message"))
    msg = await message.answer(emoji.emojize(f":speech_balloon:"), parse_mode="Markdown")
    captcha = sqlite3_query(f"SELECT captcha FROM user WHERE id = {message.chat.id}")

    await message.answer_chat_action("typing")
    async for text in Gibdd_Parsing.gibdd(message.chat.id, message.text, captcha[0][0]):
        if text[1] == False:
            await message.answer(emoji.emojize(text[0]), parse_mode="Markdown", disable_web_page_preview=True, disable_notification=True, reply_markup=markup)
        else:
            await bot.send_photo(message.chat.id, types.InputFile(fr'data\data_photo/{text[1]}'),caption=emoji.emojize(text[0]), parse_mode='Markdown', reply_markup=markup, disable_notification=True)
    await bot.delete_message(message.chat.id, msg.message_id)

def log_print(user_id, user_name, mark="blue_mark", text="None"):
    print(emoji.emojize(f"[{mark}]LOG|[{datetime.now().time().replace(microsecond=0)}]|ID:{user_id}|{user_name}|{text}|"))

@dp.callback_query_handler(text="close_message")
async def close_message(call: types.CallbackQuery):
    await bot.answer_callback_query(call.id)
    await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)

def sqlite3_query(query):
    connect_to_DataBase = sqlite3.connect(r"data\users.db")
    cursor = connect_to_DataBase.cursor()
    cursor.execute(query)
    connect_to_DataBase.commit()
    result = cursor.fetchall()
    connect_to_DataBase.close()
    return result

def save_new_user(id, name):
    sqlite3_query(f"CREATE TABLE IF NOT EXISTS user (id TEXT, name TEXT, subscribe_date TEXT, search_link TEXT, search_status BOOLEAN, captcha TEXT, message TEXT, second_message TEXT, count_ads INTEGER)")
    if len(sqlite3_query(f"SELECT * FROM user WHERE id = {id}")) == 0:
        sqlite3_query(f"""INSERT INTO user (id, name, subscribe_date, search_link, search_status, captcha, message, second_message, count_ads) 
                VALUES ('{id}', '{name}', '2022-09-25', '0', 0, '0', '0', '0', 0)""")

if __name__ == '__main__':
    executor.start_polling(dp, loop=loop, skip_updates=True)
