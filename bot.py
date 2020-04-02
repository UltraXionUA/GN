"""Mains file for GNBot"""
from telebot.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove
from funcs import tr_w, rend_d, hi_r, log, download_song
from config import TOKEN, API, PasteBin
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
# import os
# import shutil
# import subprocess


bot = TeleBot(TOKEN)
log('Bot is successful running!')
# Dice local storage
first_dice: dict = {'username': None, 'dice': 0}
second_dice: dict = {'username': None, 'dice': 0}


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


@bot.message_handler(content_types=['text'], regexp=r'^-parser$')  # Turn on parser
def parser_handler(message: Message) -> None:
    parser_memes()
    bot.reply_to(message, random.choice(['Я сделаль', 'Завдання виконано', 'Готово',
                                         'Задание выполнено', 'Затея увенчалась успехом']))


@bot.message_handler(content_types=['text'], regexp=r'^\+$')  # Change karma
@bot.message_handler(content_types=['text'], regexp=r'^\-$')
def text_handler(message: Message) -> None:
    if message.reply_to_message:
        log(message, 'info')
        reply_to = message.reply_to_message.from_user
        if message.text == '+':
            bot.send_message(message.chat.id, f'{message.from_user.username.title()} подкинул 10 к карме '
                                              f'{reply_to.username.title()}\nИтого карма: '
                                              f'{db.change_karma(reply_to, "+")}')
        else:
            bot.send_message(message.chat.id, f'{message.from_user.username.title()} осуждает на -10 '
                                              f'{reply_to.username.title()}\nИтого карма: '
                                              f'{db.change_karma(reply_to, "-")}')
        db.change_karma(reply_to, message.text)
        time.sleep(20)


@bot.message_handler(content_types=['text'], regexp=r'^-.+$')  # Add answer to DB
def text_handler(message: Message) -> None:
    db.add_answer(message.text.replace('-', '').lstrip())
    bot.reply_to(message, random.choice(['Принял во внимание', 'Услышал', '+', 'Запомнил', 'Твои мольбы услышаны']))


@bot.message_handler(content_types=['text'], regexp=r'^\w+.?-.?\w.+$')  # Add answer with word to DB
def text_handler(message: Message) -> None:
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
def callback_query(call) -> None:
    time.sleep(1)
    if call.data == '<-' or call.data == '->':
        bot.send_message(call.message.chat.id, "Услышал <- или ->")
    elif re.fullmatch(r'^.+-.+$', call.data):
        name_title = call.data.replace('-', ' ').replace(' ', '+')
        print(name_title)
        res = requests.get(API['API_Deezer'] + 'track?q=' + name_title).json()
        data = {'link': res['data'][0]['link'], 'preview': res['data'][0]['preview'],
                'title': res['data'][0]['title'], 'name': res['data'][0]['artist']['name'],
                'duration': res['data'][0]['duration']}
        bot.send_chat_action(call.message.chat.id, 'upload_document')
        bot.send_audio(call.message.chat.id, audio=download_song(data['preview']), caption=data['link'],
                       duration=data['duration'], performer=data['name'], title=data['title'])
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


def set_name(message: Message, leng: str) -> None:  # Set file name
    bot.send_chat_action(message.from_user.id, 'typing')
    time.sleep(1)
    name = bot.send_message(message.chat.id, 'Укажите имя проекта💡')
    bot.register_next_step_handler(name, get_url, message.text, leng)
    log(message, 'info')


def get_url(message: Message, code: str, leng: str) -> None:  # Url PasteBin
    log(message, 'info')
    values = {'api_option': 'paste', 'api_dev_key': f'{PasteBin["DevApi"]}',
              'api_paste_code': f'{code}', 'api_paste_private': '0',
              'api_paste_name': f'{message.text}', 'api_paste_expire_date': '1H',
              'api_paste_format': f'{leng}', 'api_user_key': f'{PasteBin["UserApi"]}',
              'api_paste_name': f'{message.text}', 'api_paste_code': f'{code}'}
    data = parse.urlencode(values).encode('utf-8')
    req = request.Request(PasteBin['URL'], data)
    with request.urlopen(req) as response:
        url_bin = str(response.read()).replace('b\'', '').replace('\'', '')
    bot.send_chat_action(message.chat.id, 'typing')
    time.sleep(1)
    bot.send_message(message.chat.id, url_bin)


def get_song(message: Message, choice: str) -> None:
    log(message, 'info')
    res = requests.get(API['API_Deezer'] + choice + message.text.replace(' ', '+')).json()
    keyboard = InlineKeyboardMarkup()
    try:
        if res['data']:
            if choice == 'artist?q=':
                songs = requests.get(res['data'][0]['tracklist'].replace('50', f'{5}')).json()
                if songs['data']:
                    data = [{'title': i['title'], 'name': i['contributors'][0]['name']} for i in songs['data']]
                    if data:
                        print(data)
                        for song in data:
                            keyboard.add(InlineKeyboardButton(f"{song['name']} - {song['title']}",
                                                              callback_data=f"{song['name']}-{song['title']}"))
                        keyboard.add(InlineKeyboardButton('⬅️', callback_data='<-'),
                                     InlineKeyboardButton('➡️', callback_data='->'))
                        bot.send_photo(message.chat.id, res['data'][0]['picture_xl'], reply_markup=keyboard)
                    else:
                        raise FileExistsError
            elif choice == 'track?q=':
                data = [{'title': i['title'], 'name': i['artist']['name']} for i in res['data']]
                if data:
                    for i in range(5):
                        keyboard.add(InlineKeyboardButton(f"{data[i]['name']} - {data[i]['title']}",
                                                          callback_data=f"{data[i]['name']}-{data[i]['title']}"))
                        print(data[i]['name'], data[i]['title'])
                    keyboard.add(InlineKeyboardButton('⬅️', callback_data='<-'),
                                 InlineKeyboardButton('➡️', callback_data='->'))
                    bot.send_message(message.chat.id, f'Результат поиска:', reply_markup=keyboard)
                else:
                    raise FileExistsError
            else:
                raise FileExistsError
        else:
            raise FileExistsError
    except FileExistsError:
        bot.send_message(message.chat.id, 'К сожеления ничего не нашлось😔')


def trans_word(message: Message) -> None:
    log(message, 'info')
    bot.send_chat_action(message.chat.id, 'typing')
    bot.send_message(message.chat.id, tr_w(message.text))


def reset_users() -> None:
    first_dice['username'] = None
    first_dice['dice'] = 0
    second_dice['username'] = None
    second_dice['dice'] = 0


bot.polling(none_stop=True)
time.sleep(100)

# requests.post(f'https://api.telegram.org/bot{TOKEN}/sendAudio?chat_id={message.chat.id}'
#                               f'&audio={preview}&caption={link}&duration={duration}&performer={name}'
#                               f'&title={title}&disable_notification=True')


# song = None
#             try:
#                 subprocess.Popen(["ypc", f"\"{message.text}\"", "-nAudio", "-a"], stdout=subprocess.PIPE,
#                                                                                          stderr=subprocess.STDOUT)
#                 folder, dir = [] '/Users/ultraxion/PycharmProjects/GN/Audio'
#                 for i in os.walk(dir):
#                     folder.append(i)
#                 for address, dirs, files in folder:
#                     for file in files:
#                         if file.endswith('.mp3') and song is None:
#                             song = file
#                             print(song)
#                 for the_file in os.listdir(dir):
#                     file_path = os.path.join(dir, the_file)
#                     try:
#                         if os.path.isfile(file_path):
#                             os.unlink(file_path)
#                         elif os.path.isdir(file_path):
#                             shutil.rmtree(file_path)
#                     except Exception as e:
#                         print(e)
#             except Exception as e:
#                 print("PIZDA!", e)
