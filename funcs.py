# -*- coding: utf-8 -*-
"""Function file for GNBot"""
from googletrans import Translator
from random import randint
from langdetect import detect
from datetime import datetime as dt
import logging
import re


logging.basicConfig(filename="logger.log", level=logging.INFO, filemode='w')  # Turn on logger


def log(message, type_l='None') -> None:  # Message processing
    if type(message) is not str:
        def get_info():
            return "<!-------!> " + str(dt.now().strftime("%Y-%m-%d-%H.%M.%S")) + " <!-------!>\n " \
                                               f"Сообщение от {message.from_user.first_name}" \
                                               f"{message.from_user.last_name} " \
                                               f"(id = {str(message.from_user.id)})\n" \
                                               f"\'{message.text}\'"
        print(get_info())
        if type_l == 'info':
            logging.info(get_info())
        elif type_l == 'error':
            logging.error(get_info())
        elif type_l == 'warning':
            logging.warning(get_info())
        else:
            print('Wrong type logging input')
    else:
        print("<!-------!>", dt.now().strftime("%Y-%m-%d-%H.%M.%S"), "<!-------!>\n", message)
        logging.info(message + ' ' + str(dt.now().strftime("%Y-%m-%d-%H.%M.%S")))


def get_weather_emoji(code: str) -> str:
    for emoji, codes in {'🌦': ['200', '201', '202'], '🌩': ['230', '231', '232', '233'],
                         '🌧': ['500', '501', '502', '511', '520'],
                         '🌨': ['600', '601', '602', '610', '621', '622', '300', '301', '302', '521'],
                         '☁️': ['611', '612', '804'], '⛅️': ['700', '711', '721', '731', '741', '751', '802'],
                         '☀️': ['800'], '️🌤️': ['801'], '🌥': ['803']}.items():
        if code in codes:
            return emoji
    else:
        return '🌪'


def get_day(data: str) -> str:
    week_day = dt.strptime(data, '%Y-%m-%d').isoweekday()
    for num, day in {1: 'ПН', 2: 'ВТ', 3: 'СР', 4: 'ЧТ', 5: 'ПТ', 6: 'СБ', 7: 'ВС'}.items():
        if num == week_day:
            return day
    else:
        log('Wrong day of week', 'warning')


def sec_to_time(seconds: int) -> str:
    minutes = int(seconds / 60)
    if minutes < 10:
        minutes = '0' + str(minutes)
    sec = int(seconds % 60)
    if sec == 0:
        sec = '00'
    elif sec < 10:
        sec = '0' + str(sec)
    return f"{minutes}:{sec}"


def tr_w(words) -> str:  # Define and translate
    leng_code = detect(words)
    if leng_code == 'mk':
        return 'Не удалось распознать язык⛔️'
    return Translator().translate(words, dest='en').text if leng_code == 'ru' \
        else Translator().translate(words, dest='ru').text


def clear_link(string: str) -> str:  # Clear string of links
    clear_string = re.sub(r'https?://.*[\r\n]*|[www.]?\w+\-?\w+\.\w.', '', string, flags=re.MULTILINE)
    clear_string = re.sub(r'\s+', ' ', clear_string, flags=re.MULTILINE)
    clear_string = re.sub(r'(\s-\s+m)?', '', clear_string, flags=re.MULTILINE)
    clear_string = re.sub(r'&\w+;', ' ', clear_string, flags=re.MULTILINE)
    return clear_string



def clear_date(string: str) -> str:
    date = re.sub('T', ' ', string)
    date = re.sub('Z', '', date)
    return date


def rend_d(percent: int) -> bool:  # Random True or False
    return True if randint(1, 100) <= percent else False


def hi_r(data: str) -> bool:  # Filter age rating
    return True if data == 'r' or 'pg-13' or 'pg' else False
