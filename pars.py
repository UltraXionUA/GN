#!/home/ultraxion/GNBot/GN/.venv/bin/activate
#!/usr/bin/ python3.8
# -*- coding: utf-8 -*-
"""Parser file for GNBot"""
from casino import daily_roulette
from Config_GNBot.config import URLS, bot
from user_agent import generate_user_agent
from urllib.parse import quote
from bs4 import BeautifulSoup
from funcs import log
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


send_bad_guy()
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