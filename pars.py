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
from funcs import log
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
        text = '🎉<b>Пидор' + f"{'ы' if len(users) > 1 else ''}" + ' дня</b>🎉\n'
        for user in users:
            text += f"🎊💙<i>{db.get_from(user['id'], 'Users_name')}</i>💙🎊\n"
        text += f'Прийми{"те" if len(users) > 1 else ""} наши поздравления👍'
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


def play_roulette() -> None:
    global chips_data, msg_res
    def get_color(num: [int,str]) -> str:
        if type(num) == int:
            return f'{num}⭕' if num == 0 else f'{num}🔴' if num % 2 == 0 else f'{num}⚫'
        else:
            return 'zero' if num == '⭕' else 'red' if num == '🔴' else 'black'


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
            msg_res[chat_id] = bot.edit_message_text(
                f'[{text[0]}] [{text[1]}]  ➡️[{text[2]}]⬅️ [{text[3]}] [{text[4]}]',
                msg_res[chat_id].chat.id, msg_res[chat_id].message_id)
        text = msg_res[chat_id].text.split()[2].replace("➡️[", "").replace("]⬅️", "")
        name_color = get_color(list(text)[-1])
        summary = defaultdict(dict)
        for user_id, bids in data.items():
            summary[user_id] = 0
            for bid in bids:
                if bid['color'] == name_color:
                    if name_color == 'zero':
                        summary[user_id] += int(bid['chips']) * 10
                        db.change_karma(user_id, '+', int(bid['chips']) * 10)
                    else:
                        summary[user_id] += int(bid['chips'])
                        db.change_karma(user_id, '+', int(bid['chips']))
                else:
                    summary[user_id] -= int(bid['chips'])
                    db.change_karma(user_id, '-', int(bid['chips']))
        users_text = ''
        list_d = list(summary.items())
        list_d.sort(key=lambda i: i[1], reverse=True)
        for user_id, res in list_d:
            users_text += f'<b>{db.get_from(user_id, "Users_name")}</b> {"+" if res > 0 else ""}{res} очков\n'
        bot.edit_message_text(f'{msg_res[chat_id].text}\n\nВыпало <b>{text}</b>\n\n{users_text}',
                              msg_res[chat_id].chat.id, msg_res[chat_id].message_id, parse_mode='HTML')
        summary.clear()

    for chat_id_, data_ in chips_data.items():
        Thread(target=casino, name='Casino', args=[chat_id_, data_]).start()

    chips_msg.clear()
    chips_data.clear()


def daily_roulette():
    global chips_msg, chips_data
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton('50⚫', callback_data='roulette 50 black'),
                 InlineKeyboardButton('100⚫', callback_data='roulette 100 black'),
                 InlineKeyboardButton('250⚫', callback_data='roulette 250 black'))
    keyboard.add(InlineKeyboardButton('50🔴', callback_data='roulette 50 red'),
                 InlineKeyboardButton('100🔴', callback_data='roulette 100 red'),
                 InlineKeyboardButton('250🔴', callback_data='roulette 250 red'))
    keyboard.add(InlineKeyboardButton('10⭕', callback_data='roulette 10 zero'),
                 InlineKeyboardButton('50⭕', callback_data='roulette 50 zero'),
                 InlineKeyboardButton('100⭕', callback_data='roulette 100 zero'))
    time_end = str(dt.now() + timedelta(minutes=60.0)).split()[-1].split(':')
    for chat in db.get_roulette():
        data = db.get_from(chat['id'], 'Setting')
        users_alert = ''
        if data['alert'] == 'On':
            users = db.get_all_from(chat['id'])
            for en, user in enumerate(users, 1):
                if user['username'] is not None and user['username'] != 'None':
                    users_alert += f'@{user["username"]}{", " if len(users) != en else ""}'
        try:
            msg = bot.send_message(chat['id'], f'<b><i>Добро пожаловать в казино</i></b>🌃😎\n{users_alert}\nКонец в '
                                               f'<b>{time_end[0]}:{time_end[1]}</b>\n'
                                               f'Делайте ваши ставки\n',
                                   reply_markup=keyboard, parse_mode='HTML')
            bot.pin_chat_message(chat['id'], msg.message_id, disable_notification=True)
        except Exception:
            log('Error in daily roulette', 'error')
        else:
            Timer(3600.0, play_roulette).start()


@bot.callback_query_handler(func=lambda call: re.fullmatch(r'roulette\s\d+\s\w+$', call.data))
def callback_query(call):
    global chips_data, chips_msg
    if str(dt.now()).split()[1].split(':')[0] == '20':
        chips, color = call.data.split()[1:]
        if db.get_user_karma(call.from_user.id) > int(chips):
            user = f"{call.from_user.first_name} {call.from_user.last_name}" if call.from_user.last_name is not None else call.from_user.first_name
            if call.message.chat.id not in chips_data:
                chips_msg[call.message.chat.id] = bot.send_message(call.message.chat.id, 'Ставки:')
            if call.from_user.id not in chips_data[call.message.chat.id]:
                chips_data[call.message.chat.id][call.from_user.id] = []
            if len(chips_data[call.message.chat.id][call.from_user.id]) < 3:
                bot.answer_callback_query(call.id, 'Ставка принята')
                chips_data[call.message.chat.id][call.from_user.id].append({'color': color, 'chips': chips})
                chips_msg[call.message.chat.id] = bot.edit_message_text(f'{chips_msg[call.message.chat.id].text}\n'
                                                                    f'{user} {chips}{"🔴" if color == "red" else "⚫" if color == "black" else "⭕"}',
                                                                    call.message.chat.id, chips_msg[call.message.chat.id].message_id)
            else:
                bot.answer_callback_query(call.id, 'Превышен лимит ставок')
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