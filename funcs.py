# -*- coding: utf-8 -*-
"""Function file for GNBot"""
from googletrans import Translator
from random import randint
from langdetect import detect
from datetime import datetime
import logging
import requests
import re


logging.basicConfig(filename="logger.log", level=logging.INFO)  # Turn on logger


def log(message, type_l='None') -> None:  # Message processing
    if type(message) is not str:
        def get_info():
            return "<!-------!> " + str(datetime.now().strftime("%Y-%m-%d-%H.%M.%S")) + " <!-------!>\n " \
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
        print("<!-------!>", datetime.now().strftime("%Y-%m-%d-%H.%M.%S"), "<!-------!>\n", message)
        logging.info(message + ' ' + str(datetime.now().strftime("%Y-%m-%d-%H.%M.%S")))


def download_song(url_mp3: str):
    req = requests.get(url_mp3, stream=True)
    file_name = 'Buffer_for_song'
    with open('Buffer_for_song' + '.mp3', 'wb') as f:
        f.write(req.content)
    file = open(file_name + '.mp3', 'rb')
    return file


def tr_w(words) -> str:  # Define and translate
    leng_code = detect(words)
    if leng_code == 'mk':
        return 'Не удалось распознат язык⛔️'
    return Translator().translate(words, dest='en').text if leng_code == 'ru' \
        else Translator().translate(words, dest='ru').text


def clear_link(string: str) -> str:  # Clear string of links
    clear_string = re.sub(r'^https?:\/\/.*[\r\n]*|[www\.]?\w+\-?\w+\.\w.', '', string, flags=re.MULTILINE)
    clear_string = re.sub(r'\s+', ' ', clear_string, flags=re.MULTILINE)
    clear_string = re.sub(r'(\s-\s+m)?', '', clear_string, flags=re.MULTILINE)
    return clear_string


def rend_d() -> bool:  # Random True or False
    return True if randint(1, 100) < 20 else False


def hi_r(data: str) -> bool:  # Filter age rating
    return True if data == 'r' or 'pg-13' or 'pg' else False

