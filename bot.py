"""Mains file for GNBot"""
from telebot.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove, InputMediaPhoto
from funcs import tr_w, rend_d, hi_r, log, download_song
from config import TOKEN, API
from datetime import datetime as dt
from urllib import parse, request
from pars import parser_memes
from threading import Timer
from telebot import TeleBot
import requests
import db
import time
import random
import re


bot = TeleBot(TOKEN)
log('Bot is successful running!')
# Dice local storage
first_dice: dict = {'username': None, 'dice': 0}
second_dice: dict = {'username': None, 'dice': 0}
data_songs = []
len_songs = 0


@bot.message_handler(commands=['start'])  # /start
def start_handler(message: Message) -> None:
    bot.send_chat_action(message.chat.id, 'typing')
    bot.send_message(message.chat.id, 'Здравствуй, меня зовут GNBot🖥\n'
                                      'Я создан дабы служить верой и правдой сообществу 💎Голубой носок💎')
    log(message, 'info')


@bot.message_handler(commands=['help'])  # /help
def help_handler(message: Message) -> None:
    bot.send_chat_action(message.chat.id, 'typing')
    bot.send_message(message.chat.id, 'Тут должна была быть помощь🆘, но её тут не будет🌚\n'
                                      'Если что пиши мне: 💢@Ultra_Xion💢')
    log(message, 'info')


@bot.message_handler(commands=['gif'])  # /gif
def gif_handler(message: Message) -> None:
    bot.send_chat_action(message.chat.id, 'upload_video')
    while True:
        data = requests.get(API['API_Gif']).json()
        if hi_r(data['data']['rating']):
            bot.send_document(message.chat.id, data['data']['images']['downsized_large']['url'])
            break
    log(message, 'info')


@bot.message_handler(commands=['joke'])  # /joke
def joke_handler(message: Message) -> None:
    log(message, 'info')
    bot.send_chat_action(message.chat.id, 'typing')
    time.sleep(2)
    joke = db.get_joke()
    if joke['panchline'] != 'False':
        bot.send_message(message.chat.id, joke['setup'] + '🧐')
        time.sleep(4)
        bot.send_message(message.chat.id, joke['panchline'] + '🌚')
    else:
        bot.send_message(message.chat.id, joke['setup'] + '🌚')


@bot.message_handler(commands=['ru_meme'])  # /ru_meme
def meme_handler(message: Message) -> None:
    bot.send_chat_action(message.chat.id, 'upload_photo')
    bot.send_photo(message.chat.id, db.random_meme())
    log(message, 'info')


@bot.message_handler(commands=['en_meme'])  # /en_meme
def meme_en_handler(message: Message) -> None:
    bot.send_chat_action(message.chat.id, 'upload_photo')
    meme = requests.get(API['API_Meme']).json()
    bot.send_photo(message.chat.id, meme['url'])
    log(message, 'info')


@bot.message_handler(commands=['weather'])  # /weather
def weather_handler(message: Message) -> None:
    log(message, 'info')
    bot.send_chat_action(message.chat.id, 'typing')
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(InlineKeyboardButton('Харьков', callback_data='Kharkov'),
                 InlineKeyboardButton('Полтава', callback_data='Poltava'))
    msg = bot.send_message(message.chat.id, 'Погода в каком из города вас интерсует?🧐', reply_markup=keyboard)
    time.sleep(10)
    bot.delete_message(msg.chat.id, msg.message_id)


@bot.message_handler(commands=['detect'])  # /music
def detect_handler(message: Message) -> None:
    log(message, 'info')
    msg = bot.send_message(message.chat.id, 'Запишите песню которую нужно определить')
    bot.register_next_step_handler(msg, detect_music)


@bot.message_handler(commands=['music'])  # /music
def music_handler(message: Message) -> None:
    log(message, 'info')
    bot.send_chat_action(message.chat.id, 'typing')
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(InlineKeyboardButton('По исполнителю🎤', callback_data='artist?q='),
                 InlineKeyboardButton('По треку🎼', callback_data='track?q='))
    msg = bot.send_message(message.chat.id, 'Как будем искать музыку?🎧', reply_markup=keyboard)
    time.sleep(15)
    bot.delete_message(message.chat.id, msg.message_id)


@bot.message_handler(commands=['translate'])  # /translate
def translate_handler(message) -> None:
    bot.send_chat_action(message.chat.id, 'typing')
    msg = bot.send_message(message.chat.id, 'Введите то что нужно перевести👁‍🗨')
    bot.register_next_step_handler(msg, trans_word)
    log(message, 'info')


@bot.message_handler(commands=['sticker_gn'])  # /sticker_gn
def gn_sticker_handler(message: Message) -> None:
    bot.send_chat_action(message.chat.id, 'upload_photo')
    bot.send_sticker(message.chat.id, db.random_gn_sticker())
    log(message, 'info')


@bot.message_handler(commands=['sticker'])  # /sticker
def sticker_handler(message: Message) -> None:
    bot.send_chat_action(message.chat.id, 'upload_photo')
    bot.send_sticker(message.chat.id, db.random_sticker())
    log(message, 'info')


@bot.message_handler(content_types=['sticker'])  # Add new sticker
def add_sticker_handler(message: Message) -> None:
    db.add_sticker(message.sticker.file_id, message.sticker.emoji, message.sticker.set_name)


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


@bot.message_handler(content_types=['text'], regexp=r'^\++$')  # Change karma
@bot.message_handler(content_types=['text'], regexp=r'^\-+$')
def text_handler(message: Message) -> None:
    if message.reply_to_message:
        log(message, 'info')
        msg = list(message.text)
        reply_to = message.reply_to_message.from_user
        if msg[0] == '+':
            bot.send_message(message.chat.id, f'{message.from_user.username.title()} подкинул {len(msg) * 10} к карме '
                                              f'{reply_to.username.title()}\nИтого карма: '
                                              f'{db.change_karma(reply_to, msg)}')
        else:
            bot.send_message(message.chat.id, f'{message.from_user.username.title()} осуждает на -{len(msg) * 10} '
                                              f'{reply_to.username.title()}\nИтого карма: '
                                              f'{db.change_karma(reply_to, msg)}')


@bot.message_handler(content_types=['text'], regexp=r'^-.+$')  # Add answer to DB
def text_handler(message: Message) -> None:
    db.add_answer(message.text.replace('-', '').lstrip())
    bot.reply_to(message, random.choice(['Принял во внимание', 'Услышал', '+', 'Запомнил', 'Твои мольбы услышаны']))


@bot.message_handler(content_types=['text'], regexp=r'^\w+.?-.?\w.+$')  # Add answer with word to DB
def text_handler(message: Message) -> None:
    buf = message.text.lower().split()
    print(buf)
    if buf[0] not in ['---', 'кто-то', 'где-то', 'когда-нибудь', 'кто-нибудь', 'зачем-то']:
        word = re.findall(r'\w.+-', message.text)[0].replace('-', '').rstrip()
        answer = re.findall(r'-.\w.+', message.text)[0].replace('-', '').lstrip()
        db.add_to_db(word, answer)
        bot.reply_to(message, random.choice(['Принял во внимание', 'Услышал', '+', 'Запомнил', 'Твои мольбы услышаны']))


@bot.message_handler(commands=['code'])  # Send url on PasteBin
def code_handler(message: Message) -> None:
    log(message, 'info')
    bot.send_chat_action(message.chat.id, 'typing')
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton('Bash', callback_data='bash'),
                 InlineKeyboardButton('HTML 5', callback_data='html5'),
                 InlineKeyboardButton('CSS', callback_data='css'))
    keyboard.add(InlineKeyboardButton('JavaScript', callback_data='javascript'),
                 InlineKeyboardButton('Pascal', callback_data='pascal'),
                 InlineKeyboardButton('JSON', callback_data='json'))
    keyboard.add(InlineKeyboardButton('Perl', callback_data='perl'),
                 InlineKeyboardButton('C#', callback_data=' csharp'),
                 InlineKeyboardButton('Objective C', callback_data='objc'))
    keyboard.add(InlineKeyboardButton('C', callback_data='c'),
                 InlineKeyboardButton('C++', callback_data='cpp'),
                 InlineKeyboardButton('Ruby', callback_data='ruby'))
    keyboard.add(InlineKeyboardButton('Delphi', callback_data='delphi'),
                 InlineKeyboardButton('Java', callback_data='java'),
                 InlineKeyboardButton('CoffeeScript', callback_data='coffeescript'))
    keyboard.add(InlineKeyboardButton('PHP', callback_data='php'),
                 InlineKeyboardButton('Python', callback_data='python'),
                 InlineKeyboardButton('PostgreSQL', callback_data='postgresql'))
    keyboard.add(InlineKeyboardButton('SQL', callback_data='sql'),
                 InlineKeyboardButton('Swift', callback_data='swift'),
                 InlineKeyboardButton('Rust', callback_data='rust'))
    leng = bot.send_message(message.chat.id, 'Выберите нужный вам язык😈', reply_markup=keyboard)
    time.sleep(20)
    bot.delete_message(message.chat.id, leng.message_id)


@bot.message_handler(commands=['dice'])  # /dice
def dice_handler(message: Message) -> None:
    log(message, 'info')
    res = requests.post(f'https://api.telegram.org/bot{TOKEN}/sendDice?chat_id={message.chat.id}').json()
    log(message, 'info')
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
            for i in [',', '.', '!', '?', '\'', '\"', '-']:
                text = text.replace(i, '')
            text = list(text.split(' '))
            result = [x for x in text if x in db.get_all_word()]
            if result:
                bot.send_chat_action(message.chat.id, 'typing')
                bot.reply_to(message, db.get_answer(random.choice(result)))
            elif rend_d():
                bot.reply_to(message, db.get_simple_answer())


@bot.callback_query_handler(func=lambda call: True)  # Catch callback's
def callback_query(call):
    if call.data == 'move_to pass':
        bot.answer_callback_query(call.id, '⛔️')
    elif re.fullmatch(r'^move_to\s\d$', call.data):
        if call.message.content_type == 'photo':
            bot.edit_message_media(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                   media=InputMediaPhoto(call.message.photo[-1].file_id),
                                   reply_markup=inline_keyboard(int(call.data.split()[1])))
        else:
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  text=call.message.text,
                                  reply_markup=inline_keyboard(int(call.data.split()[1])))
        bot.answer_callback_query(call.id)
    elif re.fullmatch(r'^ID:\s?\d+$', call.data):
        song_id = call.data.replace('ID: ', '')
        global data_songs
        for i in data_songs:
            if i['id'] == int(song_id):
                bot.send_chat_action(call.message.chat.id, 'upload_document')
                bot.send_audio(call.message.chat.id, audio=download_song(i['preview']), caption=i['link'],
                                performer=i['name'], title=i['title'])
                break
    elif call.data == 'artist?q=' or call.data == 'track?q=':
        bot.edit_message_text(call.message.text, call.message.chat.id, call.message.message_id)
        bot.send_chat_action(call.message.chat.id, 'typing')
        time.sleep(1)
        if call.data == 'artist?q=':
            bot.answer_callback_query(call.id, 'Вы выбрали поиск по артисту')
            msg = bot.send_message(call.message.chat.id, 'Введите исполнителя👤')
        else:
            bot.answer_callback_query(call.id, 'Вы выбрали поиск по треку')
            msg = bot.send_message(call.message.chat.id, 'Введите название трека🖊')
        bot.register_next_step_handler(msg, get_song, call.data)
    elif call.data == 'Kharkov' or call.data == 'Poltava':
        bot.edit_message_text(call.message.text, call.message.chat.id, call.message.message_id)
        res = requests.get(API['API_Weather'].format(call.data)).json()
        bot.answer_callback_query(call.id, 'Вы выбрали ' + tr_w(call.data))
        bot.send_message(call.message.chat.id, f"Город: {tr_w(call.data).title()}🏢\n"
                                               f"Погода: {tr_w(res['weather'][0]['description']).title()}☀️\n"
                                               f"Теспература: {(res['main']['temp'])}°C🌡\n"
                                               f"По ощушению: {(res['main']['feels_like'])}°C🌡\n"
                                               f"Атмосферное давление: {res['main']['pressure']} дин·см²⏲\n"
                                               f"Влажность: {res['main']['humidity']} %💧\n"
                                               f"Ветер: {res['wind']['speed']} м\\с💨\n",
                         reply_markup=ReplyKeyboardRemove(selective=True))
    else:
        bot.edit_message_text(call.message.text, call.message.chat.id, call.message.message_id)
        bot.send_chat_action(call.from_user.id, 'typing')
        time.sleep(1)
        code = bot.send_message(call.message.chat.id, 'Отправьте мне ваш код👾')
        bot.register_next_step_handler(code, set_name, call.data)


def detect_music(message: Message):  # Detect your music
    API['AUDD_data']['url'] = bot.get_file_url(message.voice.file_id).replace('https://api.telegram.org',
                                                                              'http://esc-ru.appspot.com/') \
                              + '?host=api.telegram.org'
    result = requests.post(API['AUDD'], data=API['AUDD_data']).json()
    if result['status'] == 'success' and result['result'] is not None:
        if result['result']['deezer']:
            bot.send_photo(message.chat.id, result['result']['deezer']['artist']['picture_xl'],
                           caption=f"{result['result']['artist']} - {result['result']['title']}\n"
                                   f"{result['result']['deezer']['link']}")
        else:
            bot.send_message(message.chat.id, f"{result['result']['artist']} - {result['result']['title']}")


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
              'api_paste_format': f'{leng}', 'api_user_key': f"{API['PasteBin']['UserApi']}",
              'api_paste_name': f'{message.text}', 'api_paste_code': f'{code}'}
    data = parse.urlencode(values).encode('utf-8')
    req = request.Request(API['PasteBin']['URL'], data)
    with request.urlopen(req) as response:
        url_bin = str(response.read()).replace('b\'', '').replace('\'', '')
    bot.send_chat_action(message.chat.id, 'typing')
    time.sleep(1)
    bot.send_message(message.chat.id, url_bin)


def get_song(message: Message, choice: str) -> None:  # Get song
    log(message, 'info')
    global data_songs
    res = requests.get(API['API_Deezer'] + choice + message.text.replace(' ', '+')).json()
    print(res)
    try:
        if res['data']:
            if choice == 'artist?q=':
                songs = requests.get(res['data'][0]['tracklist'].replace('limit=50', 'limit=100')).json()
                if songs['data']:
                    data_songs.clear()
                    data_songs = [{'id': i['id'], 'title': i['title'], 'name': i['contributors'][0]['name'],
                                   'link': i['link'], 'preview': i['preview']} for i in songs['data']]
                    if data_songs:
                        bot.send_photo(message.chat.id, res['data'][0]['picture_xl'],
                                       reply_markup=inline_keyboard(0))
                    else:
                        raise FileExistsError
            elif choice == 'track?q=':
                data_songs.clear()
                data_songs = [{'id': i['id'], 'title': i['title'], 'name': i['artist']['name'],
                               'link': i['link'], 'preview': i['preview']} for i in res['data']]
                if data_songs:
                    bot.send_message(message.chat.id, 'Результат поиска🔎', reply_markup=inline_keyboard(0))
                else:
                    raise FileExistsError
            else:
                raise FileExistsError
        else:
            raise FileExistsError
    except FileExistsError:
        bot.send_message(message.chat.id, 'К сожеления ничего не нашлось😔')


def inline_keyboard(some_index) -> InlineKeyboardMarkup:  # Navigation for music
    global data_songs, len_songs
    some_keyboard = choose_keyboard(some_index)
    some_keyboard.add(
        InlineKeyboardButton(text="⬅️️",
                             callback_data=f"move_to {some_index - 1 if some_index > 0 else 'pass'}"),
        InlineKeyboardButton(text="➡️",
                             callback_data=f"move_to "
                                           f"{some_index + 1 if some_index < len_songs - 1 else 'pass'}"))
    return some_keyboard


def choose_keyboard(some_index) -> InlineKeyboardMarkup:  # Buttons for music
    global data_songs, len_songs
    some_keyboard = InlineKeyboardMarkup()
    list_data, buf = [], []
    for i, en in enumerate(data_songs, 1):
        buf.append(en)
        if i % 5 == 0:
            list_data.append(buf.copy())
            buf.clear()
    len_songs = len(list_data)
    for songs in list_data[some_index]:
        some_keyboard.add(InlineKeyboardButton(f"{songs['name']} - {songs['title']}",
                                               callback_data=f"ID: {songs['id']}"))
    return some_keyboard


def trans_word(message: Message) -> None:  # Translate function
    log(message, 'info')
    bot.send_chat_action(message.chat.id, 'typing')
    bot.send_message(message.chat.id, tr_w(message.text))


def reset_users() -> None:  # Reset users for Dice game
    first_dice['username'] = None
    first_dice['dice'] = 0
    second_dice['username'] = None
    second_dice['dice'] = 0


bot.polling(none_stop=True)
time.sleep(100)
