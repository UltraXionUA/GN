#!/home/UltraXionUA/.virtualenvs/myvirtualenv/bin/python3.8
# -*- coding: utf-8 -*-
"""Parser file for GNBot"""
from user_agent import generate_user_agent
from urllib.parse import quote
from bs4 import BeautifulSoup
from Config_GNBot.config import URLS
from funcs import log
import requests
import schedule
import db
import time
import re


def get_instagram_video(link: str) -> list:
    data = []
    res = requests.get(link + '?__a=1').json()
    try:
        list_items = res['graphql']['shortcode_media']['edge_sidecar_to_children']['edges']
    except KeyError:
        try:
            data.append({'url': res['graphql']['shortcode_media']['video_url'],
                        'is_video': res['graphql']['shortcode_media']['is_video']})
        except KeyError:
            pass
    else:
        for i in list_items:
            if i['node']['is_video'] is True:
                data.append({'url': i['node']['video_url'], 'is_video': i['node']['is_video']})
            else:
                data.append({'url': i['node']['display_resources'][2]['src'], 'is_video': i['node']['is_video']})
    return data


def get_instagram_photos(link: str) -> list:
    data = []
    res = requests.get(link + '?__a=1').json()
    try:
        list_photos = res['graphql']['shortcode_media']['edge_sidecar_to_children']['edges']
    except KeyError:
        try:
            data.append(res['graphql']['shortcode_media']['display_resources'][2]['src'])
        except KeyError:
            pass
    else:
        for i in list_photos:
            data.append(i['node']['display_resources'][2]['src'])
    return data


def get_torrents3(search: str) -> list:
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
    data = []
    soup = BeautifulSoup(requests.get(URLS['torrent2']['search'].replace('TEXT',  search.replace(' ', '+')),
                                      headers={'User-Agent': generate_user_agent()}).content, 'html.parser')
    list_divs = soup.find('div', id='maincol').find_all_next('table')
    if list_divs:
        for i in list_divs:
            link = i.find('a').get('href')
            name = i.find('a').get_text()
            if link.startswith('/'):
                link = URLS['torrent2']['main'] + link
            soup_link = BeautifulSoup(requests.get(link, headers={'User-Agent': generate_user_agent()}).content,
                                      'html.parser')
            link_t = soup_link.find('div', class_='download_torrent')
            if link_t is not None:
                link_t = URLS['torrent2']['main'] + link_t.find_all_next('a')[0].get('href')
                size = soup_link.find('div',
                                      class_='download_torrent').find_all_next('span',
                                                                               class_='torrent-size')[0].get_text()\
                                                                                .replace('Размер игры: ', '')
                data.append({'name': name, 'size': size, 'link_t': link_t, 'link': link})
    return data


def get_torrents1(search: str) -> list:
    data = []
    soup = BeautifulSoup(requests.get(URLS['torrent']['search'] + quote(search.encode('cp1251')),
                                      headers={'User-Agent': generate_user_agent()}).content, 'html.parser')
    list_divs = soup.find('div', id='center-block').find_all_next('div', class_='blog_brief_news')
    if list_divs:
        del list_divs[0]
        for en, i in enumerate(list_divs, 1):
            size = i.find('div', class_='center col px65').get_text()
            if size != '0':
                name = i.find('strong').get_text()
                link = i.find('a').get('href')
                soup_link = BeautifulSoup(requests.get(link, headers={
                    'User-Agent': generate_user_agent()}).content, 'html.parser')
                link_t = soup_link.find('div', class_='title-tor')
                if link_t is not None:
                    link_t = link_t.find_all_next('a')[0].get('href').replace('/engine/download.php?id=', '')
                    data.append({'name': name, 'size': size, 'link_t': link_t, 'link': link})
        return data


def parser_memes() -> None:  # Main parser
    user = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) ' \
           'Chrome/80.0.3987.116 Safari/537.36 OPR/67.0.3575.87'
    for i in URLS['memes']:
        #  On prod use without UserAgent
        soup = BeautifulSoup(requests.get(i, headers={'User-Agent': user, 'accept': '*/*'}).content, 'html.parser')
        links = set()
        for link in soup.find_all('a'):
            url = link.get('href')
            if re.fullmatch(r'https?://i.redd.it/?\.?\w+.?\w+', url):
                links.add(url)
        db.add_memes(links)
        log('Parser is done', 'info')


def reset_daily():
    log('Reset daily karama is done', 'info')
    db.reset_users()

def send_bad_guy():
    from Config_GNBot.config import bot
    log('Send bad guy is done', 'info')
    bad_guys = db.get_bad_guy()
    for i in bad_guys.keys():
        settings = db.get_setting(i)
        if settings is not  None:
            if settings['bad_guy'] == 'On':
                print(bad_guys[i]["first_name"] + ' ' + bad_guys[i]["last_name"])
                bot.send_message(i, f'Пидор дня: {bad_guys[i]["first_name"]} {bad_guys[i]["last_name"]}')

reset_daily()

def main():
    schedule.every().day.at("20:00").do(send_bad_guy)
    schedule.every().day.at("06:00").do(reset_daily)
    schedule.every().day.at("18:00").do(parser_memes)  # Do pars every 18:00
    schedule.every().day.at("12:00").do(parser_memes)  # Do pars every 12:00
    schedule.every().day.at("06:00").do(parser_memes)  # Do pars every 06:00
    schedule.every().day.at("00:00").do(parser_memes)  # do pars every 00:00

    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    main()


# def get_elner() -> list:
#     data = []
#     soup = BeautifulSoup(requests.get('https://euler.jakumo.org/problems/showall.html',
#                                       headers={'User-Agent': generate_user_agent()}).content, 'html.parser')
#     trs = soup.find('table', class_='problems').find_all_next('tr')
#     for i in trs:
#         link =  i.find('a')
#         if link is not None:
#             data.append({'name': link.get_text(), 'url': link.get('href')})
#     set_eluler(data)


# def get_tasks() -> dict:
#     data = {}
#     soup = BeautifulSoup(requests.get(URLS['logic_tasks']['main'],
#                                       headers={'User-Agent': generate_user_agent()}).content, 'html.parser')
#     div = soup.find('div', class_='article-single-content main-page-content')
#     questions = div.find_all_next('p', style='text-align: left')
#     answers = div.find_all_next('div', id='reply')
#     for question, answer in zip(answers, questions):
#         data[re.sub(r'^\d+.\s', '', answer.find('strong').get_text())] = question.get_text()
#     add_logic_tasks(data)
#



# def girl_parser() -> list:
#     data = []
#     for en, page in enumerate(range(20), 1):
#         print('Page:', en)
#         soup = BeautifulSoup(requests.get(URLS['girl']['search'].replace('PAGE', str(en)),
#                                       headers={'User-Agent': generate_user_agent()}).content, 'html.parser')
#         links = soup.find_all('a', class_='color_button site_button more_button')
#         for i in links:
#             girls = BeautifulSoup(requests.get(i.get('href'),
#                                               headers={'User-Agent': generate_user_agent()}).content, 'html.parser')
#             images = girls.find('div', class_='post_content m20').find_all_next('img')
#             for image in images:
#                 link = URLS['girl']['main'] + image.get('src')
#                 if re.fullmatch(r'https?://paprikolu.net/uploads/posts/.+/thumbs/.+.\w+$', link):
#                     data.append(link)
#         print('+')
#         if data:
#             add_girls(data)
#         data.clear()
#


# def loli_parser() -> None:
#     data = []
#     for id_p in ['66']:  # '109', '49', '43', '7', '311', '285', '311', '286', '46', '93'
#         link = URLS['loli']['search'].replace('66', id_p)
#         for i in range(1000):
#             if i != 0:
#                 print(f'Page: {i}')
#                 soup = BeautifulSoup(requests.get(link + str(i),
#                                                   headers={'User-Agent': generate_user_agent()}).content, 'html.parser')
#                 if soup.find('h2', class_='error-title') is None:
#                     list_loli = soup.find('div', id='maincontent').find_all_next('div', class_='pic-plus')
#                     if list_loli is not None:
#                         print('+')
#                         for q in list_loli:
#                             http = q.find('img').get('src')
#                             if http.startswith('http'):
#                                 data.append(http)
#                             else:
#                                 http = URLS['loli']['main'] + http
#                                 data.append(http)
#                         add_lolis(data)
#                         data.clear()
#                     else:
#                         print('-')
#                 else:
#                     break
#



# from pyvirtualdisplay import Display
# from selenium import webdriver
# from selenium.webdriver.opera.options import Options
# def parser_books() -> None:
#     # options = Options()
#     # options.binary_location = r'/Applications/Opera GX.app'
#     driver = webdriver.Opera(executable_path='/Users/ultraxion/PycharmProjects/GN/operadriver')
#     try:
#         driver.get('http://www.google.com')
#         print(driver.title)  # this should print "Google"
#     finally:
#         driver.quit()


