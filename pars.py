# -*- coding: utf-8 -*-
"""Parser file for GNBot"""
from user_agent import generate_user_agent
from bs4 import BeautifulSoup
from db import add_memes
from config import URLS
from funcs import log
import requests
import schedule
import time
import re


def get_torrents(search: str) -> list:
    data = []
    soup = BeautifulSoup(requests.get(URLS['torrent'] + search.replace(' ', '+'),
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
        add_memes(links)
        log('Parser is done', 'info')


def main():
    schedule.every().day.at("18:00").do(parser_memes)  # Do pars every 18:00
    schedule.every().day.at("12:00").do(parser_memes)  # Do pars every 12:00
    schedule.every().day.at("06:00").do(parser_memes)  # Do pars every 06:00
    schedule.every().day.at("00:00").do(parser_memes)  # do pars every 00:00
    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    main()
