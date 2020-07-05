#!/home/ultraxion/GNBot/GN/.venv/bin/activate
#!/usr/bin/ python3.8
# -*- coding: utf-8 -*-
"""Parser file for GNBot"""

from telebot.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from datetime import datetime as dt, timedelta
from Config_GNBot.config import URLS, bot
from user_agent import generate_user_agent
from collections import defaultdict
from urllib.parse import quote
from bs4 import BeautifulSoup
from threading import Thread
from threading import Timer
from funcs import log, get_bid_size
import random
import requests
import schedule
import db
import time
import re

# <<< Proxy >>
https = ['194.44.199.242:8880', '213.6.65.30:8080', '109.87.40.23:44343']

def get_instagram_videos(link: str) -> list:
    """
    :param link
    :type link: str
    :return: list videos instagram
    :rtype: list
    """
    data = []
    for https_ in https:
        proxy = {'http': f'http://{https_}', 'https': f'https://{https_}'}
        try:
            res = requests.get(link + '?__a=1', proxies=proxy, headers={'User-Agent': generate_user_agent()}).json()
        except Exception:
            continue
        else:
            try:
                list_items = res['graphql']['shortcode_media']['edge_sidecar_to_children']['edges']
            except KeyError:
                try:
                    data.append({'url': res['graphql']['shortcode_media']['video_url'],
                                'is_video': res['graphql']['shortcode_media']['is_video']})
                except KeyError:
                    return data
            else:
                for item in list_items:
                    if item['node']['is_video'] is True:
                        data.append({'url': item['node']['video_url'], 'is_video': item['node']['is_video']})
                    else:
                        data.append({'url': item['node']['display_resources'][2]['src'], 'is_video': item['node']['is_video']})
            return data


def get_instagram_photos(link: str) -> list:
    """
    :param link
    :type link: str
    :return: list photos instagram
    :rtype: list
    """
    data = []
    for https_ in https:
        try:
            res = requests.get(link + '?__a=1', proxies={'http': f'http://{https_}', 'https': f'https://{https_}'},
                               headers={'User-Agent': generate_user_agent()}).json()
        except Exception:
            continue
        else:
            try:
                list_photos = res['graphql']['shortcode_media']['edge_sidecar_to_children']['edges']
            except KeyError:
                try:
                    data.append(res['graphql']['shortcode_media']['display_resources'][2]['src'])
                except KeyError:
                    return data
            else:
                for photo in list_photos:
                    data.append(photo['node']['display_resources'][2]['src'])
            return data


def get_torrents3(search: str) -> list:
    """
    :param search
    :type search: str
    :return: list torrents
    :rtype: list
    """
    data = []
    soup = BeautifulSoup(requests.get(URLS['torrent3']['search'] + quote(search),
                                    headers={'User-Agent': generate_user_agent()}).content, 'html.parser')
    list_gai = soup.find_all('tr', class_='gai')
    list_tum = soup.find_all('tr', class_='tum')
    if list_gai and list_tum:
        for gai, tum in zip(list_gai, list_tum):
            link1 = gai.find_all_next('a')
            link2 = tum.find_all_next('a')
            load1 = link1[0].get('href')
            load2 = link2[0].get('href')
            if load1 is not None and load2 is not None:
                text1 = link1[2].get_text()
                text2 = link2[2].get_text()
                link1 = URLS['torrent3']['main'] + link1[2].get('href')
                link2 = URLS['torrent3']['main'] + link2[2].get('href')
                size1 = gai.find_all_next('td')[3].get_text()
                size2 = tum.find_all_next('td')[3].get_text()
                data.append({'name': text1, 'size': size1, 'link_t': load1, 'link': link1})
                data.append({'name': text2, 'size': size2, 'link_t': load2, 'link': link2})
    return data


def get_torrents2(search: str) -> list:
    """
    :param search
    :type search: str
    :return: list torrents
    :rtype: list
    """
    data = []
    soup = BeautifulSoup(requests.get(URLS['torrent2']['search'].replace('TEXT',  search.replace(' ', '+')),
                                      headers={'User-Agent': generate_user_agent()}).content, 'html.parser')
    list_divs = soup.find('div', id='maincol').find_all_next('table')
    if list_divs:
        for div in list_divs:
            link = div.find('a').get('href')
            name = div.find('a').get_text()
            if link.startswith('/'):
                link = URLS['torrent2']['main'] + link
            soup_link = BeautifulSoup(requests.get(link, headers={'User-Agent': generate_user_agent()}).content,
                                      'html.parser')
            link_t = soup_link.find('div', class_='download_torrent')
            if link_t is not None:
                link_t = URLS['torrent2']['main'] + link_t.find_all_next('a')[0].get('href')
                size = soup_link.find('div', class_='download_torrent').find_all_next('span', class_='torrent-size')[0].get_text().replace('Размер игры: ', '')
                data.append({'name': name, 'size': size, 'link_t': link_t, 'link': link})
    return data


def get_torrents1(search: str) -> list:
    """
    :param search
    :type search: str
    :return: list torrents
    :rtype: list
    """
    data = []
    soup = BeautifulSoup(requests.get(URLS['torrent']['search'] + quote(search.encode('cp1251')),
                                      headers={'User-Agent': generate_user_agent()}).content, 'html.parser')
    list_divs = soup.find('div', id='center-block').find_all_next('div', class_='blog_brief_news')
    if list_divs:
        del list_divs[0]
        for div in list_divs:
            size = div.find('div', class_='center col px65').get_text()
            if size != '0':
                name = div.find('strong').get_text()
                link = div.find('a').get('href')
                soup_link = BeautifulSoup(requests.get(link, headers={
                    'User-Agent': generate_user_agent()}).content, 'html.parser')
                link_t = soup_link.find('div', class_='title-tor')
                if link_t is not None:
                    link_t = link_t.find_all_next('a')[0].get('href').replace('/engine/download.php?id=', '')
                    data.append({'name': name, 'size': size, 'link_t': link_t, 'link': link})
        return data


def parser_memes() -> None:
    """
    .. notes:: Dayle pasre memes from redit
    :return: None
    """
    log('Parser is done', 'info')
    soup = BeautifulSoup(requests.get(URLS['memes'], headers={'User-Agent': generate_user_agent()}).content, 'html.parser')
    links = set()
    for link in soup.find_all('a'):
        url = link.get('href')
        if url is not None and re.fullmatch(r'https?://i.redd.it/?\.?\w+.?\w+', url):
            links.add(url)
    db.add_memes(links)


def unpin_msg(chat_id: [str or int]) -> None:
    try:
        bot.unpin_chat_message(chat_id)
    except Exception:
        log('Error in unpin', 'error')


# <<< Bag guys >>
def send_bad_guy() -> None:
    """
    .. notes:: Select most active users un group
    :return: None
    """
    log('Send bad guy is done', 'info')
    for chat_id, users in db.get_bad_guy().items():
        text = '🎉<b>Пидор' + f"{'ы' if len(users) > 1 else ''}" + ' дня</b>🎉\n' + ''.join(f"🎊💙<i>{db.get_from(user['id'], 'Users_name')}</i>💙🎊\n" for user in users) + f'Прийми{"те" if len(users) > 1 else ""} наши поздравления👍'
        try:
            msg = bot.send_message(chat_id, text, parse_mode='HTML')
            bot.pin_chat_message(msg.chat.id, msg.message_id, disable_notification=False)
            Timer(28800.0, unpin_msg, msg.chat.id).start()
        except Exception:
            log('Error in bad guy', 'error')
    db.reset_users()

# <<< End bag guys >>


# <<< Roulette >>
chips_data = defaultdict(dict)
chips_msg = defaultdict(Message)
msg_res = defaultdict(Message)
summary = defaultdict(dict)

def get_color(num: int) -> str:
    return f'{num}🔴' if num in [1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36] else '0️⃣' if num == 0 else f'{num}⚫'


def play_roulette() -> None:
    global summary
    def casino(chat_id: str, data: dict) -> None:
        try:
            bot.unpin_chat_message(chat_id)
        except Exception:
            log('Error in unpin casino', 'Warning')
        nums = [num for num in range(0, 36)]
        random.shuffle(nums)
        msg_res[chat_id] = bot.send_message(chat_id, f'[{get_color(nums.pop(0))}] [{get_color(nums.pop(0))}] '
                                                     f'➡️[{get_color(nums.pop(0))}]⬅️ [{get_color(nums.pop(0))}] '
                                                     f'[{get_color(nums.pop(0))}]')
        start = random.randint(1, 20)
        for num in nums[start:start + 10]:
            time.sleep(0.75)
            text = msg_res[chat_id].text.replace('➡️', '').replace('⬅️', '').replace('[', '').replace(']', '').split()[1:]
            text.append(get_color(num))
            msg_res[chat_id] = bot.edit_message_text(f'[{text[0]}] [{text[1]}]  ➡️[{text[2]}]⬅️ [{text[3]}] [{text[4]}]',
                                                        msg_res[chat_id].chat.id, msg_res[chat_id].message_id)
        text = msg_res[chat_id].text.split()[2].replace("➡️[", "").replace("]⬅️", "")
        bid_size = get_bid_size(db.get_all_from(chat_id))
        for user_id, bids in data.items():
            summary[user_id] = 0
            for number, count in bids.items():
                if get_color(int(number))[-1] == text[-1]:
                    if text[-1] == '⃣':
                        summary[user_id] += count * bid_size
                        db.change_karma(user_id, '+', count * bid_size)
                    else:
                        summary[user_id] += count * bid_size
                        db.change_karma(user_id, '+', count * bid_size)
                else:
                    summary[user_id] -= count * bid_size
                    db.change_karma(user_id, '-', count * bid_size)
        list_d = list(summary.items())
        list_d.sort(key=lambda i: i[1], reverse=True)
        users_text = ''.join(f'<b>{db.get_from(user_id, "Users_name")}</b> {"+" if res > 0 else ""}{res} очков\n' for user_id, res in list_d)
        bot.edit_message_text(f'{msg_res[chat_id].text}\n\nВыпало <b>{text}</b>\n\n{users_text}',
                              msg_res[chat_id].chat.id, msg_res[chat_id].message_id, parse_mode='HTML')
        summary.clear()

    for chat_id_, data_ in chips_data.items():
        Thread(target=casino, name='Casino', args=[chat_id_, data_]).start()
    chips_msg.clear()
    chips_data.clear()


def daily_roulette():
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton('36🔴', callback_data='roulette 36 red'),
                 InlineKeyboardButton('35⚫', callback_data='roulette 35 black'),
                 InlineKeyboardButton('34🔴', callback_data='roulette 34 red'))
    keyboard.add(InlineKeyboardButton('33⚫', callback_data='roulette 33 black'),
                 InlineKeyboardButton('32🔴', callback_data='roulette 32 red'),
                 InlineKeyboardButton('31⚫', callback_data='roulette 31 black'))
    keyboard.add(InlineKeyboardButton('30🔴', callback_data='roulette 30 red'),
                 InlineKeyboardButton('29⚫', callback_data='roulette 29 black'),
                 InlineKeyboardButton('28⚫', callback_data='roulette 28 black'))
    keyboard.add(InlineKeyboardButton('27🔴', callback_data='roulette 27 red'),
                 InlineKeyboardButton('26⚫', callback_data='roulette 26 black'),
                 InlineKeyboardButton('25🔴', callback_data='roulette 25 red'))
    keyboard.add(InlineKeyboardButton('24⚫', callback_data='roulette 24 black'),
                 InlineKeyboardButton('23🔴', callback_data='roulette 23 red'),
                 InlineKeyboardButton('22⚫', callback_data='roulette 22 black'))
    keyboard.add(InlineKeyboardButton('21🔴', callback_data='roulette 21 red'),
                 InlineKeyboardButton('20⚫', callback_data='roulette 20 black'),
                 InlineKeyboardButton('19🔴', callback_data='roulette 19 red'))
    keyboard.add(InlineKeyboardButton('18🔴', callback_data='roulette 18 red'),
                 InlineKeyboardButton('17⚫', callback_data='roulette 17 black'),
                 InlineKeyboardButton('16🔴', callback_data='roulette 16 red'))
    keyboard.add(InlineKeyboardButton('15⚫', callback_data='roulette 15 black'),
                 InlineKeyboardButton('14🔴', callback_data='roulette 14 red'),
                 InlineKeyboardButton('13⚫', callback_data='roulette 13 black'))
    keyboard.add(InlineKeyboardButton('12🔴', callback_data='roulette 12 red'),
                 InlineKeyboardButton('11⚫', callback_data='roulette 11 black'),
                 InlineKeyboardButton('10⚫', callback_data='roulette 10 black'))
    keyboard.add(InlineKeyboardButton('9🔴', callback_data='roulette 9 red'),
                 InlineKeyboardButton('8⚫', callback_data='roulette 8 black'),
                 InlineKeyboardButton('7🔴', callback_data='roulette 7 red'))
    keyboard.add(InlineKeyboardButton('6⚫', callback_data='roulette 6 black'),
                 InlineKeyboardButton('5🔴', callback_data='roulette 5 red'),
                 InlineKeyboardButton('4⚫', callback_data='roulette 4 black'))
    keyboard.add(InlineKeyboardButton('3🔴', callback_data='roulette 3 red'),
                 InlineKeyboardButton('2⚫', callback_data='roulette 2 black'),
                 InlineKeyboardButton('1🔴', callback_data='roulette 1 red'))
    keyboard.add(InlineKeyboardButton('0️⃣', callback_data='roulette 0 zero'))
    time_end = str(dt.now() + timedelta(minutes=60.0)).split()[-1].split(':')
    for chat in db.get_roulette():
        data = db.get_from(chat['id'], 'Setting')
        users_alert = '<b><i>Добро пожаловать в казино</i></b>🌃😎\n'
        if data['alert'] == 'On':
            users = db.get_all_from(chat['id'])
            users_alert += ''.join(f'@{user["username"]}, ' if len(users) != en else f'@{user["username"]}\n' for en, user in enumerate(users, 1) if user['username'] != 'None')
        try:
            msg = bot.send_message(chat['id'], f'{users_alert}'
                                               f'Минимальная ставка {get_bid_size(db.get_all_from(chat["id"]))} очков\n'
                                               f'Конец в <b>{time_end[0]}:{time_end[1]}</b>\n',
                                   reply_markup=keyboard, parse_mode='HTML')
            bot.pin_chat_message(chat['id'], msg.message_id, disable_notification=True)
        except Exception:
            log('Error in daily roulette', 'error')
        else:
            Timer(3600.0, play_roulette).start()


def get_access(chat_id: int, user_id: int) -> bool:
    bid_size = get_bid_size(db.get_all_from(chat_id))
    if user_id not in chips_data[chat_id] and db.get_user_karma(user_id) >= bid_size or \
            db.get_user_karma(user_id) > sum([count for count in chips_data[chat_id][user_id].values()]) * bid_size:
        return True
    return False


def edit_roulette_msg(chat_id: int, user_id: int):
    global chips_msg
    bid_size = get_bid_size(db.get_all_from(chat_id))
    text = 'Ставки:\n' + ''.join(f'{db.get_from(user_id, "Users_name")} {get_color(int(number))} — {count * bid_size}\n' for number, count in chips_data[chat_id][user_id].items())
    chips_msg[chat_id] = bot.send_message(chat_id, text) if chat_id not in chips_msg else bot.edit_message_text(text, chat_id, chips_msg[chat_id].message_id)



@bot.callback_query_handler(func=lambda call: re.fullmatch(r'roulette\s\d+\s\w+$', call.data))
def callback_query(call):
    global chips_data, chips_msg
    if str(dt.now()).split()[1].split(':')[0] == '20':
        number, color = call.data.split()[1:]
        if get_access(call.message.chat.id, call.from_user.id):
            bot.answer_callback_query(call.id, 'Ставка принята')
            if call.from_user.id not in chips_data[call.message.chat.id]:
                chips_data[call.message.chat.id][call.from_user.id] = {}
            if number not in chips_data[call.message.chat.id][call.from_user.id]:
                chips_data[call.message.chat.id][call.from_user.id][number] = 0
            chips_data[call.message.chat.id][call.from_user.id][number] += 1
            edit_roulette_msg(call.message.chat.id, call.from_user.id)
        else:
            bot.answer_callback_query(call.id, 'У вас не хватает фишек')
    else:
        bot.answer_callback_query(call.id, 'Прийом ставок закончен')

# <<< End roulette >>


def main() -> None:
    """
    .. notes:: Daily tasks
    :return: None
    """
    schedule.every().day.at("00:00").do(parser_memes)  # Do pars every 00:00
    schedule.every().day.at("18:00").do(parser_memes)  # Do pars every 18:00
    schedule.every().day.at("20:00").do(daily_roulette) # Daily roulette 20:00
    schedule.every().day.at("22:00").do(send_bad_guy)  # Identify bad guy's
    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    main()