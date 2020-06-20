#!/home/ultraxion/GNBot/GN/.venv/bin/activate
#!/usr/bin/ python3.8
# -*- coding: utf-8 -*-
"""Mains file for GNBot"""
# <<< Import's >>
from telebot.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto, InputMediaVideo
from telebot.types import LabeledPrice, PreCheckoutQuery, ShippingQuery
from pars import main, get_torrents1, get_torrents2, get_torrents3, get_instagram_videos, get_instagram_photos
from funcs import tr_w, rend_d, hi_r, log, clear_link, get_day, get_weather_emoji, sec_to_time, clear_date
from Config_GNBot.config import API, URLS, GNBot_ID, bot, PAYMENT_TOKEN, Admins
from youtube_unlimited_search import YoutubeUnlimitedSearch
from urllib import parse, request, error
from pytube import YouTube, exceptions
from datetime import datetime as dt, timedelta
from collections import defaultdict
from json import JSONDecodeError
import speech_recognition as sr
from pydub import AudioSegment
from threading import Thread
from threading import Timer
import wikipediaapi
import wikipedia
import tempfile
import requests
import ffmpeg
import random
import time
import db
import os
import re

# <<< End import's>>
log('Bot is successful running!', 'info')

# Turn on daily tasks
Parser = Thread(target=main, name='Parser')
Parser.start()


# <<< Start >>>
@bot.message_handler(commands=['start'])
def start_handler(message: Message) -> None:
    """
    :param message
    :type message: telebot.types.Message
    :return: None
    .. seealso:: Enter /start to see start menu
    """
    if str(dt.fromtimestamp(message.date).strftime('%Y-%m-%d %H:%M')) == str(dt.now().strftime('%Y-%m-%d %H:%M')):
        if message.chat.type != 'private':
            db.change_karma(message.from_user.id, '+', 1)
        log(message, 'info')
        db.add_user(message.from_user) if message.chat.type == 'private' else db.add_user(message.from_user, message.chat)
        bot.send_chat_action(message.chat.id, 'typing')
        bot.send_message(message.chat.id, 'Здравствуй, меня зовут <b>GNBot</b>🖥\n'
                                          'Я многофункциональный и мултимедийный бот👾\n'
                                          '<b>Помощь</b> <i>/help</i>', parse_mode='HTML')


# <<< End start >>>


# <<< Help >>>
@bot.message_handler(commands=['help'])
def help_handler(message: Message) -> None:
    """
    :param message
    :type message: telebot.types.Message
    :return: None
    .. seealso::  Enter /help to see help info and contacts
    """
    if str(dt.fromtimestamp(message.date).strftime('%Y-%m-%d %H:%M')) == str(dt.now().strftime('%Y-%m-%d %H:%M')):
        if message.chat.type != 'private':
            db.change_karma(message.from_user.id, '+', 1)
        log(message, 'info')
        db.add_user(message.from_user) if message.chat.type == 'private' else db.add_user(message.from_user, message.chat)
        bot.send_chat_action(message.chat.id, 'typing')
        bot.send_message(message.chat.id, '<b>Тут должна была быть помощь</b>🆘, но её тут не будет🌚\n'
                                          'Список всех команд можно увидеть введя <b>\" </b>/<b> \"</b>\n'
                                          'Бот работает как в приватных чатах так и в группах😱'
                                          'Также бот имеет ввести учет кармы 😇(<i>работает в группах</i>)\n'
                                          'Админ команды (<b>!ban</b>, <b>!mute {<i>time</i>}</b>, <b>!kick</b>)\n'
                                          'Бота можно настроить под себя перейдя в /settings\n'
                                          'Все свои вопросы, предложения или информацию по найдемным '
                                          'багам и ошибкам вы можете отправить введя /feedback\n'
                                          '<b>Почта:</b> <i>ultra25813@gmail.com</i>', parse_mode='HTML')


# <<< End help >>>


# <<< Gif >>>
@bot.message_handler(commands=['gif'])
def gif_handler(message: Message) -> None:
    """
    :param message
    :type message: telebot.types.Message
    :return: None
    .. seealso:: Enter /gif to get random Gif
    .. notes:: Api: https://api.giphy.com
    """
    if str(dt.fromtimestamp(message.date).strftime('%Y-%m-%d %H:%M')) == str(dt.now().strftime('%Y-%m-%d %H:%M')):
        if message.chat.type != 'private':
            db.change_karma(message.from_user.id, '+', 1)
        log(message, 'info')
        bot.send_chat_action(message.chat.id, 'upload_video')
        db.add_user(message.from_user) if message.chat.type == 'private' else db.add_user(message.from_user, message.chat)
        while True:
            try:
                data = requests.get(API['API_Gif']).json()
                if hi_r(data['data']['rating']):
                    bot.send_document(message.chat.id, data['data']['images']['downsized_large']['url'])
                    break
            except Exception:
                continue



# <<< End gif >>>


# <<< QR Code >>>
qr_msg = defaultdict(Message)


@bot.message_handler(commands=['qrcode'])
def qrcode_handler(message: Message) -> None:
    """
    :param message
    :type message: telebot.types.Message
    :return: None
    .. seealso:: Enter /qrcode to crate or reed QR Code
    .. notes:: Api: https://api.qrserver.com
    """
    if str(dt.fromtimestamp(message.date).strftime('%Y-%m-%d %H:%M')) == str(dt.now().strftime('%Y-%m-%d %H:%M')):
        if message.chat.type != 'private':
            db.change_karma(message.from_user.id, '+', 1)
        log(message, 'info')
        db.add_user(message.from_user) if message.chat.type == 'private' else db.add_user(message.from_user, message.chat)
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton('Создать', callback_data='Create_QRCode'),
                     InlineKeyboardButton('Считать', callback_data='Read_QRCode'))
        qr_msg[message.chat.id] = bot.send_message(message.chat.id, 'Выберите опцию🧐', reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: re.fullmatch(r'^Create_QRCode$', call.data))
def create_qrcode(call) -> None:
    global qr_msg
    bot.answer_callback_query(call.id, 'Вы выбрали создать')
    bot.delete_message(qr_msg[call.message.chat.id].chat.id, qr_msg[call.message.chat.id].message_id)
    msg = bot.send_message(call.message.chat.id, 'Введите текст или URL✒️')
    bot.register_next_step_handler(msg, send_qrcode)


@bot.callback_query_handler(func=lambda call: re.fullmatch(r'^Read_QRCode$', call.data))
def read_qrcode(call) -> None:
    bot.answer_callback_query(call.id, 'Вы выбрали считать')
    bot.delete_message(qr_msg[call.message.chat.id].chat.id, qr_msg[call.message.chat.id].message_id)
    msg = bot.send_message(call.message.chat.id, 'Отправь мне QR Code или его фотографию📸')
    bot.register_next_step_handler(msg, read_text)


def read_text(message: Message) -> None:
    if message.content_type == 'photo':
        res = requests.post(API['QRCode']['Read'].replace('FILE', bot.get_file_url(message.photo[0].file_id))).json()
        if res[0]['symbol'][0]['data'] is not None:
            bot.send_message(message.chat.id, '<b>Полученный результат</b>📝\n' + res[0]['symbol'][0]['data'], parse_mode='HTML')
        else:
            bot.send_message(message.chat.id, 'QR Code не обнаружен😔')
    else:
        bot.send_message(message.chat.id, 'Не верный формат данных😔')


def send_qrcode(message: Message) -> None:
    bot.send_photo(message.chat.id, requests.get(API['QRCode']['Create'].replace('DATA', message.text.replace(' ', '+'))).content)


# <<< End QR Code >>>


# <<< Joke >>>
jokes_data = defaultdict(list)


@bot.message_handler(commands=['joke'])
def joke_handler(message: Message) -> None:
    """
    :param message
    :type message: telebot.types.Message
    :return: None
    .. seealso:: Enter /joke to get random jock(18+)
    """
    global jokes_data
    if str(dt.fromtimestamp(message.date).strftime('%Y-%m-%d %H:%M')) == str(dt.now().strftime('%Y-%m-%d %H:%M')):
        if message.chat.type != 'private':
            db.change_karma(message.from_user.id, '+', 1)
        log(message, 'info')
        db.add_user(message.from_user) if message.chat.type == 'private' else db.add_user(message.from_user, message.chat)
        if message.chat.id not in jokes_data or len(jokes_data[message.chat.id]) == 1:
            jokes_data[message.chat.id] = db.get_all('Joke')
        joke = jokes_data[message.chat.id].pop(random.choice(range(len(jokes_data[message.chat.id]) - 1)))
        bot.send_chat_action(message.chat.id, 'typing')
        time.sleep(1.25)
        keyboard = InlineKeyboardMarkup()
        joke_msg = bot.send_message(message.chat.id, joke['setup'] + random.choice(['🧐', '🤨', '🤔']))
        if joke['panchline'] != 'False':
            time.sleep(3.5)
            keyboard.add(InlineKeyboardButton('Удалить', callback_data=f'del {joke_msg.message_id} {message.message_id}'))
            bot.edit_message_text(joke_msg.text + '\n\n' + joke['panchline'] + random.choice(['🌚', '😅', '🤫']),
                                  message.chat.id, joke_msg.message_id, reply_markup=keyboard)
        else:
            keyboard.add(InlineKeyboardButton('Удалить', callback_data=f'del {joke_msg.message_id} {message.message_id}'))
            bot.edit_message_text(joke_msg.text, message.chat.id, joke_msg.message_id, reply_markup=keyboard)


# <<< End joke >>>


# <<< Ogg to Mp3 >>>
msg_mp3ogg = defaultdict(Message)


@bot.message_handler(commands=['oggtomp3'])
def oggtomp3_handler(message: Message) -> None:
    """
    :param message
    :type message: telebot.types.Message
    :return: None
    .. seealso:: Enter /oggtomp3 to convert your voice or ogg file to .mp3
    """
    global msg_mp3ogg
    if str(dt.fromtimestamp(message.date).strftime('%Y-%m-%d %H:%M')) == str(dt.now().strftime('%Y-%m-%d %H:%M')):
        if message.chat.type != 'private':
            db.change_karma(message.from_user.id, '+', 1)
        log(message, 'info')
        db.add_user(message.from_user) if message.chat.type == 'private' else db.add_user(message.from_user, message.chat)
        msg_mp3ogg[message.chat.id] = bot.send_message(message.chat.id, 'Запишите или отправьте аудиосообщение🎙')
        bot.register_next_step_handler(msg_mp3ogg[message.chat.id], set_name_mp3)


def set_name_mp3(message: Message) -> None:
    global msg_mp3ogg
    if message.content_type == 'voice':
        bot.delete_message(msg_mp3ogg[message.chat.id].chat.id, msg_mp3ogg[message.chat.id].message_id)
        bot.delete_message(message.chat.id, message.message_id)
        msg_mp3ogg[message.chat.id] = bot.send_message(message.chat.id, 'Введите имя файла✒️')
        bot.register_next_step_handler(msg_mp3ogg[message.chat.id], send_mp3,  message.voice.file_id)
    else:
        bot.send_message(message.chat.id, 'Не верный формат данных😔')


def send_mp3(message: Message, file_id: int) -> None:
    global msg_mp3ogg
    if message.content_type != 'text':
        bot.send_message(message.chat.id, 'Не верный формат данных😔')
    else:
        bot.send_chat_action(message.chat.id, 'upload_voice')
        bot.delete_message(msg_mp3ogg[message.chat.id].chat.id, msg_mp3ogg[message.chat.id].message_id)
        bot.delete_message(message.chat.id, message.message_id)
        data = request.urlopen(bot.get_file_url(file_id)).read()
        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.write(data)
        audio = AudioSegment.from_ogg(f.name)
        audio.export(f'{message.text}.mp3', format='mp3')
        bot.send_audio(message.chat.id, open(f'{message.text}.mp3', 'rb'))
        try:
            os.remove(os.path.join(os.path.abspath(os.path.dirname(__file__)), f'{message.text}' + '.mp3'))
        except (FileNotFoundError, NameError):
            log('Error! Can\'t remove file', 'warning')


# <<< End Ogg to Mp3 >>>


# <<< Meme >>>
meme_data = defaultdict(list)


@bot.message_handler(commands=['meme'])
def meme_handler(message: Message) -> None:
    """
    :param message
    :type message: telebot.types.Message
    :return: None
    .. seealso:: Enter /meme to get random meme on rus or eng lang
    """
    global meme_data
    if str(dt.fromtimestamp(message.date).strftime('%Y-%m-%d %H:%M')) == str(dt.now().strftime('%Y-%m-%d %H:%M')):
        if message.chat.type != 'private':
            db.change_karma(message.from_user.id, '+', 1)
        log(message, 'info')
        db.add_user(message.from_user) if message.chat.type == 'private' else db.add_user(message.from_user, message.chat)
        bot.send_chat_action(message.chat.id, 'upload_photo')
        data = db.get_setting(message.chat.id)
        if data['meme'] == 'Ru':
            if message.chat.id not in meme_data or len(meme_data[message.chat.id]) == 1:
                meme_data[message.chat.id] = db.get_all('Memes')
            while True:
                meme = meme_data[message.chat.id].pop(random.choice(range(len(meme_data[message.chat.id]) - 1)))
                try:
                    msg = bot.send_photo(message.chat.id, meme['url'])
                    keyboard = InlineKeyboardMarkup()
                    if str(message.from_user.id) in Admins:
                        keyboard.add(InlineKeyboardButton('Удалить',
                                                          callback_data=f'del_from_db {meme["id"]} {message.message_id}'
                                                                        f' {msg.message_id}'))
                    else:
                        keyboard.add(InlineKeyboardButton('Закрыть',
                                                          callback_data=f'del {message.message_id} {msg.message_id}'))
                    bot.edit_message_media(chat_id=msg.chat.id, message_id=msg.message_id,
                                           media=InputMediaPhoto(msg.photo[-1].file_id),
                                           reply_markup=keyboard)
                    break
                except Exception:
                    db.del_meme(meme['id'])
                    continue
        else:
            meme = requests.get(API['API_Meme']).json()
            bot.send_photo(message.chat.id, meme['url'])


@bot.callback_query_handler(func=lambda call: re.fullmatch(r'^del_from_db\s.+\s.+\s.+$', call.data))
def del_meme_query(call):
    bot.answer_callback_query(call.id, 'Удалено')
    for msg_id in call.data.split()[2:]:
        bot.delete_message(call.message.chat.id, msg_id)
    db.del_meme(call.data.split()[1])
# <<< End meme >>>


# <<< Donate >>>
@bot.message_handler(commands=['donate'])
def donate_handler(message: Message) -> None:
    """
    :param message
    :type message: telebot.types.Message
    :return: None
    .. seealso:: Enter /donate to see donate menu(not finished!)
    """
    if str(dt.fromtimestamp(message.date).strftime('%Y-%m-%d %H:%M')) == str(dt.now().strftime('%Y-%m-%d %H:%M')):
        db.change_karma(message.from_user.id, '+', 1)
        log(message, 'info')
        bot.send_chat_action(message.chat.id, 'typing')
        if message.chat.type == 'private':
            bot.send_message(message.chat.id, '<b>К сожеление функция не доработана</b>😔\n'
                                              'Если вы хотите поддержать проект, '
                                              'вы можете превести желаемую сумму на карту\n'
                                              '<b>MonoBank:</b> <i>5375 4141 1577 0850</i>\n'
                                              '<b>C уважением <i>@Ultra_Xion</i></b>', parse_mode='HTML')
            # bot.send_message(message.chat.id, 'Здесь вы можете поддержать разработчика и дать мотивацию '
            #                                   'на внесение нового фунционала в <b>GNBot</b>\n'
            #                                   'C уважением <i>@Ultra_Xion</i>', parse_mode='HTML')
            # if PAYMENT_TOKEN.split(':')[1] == 'LIVE':
            #     keyboard = InlineKeyboardMarkup(row_width=1)
            #     keyboard.add(InlineKeyboardButton('1 грн', callback_data='1 UAH'),
            #                  InlineKeyboardButton('10 грн', callback_data='10 UAH'),
            #                  InlineKeyboardButton('100 грн', callback_data='100 UAH'),
            #                  InlineKeyboardButton('1000 грн', callback_data='1000 UAH'),
            #                  InlineKeyboardButton('Своя сумма', callback_data='Своя сумма'))
            #     msg = bot.send_message(message.chat.id, 'Сумма поддержки💸', reply_markup=keyboard)
            #     time.sleep(20)
            #     bot.delete_message(msg.chat.id, msg.message_id)
        else:
            bot.send_message(message.chat.id, 'К сожелению в группе эта функция недоступна😔\n'
                                              'Что бы поддержать нас вы можете восползоваться'
                                              'этой командой в личном чате с ботом 💢<b>@GNTMBot</b>💢',
                             parse_mode='HTML')


@bot.callback_query_handler(func=lambda call: re.fullmatch(r'^\d+\sUAH$', call.data) or call.data == 'Своя сумма')
def donate_query(call):
    bot.answer_callback_query(call.id, 'Вы выбрали ' + call.data)
    bot.edit_message_text(call.message.text, call.message.chat.id, call.message.message_id)
    if call.data == 'Своя сумма':
        msg = bot.send_message(call.message.chat.id, 'Введите сумму🧐')
        bot.register_next_step_handler(msg, send_payment, 'UAH')
    else:
        send_payment(call.message, call.data)


def send_payment(message: Message, money) -> None:
    if money == 'UAH' and message.text.isdigit():
        local_money = message.text + ' ' + money
    else:
        local_money = money
    price = LabeledPrice('Поддержать', amount=int(local_money.split()[0]) * 100)
    bot.send_invoice(message.chat.id, title='Поддержка',
                     description='Поддержка разработчика GNBot',
                     provider_token=PAYMENT_TOKEN, currency='uah',
                     photo_url=URLS['logo'],
                     photo_height=1494, photo_width=1295, photo_size=142,
                     is_flexible=False, prices=[price],
                     start_parameter='donate-programmer-gnbot',
                     invoice_payload='donate-is-done')


@bot.shipping_query_handler(func=lambda query: True)
def shipping(shipping_query: ShippingQuery):
    bot.answer_shipping_query(shipping_query.id, ok=True,
                              error_message='Что-то пошло не так😔\n!'
                                            'Попробуйте повторить операцию чуть позже')


@bot.pre_checkout_query_handler(func=lambda query: True)
def process_pre_checkout_query(pre_checkout_query: PreCheckoutQuery):
    bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True,
                                    error_message="Что-то пошло не так😔\n"
                                                  "Удебитель в правельности вводимых данные "
                                                  "и попробуйте снова через пару минут")


@bot.message_handler(content_types=['successful_payment'])
def process_successful_payment(message: Message) -> None:
    promo = message.successful_payment
    log(f'Successful_payment\nType: {promo.invoice_payload}\nSum: {promo.total_amount}{promo.currency}')
    bot.send_message(message.chat.id, f'Платеж прошел успешно😌\n'
                                      f'{message.successful_payment.total_amount // 100} '
                                      f'{message.successful_payment.currency} были начислены на свет\n'
                                      f'Благодарим вас за поддержку проекта🥳')


# <<< End donate >>>


# <<< Weather >>>
weather_data = defaultdict(dict)
weather_msg = defaultdict(Message)
city_data = defaultdict(dict)
city_msg = defaultdict(Message)


@bot.message_handler(commands=['weather'])
def weather_handler(message: Message) -> None:
    """
    :param message
    :type message: telebot.types.Message
    :return: None
    .. seealso::  Enter /weather and enter your city to see weather broadcast on 16th days
    .. notes:: Api:  https://api.weatherbit.io
    """
    if str(dt.fromtimestamp(message.date).strftime('%Y-%m-%d %H:%M')) == str(dt.now().strftime('%Y-%m-%d %H:%M')):
        if message.chat.type != 'private':
            db.change_karma(message.from_user.id, '+', 1)
        log(message, 'info')
        db.add_user(message.from_user) if message.chat.type == 'private' else db.add_user(message.from_user, message.chat)
        city_msg[message.chat.id] = bot.send_message(message.chat.id, 'Введите название города✒️')
        bot.register_next_step_handler(city_msg[message.chat.id], show_weather)


def weather(message: Message, index: int) -> None:
    if not message.text.startswith('20'):
        bot.delete_message(message.chat.id, message.message_id)
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton(text="⬅️️", callback_data=f"weather_move_to {index - 1 if index > 0 else 'pass'}"),
        InlineKeyboardButton(text="➡️", callback_data=f"weather_move_to "
                             f"{index + 1 if index < len(weather_data[message.chat.id]) - 1 else 'pass'}"))
    keyboard.add(InlineKeyboardButton('Погода', url='https://' +
                                                    f'darksky.net/forecast/{city_data[message.chat.id]["lat"]},'
                                                    f'{city_data[message.chat.id]["lon"]}/us12/en'))
    keyboard.add(InlineKeyboardButton('Закрыть', callback_data=f'del {weather_msg[message.chat.id].message_id}'))
    try:
        bot.edit_message_text(chat_id=weather_msg[message.chat.id].chat.id,
                              message_id=weather_msg[message.chat.id].message_id,
                              text=f"<i>{weather_data[message.chat.id][index]['valid_date']} "
                                   f"{get_day(weather_data[message.chat.id][index]['valid_date'])}</i>\n"
                                   f"<b>Город {tr_w(city_data[message.chat.id]['city_name'])} "
                                   f"{city_data[message.chat.id]['country_code']}</b>🏢\n\n"
                                   f"<b>Погода</b> {weather_data[message.chat.id][index]['weather']['description']}️"
                                   f"{get_weather_emoji(str(weather_data[message.chat.id][index]['weather']['code']))}"
                                   f"\n<b>Теспература</b> {weather_data[message.chat.id][index]['low_temp']} - "
                                   f"{weather_data[message.chat.id][index]['max_temp']}°C🌡\n"
                                   f"<b>По ощушению</b> {weather_data[message.chat.id][index]['app_min_temp']} - "
                                   f"{weather_data[message.chat.id][index]['app_max_temp']}°C🌡\n"
                                   f"<b>Облачность</b> {weather_data[message.chat.id][index]['clouds']}%☁️\n"
                                   f"<b>Вероятность осадков</b> {weather_data[message.chat.id][index]['pop']}%☔️️\n"
                                   f"<b>Видимость</b> {weather_data[message.chat.id][index]['vis']} км🔭\n"
                                   f"<b>Влажность</b> {weather_data[message.chat.id][index]['rh']} %💧\n"
                                   f"<b>Атмоc. давление</b> "
                                   f"{weather_data[message.chat.id][index]['pres']} дин·см²⏲\n"
                                   f"<b>Ветер</b> {weather_data[message.chat.id][index]['wind_cdir_full']} 🧭\n"
                                   f"<b>Cкорость ветра</b> "
                                   f"{float('{:.1f}'.format(weather_data[message.chat.id][index]['wind_spd']))}"
                                   f" м\\с💨\n",
                              reply_markup=keyboard, parse_mode='HTML')
    except KeyError:
        log('Key Error in weather', 'warning')
        bot.send_chat_action(message.chat.id, '⛔️')


def show_weather(message: Message) -> None:
    global weather_msg, city_data, weather_data, city_msg
    if message.content_type != 'text':
        bot.send_message(message.chat.id, 'Не верный формат данных😔')
    else:
        bot.delete_message(city_msg[message.chat.id].chat.id, city_msg[message.chat.id].message_id)
        try:
            res = requests.get(API['API_Weather'].replace('CityName', message.text.title())).json()
        except JSONDecodeError:
            bot.send_message(message.chat.id, 'Не удалось найти ваш город😔')
        else:
            if message.chat.id in weather_msg:
                bot.delete_message(weather_msg[message.chat.id].chat.id, weather_msg[message.chat.id].message_id)
            city_data[message.chat.id] = {'city_name': res['city_name'], 'country_code': res['country_code'],
                                          'lat': res['lat'], 'lon': res['lon']}
            weather_data[message.chat.id] = res['data']
            weather_msg[message.chat.id] = bot.send_message(message.chat.id, 'Загрузка...')
            weather(message, 0)


@bot.callback_query_handler(func=lambda call: re.fullmatch(r'^weather_move_to\s\d+$', call.data))
def weather_query(call):
    global weather_data
    index = int(call.data.split()[1])
    if 0 <= index < len(weather_data[call.message.chat.id]):
        bot.answer_callback_query(call.id, f'Вы выбрали стр.{index + 1}')
        weather(call.message, index)
    else:
        bot.answer_callback_query(call.id, '⛔️')


# <<< End weather >>>


# <<< Detect music >>>
detect_msg = defaultdict(Message)
data_detect = defaultdict(list)


@bot.message_handler(commands=['detect'])
def detect_handler(message: Message) -> None:
    """
    :param message
    :type message: telebot.types.Message
    :return: None
    .. seealso:: Enter /detect to detect what song play now or you can humming song
    .. notes:: Api: https://api.audd.io
    """
    global detect_msg
    if str(dt.fromtimestamp(message.date).strftime('%Y-%m-%d %H:%M')) == str(dt.now().strftime('%Y-%m-%d %H:%M')):
        if message.chat.type != 'private':
            db.change_karma(message.from_user.id, '+', 1)
        log(message, 'info')
        db.add_user(message.from_user) if message.chat.type == 'private' else db.add_user(message.from_user, message.chat)
        bot.send_chat_action(message.chat.id, 'typing')
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton('Записать🔊', callback_data='record'),
                     InlineKeyboardButton('Напеть🎙', callback_data='sing'))
        detect_msg[message.chat.id] = bot.send_message(message.chat.id, 'Выберите что нужно определить🧐',
                                                       reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: call.data == 'record' or call.data == 'sing')
def callback_query(call):
    bot.delete_message(detect_msg[call.message.chat.id].chat.id, detect_msg[call.message.chat.id].message_id)
    if call.data == 'record':
        bot.answer_callback_query(call.id, 'Вы выбрали ' + 'Записать')
    else:
        bot.answer_callback_query(call.id, 'Вы выбрали ' + 'Напеть')
    msg = bot.send_message(call.message.chat.id, 'Запишите то что нужно определить🎤')
    bot.register_next_step_handler(msg, detect_music, call.data)


def detect_music(message: Message, type_r) -> None:
    global data_detect
    if message.content_type != 'voice':
        bot.send_message(message.chat.id, 'Не верный формат данных😔')
    else:
        API['AUDD_data']['url'] = bot.get_file_url(message.voice.file_id).replace('https://' + 'api.telegram.org',
                                                                                  'http://' + 'esc-ru.appspot.com/') \
                                  + '?host=api.telegram.org'
        if type_r == 'sing':
            data_detect[message.chat.id] = requests.post(API['AUDD'] + 'recognizeWithOffset/',
                                   data={'url': API['AUDD_data']['url'], 'api_token': API['AUDD_data']['api_token']}).json()
        else:
            data_detect[message.chat.id] = requests.post(API['AUDD'], data=API['AUDD_data']).json()
        if data_detect[message.chat.id]['status'] == 'success' and data_detect[message.chat.id]['result'] is not None:
            if type_r != 'sing':
                if data_detect[message.chat.id]['result']['deezer']:
                    keyboard = InlineKeyboardMarkup()
                    res = YoutubeUnlimitedSearch(f"{data_detect[message.chat.id]['result']['artist']} - "
                                                 f"{data_detect[message.chat.id]['result']['title']}",
                                                 max_results=1).get()
                    keyboard.add(InlineKeyboardButton('Текст', callback_data=f"Lyric detect {str(data_detect[message.chat.id]['result']['deezer']['id'])}"),
                                InlineKeyboardButton('Песня', callback_data=res[0]['link']))
                    keyboard.add(InlineKeyboardButton('Dezeer', url=data_detect[message.chat.id]['result']['deezer']['link']))
                    bot.send_photo(message.chat.id, data_detect[message.chat.id]['result']['deezer']['artist']['picture_xl'],
                                   caption=f"{data_detect[message.chat.id]['result']['artist']} - {data_detect[message.chat.id]['result']['title']}🎵",
                                   reply_markup=keyboard)
                else:
                    bot.send_message(message.chat.id, f"<b>{data_detect[message.chat.id]['result']['artist']}</b>"
                                                      f" - {data_detect[message.chat.id]['result']['title']}🎵", parse_mode='HTML')
            else:
                msg = "<b>Результат</b> "
                for i in data_detect[message.chat.id]['result']['list']:
                    msg += f"\nСовпадение: <i>{i['score']}%</i>\n{i['artist']} - {i['title']}🎵"
                bot.send_message(message.chat.id, msg, parse_mode='HTML')
        else:
            bot.send_message(message.chat.id, 'Ничего не нашлось😔')


@bot.callback_query_handler(func=lambda call: re.fullmatch(r'/watch\?v=\w+.+', call.data))
def callback_query(call):
    bot.send_chat_action(call.message.chat.id, 'upload_audio')
    for i in range(5):
        try:
            yt = YouTube('https://' + 'www.youtube.com/' + call.data.split()[0])
        except KeyError:
            continue
        else:
            bot.send_audio(call.message.chat.id,
                           open(yt.streams.filter(only_audio=True)[0].download(filename='file'), 'rb'),
                           title=yt.title, duration=yt.length, performer=yt.author,
                           caption=f'🎧 {sec_to_time(yt.length)} '
                                   f'| {round(os.path.getsize("file.mp4") / 1000000, 1)} MB |'
                                   f' {yt.streams.filter(only_audio=True)[0].abr.replace("kbps", "")} Kbps')
            try:
                os.remove(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'file' + '.mp4'))
            except (FileNotFoundError, NameError):
                log('Error! Can\'t remove file', 'warning')
            break


# <<< End detect music >>>


# <<< Roulette >>>
chips_data = defaultdict(dict)
chips_msg = defaultdict(Message)


@bot.message_handler(commands=['roulette'])
def roulette_handler(message: Message) -> None:
    """
    :param message
    :type message: telebot.types.Message
    :return: None
    .. seealso:: Enter /roulette to play in roulette with another members putting your karma points
    """
    if str(dt.fromtimestamp(message.date).strftime('%Y-%m-%d %H:%M')) == str(dt.now().strftime('%Y-%m-%d %H:%M')):
        # if message.chat.type != 'private':
        log(message, 'info')
        db.add_user(message.from_user) if message.chat.type == 'private' else db.add_user(message.from_user, message.chat)
        msg = bot.send_message(message.chat.id, 'Введите времмя на ставк (в минутах)🖊')
        bot.register_next_step_handler(msg, set_time_roulette, msg.message_id)

        # else:
        #     bot.send_message(message.chat.id, 'Функция доступна только в группах😔')


def play_roulette():
    global chips_data
    if chips_data:
        for chat_id, data in chips_data.items():
            if str(dt.now()).split('.')[:-1] == str(data['time']).split('.')[:-1]:
                del data['time']
                win_num = random.randint(0, 36)
                win_color = 'zero' if win_num == 0 else 'red' if win_num % 2 == 0 else 'black'
                bot.send_message(chat_id, f'Побеило {win_num} {"🔴" if win_color == "red" else "⚫" if win_color == "black" else "⭕"}')
                for user_id, bids in data.items():
                    for bid in bids:
                        if bid['color'] == win_color:
                            if win_color == 'zero':
                                db.change_karma(user_id, '+', int(bid['chips']) * 5)
                            else:
                                db.change_karma(user_id, '+', int(bid['chips']))
                        else:
                            db.change_karma(user_id, '-', int(bid['chips']))



def set_time_roulette(message: Message, message_id) -> None:
    global chips_data, chips_msg
    if message.text.isdigit():
        bot.delete_message(message.chat.id, message_id)
        bot.delete_message(message.chat.id, message.message_id)
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton('10⚫', callback_data='roulette 10 black'),
                     InlineKeyboardButton('100⚫', callback_data='roulette 100 black'),
                     InlineKeyboardButton('250⚫', callback_data='roulette 250 black'))
        keyboard.add(InlineKeyboardButton('10🔴', callback_data='roulette 10 red'),
                     InlineKeyboardButton('100🔴', callback_data='roulette 100 red'),
                     InlineKeyboardButton('250🔴', callback_data='roulette 250 red'))
        keyboard.add(InlineKeyboardButton('10⭕', callback_data='roulette 10 zero'),
                     InlineKeyboardButton('100⭕', callback_data='roulette 100 zero'),
                     InlineKeyboardButton('250⭕', callback_data='roulette 250 zero'))
        msg = bot.send_message(message.chat.id, 'Ваши ставки', reply_markup=keyboard)
        chips_data[message.chat.id] = {'time': dt.now() + timedelta(minutes=float(message.text))}
        Timer(float(message.text) * 60, play_roulette).run()
        del chips_data[message.chat.id]
        del chips_msg[message.chat.id]
        bot.delete_message(msg.chat.id, msg.message_id)
    else:
        bot.send_message(message.chat.id, 'Не верный формат данных😔')


@bot.callback_query_handler(func=lambda call: re.fullmatch(r'roulette\s\d+\s\w+$', call.data))
def callback_query(call):
    global chips_data, chips_msg
    if call.message.chat.id in chips_data:
        bot.answer_callback_query(call.id, 'Ставка принята')
        chips, color = call.data.split()[1:]
        user = f"{call.from_user.first_name + ' ' + call.from_user.last_name}" if call.from_user.last_name is not None else call.from_user.first_name
        if len(chips_data[call.message.chat.id].keys()) == 1:
            chips_msg[call.message.chat.id] = bot.send_message(call.message.chat.id, f'{user} {chips}{"🔴" if color == "red" else "⚫" if color == "black" else "⭕"}')
        else:
            chips_msg[call.message.chat.id] = bot.edit_message_text(chips_msg[call.message.chat.id].text + f'\n{user} {chips}{"🔴" if color == "red" else "⚫" if color == "black" else "⭕"}',
                                  call.message.chat.id, chips_msg[call.message.chat.id].message_id)
        if call.from_user.id not in chips_data[call.message.chat.id]:
            chips_data[call.message.chat.id][call.from_user.id] = [{'color': color, 'chips': chips}]
        else:
            chips_data[call.message.chat.id][call.from_user.id].append({'color': color, 'chips': chips})
    else:
        bot.answer_callback_query(call.id,  'Игра еще не создана😔')
# <<< End Roulette >>>


# <<< Music >>>
data_songs = defaultdict(list)
song_msg = defaultdict(Message)
msg_song = defaultdict(Message)


@bot.message_handler(commands=['music'])
def music_handler(message: Message) -> None:
    """
    :param message
    :type message: telebot.types.Message
    :return: None
    .. seealso:: Enter /music to found music by artist or title song you can get song and them lyric
    .. notes:: Api: https://api.deezer.com/search & Lib: PyTube
    """
    if str(dt.fromtimestamp(message.date).strftime('%Y-%m-%d %H:%M')) == str(dt.now().strftime('%Y-%m-%d %H:%M')):
        if message.chat.type != 'private':
            db.change_karma(message.from_user.id, '+', 1)
        log(message, 'info')
        db.add_user(message.from_user) if message.chat.type == 'private' else db.add_user(message.from_user, message.chat)
        bot.send_chat_action(message.chat.id, 'typing')
        keyboard = InlineKeyboardMarkup(row_width=2)
        keyboard.add(InlineKeyboardButton('По исполнителю🎤', callback_data='artist?q='),
                     InlineKeyboardButton('По треку🎼', callback_data='track?q='))
        msg_song[message.chat.id] = bot.send_message(message.chat.id, 'Как будем искать музыку?🎧', reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: call.data == 'artist?q=' or call.data == 'track?q=')
def callback_query(call):
    bot.delete_message(msg_song[call.message.chat.id].chat.id, msg_song[call.message.chat.id].message_id)
    if call.data == 'artist?q=':
        bot.answer_callback_query(call.id, 'Вы выбрали поиск по артисту')
        msg = bot.send_message(call.message.chat.id, 'Введите исполнителя👤')
    else:
        bot.answer_callback_query(call.id, 'Вы выбрали поиск по треку')
        msg = bot.send_message(call.message.chat.id, 'Введите название трека🖊')
    bot.register_next_step_handler(msg, get_song, call.data, msg.message_id)


def get_song(message: Message, choice: str, message_id: str) -> None:
    global data_songs, song_msg
    if message.content_type != 'text':
        bot.send_message(message.chat.id, 'Не верный формат данных😔')
    else:
        bot.delete_message(message.chat.id, message.message_id)
        bot.delete_message(message.chat.id, message_id)
        res = requests.get(API['API_Deezer'] + choice + message.text.replace(' ', '+')).json()
        try:
            if res['data']:
                if choice == 'artist?q=':
                    songs = requests.get(res['data'][0]['tracklist'].replace('limit=50', 'limit=100')).json()
                    if songs['data']:
                        data_songs[message.chat.id] = [
                            {'id': song['id'], 'title': song['title'], 'name': song['contributors'][0]['name'],
                             'link': song['link'], 'preview': song['preview'], 'duration': song['duration']}
                            for song in songs['data']]
                        create_data_song(message)
                        if data_songs[message.chat.id]:
                            if message.chat.id in song_msg:
                                bot.delete_message(song_msg[message.chat.id].chat.id,
                                                   song_msg[message.chat.id].message_id)
                            song_msg[message.chat.id] = bot.send_photo(message.chat.id, res['data'][0]['picture_xl'],
                                                                       reply_markup=inline_keyboard(message, 0))
                        else:
                            raise FileExistsError
                elif choice == 'track?q=':
                    data_songs[message.chat.id] = [{'id': i['id'], 'title': i['title'], 'name': i['artist']['name'],
                                                    'link': i['link'], 'preview': i['preview'],
                                                    'duration': i['duration']} for i in res['data']]
                    create_data_song(message)
                    if data_songs[message.chat.id]:
                        if message.chat.id in song_msg:
                            bot.delete_message(song_msg[message.chat.id].chat.id, song_msg[message.chat.id].message_id)
                        song_msg[message.chat.id] = bot.send_message(message.chat.id,
                                                                     f'Результат поиска <b>{message.text}</b>🔎',
                                                                     parse_mode='HTML',
                                                                     reply_markup=inline_keyboard(message, 0))
                    else:
                        raise FileExistsError
                else:
                    raise FileExistsError
            else:
                raise FileExistsError
        except FileExistsError:
            bot.send_message(message.chat.id, 'К сожеления ничего не нашлось😔')


def create_data_song(message: Message) -> None:
    global data_songs
    list_music, buf = [], []
    for i, en in enumerate(data_songs[message.chat.id], 1):
        buf.append(en)
        if i % 5 == 0:
            list_music.append(buf.copy())
            buf.clear()
    if buf:
        list_music.append(buf.copy())
    data_songs[message.chat.id] = list_music.copy()


def inline_keyboard(message: Message, some_index) -> InlineKeyboardMarkup:  # Navigation for music
    global data_songs
    some_keyboard = InlineKeyboardMarkup()
    try:
        for songs in data_songs[message.chat.id][some_index]:
            some_keyboard.add(InlineKeyboardButton(f"{songs['name']} - {songs['title']}",
                                                   callback_data=f"ID: {songs['id']}"))
        some_keyboard.add(
            InlineKeyboardButton(text="⬅️️", callback_data=f"music_move_to {some_index - 1 if some_index > 0 else 'pass'}"),
            InlineKeyboardButton(text="➡️", callback_data=f"music_move_to "
                                 f"{some_index + 1 if some_index < len(data_songs[message.chat.id]) - 1 else 'pass'}"))
        return some_keyboard
    except KeyError:
        log('Key Error in music', 'warning')


@bot.callback_query_handler(func=lambda call: re.fullmatch(r'^music_move_to\s\d$', call.data))
def callback_query(call):
    global data_songs
    index = int(call.data.split()[1])
    if 0 <= index < len(data_songs[call.message.chat.id]):
        bot.answer_callback_query(call.id, f'Вы выбрали стр.{index + 1}')
        if call.message.content_type == 'photo':
            bot.edit_message_media(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                   media=InputMediaPhoto(call.message.photo[-1].file_id),
                                   reply_markup=inline_keyboard(call.message, index))
        else:
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  text=call.message.text,
                                  reply_markup=inline_keyboard(call.message, index))
    else:
        bot.answer_callback_query(call.id, '⛔️')


@bot.callback_query_handler(func=lambda call: re.fullmatch(r'^ID:\s?\d+$', call.data))
def callback_query(call):
    song_id = call.data.replace('ID: ', '')
    global data_songs
    for song in data_songs[call.message.chat.id]:
        for item in song:
            if item['id'] == int(song_id):
                for i in range(5):
                    try:
                        res = YoutubeUnlimitedSearch(f'{item["name"]} - {item["title"]}', max_results=1).get()
                        yt = YouTube('https://' + 'www.youtube.com/' + res[0]['link'])
                    except (KeyError, IndexError):
                        continue
                    else:
                        bot.answer_callback_query(call.id, 'Вы выбрали ' + item["name"] + ' - ' + item["title"])
                        bot.send_chat_action(call.message.chat.id, 'upload_audio')
                        keyboard = InlineKeyboardMarkup(row_width=2)
                        keyboard.add(InlineKeyboardButton('Текст', callback_data=f'Lyric music {str(song_id)}'),
                                     InlineKeyboardButton('Dezeer', url=item['link']))
                        bot.send_audio(call.message.chat.id, audio=open(yt.streams.filter(
                            only_audio=True)[0].download(filename='file'), 'rb'),
                                       reply_markup=keyboard, performer=item['name'],
                                       title=item['title'], duration=item['duration'],
                                       caption=f'🎧 {sec_to_time(yt.length)} '
                                               f'| {round(os.path.getsize("file.mp4") / 1000000, 1)} MB |'
                                               f' {yt.streams.filter(only_audio=True)[0].abr.replace("kbps", "")}'
                                               f' Kbps')
                        try:
                            os.remove(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'file' + '.mp4'))
                        except (FileNotFoundError, NameError):
                            log('Error! Can\'t remove file', 'warning')
                        break
                else:
                    bot.answer_callback_query(call.id, 'В данный момент трек не доступен😔')
    else:
        bot.answer_callback_query(call.id, 'Список песен пуст, выполните поиск заново😔')



# <<< End music >>>


# <<< Lyric >>>
@bot.callback_query_handler(func=lambda call: re.fullmatch(r'^Lyric\s\w+\s\d+$', call.data))
def callback_query(call):
    """
   :param call
   :return: None
   .. seealso:: Get lyric from song
   .. notes:: Api: https://api.audd.io/
   """
    global data_songs, data_detect
    type_lyric, song_id = call.data.split()[1:]
    keyboard = InlineKeyboardMarkup()
    res = None
    if type_lyric == 'music':
        for song in data_songs[call.message.chat.id]:
            for item in song:
                if item['id'] == int(song_id):
                    bot.answer_callback_query(call.id, f'Текст {item["name"]} - {item["title"]}')
                    res = requests.get(API['AUDD'] + 'findLyrics/?q=' + item['name'] + ' ' + item['title']).json()
    elif type_lyric == 'detect':
        res = requests.get(API['AUDD'] + 'findLyrics/?q=' + data_detect[call.message.chat.id]['result']['artist'] + ' ' +
                           data_detect[call.message.chat.id]['result']['title']).json()
    if res['status'] == 'success' and res['result'] is not None:
        msg = bot.reply_to(call.message, res['result'][0]['lyrics'])
        keyboard.add(InlineKeyboardButton('Удалить', callback_data=f'del {msg.message_id}'))
        bot.edit_message_text(chat_id=msg.chat.id, message_id=msg.message_id,
                              text=msg.text,
                              reply_markup=keyboard)

# <<< End lyric >>>


# <<< Loli&Hentai&Girl >>>
@bot.message_handler(commands=['loli'])
@bot.message_handler(commands=['girl'])
@bot.message_handler(commands=['hentai'])
def forbidden_handler(message: Message) -> None:
    """
    :param message
    :type message: telebot.types.Message
    :return: None
    .. seealso:: Enter /{command} to get random hentai(18+) or loli(18+), or girl(18+). Access is limited
    """
    if str(dt.fromtimestamp(message.date).strftime('%Y-%m-%d %H:%M')) == str(dt.now().strftime('%Y-%m-%d %H:%M')):
        log(message, 'info')
        keyboard = InlineKeyboardMarkup()
        db.add_user(message.from_user) if message.chat.type == 'private' else db.add_user(message.from_user, message.chat)
        setting = db.get_setting(message.chat.id)
        if setting['censure'] == 'Off':
            if message.chat.type != 'private':
                db.change_karma(message.from_user.id, '-', 10)
            while True:
                if message.text.lower() in ['/loli', 'лоли', 'loli', '/loli@gntmbot', '/loli@pineapple_test_bot']:
                    data = db.get_forbidden('loli')
                elif message.text.lower() in ['/hentai', 'хентай', 'hentai', '/hentai@gntmbot', '/hentai@pineapple_test_bot']:
                    data = db.get_forbidden('hentai')
                else:
                    data = db.get_forbidden('girls')
                try:
                    if requests.get(data).ok:
                        msg = bot.send_photo(message.chat.id, data)
                        keyboard.add((InlineKeyboardButton('Удалить',
                                                           callback_data=f'del {msg.message_id} {message.message_id}')))
                        bot.edit_message_media(chat_id=msg.chat.id, message_id=msg.message_id,
                                               media=InputMediaPhoto(msg.photo[-1].file_id),
                                               reply_markup=keyboard)
                        break
                except Exception:
                    continue
        else:
            bot.send_message(message.chat.id, 'Цензура включена, функция недоступна😔\nОтключить цензуру можно <i>/settings</i>',
                            parse_mode='HTML')

# <<< End loli&hentai&girl >>>


# <<< News >>>
news = defaultdict(list)
news_msg = defaultdict(Message)


@bot.message_handler(commands=['news'])
def news_handler(message: Message) -> None:
    """
    :param message
    :type message: telebot.types.Message
    :return: None
    .. seealso:: Enter /news to get news in 8th different categories and links on themd
    .. notes:: Api: https://newsapi.org
    """
    if str(dt.fromtimestamp(message.date).strftime('%Y-%m-%d %H:%M')) == str(dt.now().strftime('%Y-%m-%d %H:%M')):
        if message.chat.type != 'private':
            db.change_karma(message.from_user.id, '+', 1)
        log(message, 'info')
        db.add_user(message.from_user) if message.chat.type == 'private' else db.add_user(message.from_user, message.chat)
        keyboard = InlineKeyboardMarkup(row_width=2)
        keyboard.add(InlineKeyboardButton('Технологии', callback_data='News technology'),
                     InlineKeyboardButton('Наука', callback_data='News science'))
        keyboard.add(InlineKeyboardButton('Здоровье', callback_data='News health'),
                     InlineKeyboardButton('Общие', callback_data='News general'))
        keyboard.add(InlineKeyboardButton('Развлечения', callback_data='News entertainment'),
                     InlineKeyboardButton('Спорт', callback_data='News sports'))
        bot.send_message(message.chat.id, '<b>Подборка новостей</b>', reply_markup=keyboard, parse_mode='HTML')


def main_news(message: Message, news_type: str) -> None:
    global news
    global news_msg
    setting = db.get_setting(message.chat.id)
    api = API['News']['URL'].replace('Country', f'{"ua" if setting["news"] == "Ua" else "ru" if setting["news"] == "Ru" else "us"}')
    res = requests.get(api.replace('Method', f'{news_type}') + API['News']['Api_Key']).json()
    if res['status'] == 'ok':
        news[message.chat.id] = [{'title': i['title'], 'description': i['description'],
                                  'url': i['url'], 'image': i['urlToImage'], 'published': i['publishedAt']} for i in
                                 res['articles']]
    for i in news[message.chat.id]:
        if i['image'] is not None:
            i['title'] = clear_link(i['title'])
            if i['description'] is not None:
                i['description'] = clear_link(i['description'])
    news_msg[message.chat.id] = bot.send_photo(message.chat.id, API['News']['image'])
    send_news(message, 0)


def send_news(message: Message, index: int) -> None:
    keyboard2 = InlineKeyboardMarkup()
    keyboard2.add(
        InlineKeyboardButton(text="⬅️️", callback_data=f"news_move_to {index - 1 if index > 0 else 'pass'}"),
        InlineKeyboardButton(text="➡️", callback_data=f"news_move_to "
                                                      f"{index + 1 if index < len(news[message.chat.id]) - 1 else 'pass'}"))
    if news[message.chat.id][index]['title'] == news[message.chat.id][index + 1]['title']:
        news[message.chat.id].pop(index)
        send_news(message, index + 1)
        return
    else:
        try:
            if requests.get(news[message.chat.id][index]['url']).ok:
                keyboard2.add(InlineKeyboardButton('Читать', url=news[message.chat.id][index]['url']))
        except (requests.exceptions.ConnectionError, requests.exceptions.MissingSchema):
            news[message.chat.id].pop(index)
            send_news(message, index + 1)
            return
        except IndexError:
            log('Index Error in news url', 'warning')
        if news[message.chat.id][index]['image'] is None or news[message.chat.id][index]['image'] == '':
            if news[message.chat.id][index]['description'] is not None:
                bot.edit_message_media(chat_id=news_msg[message.chat.id].chat.id,
                                       message_id=news_msg[message.chat.id].message_id,
                                       media=InputMediaPhoto(API['News']['image'],
                                                             caption=f"<b>{news[message.chat.id][index]['title']}</b>"
                                                                     f"\n\n{news[message.chat.id][index]['description']}"
                                                                     f"\n\n<i>{clear_date(news[message.chat.id][index]['published'])}</i>",
                                                             parse_mode='HTML'), reply_markup=keyboard2)
            else:
                bot.edit_message_media(chat_id=news_msg[message.chat.id].chat.id,
                                       message_id=news_msg[message.chat.id].message_id,
                                       media=InputMediaPhoto(API['News']['image'],
                                                             caption=f"<b>{news[message.chat.id][index]['title']}</b>\n<i>\n"
                                                                     f"{clear_date(news[message.chat.id][index]['published'])}</i>",
                                                             parse_mode='HTML'), reply_markup=keyboard2)
        else:
            try:
                if requests.get(news[message.chat.id][index]['image']).ok is True:
                    req = request.Request(news[message.chat.id][index]['image'], method='HEAD')
                    f = request.urlopen(req)
                    if f.headers['Content-Length'] is not None:
                        if int(f.headers['Content-Length']) > 5242880:
                            news[message.chat.id].pop(index)
                            send_news(message, index + 1)
                            return
                    else:
                        news[message.chat.id].pop(index)
                        send_news(message, index + 1)
                        return
                else:
                    news[message.chat.id].pop(index)
                    send_news(message, index + 1)
                    return
            except (requests.exceptions.ConnectionError, requests.exceptions.MissingSchema, error.URLError,
                    UnicodeEncodeError):
                news[message.chat.id].pop(index)
                send_news(message, index + 1)
                return
            except IndexError:
                log('Index Error in news', 'warning')
            try:
                if news[message.chat.id][index]['description'] is not None:
                    bot.edit_message_media(chat_id=news_msg[message.chat.id].chat.id,
                                           message_id=news_msg[message.chat.id].message_id,
                                           media=InputMediaPhoto(news[message.chat.id][index]['image'],
                                           caption=f"<b>{news[message.chat.id][index]['title']}</b>"
                                                   f"\n\n{news[message.chat.id][index]['description']}"
                                                   f"\n\n<i>{clear_date(news[message.chat.id][index]['published'])}</i>",
                                           parse_mode='HTML'), reply_markup=keyboard2)
                else:
                    bot.edit_message_media(chat_id=news_msg[message.chat.id].chat.id,
                                           message_id=news_msg[message.chat.id].message_id,
                                           media=InputMediaPhoto(news[message.chat.id][index]['image'],
                                           caption=f"<b>{news[message.chat.id][index]['title']}</b>\n<i>"
                                                   f"{clear_date(news[message.chat.id][index]['published'])}</i>",
                                           parse_mode='HTML'), reply_markup=keyboard2)
            except Exception:
                news[message.chat.id].pop(index)
                send_news(message, index + 1)


@bot.callback_query_handler(func=lambda call: re.fullmatch(r'^News\s?\w+$', call.data))
def choice_news_query(call):
    global news_msg
    bot.delete_message(call.message.chat.id, call.message.message_id)
    bot.answer_callback_query(call.id, f'Вы выбрали стр.1')
    if call.message.chat.id in news_msg:
        bot.delete_message(news_msg[call.message.chat.id].chat.id, news_msg[call.message.chat.id].message_id)
    main_news(call.message, call.data.split()[1])



@bot.callback_query_handler(func=lambda call: re.fullmatch(r'^news_move_to\s\d+$', call.data))
def next_news_query(call):
    global news
    index = int(call.data.split()[1])
    if 0 <= index < len(news[call.message.chat.id]) - 1:
        bot.answer_callback_query(call.id, f'Вы выбрали стр.{index + 1}')
        send_news(call.message, index)
    else:
        bot.answer_callback_query(call.id, '⛔️')


# <<< End news >>>


# <<< YouTube >>>
@bot.message_handler(commands=['youtube'])
def youtube_handler(message: Message) -> None:
    """
    :param message
    :type message: telebot.types.Message
    :return: None
    .. seealso::  Enter /youtube to get audio or video from youtube link
    .. notes:: Lib: PyTube
    """
    if str(dt.fromtimestamp(message.date).strftime('%Y-%m-%d %H:%M')) == str(dt.now().strftime('%Y-%m-%d %H:%M')):
        if message.chat.type != 'private':
            db.change_karma(message.from_user.id, '+', 1)
        log(message, 'info')
        db.add_user(message.from_user) if message.chat.type == 'private' else db.add_user(message.from_user, message.chat)
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton('Видео📺', callback_data='Video'),
                     InlineKeyboardButton('Аудио🎧', callback_data='Audio'))
        bot.send_message(message.chat.id, 'Выберите что вам отправить🧐', reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: call.data == 'Audio' or call.data == 'Video')
def youtube_call(call):
    bot.answer_callback_query(call.id, 'Вы выбрали ' + tr_w(call.data))
    bot.delete_message(call.message.chat.id, call.message.message_id)
    link = bot.send_message(call.message.chat.id, 'Отправьте мне ссылку на видео🔗')
    bot.register_next_step_handler(link, send_audio, call.data, link.message_id)


def send_audio(message: Message, method: str, message_id: int) -> None:
    if message.content_type != 'text':
        bot.send_message(message.chat.id, 'Не верный формат данных😔')
    else:
        if re.fullmatch(r'^https?://.*[\r\n]*$', message.text):
            keyboard = InlineKeyboardMarkup()
            keyboard.add(InlineKeyboardButton('YouTube', url=message.text))
            for i in range(5):
                try:
                    yt = YouTube(message.text)
                except error.HTTPError:
                    bot.send_message(message.chat.id, 'Не могу найти файл😔')
                    break
                except exceptions.RegexMatchError:
                    bot.send_message(message.chat.id, 'Не верный формат ссылки😔')
                    break
                except KeyError:
                    continue
                else:
                    if method == 'Audio':
                        bot.send_chat_action(message.chat.id, 'upload_audio')
                        yt.streams.filter(only_audio=True)[0].download(filename='file')
                        if round(os.path.getsize("file.mp4") / 1000000, 1) < 50:
                            bot.send_audio(message.chat.id, open('file.mp4', 'rb'),
                                           reply_markup=keyboard, duration=yt.length, title=yt.title, performer=yt.author,
                                           caption=f'🎧 {sec_to_time(yt.length)} '
                                                   f'| {round(os.path.getsize("file.mp4") / 1000000, 1)} MB |'
                                                   f' {yt.streams.filter(only_audio=True)[0].abr.replace("kbps", "")} Kbps')
                            bot.delete_message(message.chat.id, message.message_id)
                            bot.delete_message(message.chat.id, message_id)
                        else:
                            bot.send_message(message.chat.id, 'Размер файла слишком большой😔')
                        try:
                            os.remove(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'file' + '.mp4'))
                        except (FileNotFoundError, NameError):
                            log('Error! Can\'t remove file', 'warning')
                        break
                    else:
                        try:
                            resolution = '480p'
                            yt.streams.filter(res="480p").order_by('resolution').desc()[0].download(filename='video')
                        except (error.HTTPError, IndexError):
                            try:
                                resolution = '320p'
                                yt.streams.filter(res="320p").order_by('resolution').desc()[0].download(filename='video')
                            except (error.HTTPError, IndexError):
                                try:
                                    resolution = '240p'
                                    yt.streams.filter(res="240p").order_by('resolution').desc()[0].download(filename='video')
                                except (error.HTTPError, IndexError):
                                    try:
                                        resolution = '144p'
                                        yt.streams.filter(res="144p").order_by('resolution').desc()[0].download(filename='video')
                                    except error.HTTPError:
                                        bot.send_message(message.chat.id, 'Не могу найти файл😔')
                                    except IndexError:
                                        bot.send_message(message.chat.id, 'Размер видео слишком большой😔')
                                    else:
                                        load_video(message, yt, keyboard, resolution)
                                        bot.delete_message(message.chat.id, message_id)
                                        break
                                else:
                                    load_video(message, yt, keyboard, resolution)
                                    bot.delete_message(message.chat.id, message_id)
                                    break
                            else:
                                load_video(message, yt, keyboard, resolution)
                                bot.delete_message(message.chat.id, message_id)
                                break
                        else:
                            load_video(message, yt, keyboard, resolution)
                            bot.delete_message(message.chat.id, message_id)
                            break
        else:
            bot.send_message(message.chat.id, 'Не верный формат данных😔')


def load_video(message: Message, yt, keyboard, resolution):
    yt.streams.filter(only_audio=True)[0].download(filename='audio')
    ffmpeg_work = Thread(target=ffmpeg_run, name='ffmpeg_work')
    msg = bot.send_message(message.chat.id, 'Загрузка...')
    ffmpeg_work.start()
    ffmpeg_work.join()
    time.sleep(1)
    if round(os.path.getsize("file.mp4") / 1000000, 1) < 50:
        bot.delete_message(message.chat.id, message.message_id)
        bot.delete_message(msg.chat.id, msg.message_id)
        bot.send_video(message.chat.id, open('file.mp4', 'rb'),
                       duration=yt.length, reply_markup=keyboard,
                       caption=f'🎧 {sec_to_time(yt.length)} '
                               f'| {round(os.path.getsize("file.mp4") / 1000000, 1)} MB '
                               f'| {yt.streams.filter(only_audio=True)[0].abr.replace("kbps", "")} Kbps '
                               f'| {resolution}')
    else:
        bot.send_message(message.chat.id, 'Даное видео имеет слигком большой объем,'
                                          ' мой лимит 50МБ😔')
    try:
        for i in os.listdir(os.path.dirname(__file__)):
            if i.startswith('video') or i.startswith('audio') or i.startswith('file'):
                os.remove(os.path.join(os.path.abspath(os.path.dirname(__file__)), i))
    except (FileNotFoundError, NameError):
        log('Error! Can\'t remove file', 'warning')


def ffmpeg_run():
    input_audio, input_video = None, None
    for i in os.listdir(os.path.dirname(__file__)):
        if i.startswith('audio'):
            input_audio = ffmpeg.input(i)
        elif i.startswith('video'):
            input_video = ffmpeg.input(i)
    input_video = ffmpeg.filter(input_video, 'fps', fps=25, round='up')
    ffmpeg.output(input_video, input_audio, "file.mp4", preset='faster',
                  vcodec='libx264', acodec='mp3', **{'qscale:v': 10}).run(overwrite_output=True)


# <<< End YouTube >>>


# <<< Instagram >>>
msg_instagram = defaultdict(Message)


@bot.message_handler(commands=['instagram'])
def instagram_handler(message: Message) -> None:
    """
    :param message
    :type message: telebot.types.Message
    :return: None
    .. seealso::  Enter /instagram to get photo(s) or video(s) from instagram link
    """
    if str(dt.fromtimestamp(message.date).strftime('%Y-%m-%d %H:%M')) == str(dt.now().strftime('%Y-%m-%d %H:%M')):
        if message.chat.type != 'private':
            db.change_karma(message.from_user.id, '+', 1)
        log(message, 'info')
        db.add_user(message.from_user) if message.chat.type == 'private' else db.add_user(message.from_user, message.chat)
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton('Фото📷', callback_data='Instagram photo'),
                     InlineKeyboardButton('Видео📹', callback_data='Instagram video'))
        msg_instagram[message.chat.id] = bot.send_message(message.chat.id, '<b>Что вы хотите получить</b>',
                                                          parse_mode='HTML', reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: re.fullmatch(r'Instagram\s\w+', call.data))
def callback_query(call):
    bot.delete_message(msg_instagram[call.message.chat.id].chat.id, msg_instagram[call.message.chat.id].message_id)
    msg = bot.send_message(call.message.chat.id, 'Отправьте мне ссылку✒️')
    if call.data.split()[1] == 'video':
        bot.answer_callback_query(call.id, 'Вы выбрали видео')
        bot.register_next_step_handler(msg, get_instagram_video, msg.message_id)
    else:
        bot.answer_callback_query(call.id, 'Вы выбрали фото')
        bot.register_next_step_handler(msg, get_instagram_photo, msg.message_id)


def get_instagram_video(message: Message, message_id: str) -> None:
    if message.content_type != 'text':
        bot.send_message(message.chat.id, 'Не верный формат данных😔')
    else:
        if re.match(r'^https?://(www.)?instagram.com/\w+/.+', message.text):
            url = re.search(r'^https?://(www.)?instagram.com/\w+/.+/', message.text).group(0)
            bot.delete_message(message.chat.id, message_id)
            bot.delete_message(message.chat.id, message.message_id)
            if url is not None:
                try:
                    data = get_instagram_videos(url)
                except JSONDecodeError:
                    bot.send_message(message.chat.id, 'Не поддерживаются работа закрытыми аккаунтами😔')
                else:
                    if data:
                        bot.send_chat_action(message.chat.id, 'upload_video')
                        if len(data) == 1:
                            if data[0]['is_video'] is True:
                                try:
                                    keyboard = InlineKeyboardMarkup()
                                    keyboard.add(InlineKeyboardButton('Instagram', url=url))
                                    bot.send_video(message.chat.id, data[0]['url'], reply_markup=keyboard)
                                except Exception:
                                    bot.send_message(message.chat.id, 'Размер видео слишком большой😔')
                            else:
                                bot.send_message(message.chat.id, 'По ссылке нет видео😔')
                        else:
                            list_data = []
                            for i in data:
                                if i['is_video'] is True:
                                    list_data.append(InputMediaVideo(i['url']))
                                else:
                                    list_data.append(InputMediaPhoto(i['url']))
                            try:
                                bot.send_media_group(message.chat.id, list_data)
                            except Exception:
                                bot.send_message(message.chat.id, 'Размер медиа данных слишком большой😔')
                    else:
                        bot.send_message(message.chat.id, 'По ссылке ничего не обнаружено😔')
            else:
                bot.send_message(message.chat.id, 'Не смог получить данные😔')
        else:
            bot.send_message(message.chat.id, 'Не верный формат ссылки😔')


def get_instagram_photo(message: Message, message_id: str) -> None:
    bot.send_chat_action(message.chat.id, 'upload_photo')
    if re.match(r'^https?://(www.)?instagram.com/\w+/.+', message.text):
        url = re.search(r'^https?://(www.)?instagram.com/\w+/.+/', message.text).group(0)
        bot.delete_message(message.chat.id, message_id)
        bot.delete_message(message.chat.id, message.message_id)
        if url is not None:
            try:
                data = get_instagram_photos(url)
            except JSONDecodeError:
                bot.send_message(message.chat.id, 'Не поддерживаются работа закрытыми аккаунтами😔')
            else:
                if data:
                    if len(data) == 1:
                        keyboard = InlineKeyboardMarkup()
                        keyboard.add(InlineKeyboardButton('Instagram', url=url))
                        bot.send_photo(message.chat.id, data[0], reply_markup=keyboard)
                    else:
                        bot.send_media_group(message.chat.id, [InputMediaPhoto(photo) for photo in data])
                else:
                    bot.send_message(message.chat.id, 'По данной ссылке фотографий не найдено😔')
        else:
            bot.send_message(message.chat.id, 'Не смог получить данные😔')
    else:
        bot.send_message(message.chat.id, 'Не верный формат ссылки😔')


# <<< End Instagram >>>


# <<< Torrent >>>
data_torrents = defaultdict(dict)
torrent_msg = defaultdict(Message)
search_msg = defaultdict(str)
tracker = defaultdict(str)
search = defaultdict(Message)


@bot.message_handler(commands=['torrent'])
def torrents_handler(message: Message) -> None:
    """
    :param message
    :type message: telebot.types.Message
    :return: None
    .. seealso:: Enter /torrent to search torrents on Rutor.info, GTorrent.ru or Gamestracker.org
    """
    if str(dt.fromtimestamp(message.date).strftime('%Y-%m-%d %H:%M')) == str(dt.now().strftime('%Y-%m-%d %H:%M')):
        if message.chat.type != 'private':
            db.change_karma(message.from_user.id, '+', 1)
        log(message, 'info')
        db.add_user(message.from_user) if message.chat.type == 'private' else db.add_user(message.from_user, message.chat)
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton('Rutor.info🇷🇺', callback_data='Rutor.info'))
        keyboard.add(InlineKeyboardButton('GTorrent.ru🇷🇺', callback_data='GTorrent.ru'))
        keyboard.add(InlineKeyboardButton('Gamestracker.org🇷🇺', callback_data='Gamestracker.org'))
        search[message.chat.id] = bot.send_message(message.chat.id, 'Выберите платформу️', reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: call.data in ['Gamestracker.org', 'GTorrent.ru', 'Rutor.info'])
def callback_query(call):
    global tracker, search
    bot.delete_message(search[call.message.chat.id].chat.id, search[call.message.chat.id].message_id)
    tracker[call.message.chat.id] = call.data
    msg = bot.send_message(call.message.chat.id, 'Введите ваш запрос✒️')
    bot.register_next_step_handler(msg, send_urls)


def send_urls(message: Message) -> None:
    global data_torrents, torrent_msg, tracker
    if message.content_type != 'text':
        bot.send_message(message.chat.id, 'Не верный формат данных😔')
    else:
        search_msg[message.chat.id] = message.text
        if message.chat.id in data_torrents:
            bot.delete_message(torrent_msg[message.chat.id].chat.id, torrent_msg[message.chat.id].message_id)
        try:
            if tracker[message.chat.id] == URLS['torrent']['name']:
                data_torrents[message.chat.id] = get_torrents1(message.text)
            elif tracker[message.chat.id] == URLS['torrent2']['name']:
                data_torrents[message.chat.id] = get_torrents2(message.text)
            elif tracker[message.chat.id] == URLS['torrent3']['name']:
                data_torrents[message.chat.id] = get_torrents3(message.text)
        except requests.exceptions.ConnectionError:
            bot.send_message(message.chat.id, 'Возникла непредвиденная ошибка😔')
        else:
            if data_torrents[message.chat.id]:
                create_data_torrents(message)
                torrent_msg[message.chat.id] = bot.send_message(message.chat.id, 'Загрузка...')
                torrent_keyboard(torrent_msg[message.chat.id], 0)
            else:
                torrent_msg[message.chat.id] = bot.send_message(message.chat.id, 'Ничего не нашлось😔')


def create_data_torrents(message: Message) -> None:
    global data_torrents
    list_torrent, buf = [], []
    for i, en in enumerate(data_torrents[message.chat.id], 1):
        buf.append(en)
        if i % 5 == 0:
            list_torrent.append(buf.copy())
            buf.clear()
    if buf:
        list_torrent.append(buf.copy())
    data_torrents[message.chat.id] = list_torrent.copy()


def torrent_keyboard(message: Message, index: int) -> None:
    global data_torrents, torrent_msg, search_msg, tracker
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton(text="⬅️️", callback_data=f"torrent_move_to {index - 1 if index > 0 else 'pass'}"),
                 InlineKeyboardButton(text="➡️", callback_data=f"torrent_move_to "
                                      f"{index + 1 if index < len(data_torrents[message.chat.id]) - 1 else 'pass'}"))
    text_t = None
    if tracker[message.chat.id] == URLS['torrent']['name']:
        text_t = f'<a href="{URLS["torrent"]["main"]}">{tracker[message.chat.id]}🇷🇺</a>\nРезультат поиска <b>' \
                 f'{search_msg[message.chat.id]}</b>'
    elif tracker[message.chat.id] == URLS['torrent2']['name']:
        text_t = f'<a href="{URLS["torrent2"]["main"]}">{tracker[message.chat.id]}🇷🇺</a>\nРезультат поиска <b>' \
                 f'{search_msg[message.chat.id]}</b>'
    elif tracker[message.chat.id] == URLS['torrent3']['name']:
        text_t = f'<a href="{URLS["torrent3"]["main"]}">{tracker[message.chat.id]}🇷🇺</a>\nРезультат поиска <b>' \
                 f'{search_msg[message.chat.id]}</b>'
    try:
        for i in data_torrents[message.chat.id][index]:
            if tracker[message.chat.id] == 'GTorrent.ru':
                text_t += f'\n\n{i["name"]} | [{i["size"]}] \n[<i>/download_{i["link_t"]}</i>] ' \
                          f'[<a href="{i["link"]}">раздача</a>]'
            elif tracker[message.chat.id] == 'Gamestracker.org':
                link_t = i["link_t"].split('-')
                link_t = link_t[-2] + '_' + link_t[-1]
                text_t += f'\n\n{i["name"]} | {i["size"]} \n[<i>/download_{link_t}</i>] ' \
                          f'[<a href="{i["link"]}">раздача</a>]'
            elif tracker[message.chat.id] == 'Rutor.info':
                text_t += f'\n\n{i["name"]} | [{i["size"]}] \n[<i>/download__{i["link_t"].split("/")[-1]}</i>] ' \
                          f'[<a href="{i["link"]}">раздача</a>]'
    except KeyError:
        log('Key Error in torrents', 'warning')
    else:
        bot.edit_message_text(chat_id=torrent_msg[message.chat.id].chat.id,
                                                 message_id=torrent_msg[message.chat.id].message_id,
                                                 text=text_t, reply_markup=keyboard, parse_mode='HTML',
                                                 disable_web_page_preview=True)


@bot.message_handler(func=lambda message: re.match(r'^/\w{8}_\d+_\d+$', str(message.text), flags=re.M))
def load_handler(message: Message):
    global data_torrents
    id_torrent =  message.text.split("_")[1] + '-' +  message.text.split("_")[2]
    for torrent in data_torrents[message.chat.id]:
        for item in torrent:
            if item['link_t'].endswith(id_torrent):
                with open(f'file{id_torrent}.torrent', 'wb') as f:
                    for link in requests.get(URLS['torrent3']['download'] + id_torrent, stream=True).iter_content(1024):
                        f.write(link)
                bot.send_document(message.chat.id, open(f'file{id_torrent}.torrent', 'rb'))
                try:
                    os.remove(os.path.join(os.path.abspath(os.path.dirname(__file__)), f'file{id_torrent}.torrent'))
                except (FileNotFoundError, NameError):
                    log('Error! Can\'t remove file', 'warning')


@bot.message_handler(func=lambda message: re.match(r'^/\w{8}__\d+$', str(message.text), flags=re.M))
def load_handler(message: Message):
    id_torrent = message.text.split("_")[-1]
    with open(f'file{id_torrent}.torrent', 'wb') as f:
        for torrent in requests.get(URLS['torrent3']['download'] + id_torrent, stream=True).iter_content(1024):
            f.write(torrent)
    bot.send_document(message.chat.id, open(f'file{id_torrent}.torrent', 'rb'))
    try:
        os.remove(os.path.join(os.path.abspath(os.path.dirname(__file__)), f'file{id_torrent}.torrent'))
    except (FileNotFoundError, NameError):
        log('Error! Can\'t remove file', 'warning')


@bot.message_handler(func=lambda message: re.match(r'^/\w{8}_\d+$', str(message.text), flags=re.M))
def load_handler(message: Message):
    id_torrent = message.text.split("_")[1]
    with open(f'file{id_torrent}.torrent', 'wb') as f:
        for torrent in requests.get(URLS['torrent3']['download'] + id_torrent, stream=True).iter_content(1024):
            f.write(torrent)
    bot.send_document(message.chat.id, open(f'file{id_torrent}.torrent', 'rb'))
    try:
        os.remove(os.path.join(os.path.abspath(os.path.dirname(__file__)), f'file{id_torrent}.torrent'))
    except (FileNotFoundError, NameError):
        log('Error! Can\'t remove file', 'warning')


@bot.callback_query_handler(func=lambda call: re.fullmatch(r'^torrent_move_to\s\d+$', call.data))
def callback_query(call):
    global data_torrents
    index = int(call.data.split()[1])
    if 0 <= index < len(data_torrents[call.message.chat.id]):
        bot.answer_callback_query(call.id, f'Вы выбрали стр.{index + 1}')
        torrent_keyboard(call.message, index)
    else:
        bot.answer_callback_query(call.id, '⛔️')


# <<< End torrent >>>


# <<< Translate >>>
@bot.message_handler(commands=['translate'])
def translate_handler(message: Message) -> None:
    """
    :param message
    :type message: telebot.types.Message
    :return: None
    .. seealso:: Enter /translate to translate any sentence on any leng to russian or russian sentence to english
    """
    if str(dt.fromtimestamp(message.date).strftime('%Y-%m-%d %H:%M')) == str(dt.now().strftime('%Y-%m-%d %H:%M')):
        if message.chat.type != 'private':
            db.change_karma(message.from_user.id, '+', 1)
        log(message, 'info')
        db.add_user(message.from_user) if message.chat.type == 'private' else db.add_user(message.from_user, message.chat)
        bot.send_chat_action(message.chat.id, 'typing')
        msg = bot.send_message(message.chat.id, 'Введите то что нужно перевести👁‍🗨')
        bot.register_next_step_handler(msg, trans_word)


def trans_word(message: Message) -> None:  # Translate function
    bot.send_chat_action(message.chat.id, 'typing')
    bot.send_message(message.chat.id, tr_w(message.text))


# <<< End Translate >>>


# <<< Sticker GN >>>
@bot.message_handler(commands=['sticker_gn'])
def gn_sticker_handler(message: Message) -> None:
    """
    :param message
    :type message: telebot.types.Message
    :return: None
    .. seealso:: Enter /sticker_gn to get random sticker from GN, access limited
    """
    if str(dt.fromtimestamp(message.date).strftime('%Y-%m-%d %H:%M')) == str(dt.now().strftime('%Y-%m-%d %H:%M')):
        if message.chat.type != 'private':
            db.change_karma(message.from_user.id, '+', 1)
        log(message, 'info')
        db.add_user(message.from_user) if message.chat.type == 'private' else db.add_user(message.from_user, message.chat)
        if db.check(message.from_user.id, 'is_gn'):
            bot.send_sticker(message.chat.id, db.random_sticker(True))
        else:
            bot.send_message(message.chat.id, 'Эта функция вам недоступна😔')


# <<< End sticker GN >>>


# <<< Sticker >>>
@bot.message_handler(commands=['sticker'])
def sticker_handler(message: Message) -> None:
    """
    :param message
    :type message: telebot.types.Message
    :return: None
    .. seealso:: Enter /sticker to get random sticker
    """
    if str(dt.fromtimestamp(message.date).strftime('%Y-%m-%d %H:%M')) == str(dt.now().strftime('%Y-%m-%d %H:%M')):
        if message.chat.type != 'private':
            db.change_karma(message.from_user.id, '+', 1)
        log(message, 'info')
        db.add_user(message.from_user) if message.chat.type == 'private' else db.add_user(message.from_user, message.chat)
        bot.send_sticker(message.chat.id, db.random_sticker())


# <<< End sticker >>>


# <<< Add new sticker >>>
@bot.message_handler(content_types=['sticker'])
def add_sticker_handler(message: Message) -> None:
    """
    :param message
    :type message: telebot.types.Message
    :return: None
    .. seealso:: Send sticker in chat with bot to add him in our database
    """
    if message.chat.type != 'private':
        db.change_karma(message.from_user.id, '+', 1)
    db.add_user(message.from_user) if message.chat.type == 'private' else db.add_user(message.from_user, message.chat)
    db.add_sticker(message.sticker.file_id, message.sticker.emoji, message.sticker.set_name)


# <<< End add new sticker  >>>


# <<< Stat  >>>
stat_msg = defaultdict(Message)
com_stat_msg = defaultdict(Message)


@bot.message_handler(commands=['stat'])
def stat_handler(message: Message) -> None:
    """
    :param message
    :type message: telebot.types.Message
    :return: None
    .. seealso:: Enter /stat to see statistic in group
    """
    global stat_msg, com_stat_msg
    if str(dt.fromtimestamp(message.date).strftime('%Y-%m-%d %H:%M')) == str(dt.now().strftime('%Y-%m-%d %H:%M')):
        log(message, 'info')
        db.add_user(message.from_user) if message.chat.type == 'private' else db.add_user(message.from_user, message.chat)
        if message.chat.type != 'private':
            db.change_karma(message.from_user.id, '+', 1)
            data = db.get_stat(message.chat)
            if data:
                keyboard = InlineKeyboardMarkup()
                text = '<b>Статистика:</b>\n'
                for en, i in enumerate(data, 1):
                    if en == 6:
                        break
                    medal = '🥇' if en == 1 else '🥈' if en == 2 else '🥉' if en == 3 else None
                    text += f"<i>{en}.</i> {i['first_name']} {i['last_name'] if i['last_name'] != 'None' else ''}" \
                            f" - <i>{i['karma']}</i>{medal if medal is not None else ''}\n"
                text += '...\nНажмите /me что бы увидеть себя'
                msg = bot.send_message(message.chat.id, text, parse_mode='HTML')
                keyboard.add(InlineKeyboardButton('Закрыть', callback_data=f'del {msg.message_id} {message.message_id}'))
                bot.edit_message_text(chat_id=msg.chat.id, message_id=msg.message_id,
                                      text=msg.text,
                                      reply_markup=keyboard)
        else:
            bot.send_message(message.chat.id, 'Функция достпуна только в группах😔')


# <<< End Stat >>>


# <<< Me >>>
@bot.message_handler(commands=['me'])
def me_handler(message: Message) -> None:
    """
    :param message
    :type message: telebot.types.Message
    :return: None
    .. seealso:: Enter /me to see your stat in group
    """
    if str(dt.fromtimestamp(message.date).strftime('%Y-%m-%d %H:%M')) == str(dt.now().strftime('%Y-%m-%d %H:%M')):
        log(message, 'info')
        db.add_user(message.from_user) if message.chat.type == 'private' else db.add_user(message.from_user, message.chat)
        if message.chat.type != 'private':
            db.change_karma(message.from_user.id, '+', 1)
            keyboard = InlineKeyboardMarkup()
            data_user, position = db.get_user(message.from_user, message.chat)
            if data_user is not False or position is not False:
                    user = data_user['first_name']
                    user += f"{' ' + data_user['last_name']}" if data_user['last_name'] != 'None' else ''
                    msg = bot.send_message(message.chat.id, f'Ваш рейтинг:\n'
                                                            f'<i>{position}. </i>'
                                                            f'<b>{user}</b> - '
                                                            f'<i>{data_user["karma"]}</i>🏆',
                                                             parse_mode='HTML')
                    keyboard.add(InlineKeyboardButton('Закрыть', callback_data=f'del {msg.message_id} {message.message_id}'))
                    bot.edit_message_text(chat_id=msg.chat.id, message_id=msg.message_id,
                                          text=msg.text,
                                          reply_markup=keyboard)

        else:
            bot.send_message(message.chat.id, 'Функция достпуна только в группах😔')


# <<< End me >>>


# <<< Feedback >>>
@bot.message_handler(commands=['feedback'])
def feedback_handler(message: Message) -> None:
    """
    :param message
    :type message: telebot.types.Message
    :return: None
    .. seealso:: Enter /feedback to sand feedback to admin
    """
    if str(dt.fromtimestamp(message.date).strftime('%Y-%m-%d %H:%M')) == str(dt.now().strftime('%Y-%m-%d %H:%M')):
        db.change_karma(message.from_user.id, '+', 10)
        log(message, 'info')
        db.add_user(message.from_user) if message.chat.type == 'private' else db.add_user(message.from_user, message.chat)
        msg = bot.send_message(message.chat.id, '<b>Отправьте сообщение ниже</b>📝\n'
                                                'В кратчайшие сроки оно будет проверенно админитрацией🙃', parse_mode='HTML')
        bot.register_next_step_handler(msg, send_to_admin)


def send_to_admin(message: Message) -> None:
    bot.send_message(message.chat.id, 'Ваше сообщение отправленно😌')
    keyboard = InlineKeyboardMarkup()
    msg = bot.send_message(Admins[0], f'Вам пришел <b>feedback</b> от <b>{message.from_user.first_name}</b> '
                               f'<b>{message.from_user.last_name if message.from_user.last_name is not None else ""}</b>\n'
                               f'Текст: {message.text}')
    keyboard.add(InlineKeyboardButton('Ответить', callback_data=f'answer_feedback {message.chat.id}'))
    bot.edit_message_text(msg.text, msg.chat.id, msg.message_id, reply_markup=keyboard, parse_mode='HTML')


@bot.callback_query_handler(func=lambda call: re.fullmatch(r'^answer_feedback\s.+', call.data))
def answer_feedback_query(call):
    msg = bot.send_message(call.message.chat.id, '<b>Отправьте сообщение ниже</b>📝', parse_mode='HTML')
    bot.register_next_step_handler(msg, answer_feedback, call.data.split()[1])

def answer_feedback(message: Message, chat_id: str) -> None:
    bot.send_message(message.chat.id, 'Ваше сообщение отправленно😌')
    bot.send_message(chat_id, f"<b>На ваше сообщение ответили</b> \nОтвет: {message.text}\n\n<b>Спасибо за обращение</b>😏",
                     parse_mode='HTML')
# <<< End feedback >>>


# <<< Project Euler >>>
data_euler = defaultdict(list)


@bot.message_handler(commands=['euler'])
def euler_handler(message: Message) -> None:
    """
    :param message
    :type message: telebot.types.Message
    :return: None
    .. seealso:: Enter /euler to get random task from Project Euler
    """
    global data_euler
    if str(dt.fromtimestamp(message.date).strftime('%Y-%m-%d %H:%M')) == str(dt.now().strftime('%Y-%m-%d %H:%M')):
        if message.chat.type != 'private':
            db.change_karma(message.from_user.id, '+', 1)
        log(message, 'info')
        keyboard = InlineKeyboardMarkup()
        db.add_user(message.from_user) if message.chat.type == 'private' else db.add_user(message.from_user, message.chat)
        if message.chat.id not in data_euler or len(data_euler[message.chat.id]) == 1:
            data_euler[message.chat.id] = db.get_all('Project_Euler')
        task = data_euler[message.chat.id].pop(random.choice(range(len(data_euler[message.chat.id]) - 1)))
        data_msg = [bot.send_photo(message.chat.id, image) for image in  task['image_url'].split(',')]
        id_s = str(message.message_id)
        for i in data_msg:
            id_s += str(i.message_id) + ' '
        keyboard.add(InlineKeyboardButton('Ссылка', url=task['url']),
                     InlineKeyboardButton('Удалить', callback_data=f'del {id_s}'))
        if task['other'] != 'False':
            keyboard.add(InlineKeyboardButton(task['other'].split('/')[-1] if len(task['other'].split(',')) == 1 else 'Документы',
                                              callback_data=f'load doc {task["id"]}'))
        bot.edit_message_media(chat_id=data_msg[-1].chat.id, message_id=data_msg[-1].message_id,
                               media=InputMediaPhoto(data_msg[-1].photo[-1].file_id,
                               caption=f'<b>Задача</b> <i>№{task["id"]}</i>\n<b><i>{task["name"]}</i></b>'
                                       f'\n\nПоделиться решением <i>/code</i>', parse_mode='HTML'),
                               reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: re.fullmatch(r'^load\s\w+\s\d+$', call.data))
def answer_query(call):
    urls = db.get_doc(call.data.split()[2]).split(',')
    for url in urls:
        name = url.split('/')[-1]
        bot.answer_callback_query(call.id, name)
        with open(name, 'wb') as f:
            req = requests.get(url, stream=True)
            for i in req.iter_content(1024):
                f.write(i)
        try:
            bot.send_document(call.message.chat.id, data=open(name, 'rb'))
            os.remove(os.path.join(os.path.abspath(os.path.dirname(__file__)), name))
        except (FileNotFoundError, NameError):
            log('Error! Can\'t remove file', 'warning')
        except (FileNotFoundError, FileExistsError):
            log('Error! Can\'t find file', 'warning')
# <<< End project Euler >>>


# <<< Logic tasks >>>
data_logic_tasks = defaultdict(dict)


@bot.message_handler(commands=['logic'])
def logic_handler(message: Message) -> None:
    """
    :param message
    :type message: telebot.types.Message
    :return: None
    .. seealso:: Enter /logic to get random logic task
    """
    global data_logic_tasks
    if str(dt.fromtimestamp(message.date).strftime('%Y-%m-%d %H:%M')) == str(dt.now().strftime('%Y-%m-%d %H:%M')):
        if message.chat.type != 'private':
            db.change_karma(message.from_user.id, '+', 1)
        log(message, 'info')
        db.add_user(message.from_user) if message.chat.type == 'private' else db.add_user(message.from_user, message.chat)
        keyboard = InlineKeyboardMarkup()
        if message.chat.id not in data_logic_tasks or len(data_logic_tasks[message.chat.id]) == 1:
            data_logic_tasks[message.chat.id] = db.get_all('Logic_Tasks')
        task = data_logic_tasks[message.chat.id].pop(random.choice(range(len(data_logic_tasks[message.chat.id]) - 1)))
        msg = bot.send_message(message.chat.id,
                               f'<b>Задача №</b><i>{task["id"]}</i>\n'
                               f'{task["question"]}')
        keyboard.add(InlineKeyboardButton('Ответ', callback_data=f'Answer'
                                                                 f' {task["id"]} {message.message_id} {msg.message_id}'))
        bot.edit_message_text(chat_id=msg.chat.id, message_id=msg.message_id,
                              text=msg.text, reply_markup=keyboard, parse_mode='HTML')


@bot.callback_query_handler(func=lambda call: re.fullmatch(r'^Answer\s.+\s.+$', call.data))
def answer_query(call):
    global data_logic_tasks
    bot.answer_callback_query(call.id, 'Ответ')
    id_answer, id_command, id_question = call.data.split()[1:]
    keyboard = InlineKeyboardMarkup()
    msg = bot.send_message(call.message.chat.id, f'<b>Ответ:</b> {db.get_task_answer(id_answer)}')
    keyboard.add(InlineKeyboardButton('Удалить', callback_data=f'del {msg.message_id} {id_command} {id_question}'))
    bot.edit_message_text(chat_id=msg.chat.id, message_id=msg.message_id,
                          text=msg.text, reply_markup=keyboard, parse_mode='HTML')
# <<< End logic task >>>


# <<< Wiki >>>
data_wiki = defaultdict(list)
wiki_msg = defaultdict(Message)
page_msg = defaultdict(Message)
wiki_enter_msg = defaultdict(Message)


@bot.message_handler(commands=['wiki'])
def wiki_handler(message: Message) -> None:
    """
    :param message
    :type message: telebot.types.Message
    :return: None
    .. seealso:: Enter /wiki to get result from Wikipedia and choose page what you need to read it
    """
    if str(dt.fromtimestamp(message.date).strftime('%Y-%m-%d %H:%M')) == str(dt.now().strftime('%Y-%m-%d %H:%M')):
        if message.chat.type != 'private':
            db.change_karma(message.from_user.id, '+', 1)
        log(message, 'info')
        db.add_user(message.from_user) if message.chat.type == 'private' else db.add_user(message.from_user, message.chat)
        wiki_enter_msg[message.chat.id] = bot.send_message(message.chat.id, 'Введите запрос✒️')
        bot.register_next_step_handler(wiki_enter_msg[message.chat.id], get_titles)


def get_titles(message: Message) -> None:
    global data_wiki, wiki_msg
    bot.delete_message(wiki_enter_msg[message.chat.id].chat.id, wiki_enter_msg[message.chat.id].message_id)
    bot.delete_message(message.chat.id, message.message_id)
    wikipedia.set_lang("ru")
    try:
        data_wiki[message.chat.id] = wikipedia.search(message.text, results=100, suggestion=True)
    except requests.ConnectionError:
        bot.send_message(message.chat.id, 'Возникла не предвиденная ошибка😔')
        log('Connection error in  wiki', 'error')
    else:
        if data_wiki[message.chat.id][0]:
            list_wiki, buf = [], []
            for i, en in enumerate(data_wiki[message.chat.id][0], 1):
                buf.append(en)
                if i % 5 == 0:
                    list_wiki.append(buf.copy())
                    buf.clear()
            if buf:
                list_wiki.append(buf.copy())
            data_wiki[message.chat.id] = list_wiki.copy()
            if message.chat.id in wiki_msg:
                bot.delete_message(wiki_msg[message.chat.id].chat.id, wiki_msg[message.chat.id].message_id)
            wiki_msg[message.chat.id] = bot.send_message(message.chat.id, 'Результат поиска:',
                             reply_markup=send_wiki(message, 0))
        else:
            bot.send_message(message.chat.id, 'Ничего не нашлось😔')


def send_wiki(message: Message, index: int) -> None:
    global data_wiki, wiki_msg
    keyboard = InlineKeyboardMarkup()
    try:
        for en, wiki in enumerate(data_wiki[message.chat.id][index]):
            keyboard.add(InlineKeyboardButton(f"{wiki}", callback_data=f"Wiki: {index} {en}"))
        keyboard.add(InlineKeyboardButton(text="⬅️️", callback_data=f"wiki_move_to {index - 1 if index > 0 else 'pass'}"),
                     InlineKeyboardButton(text="➡️", callback_data=f"wiki_move_to "
                                            f"{index + 1 if index < len(data_wiki[message.chat.id]) - 1 else 'pass'}"))
        return keyboard
    except KeyError:
        log('Key Error in wiki', 'warning')


@bot.callback_query_handler(func=lambda call: re.fullmatch(r'^Wiki:\s\d+\s\d+$', call.data))
def wiki_query(call):
    global data_wiki, page_msg
    wiki = wikipediaapi.Wikipedia('ru')
    index1, index2 = call.data.split()[1:]
    try:
        page = wiki.page(data_wiki[call.message.chat.id][int(index1)][int(index2)].replace(' ', '_'),)
    except requests.exceptions.ConnectionError:
        bot.answer_callback_query(call.id, '⛔️')
        log('Connection error in  wiki', 'warning')
    except IndexError:
        bot.answer_callback_query(call.id, '⛔️')
        log('Key Error in wiki', 'warning')
    else:
        if page.exists():
            if call.message.chat.id in page_msg:
                bot.delete_message(page_msg[call.message.chat.id].chat.id, page_msg[call.message.chat.id].message_id)
            bot.answer_callback_query(call.id, page.title.replace('_', ' '))
            page_msg[call.message.chat.id] = bot.send_message(call.message.chat.id,
                    f'{page.summary[0:600]}...\n\n<a href="{page.fullurl}">Статья на Wikipedia</a>', parse_mode='HTML')
        else:
            bot.send_message(call.message.chat.id, 'Статья не найдена😔')



@bot.callback_query_handler(func=lambda call: re.fullmatch(r'^wiki_move_to\s\d+$', call.data))
def wiki_move_query(call):
    global data_wiki, wiki_msg
    index = int(call.data.split()[1])
    if 0 <= index < len(data_wiki[call.message.chat.id]):
        bot.answer_callback_query(call.id, f'Вы выбрали стр.{index + 1}')
        bot.edit_message_text(chat_id=wiki_msg[call.message.chat.id].chat.id,
                              message_id=wiki_msg[call.message.chat.id].message_id,
                              text=wiki_msg[call.message.chat.id].text,
                              reply_markup=send_wiki(call.message, index))
    else:
        bot.answer_callback_query(call.id, '⛔️')

    
# <<< End Wiki >>>


# <<< Change karma >>>
time_to_change = defaultdict(bool)
msg_from_user = defaultdict(Message)


@bot.message_handler(content_types=['text'], regexp=r'^\+{1,5}$')  # Change karma
@bot.message_handler(content_types=['text'], regexp=r'^\-{1,5}$')
def text_handler(message: Message) -> None:
    """
    :param message
    :type message: telebot.types.Message
    :return: None
    .. seealso:: Func to up or down karma user in group
    """
    def set_true() -> None:
        time_to_change[message.from_user.id] = True

    global time_to_change, msg_from_user
    db.add_user(message.from_user) if message.chat.type == 'private' else db.add_user(message.from_user, message.chat)
    if message.from_user.id not in time_to_change:
        time_to_change[message.from_user.id] = True
    if message.chat.type != 'private' and message.reply_to_message:
        log(message, 'info')
        if message.from_user.id != message.reply_to_message.from_user.id:
            if time_to_change[message.from_user.id]:
                time_to_change[message.from_user.id] = False
                msg_from_user[message.from_user.id] = message
                msg = list(message.text)
                if message.reply_to_message.from_user.first_name is not None:
                    reply_user = message.reply_to_message.from_user.first_name
                    if message.reply_to_message.from_user.last_name is not None:
                        reply_user += ' ' + message.reply_to_message.from_user.last_name
                else:
                    reply_user = message.reply_to_message.from_user.username
                if message.from_user.first_name is not None:
                    from_user = message.from_user.first_name
                    if message.from_user.last_name is not None:
                        from_user += ' ' + message.from_user.last_name
                else:
                    from_user = message.reply_to_message.from_user.username
                if msg[0] == '+':
                    bot.send_message(message.chat.id, f'<b>{from_user}</b> подкинул <i>{len(msg) * 10}</i> к карме😈 '
                                                      f'<b>{reply_user}</b>\nИтого карма: '
                                f'<i>{db.change_karma(message.reply_to_message.from_user.id, msg[0], 10)}</i>',
                                     parse_mode='HTML')
                else:
                    bot.send_message(message.chat.id, f'<b>{from_user}</b> отнял от кармы <i>-{len(msg) * 10}</i>👿 '
                                                      f'<b>{reply_user}</b>\nИтого карма: '
                                f'<i>{db.change_karma(message.reply_to_message.from_user.id, msg[0], 10)}</i>',
                                     parse_mode='HTML')
                Timer(10.0, set_true).run()
            else:
                bot.send_message(message.chat.id, 'Операция доступна один раз в 10 секунд😔\nПожалуйста ожидайте')
        else:
            bot.send_message(message.chat.id, 'Нельзя менять карму самому себе😔')


# <<< End change karma >>>


# <<< Settings >>>
settings_msg = defaultdict(Message)
msg_settings = defaultdict(Message)


@bot.message_handler(commands=['settings'])
def settings_handler(message: Message) -> None:
    """
    :param message
    :type message: telebot.types.Message
    :return: None
    .. seealso::  Enter /settings to open setting menu
    """
    global settings_msg, msg_settings
    if str(dt.fromtimestamp(message.date).strftime('%Y-%m-%d %H:%M')) == str(dt.now().strftime('%Y-%m-%d %H:%M')):
        if message.chat.type != 'private':
            db.change_karma(message.from_user.id, '+', 1)
        log(message, 'info')
        db.add_user(message.from_user) if message.chat.type == 'private' else db.add_user(message.from_user, message.chat)
        msg_settings[message.chat.id] = message
        settings_msg[message.chat.id] = bot.send_message(message.chat.id, 'Загрузка...')
        set_settings(message.chat.id)


@bot.callback_query_handler(func=lambda call: re.fullmatch(r'^Settings\s.+\s\w+\s\w+$', call.data))
def callback_query(call):
    global settings_msg
    chat_id = int(call.data.split()[1])
    if chat_id in settings_msg:
        bot.answer_callback_query(call.id, f'{call.data.split()[3].title()}')
        db.change_setting(*call.data.split()[1:])
        set_settings(chat_id)
    else:
        bot.answer_callback_query(call.id, '⛔️')


def set_settings(chat_id) -> InlineKeyboardMarkup:
    global settings_msg, msg_settings
    keyboard = InlineKeyboardMarkup()
    data = db.get_setting(chat_id)
    if settings_msg[chat_id].chat.type != 'private':
        keyboard.add(InlineKeyboardButton(f'Бот отвечает: {"On🟢" if data["speak"] == "On" else "Off🔴"}',
                                          callback_data=f"Settings {chat_id} speak "
                                                        f"{'off' if data['speak'] == 'On' else 'on'}"))
    if data['speak'] == 'On' and settings_msg[chat_id].chat.type != 'private':
        keyboard.add(InlineKeyboardButton(f'Переодичность: {"Редко🔻" if data["periodicity"] == "Rarely" else "Часто🔺" if data["periodicity"] == "Often" else "Нормально" + "♦️"}',
                                 callback_data=f"Settings {chat_id} periodicity "
                                               f"{'rarely' if data['periodicity'] == 'Often' else 'often' if data['periodicity'] == 'Normal' else 'normal'}"))
    keyboard.add(InlineKeyboardButton(f'Цензура: {"On🟢" if data["censure"] == "On" else "Off🔴"}',
                                      callback_data=f"Settings {chat_id} censure "
                                                    f"{'off' if data['censure'] == 'On' else 'on'}"))
    if data['speak'] == 'On' and settings_msg[chat_id].chat.type != 'private':
        keyboard.add(InlineKeyboardButton(f'Пидор дня: {"On🟢" if data["bad_guy"] == "On" else "Off🔴"}',
                                          callback_data=f"Settings {chat_id} bad_guy "
                                                        f"{'off' if data['bad_guy'] == 'On' else 'on'}"))
    keyboard.add(InlineKeyboardButton(f'Новости: {"UA🇺🇦" if data["news"] == "Ua" else "RU🇷🇺" if data["news"] == "Ru" else "US🇺🇸"}',
                                      callback_data=f"Settings {chat_id} news "
                                                    f"{'ru' if data['news'] == 'Ua' else 'ua' if data['news'] == 'Us' else 'us'}"))
    keyboard.add(InlineKeyboardButton(f'Мемы: {"RU🇷🇺" if data["meme"] == "Ru" else "US🇺🇸"}',
                                      callback_data=f"Settings {chat_id} meme "
                                                    f"{'ru' if data['meme'] == 'En' else 'en'}"))
    keyboard.add(InlineKeyboardButton(f'Распознавание речи: '
                f'{"Wix🎤" if data["recognize"] == "Wix" else "Google🎙" if data["recognize"] == "Google" else "Off🔴"}',
                                      callback_data=f"Settings {chat_id} recognize "
                    f"{'off' if data['recognize'] == 'Google' else 'wix' if data['recognize'] == 'Off' else 'google'}"))
    if data['recognize'] == 'Google':
        keyboard.add(
            InlineKeyboardButton(f'Язык: {"RU🇷🇺" if data["leng_speak"] == "Ru" else "UA🇺🇦" if data["leng_speak"] == "Ua" else "US🇺🇸"}',
                                 callback_data=f"Settings {chat_id} leng_speak "
                                               f"{'ru' if data['leng_speak'] == 'Ua' else 'ua' if data['leng_speak'] == 'Us' else 'us'}"))
    print(data["pastebin"])
    keyboard.add(InlineKeyboardButton(f'Хранение PasteBin: {"1 Час🕰" if data["pastebin"] == "1H" else "1 Неделя🕰" if data["pastebin"] == "1W" else "1 Месяц🕰"}',
        callback_data=f"Settings {chat_id} pastebin "
                      f"{'1W' if data['pastebin'] == '1H' else '1M' if data['pastebin'] == '1W' else '1H'}"))
    keyboard.add(InlineKeyboardButton('Закрыть', callback_data=f'del {settings_msg[chat_id].message_id} '
                                                               f'{msg_settings[chat_id].message_id}'))
    bot.edit_message_text(chat_id=chat_id, message_id=settings_msg[chat_id].message_id,
                          text='Настройки:', reply_markup=keyboard)
# <<< End settings >>>


# <<< Code PasteBin >>>
leng_msg = defaultdict(Message)


@bot.message_handler(commands=['code'])
def code_handler(message: Message) -> None:
    """
    :param message
    :type message: telebot.types.Message
    :return: None
    .. seealso:: Enter /code to get link on you program code on PasteBin
    """
    global leng_msg
    if str(dt.fromtimestamp(message.date).strftime('%Y-%m-%d %H:%M')) == str(dt.now().strftime('%Y-%m-%d %H:%M')):
        if message.chat.type != 'private':
            db.change_karma(message.from_user.id, '+', 1)
        log(message, 'info')
        db.add_user(message.from_user) if message.chat.type == 'private' else db.add_user(message.from_user, message.chat)
        keyboard = InlineKeyboardMarkup(row_width=3)
        keyboard.add(InlineKeyboardButton('Bash', callback_data='Code bash'),
                     InlineKeyboardButton('HTML 5', callback_data='Code html5'),
                     InlineKeyboardButton('CSS', callback_data='Code css'))
        keyboard.add(InlineKeyboardButton('JavaScript', callback_data='Code javascript'),
                     InlineKeyboardButton('Pascal', callback_data='Code pascal'),
                     InlineKeyboardButton('JSON', callback_data='Code json'))
        keyboard.add(InlineKeyboardButton('Perl', callback_data='Code perl'),
                     InlineKeyboardButton('C#', callback_data='Code csharp'),
                     InlineKeyboardButton('Objective C', callback_data='Code objc'))
        keyboard.add(InlineKeyboardButton('C', callback_data='Code c'),
                     InlineKeyboardButton('C++', callback_data='Code cpp'),
                     InlineKeyboardButton('Ruby', callback_data='Code ruby'))
        keyboard.add(InlineKeyboardButton('Delphi', callback_data='Code delphi'),
                     InlineKeyboardButton('Java', callback_data='Code java'),
                     InlineKeyboardButton('CoffeeScript', callback_data='Code coffeescript'))
        keyboard.add(InlineKeyboardButton('PHP', callback_data='Code php'),
                     InlineKeyboardButton('Python', callback_data='Code python'),
                     InlineKeyboardButton('PostgreSQL', callback_data='Code postgresql'))
        keyboard.add(InlineKeyboardButton('SQL', callback_data='Code sql'),
                     InlineKeyboardButton('Swift', callback_data='Code swift'),
                     InlineKeyboardButton('Rust', callback_data='Code rust'))
        keyboard.add(InlineKeyboardButton('Все доступные языки', url='https://' + 'pastebin.com/languages'))
        keyboard.add(InlineKeyboardButton('Введите название нужного языка ниже', callback_data='Enter lang'))
        leng_msg[message.chat.id] = bot.send_message(message.chat.id, 'Выберите нужный вам язык😈', reply_markup=keyboard)
        bot.register_next_step_handler(leng_msg[message.chat.id], callback_to_code)


@bot.callback_query_handler(func=lambda call: re.fullmatch(r'^Enter lang$', call.data))
def callback_query(call):
    bot.answer_callback_query(call.id, 'Введите нужный язык ниже')


def callback_to_code(message: Message) -> None:
    global leng_msg
    if type(leng_msg[message.chat.id]) == 'str':
        return
    elif type(leng_msg[message.chat.id]) == Message:
        if message.content_type != 'text':
            bot.send_message(message.chat.id, 'Не верный формат данных😔')
        else:
            lang: [dict, None] = db.get_code(message.text)
            if lang is not None:
                bot.delete_message(leng_msg[message.chat.id].chat.id, leng_msg[message.chat.id].message_id)
                bot.send_chat_action(message.chat.id, 'typing')
                time.sleep(1)
                code = bot.send_message(message.chat.id, 'Отправьте мне ваш код👾')
                bot.register_next_step_handler(code, set_name, lang['code'])
            else:
                bot.send_message(message.chat.id, 'Этот язык не обнаружен в базе данных😔')


@bot.callback_query_handler(func=lambda call: re.fullmatch(r'^Code\s?\w.+$', call.data))
def code_callback_query(call):
    global leng_msg
    bot.delete_message(leng_msg[call.message.chat.id].chat.id, leng_msg[call.message.chat.id].message_id)
    leng_msg[call.message.chat.id] = call.data
    leng = call.data.replace('Code ', '')
    bot.answer_callback_query(call.id, 'Вы выбрали ' + leng)
    bot.send_chat_action(call.from_user.id, 'typing')
    time.sleep(1)
    code = bot.send_message(call.message.chat.id, 'Отправьте мне ваш код👾')
    bot.register_next_step_handler(code, set_name, leng)


def set_name(message: Message, leng: str) -> None:
    if message.content_type != 'text':
        bot.send_message(message.chat.id, 'Не верный формат данных😔')
    else:
        bot.send_chat_action(message.from_user.id, 'typing')
        time.sleep(1)
        name = bot.send_message(message.chat.id, 'Укажите имя проекта💡')
        bot.register_next_step_handler(name, get_url, message.text, leng)


def get_url(message: Message, code: str, leng: str) -> None:
    if message.content_type != 'text':
        bot.send_message(message.chat.id, 'Не верный формат данных😔')
    else:
        settings = db.get_setting(message.chat.id)
        values = {'api_option': 'paste', 'api_dev_key': f"{API['PasteBin']['DevApi']}",
                  'api_paste_code': f'{code}', 'api_paste_private': '0',
                  'api_paste_name': f'{message.text}', 'api_paste_expire_date': f'{"1H" if settings["pastebin"] == "1H" else "1W" if  settings["pastebin"] == "1W" else "1M"}',
                  'api_paste_format': f'{leng}', 'api_user_key': f"{API['PasteBin']['UserApi']}"}
        data = parse.urlencode(values).encode('utf-8')
        req = request.Request(API['PasteBin']['URL'], data)
        with request.urlopen(req) as response:
            url_bin = str(response.read()).replace('b\'', '').replace('\'', '')
        bot.send_chat_action(message.chat.id, 'typing')
        time.sleep(1)
        bot.send_message(message.chat.id, url_bin)


# <<< End code PasteBin >>>


# <<< Dice game >>>
first_dice: dict = {'user': None, 'dice': 0}
second_dice: dict = {'user': None, 'dice': 0}


@bot.message_handler(commands=['dice'])
@bot.message_handler(content_types=['dice'])
def dice_handler(message: Message) -> None:
    """
    :param message
    :type message: telebot.types.Message
    :return: None
    .. seealso:: Enter /dice or send emodji :dice: to play a dice with any member
    """
    if str(dt.fromtimestamp(message.date).strftime('%Y-%m-%d %H:%M')) == str(dt.now().strftime('%Y-%m-%d %H:%M')):
        log(message, 'info')
        db.add_user(message.from_user) if message.chat.type == 'private' else db.add_user(message.from_user, message.chat)
        if message.content_type != 'dice':
            res = bot.send_dice(message.chat.id)
        else:
            res = message
        t = Timer(60.0, reset_users)
        if first_dice['user'] is None:
            first_dice['user'], first_dice['dice'] = message.from_user, res.dice.value
            t.start()
        elif second_dice['user'] is None:
            second_dice['user'], second_dice['dice'] = message.from_user, res.dice.value
            if first_dice['user'].id != second_dice['user'].id:
                t.cancel()
                bot.send_chat_action(message.chat.id, 'typing')
                time.sleep(4.5)
                if first_dice['dice'] > second_dice['dice']:
                    bot.send_message(message.chat.id,
                                     f"{first_dice['user'].first_name} {first_dice['user'].last_name if first_dice['user'].last_name is not None else ''}🥇 победил "
                                     f"{second_dice['user'].first_name} {second_dice['user'].last_name if second_dice['user'].last_name is not None else ''}🥈")
                elif first_dice['dice'] < second_dice['dice']:
                    bot.send_message(message.chat.id,
                                     f"{second_dice['user'].first_name} {second_dice['user'].last_name if second_dice['user'].last_name is not None else ''}🥇 победил "
                                     f"{first_dice['user'].first_name} {first_dice['user'].last_name if first_dice['user'].last_name is not None else ''}🥈")
                else:
                    bot.send_message(message.chat.id, 'Победила дружба🤝')
                reset_users()
            else:
                first_dice['user'], first_dice['dice'] = message.from_user, res.dice.value
                t.cancel()
                t.start()


def reset_users() -> None:  # Reset users for Dice game
    first_dice['user'] = None
    first_dice['dice'] = 0
    second_dice['user'] = None
    second_dice['dice'] = 0


# <<< End dice game >>>


# <<< Admin menu >>>
@bot.message_handler(content_types=['text'], regexp=r'^!ban$')
def text_handler(message: Message) -> None:
    """
    :param message
    :type message: telebot.types.Message
    :return: None
    .. seealso:: !ban func for admins
    """
    log(message, 'info')
    if message.chat.type != 'private':
        ban(message)
    else:
        bot.send_message(message.chat.id, 'Функция достпна только в группах😔')


def ban(message: Message, chat=None, user=None):
    if user is None and chat is None:
        user = message.reply_to_message.from_user.id
        chat = message.chat.id
    if str(user) == str(message.from_user.id):
        bot.send_message(message.chat.id, 'Нельзя забанить самого себя😔')
        return
    else:
        for i in bot.get_chat_administrators(message.chat.id):
            if str(i.user.id) == str(user):
                bot.send_message(message.chat.id, 'Нельзя забанить администратора😔')
                return
        else:
            for i in bot.get_chat_administrators(message.chat.id):
                if i.user.id == message.from_user.id:
                    db.ban_user(user)
                    bot.send_message(message.chat.id, f'Пользователь забанен навсегда😈')
                    bot.kick_chat_member(chat, user)
                    return
            else:
                bot.send_message(message.chat.id, 'У вас недостаточно прав для этого😔')


@bot.message_handler(content_types=['text'], regexp=r'^!mute\s\d+$')
def text_handler(message: Message) -> None:
    """
    :param message
    :type message: telebot.types.Message
    :return: None
    .. seealso:: !mute {some_time} func for admin
    """
    log(message, 'info')
    if message.chat.type != 'private':
        mute(message, message.text.split()[1])
    else:
        bot.send_message(message.chat.id, 'Функция достпна только в группах😔')


def mute(message: Message, time_mute=30, chat=None, user=None):
    if user is None and chat is None:
        user = message.reply_to_message.from_user.id
        chat = message.chat.id
    if str(user) == str(message.from_user.id):
        bot.send_message(message.chat.id, 'Нельзя замутить самого себя😔')
        return
    else:
        for i in bot.get_chat_administrators(message.chat.id):
            if str(i.user.id) == str(user):
                bot.send_message(message.chat.id, 'Нельзя замутить администратора😔')
                return
        else:
            for i in bot.get_chat_administrators(message.chat.id):
                if i.user.id == message.from_user.id:
                    bot.restrict_chat_member(chat, user,  until_date=time.time() + int(time_mute) * 60,
                                             can_send_messages=False,
                                             can_send_other_messages=False, can_send_media_messages=False)
                    bot.send_message(message.chat.id, f'Пользователь замучен на {time_mute} мин🤐')
                    return
            else:
                bot.send_message(message.chat.id, 'У вас недостаточно прав для этого😔')


@bot.message_handler(content_types=['text'], regexp=r'^!kick$')
def text_handler(message: Message) -> None:
    """
    :param message
    :type message: telebot.types.Message
    :return: None
    .. seealso:: !kick func for admin
    """
    log(message, 'info')
    if message.chat.type != 'private':
        kick(message)
    else:
        bot.send_message(message.chat.id, 'Функция достпна только в группах😔')


def kick(message: Message, chat=None, user=None):
    if user is None and chat is None:
        user = message.reply_to_message.from_user.id
        chat = message.chat.id
    if str(user) == str(message.from_user.id):
        bot.send_message(message.chat.id, 'Нельзя кикнуть самого себя😔')
    else:
        for i in bot.get_chat_administrators(message.chat.id):
            if str(i.user.id) == str(user):
                bot.send_message(message.chat.id, 'Нельзя кикнуть администратора😔')
                return
        else:
            for i in bot.get_chat_administrators(message.chat.id):
                if i.user.id == message.from_user.id:
                    bot.kick_chat_member(chat, user)
                    bot.send_message(message.chat.id, 'Пользователь кикнут😈')
                    return
            else:
                bot.send_message(message.chat.id, 'У вас недостаточно прав для этого😔')


# <<< End admin menu >>>


# <<< All message >>>
@bot.message_handler(content_types=['text'])
@bot.edited_message_handler(content_types=['text'])
def text_handler(message: Message) -> None:
    """
    :param message
    :type message: telebot.types.Message
    :return: None
    .. seealso:: Check all messages by command or answer on random message
    """
    if str(dt.fromtimestamp(message.date).strftime('%Y-%m-%d %H:%M')) == str(dt.now().strftime('%Y-%m-%d %H:%M')):
        log(message, 'info')
        db.add_user(message.from_user) if message.chat.type == 'private' else db.add_user(message.from_user, message.chat)
        if str(message.from_user.id) in Admins and message.forward_from_chat is not None:
            if str(message.forward_from_chat.id) == '-1001304250568':
                db.add_joke(message.text.split('\n')[0], message.text.split('\n')[2])
        text = message.text.lower()
        if text in ['стикер', 'стикерочек', 'sticker']:
            gn_sticker_handler(message)
        elif text in ['гифка', 'гиф', 'гифон', 'gif']:
            gif_handler(message)
        elif text in ['мем', 'мемас', 'мемчик', 'meme']:
            meme_handler(message)
        elif text in ['шутка', 'шутку', 'joke', 'joke']:
            joke_handler(message)
        elif text in ['кубик', 'зарик', 'кость', 'dice']:
            dice_handler(message)
        elif text in ['хентай', 'hentai', 'лоли', 'loli', 'девушка', 'girl', 'баба', 'пизда']:
            forbidden_handler(message)
        settings = db.get_setting(message.chat.id)
        if message.chat.type != 'private' and not message.edit_date:
            count_symbols = len(list(message.text))
            if count_symbols > 75:
                db.change_karma(message.from_user.id, '+', 7)
            elif count_symbols > 50:
                db.change_karma(message.from_user.id, '+', 5)
            elif count_symbols > 30:
                db.change_karma(message.from_user.id, '+', 3)
            elif count_symbols > 10:
                db.change_karma(message.from_user.id, '+', 1)
            if str(message.from_user.id) != GNBot_ID and settings['speak'] == 'On':
                if settings['periodicity'] == 'Rarely':
                    percent = [4, 1, 30]
                elif settings['periodicity'] == 'Normal':
                    percent = [7, 3, 45]
                else:
                    percent = [15, 5, 60]
                if message.reply_to_message is not None:
                    if message.reply_to_message.from_user.id == int(GNBot_ID) and rend_d(percent[2]):
                        bot.reply_to(message, db.get_answer())
                elif rend_d(percent[0]):
                    bot.reply_to(message, db.get_answer())
                elif rend_d(percent[1]):
                        bot.send_sticker(message.chat.id, db.random_sticker(), message.message_id)


# <<< End all message >>>


# <<< Answer's  >>>
@bot.message_handler(content_types=['new_chat_members'])  # Answer on new member
def new_member_handler(message: Message) -> None:
    for user in message.new_chat_members:
        if db.check_ban_user(user.id):
            keyboard = InlineKeyboardMarkup()
            keyboard.add(InlineKeyboardButton('Кикнуть🥊', callback_data=f'Kick '
                                                                       f'{message.chat.id} {user.id}'),
                         InlineKeyboardButton('Забанить🚫', callback_data=f'Ban '
                                                                        f'{message.chat.id} {user.id}'),
                         InlineKeyboardButton('Замутить❌', callback_data=f'Mute '
                                                                          f'{message.chat.id} {user.id}')
                         )
            msg = bot.send_message(message.chat.id, random.choice(['Опа чирик! Вечер в хату', 'Приветствую тебя',
                                                              'Алоха друг мой!', 'Ну привет)', 'Хело май френд',
                                                              'Рады вас видеть господин', 'В наших рядах поплнение',
                                                              'Новобранец!', 'Рядовой!', 'Дратути']),
                                                              reply_markup=keyboard)

            time.sleep(240)
            bot.delete_message(msg.chat.id, msg.message_id)
        else:
            bot.send_message(message.chat.id, 'Добавленный пользователь в чёрном списке😞')
            bot.kick_chat_member(message.chat.id, user.id)


@bot.callback_query_handler(func=lambda call: re.fullmatch(r'^Kick\s.+\s.+$', call.data))
def code_callback_query(call):
    bot.answer_callback_query(call.id, 'Пользователь кикнут🥊')
    kick(call.message, call.data.split()[1], call.data.split()[2])


@bot.callback_query_handler(func=lambda call: re.fullmatch(r'^Ban\s.+\s.+$', call.data))
def code_callback_query(call):
    bot.answer_callback_query(call.id, 'Пользователь забанен навсегда😯')
    ban(call.message, call.data.split()[1], call.data.split()[2])


@bot.callback_query_handler(func=lambda call: re.fullmatch(r'^Mute\s.+\s.+$', call.data))
def code_callback_query(call):
    bot.answer_callback_query(call.id, 'Пользователь замучен на 30 минут🤐')
    mute(call.message, 30, call.data.split()[1], call.data.split()[2])


@bot.message_handler(content_types=['left_chat_member'])
def left_member_handler(message: Message) -> None:
    bot.send_message(message.chat.id, random.choice(['Слился падло(', 'Буенос мучачес пидрилас', 'Прощай любовь моя',
                                                     'Аривидерчи', 'Слава богу он ушел',
                                                     'Без него тут будет куда приятнее',
                                                     'Ну, теперь можно начинать весилится', 'Он был такой душный',
                                                     'Это пойдет всем на пользу', 'Что не делается все к лучшему']))


@bot.message_handler(content_types=['voice'])  # Answer on voice
def voice_handler(message: Message) -> None:
    if message.chat.type != 'private':
        db.change_karma(message.from_user.id, '+', 1)
    settings = db.get_setting(message.chat.id)
    if settings['recognize'] != 'Off':
        r = sr.Recognizer()
        data = request.urlopen(bot.get_file_url(message.voice.file_id)).read()
        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.write(data)
        audio = AudioSegment.from_ogg(f.name)
        audio.export(f'file.wav', format='wav')
        file = sr.AudioFile('file.wav')
        with file as source:
            audio = r.record(source)
        try:
            if settings['recognize'] == 'Wix':
                rec = r.recognize_wit(audio, key=API['Wit'])
                rec = rec[0].title() + rec[1:]
            else:
                setting = db.get_setting(message.chat.id)
                rec = r.recognize_google(audio,
                        language=f"{'ru-RU' if setting['leng_speak'] == 'Ru' else 'uk-UA' if setting['leng_speak'] == 'Ua' else 'en-US'}")
                rec = rec[0].title() + rec[1:]
        except (sr.UnknownValueError, sr.RequestError):
            log(f"Could not request results from Wit Recognition service", 'warning')
            bot.send_message(message.chat.id, 'Не смог распознать голос😞')
        else:
            send_text(message, rec)


def send_text(message: Message, rec: str) -> None:
    keyboard = InlineKeyboardMarkup()
    if message.forward_from is None:
        if message.from_user.first_name is not None:
            user = message.from_user.first_name
            if message.from_user.last_name is not None:
                user += ' ' + message.from_user.last_name
        else:
            user = message.from_user.username
    else:
        if message.forward_from.first_name is not None:
            user = message.forward_from.first_name
            if message.forward_from.last_name is not None:
                user += ' ' + message.forward_from.last_name
        else:
            user = message.forward_from.username
    msg = bot.reply_to(message, f'От <b><i>{user}</i></b>\n{rec}')
    keyboard.add(InlineKeyboardButton('Удалить', callback_data=f'del {msg.message_id}'))
    bot.edit_message_text(msg.text, msg.chat.id, msg.message_id, reply_markup=keyboard, parse_mode='HTML')
    try:
        os.remove(os.path.join(os.path.abspath(os.path.dirname(__file__)), f'file.wav'))
    except (FileNotFoundError, NameError):
        log('Error! Can\'t remove file', 'warning')


@bot.message_handler(content_types=['photo'])
def photo_handler(message: Message) -> None:
    if message.chat.type != 'private':
        db.change_karma(message.from_user.id, '+', 1)


@bot.message_handler(content_types=['location'])  # Answer on location
def location_handler(message: Message) -> None:
    if message.chat.type != 'private':
        db.change_karma(message.from_user.id, '+', 1)
        if rend_d(30):
            bot.reply_to(message, ['Скинул мусорам', 'Прикоп или магнит?', 'Ебеня какие то',
                                   'Та ну нафиг, я туда не поеду', 'Это ты там живешь? Сочувствую',
                                   'Ой ну и местечко для сходочки вы выбрали...',
                                   'Я бы туда не поехал будь я даже пьян',
                                   'Дебри', 'Так так, вижу степи и болото'])


@bot.message_handler(content_types=['contact'])  # Answer on contact
def contact_handler(message: Message) -> None:
    if message.chat.type != 'private':
        db.change_karma(message.from_user.id, '+', 1)
        if rend_d(30):
            bot.reply_to(message, random.choice(['Если мне будет одиноко и холодно я знаю куда позвонить',
                                                         'Трубку не берут', 'Сохранил', 'А мой запишешь?',
                                                         'Наберу тебя вечерком)', 'Разошлю его всем знакомым',
                                                         'Продам в DarkNet']))

# <<< End answer's  >>>


# <<< Unpin bad guys message  >>>
@bot.message_handler(content_types=['pinned_message'])
def pin_handler(message: Message) -> None:
    try:
        if message.pinned_message.json['text'].startswith('🎉Пидор'):
            bot.delete_message(message.chat.id, message.message_id)
    except Exception:
        log('Key error in unpin bad gay', 'error')

# <<< End unpin bad guys message  >>>


# <<< Del  >>>
@bot.callback_query_handler(func=lambda call: re.fullmatch(r'^del\s.+$', call.data))
def del_query(call):
    bot.answer_callback_query(call.id, 'Удалено')
    for i in call.data.split()[1:]:
        try:
            bot.delete_message(call.message.chat.id, i)
        except Exception:
            log(f'Can\'t delete message', 'warning')



# <<< End del  >>>


#<<< Pass >>>
@bot.callback_query_handler(func=lambda call: re.match(r'\w+_move_to\spass', call.data))
def pass_query(call):
    bot.answer_callback_query(call.id, '⛔️')


# <<< End pass  >>>


# <<< Bot polling  >>>
try:
    bot.polling(none_stop=True)
except Exception as ex:
    log('Bot polling error', 'error')
    time.sleep(15)

# <<< End bot polling  >>>
