#!/home/UltraXionUA/.virtualenvs/myvirtualenv/bin/python3.8
# -*- coding: utf-8 -*-
"""Mains file for GNBot"""
# <<< Import's >>>
from telebot.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto, InputMediaVideo
from pars import main, get_torrents1, get_torrents2, get_torrents3, get_instagram_video, get_instagram_photos
from funcs import tr_w, rend_d, hi_r, log, clear_link, get_day, get_weather_emoji, sec_to_time
from youtube_unlimited_search import YoutubeUnlimitedSearch
from config import TOKEN, API, Empty_bg, URLS
from urllib import parse, request, error
from pytube import YouTube, exceptions
from collections import defaultdict
from datetime import datetime as dt
from pytils.translit import slugify
from json import JSONDecodeError
from pydub import AudioSegment
from threading import Thread
from telebot import TeleBot
from threading import Timer
import tempfile
import requests
import ffmpeg
import random
import time
import db
import os
import re

# <<< End import's>>
# from config import TEST_TOKEN
bot = TeleBot(TOKEN)
log('Bot is successful running!', 'info')

# Turn on parser
Parser = Thread(target=main, name='Parser')
Parser.start()


# <<< Start >>>
@bot.message_handler(commands=['start'])  # /start
def start_handler(message: Message) -> None:
    log(message, 'info')
    if message.chat.type == 'private':
        db.add_user(message.from_user)
    else:
        db.add_user(message.from_user, message.chat)
    bot.send_chat_action(message.chat.id, 'typing')
    bot.send_message(message.chat.id, 'Здравствуй, меня зовут GNBot🖥\n'
                                      'Я создан дабы служить верой и правдой сообществу 💎Голубой носок💎')


# <<< End start >>>


# <<< Help >>>
@bot.message_handler(commands=['help'])  # /help
def help_handler(message: Message) -> None:
    log(message, 'info')
    bot.send_chat_action(message.chat.id, 'typing')
    bot.send_message(message.chat.id, 'Тут должна была быть помощь🆘, но её тут не будет🌚\n'
                                      'Если что пиши мне: 💢@Ultra_Xion💢')


# <<< End help >>>


# <<< Gif >>>
@bot.message_handler(commands=['gif'])  # /gif
def gif_handler(message: Message) -> None:
    log(message, 'info')
    bot.send_chat_action(message.chat.id, 'upload_video')
    while True:
        data = requests.get(API['API_Gif']).json()
        if hi_r(data['data']['rating']):
            bot.send_document(message.chat.id, data['data']['images']['downsized_large']['url'])
            break


# <<< End gif >>>


# <<< QR Code >>>
qr_msg = defaultdict(Message)


@bot.message_handler(commands=['qrcode'])  # /qrcode
def qrcode_handler(message: Message) -> None:
    log(message, 'info')
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton('Создать', callback_data='Create_QRCode'),
                 InlineKeyboardButton('Считать', callback_data='Read_QRCode'))
    qr_msg[message.chat.id] = bot.send_message(message.chat.id, 'Выберите опцию🧐', reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: re.fullmatch(r'^Create_QRCode$', call.data))
def create_sqcode(call) -> None:
    global qr_msg
    bot.answer_callback_query(call.id, 'Вы выбрали создать')
    bot.delete_message(qr_msg[call.message.chat.id].chat.id, qr_msg[call.message.chat.id].message_id)
    msg = bot.send_message(call.message.chat.id, 'Введите текст или URL✒️')
    bot.register_next_step_handler(msg, send_qrcode)


@bot.callback_query_handler(func=lambda call: re.fullmatch(r'^Read_QRCode$', call.data))
def read_sqcode(call) -> None:
    bot.answer_callback_query(call.id, 'Вы выбрали считать')
    bot.delete_message(qr_msg[call.message.chat.id].chat.id, qr_msg[call.message.chat.id].message_id)
    msg = bot.send_message(call.message.chat.id, 'Отправь мне QR Code или его фотографию📸')
    bot.register_next_step_handler(msg, read_text)


def read_text(message: Message) -> None:
    if message.content_type == 'photo':
        res = requests.post(API['QRCode']['Read'].replace('FILE', bot.get_file_url(message.photo[0].file_id))).json()
        if res[0]['symbol'][0]['data'] is not None:
            bot.send_message(message.chat.id, '<b>Полученный результат</b>📝\n' + res[0]['symbol'][0]['data'],
                             parse_mode='HTML')
        else:
            bot.send_message(message.chat.id, 'QR Code не обнаружен😔')
    else:
        bot.send_message(message.chat.id, 'Не верный формат данных😔')


def send_qrcode(message: Message) -> None:
    bot.send_photo(message.chat.id, requests.get(API['QRCode']['Create'].replace('DATA',
                                                                                 message.text.replace(' ',
                                                                                                      '+'))).content)
# <<< End QR Code >>>


# <<< Joke >>>
jokes_data = defaultdict(list)


@bot.message_handler(commands=['joke'])  # /joke
def joke_handler(message: Message) -> None:
    global jokes_data
    log(message, 'info')
    if message.chat.id not in jokes_data or len(jokes_data[message.chat.id]) == 1:
        jokes_data[message.chat.id] = db.get_all_jokes()
    joke = jokes_data[message.chat.id].pop(random.choice(range(len(jokes_data[message.chat.id]) - 1)))
    bot.send_chat_action(message.chat.id, 'typing')
    time.sleep(1.5)
    if joke['panchline'] != 'False':
        bot.send_message(message.chat.id, joke['setup'] + random.choice(['🧐', '🤨🤔', '🤔']))
        time.sleep(3.5)
        bot.send_message(message.chat.id, joke['panchline'] + random.choice(['🌚', '😅', '🤫']))
    else:
        bot.send_message(message.chat.id, joke['setup'] + random.choice(['🌚', '😅', '🤫']))


# <<< End joke >>>


# <<< Ogg to Mp3 >>>
msg_mp3ogg = defaultdict(Message)


@bot.message_handler(commands=['oggtomp3'])  # /oggtomp3
def oggtomp3_handler(message: Message) -> None:
    global msg_mp3ogg
    log(message, 'info')
    msg_mp3ogg[message.chat.id] = bot.send_message(message.chat.id, 'Запишите или отправьте аудиосообщение🎙')
    bot.register_next_step_handler(msg_mp3ogg[message.chat.id], set_name_mp3)


def set_name_mp3(message: Message) -> None:
    global msg_mp3ogg
    bot.delete_message(msg_mp3ogg[message.chat.id].chat.id, msg_mp3ogg[message.chat.id].message_id)
    bot.delete_message(message.chat.id, message.message_id)
    if message.content_type == 'voice':
        file_id = message.voice.file_id
        msg_mp3ogg[message.chat.id] = bot.send_message(message.chat.id, 'Введите имя файла✒️')
        bot.register_next_step_handler(msg_mp3ogg[message.chat.id], send_mp3, file_id)
    else:
        bot.send_message(message.chat.id, 'Не верный формат данных😔')


def send_mp3(message: Message, file_id: int) -> None:
    global msg_mp3ogg
    bot.send_chat_action(message.chat.id, 'upload_voice')
    bot.delete_message(msg_mp3ogg[message.chat.id].chat.id, msg_mp3ogg[message.chat.id].message_id)
    bot.delete_message(message.chat.id, message.message_id)
    data = request.urlopen(bot.get_file_url(file_id)).read()
    with tempfile.NamedTemporaryFile(delete=False) as f:
        f.write(data)
    time.sleep(1)
    audio = AudioSegment.from_ogg(f.name)
    audio.export(f'{message.text}.mp3', format='mp3')
    bot.send_audio(message.chat.id, open(f'{message.text}.mp3', 'rb'))
    try:
        os.remove(os.path.join(os.path.abspath(os.path.dirname(__file__)), f'{message.text}' + '.mp3'))
    except FileNotFoundError:
        log('Error! Can\'t remove file', 'warning')


# <<< End Ogg to Mp3 >>>


# <<< Ru meme >>>
@bot.message_handler(commands=['ru_meme'])  # /ru_meme
def meme_handler(message: Message) -> None:
    log(message, 'info')
    bot.send_chat_action(message.chat.id, 'upload_photo')
    bot.send_photo(message.chat.id, db.random_meme())


# <<< End ru meme >>>


# <<< En meme >>>
@bot.message_handler(commands=['en_meme'])  # /en_meme
def meme_en_handler(message: Message) -> None:
    log(message, 'info')
    bot.send_chat_action(message.chat.id, 'upload_photo')
    meme = requests.get(API['API_Meme']).json()
    bot.send_photo(message.chat.id, meme['url'])


# <<< End en meme >>>


# <<< Weather >>>
weather_data = defaultdict(dict)
weather_msg = defaultdict(Message)
city_data = defaultdict(dict)
city_msg = defaultdict(Message)


@bot.message_handler(commands=['weather'])  # /weather
def weather_handler(message: Message) -> None:
    log(message, 'info')
    city_msg[message.chat.id] = bot.send_message(message.chat.id, 'Введите название города✒️')
    bot.register_next_step_handler(city_msg[message.chat.id], show_weather)


def weather(message: Message, index: int) -> None:
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton(text="⬅️️", callback_data=f"move_to__ {index - 1 if index > 0 else 'pass'}"),
        InlineKeyboardButton(text="➡️", callback_data=f"move_to__ "
                                        f"{index + 1 if index < len(weather_data[message.chat.id]) - 1 else 'pass'}"))
    keyboard.add(InlineKeyboardButton('Погода', url='https://' +
                                                    f'darksky.net/forecast/{city_data[message.chat.id]["lat"]},'
                                                    f'{city_data[message.chat.id]["lon"]}/us12/en'))
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
    bot.delete_message(city_msg[message.chat.id].chat.id, city_msg[message.chat.id].message_id)
    if message.text.lower() == 'харьков':
        city_name = 'K' + slugify(message.text)
    else:
        city_name = slugify(message.text).title()
    try:
        res = requests.get(API['API_Weather'].replace('CityName', city_name)).json()
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


@bot.callback_query_handler(func=lambda call: re.fullmatch(r'^move_to__\s\d+$', call.data))
def weather_query(call):
    global weather_data
    index = int(call.data.split()[1])
    if 0 <= index < len(weather_data[call.message.chat.id]):
        bot.answer_callback_query(call.id, f'Вы выбрали стр.{index + 1}')
        weather(call.message, index)
    else:
        bot.answer_callback_query(call.id, '⛔️')


@bot.callback_query_handler(func=lambda call: re.fullmatch(r'^move_to__\spass$', call.data))
def pass_query(call):
    bot.answer_callback_query(call.id, '⛔️')


# <<< End weather >>>


# <<< Detect music >>>
detect_msg = defaultdict(Message)


@bot.message_handler(commands=['detect'])  # /detect_music
def detect_handler(message: Message) -> None:
    global detect_msg
    log(message, 'info')
    bot.send_chat_action(message.chat.id, 'typing')
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton('Записать🔊', callback_data='record'),
                 InlineKeyboardButton('Напеть🎙', callback_data='sing'))
    detect_msg[message.chat.id] = bot.send_message(message.chat.id,
                                                   'Выберите что нужно определить🧐', reply_markup=keyboard)


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
    API['AUDD_data']['url'] = bot.get_file_url(message.voice.file_id).replace('https://' + 'api.telegram.org',
                                                                              'http://' + 'esc-ru.appspot.com/') \
                                                                               + '?host=api.telegram.org'
    if type_r == 'sing':
        result = requests.post(API['AUDD'] + 'recognizeWithOffset/',
                               data={'url': API['AUDD_data']['url'], 'api_token': API['AUDD_data']['api_token']}).json()
    else:
        result = requests.post(API['AUDD'], data=API['AUDD_data']).json()
    if result['status'] == 'success' and result['result'] is not None:
        if type_r != 'sing':
            if result['result']['deezer']:
                keyboard = InlineKeyboardMarkup()
                res = YoutubeUnlimitedSearch(f"{result['result']['artist']} - {result['result']['title']}",
                                             max_results=1).get()
                keyboard.add(InlineKeyboardButton('Текст',
                                                  callback_data=f"Lyric2: {str(result['result']['deezer']['id'])}"),
                             InlineKeyboardButton('Dezeer', url=result['result']['deezer']['link']))
                keyboard.add(InlineKeyboardButton('Песня', callback_data=res[0]['link']))
                bot.send_photo(message.chat.id, result['result']['deezer']['artist']['picture_xl'],
                               caption=f"{result['result']['artist']} - {result['result']['title']}🎵",
                               reply_markup=keyboard)
            else:
                bot.send_message(message.chat.id, f"<b>{result['result']['artist']}</b>"
                                                  f" - {result['result']['title']}🎵", parse_mode='HTML')
        else:
            msg = "<b>Результат</b> "
            for i in result['result']['list']:
                msg += f"\nСовпадение: <i>{i['score']}%</i>\n{i['artist']} - {i['title']}🎵"
            bot.send_message(message.chat.id, msg, parse_mode='HTML')

        @bot.callback_query_handler(func=lambda call: re.fullmatch(r'^Lyric2:\s?\d+$', call.data))
        def call_lyric(call):
            res_lyric = requests.get(API['AUDD'] + 'findLyrics/?q=' + result['result']['artist'] + ' ' +
                                     result['result']['title']).json()
            bot.reply_to(call.message, res_lyric['result'][0]['lyrics'])
    else:
        bot.send_message(message.chat.id, 'Ничего не нашлось😔')


@bot.callback_query_handler(func=lambda call: re.fullmatch(r'/watch\?v=\w+.+', call.data))
def callback_query(call):
    yt = YouTube('https://' + 'www.youtube.com/' + call.data.split()[0])
    bot.send_chat_action(call.message.chat.id, 'upload_audio')
    bot.send_audio(call.message.chat.id,
                   open(yt.streams.filter(only_audio=True)[0].download(filename='file'), 'rb'),
                   title=yt.title, duration=yt.length, performer=yt.author,
                   caption=f'🎧 {sec_to_time(yt.length)} '
                           f'| {round(os.path.getsize("file.mp4") / 1000000, 1)} MB |'
                           f' {yt.streams.filter(only_audio=True)[0].abr.replace("kbps", "")} Kbps')
    try:
        os.remove(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'file' + '.mp4'))
    except FileNotFoundError:
        log('Error! Can\'t remove file', 'warning')
# <<< End detect music >>>


# <<< Music >>>
data_songs = defaultdict(list)
song_msg = defaultdict(Message)
msg_song = defaultdict(Message)


@bot.message_handler(commands=['music'])  # /music
def music_handler(message: Message) -> None:
    log(message, 'info')
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
    bot.register_next_step_handler(msg, get_song, call.data)


def get_song(message: Message, choice: str) -> None:  # Get song
    global data_songs, song_msg
    res = requests.get(API['API_Deezer'] + choice + message.text.replace(' ', '+')).json()
    try:
        if res['data']:
            if choice == 'artist?q=':
                songs = requests.get(res['data'][0]['tracklist'].replace('limit=50', 'limit=100')).json()
                if songs['data']:
                    data_songs[message.chat.id] = [
                        {'id': i['id'], 'title': i['title'], 'name': i['contributors'][0]['name'],
                         'link': i['link'], 'preview': i['preview'], 'duration': i['duration']}
                        for i in songs['data']]
                    create_data_song(message)
                    if data_songs[message.chat.id]:
                        if message.chat.id in song_msg:
                            bot.delete_message(song_msg[message.chat.id].chat.id, song_msg[message.chat.id].message_id)
                        song_msg[message.chat.id] = bot.send_photo(message.chat.id, res['data'][0]['picture_xl'],
                                                                   reply_markup=inline_keyboard(message, 0))
                    else:
                        raise FileExistsError
            elif choice == 'track?q=':
                data_songs[message.chat.id] = [{'id': i['id'], 'title': i['title'], 'name': i['artist']['name'],
                                                'link': i['link'], 'preview': i['preview'], 'duration': i['duration']}
                                               for i in res['data']]
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
            InlineKeyboardButton(text="⬅️️",
                                 callback_data=f"move_to {some_index - 1 if some_index > 0 else 'pass'}"),
            InlineKeyboardButton(text="➡️",
                                 callback_data=f"move_to "
                                 f"{some_index + 1 if some_index < len(data_songs[message.chat.id]) - 1 else 'pass'}"))
        return some_keyboard
    except KeyError:
        log('Key Error in music', 'warning')


@bot.callback_query_handler(func=lambda call: call.data == 'move_to pass')
def callback_query(call):
    bot.answer_callback_query(call.id, '⛔️')


@bot.callback_query_handler(func=lambda call: re.fullmatch(r'^move_to\s\d$', call.data))
def callback_query(call):
    global data_songs
    index = int(call.data.split()[1])
    if 0 <= index < len(news[call.message.chat.id]):
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
    for i in data_songs[call.message.chat.id]:
        for j in i:
            if j['id'] == int(song_id):
                bot.answer_callback_query(call.id, 'Вы выбрали ' + j["name"] + ' - ' + j["title"])
                res = YoutubeUnlimitedSearch(f'{j["name"]} - {j["title"]}', max_results=1).get()
                if res:
                    yt = YouTube('https://' + 'www.youtube.com/' + res[0]['link'])
                    keyboard = InlineKeyboardMarkup(row_width=2)
                    keyboard.add(InlineKeyboardButton('Текст', callback_data=f'Lyric: {str(song_id)}'),
                                 InlineKeyboardButton('Dezeer', url=j['link']))
                    bot.send_chat_action(call.message.chat.id, 'upload_audio')
                    bot.send_audio(call.message.chat.id, audio=open(yt.streams.filter(
                                                         only_audio=True)[0].download(filename='file'), 'rb'),
                                                         reply_markup=keyboard,  performer=j['name'],
                                                         title=j['title'], duration=j['duration'],
                                                         caption=f'🎧 {sec_to_time(yt.length)} '
                                                 f'| {round(os.path.getsize("file.mp4")/1000000, 1)} MB |'
                                                 f' {yt.streams.filter(only_audio=True)[0].abr.replace("kbps", "")}'
                                                                 f' Kbps')
                    try:
                        os.remove(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'file' + '.mp4'))
                    except FileNotFoundError:
                        log('Error! Can\'t remove file', 'warning')
                    break
                else:
                    bot.answer_callback_query(call.id, 'Не смог получить песню😔')
    else:
        bot.answer_callback_query(call.id, 'Список песен пуст, выполните поиск заново😔')


@bot.callback_query_handler(func=lambda call: re.fullmatch(r'^Lyric:\s?\d+$', call.data))
def callback_query(call):
    global data_songs
    song_id = call.data.replace('Lyric: ', '')
    for i in data_songs[call.message.chat.id]:
        for j in i:
            if j['id'] == int(song_id):
                res = requests.get(API['AUDD'] + 'findLyrics/?q=' + j['name'] + ' ' + j['title']).json()
                if res['status'] == 'success' and res['result'] is not None:
                    bot.reply_to(call.message, res['result'][0]['lyrics'])


# <<< End music >>>


# <<< News >>>
news = defaultdict(list)
news_msg = defaultdict(Message)


@bot.message_handler(commands=['news'])  # /news
def news_handler(message: Message) -> None:
    log(message, 'info')
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
    res = requests.get(API['News']['URL'].replace('Method', f'{news_type}') + API['News']['Api_Key']).json()
    if res['status'] == 'ok':
        news[message.chat.id] = [{'title': i['title'], 'description': i['description'],
                                  'url': i['url'], 'image': i['urlToImage'], 'published': i['publishedAt']} for i in
                                 res['articles']]
    for i in news[message.chat.id]:
        if i['image'] is not None:
            i['title'] = clear_link(i['title'])
            if i['description'] is not None:
                i['description'] = clear_link(i['description'])
    send_news(message, 0)


def send_news(message: Message, index: int) -> None:
    keyboard2 = InlineKeyboardMarkup()
    keyboard2.add(InlineKeyboardButton('Читать', url=news[message.chat.id][index]['url']))
    keyboard2.add(
        InlineKeyboardButton(text="⬅️️",
                             callback_data=f"move_to_ {index - 1 if index > 0 else 'pass'}"),
        InlineKeyboardButton(text="➡️",
                             callback_data=f"move_to_ "
                                           f"{index + 1 if index < len(news[message.chat.id]) - 1 else 'pass'}"))
    try:
        try:
            code_img = requests.get(news[message.chat.id][index]['image']).ok
        except requests.exceptions.ConnectionError:
            send_news(message, index + 1)
        except requests.exceptions.MissingSchema:
            send_news(message, index + 1)
        else:
            if news[message.chat.id][index]['image'] is not None and news[message.chat.id][index]['image'] != '' \
                    and code_img is True:
                if news[message.chat.id][index]['description'] is not None:
                    bot.edit_message_media(chat_id=news_msg[message.chat.id].chat.id,
                                           message_id=news_msg[message.chat.id].message_id,
                                           media=InputMediaPhoto(news[message.chat.id][index]['image'],
                                                                 caption='<b>' + news[message.chat.id][index][
                                                                     'title'] + '</b>\n\n' +
                                                                         news[message.chat.id][index]['description'] +
                                                                         '\n\n' + '<i>' + news[message.chat.id][index][
                                                                             'published'].replace('T', ' ').replace(
                                                                     'Z', '') + '</i>',
                                                                 parse_mode='HTML'),
                                           reply_markup=keyboard2)
                else:
                    bot.edit_message_media(chat_id=news_msg[message.chat.id].chat.id,
                                           message_id=news_msg[message.chat.id].message_id,
                                           media=InputMediaPhoto(news[message.chat.id][index]['image'],
                                                                 caption='<b>' + news[message.chat.id][index][
                                                                     'title'] + '</b>\n' +
                                                                         '<i>' + news[message.chat.id][index][
                                                                             'published'].replace('T', ' ').replace(
                                                                     'Z', '') + '</i>',
                                                                 parse_mode='HTML'),
                                           reply_markup=keyboard2)
            else:
                send_news(message, index + 1)
    except KeyError:
        log('Key Error in news', 'warning')


@bot.callback_query_handler(func=lambda call: re.fullmatch(r'^News\s?\w+$', call.data))
def choice_news_query(call):
    global news_msg
    bot.delete_message(call.message.chat.id, call.message.message_id)
    if call.message.chat.id in news_msg:
        bot.delete_message(news_msg[call.message.chat.id].chat.id, news_msg[call.message.chat.id].message_id)
    news_msg[call.message.chat.id] = bot.send_photo(call.message.chat.id, Empty_bg)
    main_news(call.message, call.data.split()[1])


@bot.callback_query_handler(func=lambda call: re.fullmatch(r'^move_to_\s\d+$', call.data))
def next_news_query(call):
    global news
    index = int(call.data.split()[1])
    if 0 <= index < len(news[call.message.chat.id]):
        bot.answer_callback_query(call.id, f'Вы выбрали стр.{index + 1}')
        send_news(call.message, index)
    else:
        bot.answer_callback_query(call.id, '⛔️')


@bot.callback_query_handler(func=lambda call: call.data == 'move_to_ pass')
def news_pass(call):
    bot.answer_callback_query(call.id, '⛔️')


# <<< End news >>>


# <<< YouTube >>>
@bot.message_handler(commands=['youtube'])  # /youtube
def youtube_handler(message: Message) -> None:
    log(message, 'info')
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton('Видео📺', callback_data='Video'),
                 InlineKeyboardButton('Аудио🎧', callback_data='Audio'))
    bot.send_message(message.chat.id, 'Выберите что вам отправить🧐', reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: call.data == 'Audio' or call.data == 'Video')
def youtube_pass(call):
    bot.answer_callback_query(call.id, 'Вы выбрали ' + tr_w(call.data))
    bot.delete_message(call.message.chat.id, call.message.message_id)
    link = bot.send_message(call.message.chat.id, 'Отправьте мне ссылку на видео🔗')
    bot.register_next_step_handler(link, send_audio, call.data)


def send_audio(message: Message, method: str) -> None:
    if re.fullmatch(r'^https?://.*[\r\n]*$', message.text):
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton('YouTube', url=message.text))
        try:
            yt = YouTube(message.text)
        except error.HTTPError:
            bot.send_message(message.chat.id, 'Не могу найти файл😔')
        except exceptions.RegexMatchError:
            bot.send_message(message.chat.id, 'Не верный формат ссылки😔')
        else:
            if method == 'Audio':
                bot.send_chat_action(message.chat.id, 'upload_audio')
                bot.delete_message(message.chat.id, message.message_id)
                bot.send_audio(message.chat.id, open(yt.streams.filter(only_audio=True)[0].download(
                               filename='file'), 'rb'),
                               reply_markup=keyboard, duration=yt.length, title=yt.title, performer=yt.author,
                               caption=f'🎧 {sec_to_time(yt.length)} '
                                       f'| {round(os.path.getsize("file.mp4") / 1000000, 1)} MB |'
                                       f' {yt.streams.filter(only_audio=True)[0].abr.replace("kbps", "")} Kbps')
                try:
                    os.remove(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'file' + '.mp4'))
                except FileNotFoundError:
                    log('Error! Can\'t remove file', 'warning')
            else:
                resolution = None
                try:
                    resolution = '480p'
                    yt.streams.filter(res="480p").order_by('resolution').desc()[0].download(
                        filename='video')
                except IndexError:
                    try:
                        resolution = '320p'
                        yt.streams.filter(res="320p").order_by('resolution').desc()[0].download(
                            filename='video')
                    except IndexError:
                        try:
                            resolution = '240p'
                            yt.streams.filter(res="240p").order_by('resolution').desc()[0].download(
                                filename='video')
                        except IndexError:
                            try:
                                resolution = '144p'
                                yt.streams.filter(res="144p").order_by('resolution').desc()[0].download(
                                    filename='video')
                            except IndexError:
                                bot.send_message(message.chat.id, 'Даное видео имеет слигком большой объем,'
                                                                  ' мой лимит 50МБ😔')
                yt.streams.filter(only_audio=True)[0].download(filename='audio')
                ffmpeg_work = Thread(target=ffmpeg_run, name='ffmpeg_work')
                msg = bot.send_message(message.chat.id, 'Загрузка...')
                ffmpeg_work.start()
                ffmpeg_work.join()
                time.sleep(5)
                bot.delete_message(message.chat.id, message.message_id)
                bot.delete_message(msg.chat.id, msg.message_id)
                bot.send_video(message.chat.id, open('file.mp4', 'rb'),
                               duration=yt.length, reply_markup=keyboard,
                               caption=f'🎧 {sec_to_time(yt.length)} '
                                       f'| {round(os.path.getsize("file.mp4") / 1000000, 1)} MB '
                                       f'| {yt.streams.filter(only_audio=True)[0].abr.replace("kbps", "")} Kbps '
                                       f'| {resolution}')
                try:
                    files = os.listdir(os.path.dirname(__file__))
                    for i in files:
                        if i.startswith('video'):
                            os.remove(os.path.join(os.path.abspath(os.path.dirname(__file__)), i))
                        elif i.startswith('audio'):
                            os.remove(os.path.join(os.path.abspath(os.path.dirname(__file__)), i))
                        elif i.startswith('file'):
                            os.remove(os.path.join(os.path.abspath(os.path.dirname(__file__)), i))
                except FileNotFoundError:
                    log('Error! Can\'t remove file', 'warning')
    else:
        bot.send_message(message.chat.id, 'Не верный формат данных😔')


def ffmpeg_run():
    files = os.listdir(os.path.dirname(__file__))
    input_audio, input_video = None, None
    for i in files:
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


@bot.message_handler(commands=['instagram'])  # /instagram
def instagram_handler(message: Message) -> None:
    log(message, 'info')
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
        bot.register_next_step_handler(msg, get_video)
    else:
        bot.answer_callback_query(call.id, 'Вы выбрали фото')
        bot.register_next_step_handler(msg, get_instagram_photo)


def get_video(message: Message) -> None:
    bot.send_chat_action(message.chat.id, 'upload_video')
    bot.delete_message(message.chat.id, message.message_id)
    if re.fullmatch('^https?://www.instagram.com/.+', message.text):
        url = re.search('^https?://www.instagram.com/p/.+/', message.text).group(0)
        try:
            data = get_instagram_video(url)
        except JSONDecodeError:
            bot.send_message(message.chat.id, 'Не поддерживаются работа закрытыми аккаунтами😔')
        else:
            if data:
                if len(data) == 1:
                    if data[0]['is_video'] is True:
                        keyboard = InlineKeyboardMarkup()
                        keyboard.add(InlineKeyboardButton('Instagram', url=url))
                        bot.send_video(message.chat.id, data[0]['url'], reply_markup=keyboard)
                    else:
                        bot.send_message(message.chat.id, 'По ссылке нет видео😔')
                else:
                    list_data = []
                    for i in data:
                        if i['is_video'] is True:
                            list_data.append(InputMediaVideo(i['url']))
                        else:
                            list_data.append(InputMediaPhoto(i['url']))
                    bot.send_media_group(message.chat.id, list_data)
            else:
                bot.send_message(message.chat.id, 'По ссылке ничего не обнаружено😔')
    else:
        bot.send_message(message.chat.id, 'Не верный формат ссылки😔')


def get_instagram_photo(message: Message) -> None:
    bot.send_chat_action(message.chat.id, 'upload_photo')
    bot.delete_message(message.chat.id, message.message_id)
    if re.fullmatch('^https?://www.instagram.com/.+', message.text):
        keyboard = InlineKeyboardMarkup()
        url = re.search('^https?://www.instagram.com/p/.+/', message.text).group(0)
        keyboard.add(InlineKeyboardButton('Instagram', url=url))
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
        bot.send_message(message.chat.id, 'Не верный формат ссылки😔')


# <<< End Instagram >>>


# <<< Torrent >>>
data_torrents = defaultdict(dict)
torrent_msg = defaultdict(Message)
search_msg = defaultdict(str)
tracker = defaultdict(str)
search = defaultdict(Message)


@bot.message_handler(commands=['torrent'])  # /torrents
def torrents_handler(message: Message) -> None:
    log(message, 'info')
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton('Rutor.info🇷🇺', callback_data='Rutor.info'))
    keyboard.add(InlineKeyboardButton('GTorrent.ru🇷🇺', callback_data='GTorrent.ru'))
    keyboard.add(InlineKeyboardButton('Gamestracker.org🇷🇺', callback_data='Gamestracker.org'))
    search[message.chat.id] = bot.send_message(message.chat.id, 'Выберите платформу️', reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: call.data == 'Gamestracker.org' or call.data == 'GTorrent.ru' or
                            call.data == 'Rutor.info')
def callback_query(call):
    global tracker, search
    bot.delete_message(search[call.message.chat.id].chat.id, search[call.message.chat.id].message_id)
    tracker[call.message.chat.id] = call.data
    msg = bot.send_message(call.message.chat.id, 'Введите ваш запрос✒️')
    bot.register_next_step_handler(msg, send_urls)


def send_urls(message: Message) -> None:
    global data_torrents, torrent_msg, tracker
    search_msg[message.chat.id] = message.text
    if message.chat.id in data_torrents:
        bot.delete_message(torrent_msg[message.chat.id].chat.id, torrent_msg[message.chat.id].message_id)
    if tracker[message.chat.id] == URLS['torrent']['name']:
        data_torrents[message.chat.id] = get_torrents1(message.text)
    elif tracker[message.chat.id] == URLS['torrent2']['name']:
        data_torrents[message.chat.id] = get_torrents2(message.text)
    elif tracker[message.chat.id] == URLS['torrent3']['name']:
        data_torrents[message.chat.id] = get_torrents3(message.text)
    if data_torrents[message.chat.id]:
        create_data_torrents(message)
        torrent_msg[message.chat.id] = bot.send_message(message.chat.id, 'Загрузка...')
        torrent_keyboard(torrent_msg[message.chat.id], 0)
    else:
        data_torrents[message.chat.id] = bot.send_message(message.chat.id, 'Ничего не нашлось😔')


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
    keyboard.add(InlineKeyboardButton(text="⬅️️", callback_data=f"move_ {index - 1 if index > 0 else 'pass'}"),
                 InlineKeyboardButton(text="➡️", callback_data=f"move_ "
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
    torrent_msg[message.chat.id] = bot.edit_message_text(chat_id=torrent_msg[message.chat.id].chat.id,
                                                         message_id=torrent_msg[message.chat.id].message_id,
                                                         text=text_t, reply_markup=keyboard, parse_mode='HTML',
                                                         disable_web_page_preview=True)


@bot.message_handler(func=lambda message: re.match(r'^/\w{8}_\d+_\d+$', str(message.text), flags=re.M))
def load_handler(message: Message):
    global data_torrents
    id_torrent = message.text.split("_")
    id_torrent = id_torrent[1] + '-' + id_torrent[2]
    for i in data_torrents[message.chat.id]:
        for j in i:
            if j['link_t'].endswith(id_torrent):
                with open(f'file{id_torrent}.torrent', 'wb') as f:
                    req = requests.get(j['link_t'], stream=True)
                    for q in req.iter_content(1024):
                        f.write(q)
                bot.send_document(message.chat.id, open(f'file{id_torrent}.torrent', 'rb'))
                try:
                    os.remove(os.path.join(os.path.abspath(os.path.dirname(__file__)), f'file{id_torrent}.torrent'))
                except FileNotFoundError:
                    log('Error! Can\'t remove file', 'warning')


@bot.message_handler(func=lambda message: re.match(r'^/\w{8}__\d+$', str(message.text), flags=re.M))
def load_handler(message: Message):
    id_torrent = message.text.split("_")[-1]
    with open(f'file{id_torrent}.torrent', 'wb') as f:
        req = requests.get(URLS['torrent3']['download'] + id_torrent, stream=True)
        for i in req.iter_content(1024):
            f.write(i)
    bot.send_document(message.chat.id, open(f'file{id_torrent}.torrent', 'rb'))
    try:
        os.remove(os.path.join(os.path.abspath(os.path.dirname(__file__)), f'file{id_torrent}.torrent'))
    except FileNotFoundError:
        log('Error! Can\'t remove file', 'warning')


@bot.message_handler(func=lambda message: re.match(r'^/\w{8}_\d+$', str(message.text), flags=re.M))
def load_handler(message: Message):
    id_torrent = message.text.split("_")[1]
    with open(f'file{id_torrent}.torrent', 'wb') as f:
        req = requests.get(URLS['torrent']['download'] + id_torrent, stream=True)
        for i in req.iter_content(1024):
            f.write(i)
    bot.send_document(message.chat.id, open(f'file{id_torrent}.torrent', 'rb'))
    try:
        os.remove(os.path.join(os.path.abspath(os.path.dirname(__file__)), f'file{id_torrent}.torrent'))
    except FileNotFoundError:
        log('Error! Can\'t remove file', 'warning')


@bot.callback_query_handler(func=lambda call: call.data == 'move_ pass')
def callback_query(call):
    bot.answer_callback_query(call.id, '⛔️')


@bot.callback_query_handler(func=lambda call: re.fullmatch(r'^move_\s\d+$', call.data))
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
@bot.message_handler(commands=['translate'])  # /translate
def translate_handler(message: Message) -> None:
    bot.send_chat_action(message.chat.id, 'typing')
    msg = bot.send_message(message.chat.id, 'Введите то что нужно перевести👁‍🗨')
    bot.register_next_step_handler(msg, trans_word)
    log(message, 'info')


def trans_word(message: Message) -> None:  # Translate function
    log(message, 'info')
    bot.send_chat_action(message.chat.id, 'typing')
    bot.send_message(message.chat.id, tr_w(message.text))


# <<< End Translate >>>


# <<< Sticker GN >>>
@bot.message_handler(commands=['sticker_gn'])  # /sticker_gn
def gn_sticker_handler(message: Message) -> None:
    if db.check_user(message.from_user.id):
        log(message, 'info')
        bot.send_chat_action(message.chat.id, 'upload_photo')
        bot.send_sticker(message.chat.id, db.random_gn_sticker())
    else:
        bot.send_message(message.chat.id, 'Эта функция вам недоступна😔')


# <<< End sticker GN >>>


# <<< Sticker >>>
@bot.message_handler(commands=['sticker'])  # /sticker
def sticker_handler(message: Message) -> None:
    log(message, 'info')
    bot.send_chat_action(message.chat.id, 'upload_photo')
    bot.send_sticker(message.chat.id, db.random_sticker())


# <<< End sticker >>>


# <<< Add new sticker >>>
@bot.message_handler(content_types=['sticker'])  # Add new sticker
def add_sticker_handler(message: Message) -> None:
    db.add_sticker(message.sticker.file_id, message.sticker.emoji, message.sticker.set_name)


# <<< End add new sticker  >>>


# <<< Stat  >>>
stat_msg = defaultdict(Message)


@bot.message_handler(commands=['stat'])  # /stat
def stat_handler(message: Message) -> None:
    global stat_msg
    log(message, 'info')
    data = db.get_stat(message.chat)
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton('Удалить', callback_data='Delete stat'))
    text = '<b>Статистика:</b>\n'
    if data:
        for en, i in enumerate(data):
            if en > 5:
                break
            text += f"<i>{en + 1}.</i> {i['first_name']}" \
                    f" {i['last_name'] if i['last_name'] != 'None' else ''} - {i['karma']}\n"
        stat_msg[message.chat.id] = bot.send_message(message.chat.id, text, parse_mode='HTML', reply_markup=keyboard)
    else:
        bot.send_message(message.chat.id, 'Функция станет доступна когда '
                                          'пользователи вашей группы поставят друг другу \'+\'')


@bot.callback_query_handler(func=lambda call: call.data == 'Delete stat')
def callback_query(call):
    global stat_msg
    if call.message.chat.id in stat_msg:
        bot.delete_message(stat_msg[call.message.chat.id].chat.id, stat_msg[call.message.chat.id].message_id)
    else:
        bot.answer_callback_query(call.id, '⛔️')

# <<< End Stat >>>


# <<< Change karma >>>
@bot.message_handler(content_types=['text'], regexp=r'^\++$')  # Change karma
@bot.message_handler(content_types=['text'], regexp=r'^\-+$')
def text_handler(message: Message) -> None:
    # if message.chat.type != 'private':
    if message.reply_to_message:
        log(message, 'info')
        msg = list(message.text)
        reply_to = message.reply_to_message.from_user
        if msg[0] == '+':
            bot.send_message(message.chat.id, f'{message.from_user.username.title()}'
                                              f' подкинул {len(msg) * 10} к карме😈 '
                                              f'{reply_to.username.title()}\nИтого карма: '
                                              f'{db.change_karma(reply_to, message.chat, msg)}')
        else:
            bot.send_message(message.chat.id, f'{message.from_user.username.title()} '
                                              f'отнял от кармы -{len(msg) * 10}👿 '
                                              f'{reply_to.username.title()}\nИтого карма: '
                                              f'{db.change_karma(reply_to, message.chat, msg)}')


# <<< End change karma >>>


# <<< Add answer >>>
@bot.message_handler(content_types=['text'], regexp=r'^-.+$')  # Add answer to DB
def text_handler(message: Message) -> None:
    db.add_answer(message.text.replace('-', '').lstrip())
    bot.reply_to(message, random.choice(['Принял во внимание', 'Услышал', '+', 'Запомнил', 'Твои мольбы услышаны']))


# <<< End add answer >>>


# <<< Add answer with word >>>
@bot.message_handler(content_types=['text'], regexp=r'^\w+\s-\s\w+$')  # Add answer with word to DB
def text_handler(message: Message) -> None:
    word = re.findall(r'\w.+-', message.text)[0].replace('-', '').rstrip()
    answer = re.findall(r'-.\w.+', message.text)[0].replace('-', '').lstrip()
    db.add_to_db(word, answer)
    bot.reply_to(message, random.choice(['Принял во внимание', 'Услышал', '+', 'Запомнил', 'Твои мольбы услышаны']))


# <<< Code PasteBin >>>
leng_msg = 'None'


@bot.message_handler(commands=['code'])  # Send url on PasteBin
def code_handler(message: Message) -> None:
    global leng_msg
    log(message, 'info')
    bot.send_chat_action(message.chat.id, 'typing')
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
    leng_msg = bot.send_message(message.chat.id, 'Выберите нужный вам язык😈', reply_markup=keyboard)
    bot.register_next_step_handler(leng_msg, callback_to_code)


@bot.callback_query_handler(func=lambda call: re.fullmatch(r'^Enter lang$', call.data))
def callback_query(call):
    bot.answer_callback_query(call.id, 'Введите нужный язык ниже')


def callback_to_code(message: Message) -> None:
    global leng_msg
    if type(leng_msg) == 'str':
        return
    elif type(leng_msg) == Message:
        lang: [dict, None] = db.get_code(message.text)
        if lang is not None:
            bot.delete_message(leng_msg.chat.id, leng_msg.message_id)
            bot.send_chat_action(message.chat.id, 'typing')
            time.sleep(1)
            code = bot.send_message(message.chat.id, 'Отправьте мне ваш код👾')
            bot.register_next_step_handler(code, set_name, lang['code'])
        else:
            bot.send_message(message.chat.id, 'Этот язык не обнаружен в базе данных😔')


@bot.callback_query_handler(func=lambda call: re.fullmatch(r'^Code\s?\w.+$', call.data))
def code_callback_query(call):
    global leng_msg
    bot.delete_message(leng_msg.chat.id, leng_msg.message_id)
    leng_msg = call.data
    leng = call.data.replace('Code ', '')
    bot.answer_callback_query(call.id, 'Вы выбрали ' + leng)
    bot.send_chat_action(call.from_user.id, 'typing')
    time.sleep(1)
    code = bot.send_message(call.message.chat.id, 'Отправьте мне ваш код👾')
    bot.register_next_step_handler(code, set_name, leng)


def set_name(message: Message, leng: str) -> None:  # Set file name
    bot.send_chat_action(message.from_user.id, 'typing')
    time.sleep(1)
    name = bot.send_message(message.chat.id, 'Укажите имя проекта💡')
    bot.register_next_step_handler(name, get_url, message.text, leng)
    log(message, 'info')


def get_url(message: Message, code: str, leng: str) -> None:  # Url PasteBin
    log(message, 'info')
    values = {'api_option': 'paste', 'api_dev_key': f"{API['PasteBin']['DevApi']}",
              'api_paste_code': f'{code}', 'api_paste_private': '0',
              'api_paste_name': f'{message.text}', 'api_paste_expire_date': '1H',
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
first_dice: dict = {'username': None, 'dice': 0}
second_dice: dict = {'username': None, 'dice': 0}


@bot.message_handler(commands=['dice'])  # /dice
def dice_handler(message: Message) -> None:
    log(message, 'info')
    res = requests.post(f'https://' + f'api.telegram.org/bot{TOKEN}/sendDice?chat_id={message.chat.id}').json()
    t = Timer(120.0, reset_users)
    if first_dice['username'] is None:
        first_dice['username'], first_dice['dice'] = message.from_user.username, res['result']['dice']['value']
        t.start()
    elif second_dice['username'] is None:
        second_dice['username'], second_dice['dice'] = message.from_user.username, res['result']['dice']['value']
        t.cancel()
        if first_dice['username'] != second_dice['username']:
            bot.send_chat_action(message.chat.id, 'typing')
            time.sleep(4)
            if first_dice['dice'] > second_dice['dice']:
                bot.send_message(message.chat.id, f'{first_dice["username"].title()}🥇 победил '
                                                  f'{second_dice["username"].title()}🥈')
            elif first_dice['dice'] < second_dice['dice']:
                bot.send_message(message.chat.id, f'{second_dice["username"].title()}🥇 победил '
                                                  f'{first_dice["username"].title()}🥈')
            else:
                bot.send_message(message.chat.id, 'Победила дружба🤝')
        reset_users()


def reset_users() -> None:  # Reset users for Dice game
    first_dice['username'] = None
    first_dice['dice'] = 0
    second_dice['username'] = None
    second_dice['dice'] = 0


# <<< End dice game >>>


# <<< All message >>>
@bot.message_handler(content_types=['text'])  # All messages
@bot.edited_message_handler(content_types=['text'])
def text_handler(message: Message) -> None:
    if dt.fromtimestamp(message.date).strftime("%Y-%m-%d-%H.%M.%S") >= dt.now().strftime("%Y-%m-%d-%H.%M.%S"):
        log(message, 'info')
        text = message.text.lower()
        if text in ['стикер', 'стикерочек', 'sticker']:
            gn_sticker_handler(message)
        elif text in ['гифка', 'гиф', 'гифон', 'gif']:
            gif_handler(message)
        elif text in ['мем', 'мемас', 'мемчик', 'meme']:
            meme_handler(message)
        elif text in ['шутка', 'шутку', 'joke']:
            joke_handler(message)
        elif text in ['кубик', 'зарик', 'кость', 'хуюбик', 'dice']:
            dice_handler(message)
        if rend_d():
            for i in [',', '.', '!', '?', '\'', '\"', '-', '_', ':', ';', '@', '(', ')', '#']:
                text = text.replace(i, '')
            text = list(text.split(' '))
            result = [x for x in text if x in db.get_all_word()]
            if result:
                bot.reply_to(message, db.get_answer(random.choice(result)))
            elif rend_d():
                bot.reply_to(message, db.get_simple_answer())


# <<< End all message >>>


# <<< Answer's  >>>
@bot.message_handler(content_types=['voice'])  # Answer on voice
def voice_handler(message: Message) -> None:
    if rend_d():
        bot.send_chat_action(message.chat.id, 'typing')
        bot.reply_to(message, random.choice(['Чё ты там пизданул? Повтори!', 'Писклявый голосок',
                                             'Лучше бы я это не слышал']))


@bot.message_handler(content_types=['new_chat_members'])  # Answer on new member
def new_member_handler(message: Message) -> None:
    bot.send_chat_action(message.chat.id, 'typing')
    bot.send_message(message.chat.id, random.choice(['Опа чирик! Вечер в хату', 'Приветствую тебя',
                                                     'Алоха друг мой!']))


@bot.message_handler(content_types=['left_chat_member'])  # Answer on left group
def left_member_handler(message: Message) -> None:
    bot.send_chat_action(message.chat.id, 'typing')
    bot.send_message(message.chat.id, random.choice(['Слился падло(', 'Буенос мучачес пидрилас', 'Прощай любовь моя']))


@bot.message_handler(content_types=['location'])  # Answer on location
def location_handler(message: Message) -> None:
    if rend_d():
        bot.send_chat_action(message.chat.id, 'typing')
        bot.reply_to(message.chat.id, ['Скинул мусорам', 'Прикоп или магнит?', 'Ебеня какие то'])


@bot.message_handler(content_types=['contact'])  # Answer on contact
def contact_handler(message: Message) -> None:
    if rend_d():
        bot.send_chat_action(message.chat.id, 'typing')
        bot.reply_to(message.chat.id, random.choice(['Если мне будет одиноко и холодно я знаю куда позвонить',
                                                     'Трубку не берут', 'Сохранил']))


# <<< End answer's  >>>


bot.polling(none_stop=True)
time.sleep(100)


# <<< Donate >>>
# @bot.message_handler(commands=['donate'])  # /donate
# def donate_handler(message: Message) -> None:
#     log(message, 'info')
#     bot.send_chat_action(message.chat.id, 'typing')
#     if message.chat.type == 'private':
#         bot.send_message(message.chat.id, 'Здесь вы можете поддержать разработчика и дать мотивацию '
#                                           'на внесение нового фунционала в <b>GNBot</b>\n'
#                                           'C уважением <i>@Ultra_Xion</i>', parse_mode='HTML')
#         if PAYMENT_TOKEN.split(':')[1] == 'LIVE':
#             keyboard = InlineKeyboardMarkup(row_width=1)
#             keyboard.add(InlineKeyboardButton('1 грн', callback_data='1 UAH'),
#                          InlineKeyboardButton('10 грн', callback_data='10 UAH'),
#                          InlineKeyboardButton('100 грн', callback_data='100 UAH'),
#                          InlineKeyboardButton('1000 грн', callback_data='1000 UAH'),
#                          InlineKeyboardButton('Своя сумма', callback_data='Своя сумма'))
#             msg = bot.send_message(message.chat.id, 'Сумма поддержки💸', reply_markup=keyboard)
#             time.sleep(20)
#             bot.delete_message(msg.chat.id, msg.message_id)
#     else:
#         bot.send_message(message.chat.id, 'К сожелению в группе эта функция недоступна😔\n'
#                                           'Что бы поддержать нас вы можете восползоваться'
#                                           'этой командой в личном чате с ботом 💢@GNTMBot💢')
#
#
# @bot.callback_query_handler(func=lambda call: re.fullmatch(r'^\d+\sUAH$', call.data) or call.data == 'Своя сумма')
# def donate_query(call):
#     bot.answer_callback_query(call.id, 'Вы выбрали ' + call.data)
#     bot.edit_message_text(call.message.text, call.message.chat.id, call.message.message_id)
#     if call.data == 'Своя сумма':
#         msg = bot.send_message(call.message.chat.id, 'Введите сумму🧐')
#         bot.register_next_step_handler(msg, send_payment, 'UAH')
#     else:
#         send_payment(call.message, call.data)
#
#
# def send_payment(message: Message, money) -> None:
#     if money == 'UAH' and message.text.isdigit():
#         local_money = message.text + ' ' + money
#     else:
#         local_money = money
#     price = LabeledPrice('Поддержать', amount=int(local_money.split()[0]) * 100)
#     bot.send_invoice(message.chat.id, title='Поддержка',
#                      description='Поддержка разработчика GNBot',
#                      provider_token=PAYMENT_TOKEN, currency='uah',
#                      photo_url=URLS['logo'],
#                      photo_height=1494, photo_width=1295, photo_size=142,
#                      is_flexible=False, prices=[price],
#                      start_parameter='donate-programmer-gnbot',
#                      invoice_payload='donate-is-done')
#
#
# @bot.shipping_query_handler(func=lambda query: True)
# def shipping(shipping_query: ShippingQuery):
#     bot.answer_shipping_query(shipping_query.id, ok=True,
#                               error_message='Что-то пошло не так😔\n!'
#                                             'Попробуйте повторить операцию чуть позже')
#
#
# @bot.pre_checkout_query_handler(func=lambda query: True)
# def process_pre_checkout_query(pre_checkout_query: PreCheckoutQuery):
#     bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True,
#                                     error_message="Что-то пошло не так😔\n"
#                                                   "Удебитель в правельности вводимых данные "
#                                                   "и попробуйте снова через пару минут")
#
#
# @bot.message_handler(content_types=['successful_payment'])
# def process_successful_payment(message: Message) -> None:
#     promo = message.successful_payment
#     log(f'Successful_payment\nType: {promo.invoice_payload}\nSum: {promo.total_amount}{promo.currency}')
#     bot.send_message(message.chat.id, f'Платеж прошел успешно😌\n'
#                                       f'{message.successful_payment.total_amount // 100} '
#                                       f'{message.successful_payment.currency} были начислены на свет\n'
#                                       f'Благодарим вас за поддержку проекта🥳')
#

# <<< End donate >>>
