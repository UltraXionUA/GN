#!/home/ultraxion/GNBot/GN/.venv/bin/activate
#!/usr/bin/ python3.8
# -*- coding: utf-8 -*-
"""Parser file for GNBot"""
from telebot.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from funcs import log, get_bid_size, get_color
from datetime import datetime as dt, timedelta
from Config_GNBot.config import URLS, bot
from user_agent import generate_user_agent
from collections import defaultdict
from urllib.parse import quote
from bs4 import BeautifulSoup
from threading import Thread
from threading import Timer
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
            res = requests.get(link + '?__a=1',proxies={'http': f'http://{https_}', 'https': f'https://{https_}'},
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
            bot.pin_chat_message(msg.chat.id, msg.message_id, disable_notification=True)
            db.set_pin_bad_gays(chat_id)
        except Exception:
            log('Error in bad guy', 'error')
    db.reset_users()


def unpin_bag_guys() -> None:
    bad_guys = db.get_pin_bad_gays()
    for chat_id in bad_guys:
        try:
            bot.unpin_chat_message(chat_id.decode('utf-8'))
        except Exception:
            log('Can\'t unpin bad_guy message', 'warning')
# <<< End bag guys >>


# <<< Roulette >>
chips_data = defaultdict(dict)
chips_msg = defaultdict(Message)
msg_res = defaultdict(Message)
summary = defaultdict(dict)
start_msg = defaultdict(Message)


def get_access(chat_id: int, user_id: int, type_: [str or int]) -> bool:
    """
    :param chat_id
    :type chat_id: int
    :param user_id
    :type user_id: int
    :param type_
    :type type_: str or int
    :rtype: bool
    .. seealso:: check user karma and bid if they has and give access to bids
    """
    bid = get_bid_size(db.get_all_from(chat_id))
    if user_id not in chips_data[chat_id]:
        if db.get_user_karma(user_id) >= (bid["simple_bid"] if type_.isdigit() else bid["upper_bid"]):
            return True
    else:
        total = sum([count * (bid["simple_bid"] if value.isdigit() else bid["upper_bid"]) for value, count in chips_data[chat_id][user_id].items()])
        if db.get_user_karma(user_id) >= (bid["simple_bid"] if type_.isdigit() else bid["upper_bid"]) + total:
            return True
    return False


def edit_roulette_msg(chat_id: int):
    global chips_msg
    text = '<b><i>Ставки:</i></b>\n'
    bid = get_bid_size(db.get_all_from(chat_id))
    for user_id, bids in chips_data[chat_id].items():
        for type_, count in bids.items():
            if type_.isdigit():
                text += f'<b>{db.get_from(user_id, "Users_name")}</b> {get_color(int(type_))} — <b>{count * bid["simple_bid"]}</b>\n'
            else:
                text += f"<b>{db.get_from(user_id, 'Users_name')}</b>" \
                        f" {'🔴' if type_ == 'red' else '⚫' if type_ == 'black' else '2️⃣' if type_ == 'even' else '1️⃣'} " \
                        f"— <b>{count * bid['upper_bid']}</b>\n"
    chips_msg[chat_id] = bot.send_message(chat_id, text, parse_mode='HTML') if chat_id not in chips_msg else \
    bot.edit_message_text(text, chat_id, chips_msg[chat_id].message_id, parse_mode='HTML')


def play_roulette() -> None:
    global summary
    def casino(chat_id: int, data: dict) -> None:
        try:
            bot.unpin_chat_message(chat_id)
        except Exception:
            log('Error in unpin casino', 'Warning')
        nums = [num for num in range(0, 37)]
        start = random.randint(0, 32)
        msg_res[chat_id] = bot.send_message(chat_id, f'[{get_color(nums.pop(start))}] [{get_color(nums.pop(start))}] '
                                                     f'➡️[{get_color(nums.pop(start))}]⬅️ [{get_color(nums.pop(start))}] '
                                                     f'[{get_color(nums.pop(start))}]')
        for num in nums[start:]:
            time.sleep(0.75)
            text = msg_res[chat_id].text.replace('➡️', '').replace('⬅️', '').replace('[', '').replace(']', '').split()[1:]
            text.append(get_color(num))
            msg_res[chat_id] = bot.edit_message_text(f'[{text[0]}] [{text[1]}]  ➡️[{text[2]}]⬅️ [{text[3]}] [{text[4]}]',
                                                        msg_res[chat_id].chat.id, msg_res[chat_id].message_id)
        if len(nums) - start < 10:
            for num in nums[:10 - (len(nums) - start)]:
                time.sleep(0.75)
                text = msg_res[chat_id].text.replace('➡️', '').replace('⬅️', '').replace('[', '').replace(']', '').split()[1:]
                text.append(get_color(num))
                msg_res[chat_id] = bot.edit_message_text(f'[{text[0]}] [{text[1]}]  ➡️[{text[2]}]⬅️ [{text[3]}] [{text[4]}]',
                                                            msg_res[chat_id].chat.id, msg_res[chat_id].message_id)
        text = msg_res[chat_id].text.split()[2].replace("➡️[", "").replace("]⬅️", "")
        bid = get_bid_size(db.get_all_from(chat_id))
        for user_id, bids in data.items():
            summary[user_id] = 0
            for type_, count in bids.items():
                if text == '0️⃣' and type_ == '0' or text != '0️⃣' and (type_.isdigit() and text[-1].isdigit()) and \
                        text == get_color(int(type_)):
                    summary[user_id] += (count * bid["simple_bid"]) * 27
                    db.change_karma(user_id, '+', (count * bid["simple_bid"]) * 27)
                elif text != '0️⃣' and (type_ == 'even' and int(text[:-1]) % 2 == 0) \
                    or (type_ == 'not_even' and int(text[:-1]) % 2 != 0) \
                    or (type_ == 'red' and text[-1] == '🔴') or (type_ == 'black' and text[-1] == '⚫'):
                    summary[user_id] += count * bid["upper_bid"]
                    db.change_karma(user_id, '+', (count * bid["upper_bid"]))
                else:
                    if type_ == 'red' or type_ == 'black' or type_ == 'even' or type_ == 'not_even':
                        summary[user_id] -= count * bid["upper_bid"]
                        db.change_karma(user_id, '-', (count * bid["upper_bid"]))
                    else:
                        summary[user_id] -= count * bid["simple_bid"]
                        db.change_karma(user_id, '-', (count * bid["simple_bid"]))
        list_d = list(summary.items())
        list_d.sort(key=lambda i: i[1], reverse=True)
        users_text = '<i><b>Результаты</b></i>\n' + ''.join(f'<b>{db.get_from(user_id, "Users_name")}</b> <i>{"+" if res > 0 else ""}{res}</i> очков\n' for user_id, res in list_d)
        bot.edit_message_text(f'{msg_res[chat_id].text}\n\nВыпало <b>{text}</b>\n\n{users_text}',
                              msg_res[chat_id].chat.id, msg_res[chat_id].message_id, parse_mode='HTML')
        summary.clear()
        try:
            del chips_msg[chat_id]
            del msg_res[chat_id]
            del chips_data[chat_id]
        except KeyError:
            log('Can\'t delete key in storage ', 'warning')


    for chat_id_, msg in start_msg.items():
        if int(chat_id_) not in chips_data:
            try:
                bot.unpin_chat_message(chat_id_)
                bot.delete_message(chat_id_, msg.message_id)
            except Exception:
                log('Can\'t delete start_msg in casino', 'warning')
    for chat_id_, data_ in chips_data.items():
        Thread(target=casino, name='Casino', args=[chat_id_, data_]).start()


def daily_roulette():
    global start_msg
    keyboard: InlineKeyboardMarkup = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton('36🔴', callback_data='roulette 36'),
                 InlineKeyboardButton('35⚫', callback_data='roulette 35'),
                 InlineKeyboardButton('34🔴', callback_data='roulette 34'))
    keyboard.add(InlineKeyboardButton('33⚫', callback_data='roulette 33'),
                 InlineKeyboardButton('32🔴', callback_data='roulette 32'),
                 InlineKeyboardButton('31⚫', callback_data='roulette 31'))
    keyboard.add(InlineKeyboardButton('30🔴', callback_data='roulette 30'),
                 InlineKeyboardButton('29⚫', callback_data='roulette 29'),
                 InlineKeyboardButton('28⚫', callback_data='roulette 28'))
    keyboard.add(InlineKeyboardButton('27🔴', callback_data='roulette 27'),
                 InlineKeyboardButton('26⚫', callback_data='roulette 26'),
                 InlineKeyboardButton('25🔴', callback_data='roulette 25'))
    keyboard.add(InlineKeyboardButton('24⚫', callback_data='roulette 24'),
                 InlineKeyboardButton('23🔴', callback_data='roulette 23'),
                 InlineKeyboardButton('22⚫', callback_data='roulette 22'))
    keyboard.add(InlineKeyboardButton('21🔴', callback_data='roulette 21'),
                 InlineKeyboardButton('20⚫', callback_data='roulette 20'),
                 InlineKeyboardButton('19🔴', callback_data='roulette 19'))
    keyboard.add(InlineKeyboardButton('18🔴', callback_data='roulette 18'),
                 InlineKeyboardButton('17⚫', callback_data='roulette 17'),
                 InlineKeyboardButton('16🔴', callback_data='roulette 16'))
    keyboard.add(InlineKeyboardButton('15⚫', callback_data='roulette 15'),
                 InlineKeyboardButton('14🔴', callback_data='roulette 14'),
                 InlineKeyboardButton('13⚫', callback_data='roulette 13'))
    keyboard.add(InlineKeyboardButton('12🔴', callback_data='roulette 12'),
                 InlineKeyboardButton('11⚫', callback_data='roulette 11'),
                 InlineKeyboardButton('10⚫', callback_data='roulette 10'))
    keyboard.add(InlineKeyboardButton('9🔴', callback_data='roulette 9'),
                 InlineKeyboardButton('8⚫', callback_data='roulette 8'),
                 InlineKeyboardButton('7🔴', callback_data='roulette 7'))
    keyboard.add(InlineKeyboardButton('6⚫', callback_data='roulette 6'),
                 InlineKeyboardButton('5🔴', callback_data='roulette 5'),
                 InlineKeyboardButton('4⚫', callback_data='roulette 4'))
    keyboard.add(InlineKeyboardButton('3🔴', callback_data='roulette 3'),
                 InlineKeyboardButton('2⚫', callback_data='roulette 2'),
                 InlineKeyboardButton('1🔴', callback_data='roulette 1'))
    keyboard.add(InlineKeyboardButton('0️⃣', callback_data='roulette 0'))
    keyboard.add(InlineKeyboardButton('🔴', callback_data='roulette red'),
                 InlineKeyboardButton('⚫', callback_data='roulette black'))
    keyboard.add(InlineKeyboardButton('2️⃣', callback_data='roulette even'),
                 InlineKeyboardButton('1️⃣', callback_data='roulette not_even'))
    time_end = str(dt.now() + timedelta(minutes=60.0)).split()[-1].split(':')
    for chat in db.get_id_from_where('Setting', 'roulette', 'On'):
        data = db.get_from(chat['id'], 'Setting')
        users_alert = '<b><i>Добро пожаловать в казино</i></b>🌃😎\n'
        if data['alert'] == 'On':
            users = db.get_all_from(chat['id'])
            users_alert += ''.join(f'<b>@{user["username"]}</b>, ' if len(users) != en else f'<b>@{user["username"]}</b>\n' for en, user in enumerate(users, 1) if user['username'] != 'None')
        bid = get_bid_size(db.get_all_from(chat['id']))
        try:
            start_msg[chat['id']] = bot.send_message(chat['id'], f'{users_alert}'
                                               f'Ставки <b>{bid["simple_bid"]}</b>\<b>{bid["upper_bid"]}</b> очков\n'
                                               f'Конец в <b>{time_end[0]}:{time_end[1]}</b>\n'
                                               f'Правила <b>/casino_rule</b>',
                                   reply_markup=keyboard, parse_mode='HTML')
            bot.pin_chat_message(chat['id'], start_msg[chat['id']].message_id, disable_notification=True)
        except Exception:
            log('Error in daily roulette', 'error')
        else:
            Timer(3601.0, play_roulette).start()


@bot.callback_query_handler(func=lambda call: re.fullmatch(r'roulette\s.+$', call.data))
def callback_query(call):
    global chips_data
    if str(dt.now()).split()[1].split(':')[0] == '20':
        type_ = call.data.split()[1]
        if get_access(call.message.chat.id, call.from_user.id, type_):
            if call.from_user.id not in chips_data[call.message.chat.id]:
                chips_data[call.message.chat.id][call.from_user.id] = {}
            if type_ not in chips_data[call.message.chat.id][call.from_user.id]:
                chips_data[call.message.chat.id][call.from_user.id][type_] = 0
            if len(chips_data[call.message.chat.id][call.from_user.id].keys()) < 4:
                bot.answer_callback_query(call.id, 'Ставка принята')
                chips_data[call.message.chat.id][call.from_user.id][type_] += 1
                edit_roulette_msg(call.message.chat.id)
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
    schedule.every().day.at("06:00").do(unpin_bag_guys)  # Unpin bad guy's 06:00
    schedule.every().day.at("18:00").do(parser_memes) # Do pars every 18:00
    schedule.every().day.at("20:00").do(daily_roulette) # Daily roulette 20:00
    schedule.every().day.at("22:00").do(send_bad_guy)  # Identify bad guy's 22:00
    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    main()