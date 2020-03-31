"""Main file for GNBot"""
from telebot.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove
from funcs import tr_w, rend_d, hi_r, log
from config import TOKEN, API  # TEST_TOKEN
from datetime import datetime as dt
from pars import parser_memes
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


@bot.message_handler(commands=['start'])  # /start
def start_handler(message: Message) -> None:
    bot.send_chat_action(message.chat.id, 'typing')
    bot.send_message(message.chat.id, 'Здравствуй, меня зовут GNBot🖥\n'
                                      'Я создан дабы служить верой и правдой сообществу 💎Голубой носок💎')
    log(message, 'info')


@bot.message_handler(commands=['help'])  # /help
def help_handler(message: Message) -> None:
    bot.send_chat_action(message.chat.id, 'typing')
    bot.send_message(message.chat.id, 'start - Начальная страница\n'
                                      'ru_meme - Рандомный мем из нашей базы данных\n'
                                      'en_meme - Рандомный англоязычный мем\n'
                                      'gif - Рандомная гифка\n'
                                      'joke - Рандомная шутка\n'
                                      'dice - Кинуть кубик\n'
                                      'sticker - Рандомный стикер нашей базы дданых\n'
                                      'sticker_gn - Рандомный стикер ГН\n'
                                      'weather - Погода на текущий день\n'
                                      'translate - Пеереводчик\n'
                                      '______Админ_команды______\n'
                                      'Обучение бота: \n'
                                      '- Любой текст (Добавить фразу в БД)\n'
                                      'Слово - Любой текст (Добавить фразу с ассоциацией к слову в БД)\n'
                                      '-parser (Отпарсить контент в БД)')
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
    msg = bot.send_message(message.chat.id, 'Погода в каком из города вас интерсует?', reply_markup=keyboard)
    time.sleep(10)
    bot.delete_message(msg.chat.id, msg.message_id)


@bot.message_handler(commands=['translate'])  # /translate
def translate_handler(message) -> None:
    bot.send_chat_action(message.chat.id, 'typing')
    msg = bot.send_message(message.chat.id, 'Введите то что нужно перевести')
    bot.register_next_step_handler(msg, trans_word)
    log(message, 'info')


def trans_word(message: Message) -> None:
    log(message, 'info')
    bot.send_message(message.chat.id, tr_w(message.text))


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


@bot.message_handler(commands=['dice'])  # /dice
def dice_handler(message: Message) -> None:
    def reset_users():
        first_dice['username'] = None
        first_dice['dice'] = 0
        second_dice['username'] = None
        second_dice['dice'] = 0
    res = requests.post(f'https://api.telegram.org/bot{TOKEN}/sendDice?chat_id={message.chat.id}').json()
    log(message, 'info')
    if first_dice['username'] is None:
        first_dice['username'] = res['result']['chat']['username']
        first_dice['dice'] = res['result']['dice']['value']
    elif second_dice['username'] is None:
        second_dice['username'] = res['result']['chat']['username']
        second_dice['dice'] = res['result']['dice']['value']
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
    print(message)
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
        elif text in ['кубик', 'зарик', 'кости', 'dice']:
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
    bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id, text=call.message.text)
    if call.data == 'Kharkov' or 'Poltava':
        res = requests.get(API['API_Weather'].format(call.data)).json()
        bot.answer_callback_query(call.id, 'Вы выбрали ' + tr_w(call.data))
        bot.send_message(call.from_user.id, f"Город: {tr_w(call.data).title()}🏢\n"
                                            f"Погода: {tr_w(res['weather'][0]['description']).title()}☀️\n"
                                            f"Теспература: {(res['main']['temp'])}°C🌡\n"
                                            f"По ощушению: {(res['main']['feels_like'])}°C🌡\n"
                                            f"Атмосферное давление: {res['main']['pressure']} дин·см²⏲\n"
                                            f"Влажность: {res['main']['humidity']} %💧\n"
                                            f"Ветер: {res['wind']['speed']} м\\с💨\n",
                         reply_markup=ReplyKeyboardRemove(selective=True))


bot.polling(none_stop=True)
time.sleep(100)
