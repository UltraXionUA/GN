# -*- coding: utf-8 -*-
from googletrans import Translator
from random import randint
from langdetect import detect
from datetime import datetime


def log(message) -> None:  # Лог в консоль
    print("<!-------!>", datetime.now(), "<!-------!>\n",
          "Сообщение от {0} {1} (id = {2}) \n \'{3}\'".format(message.from_user.first_name,
                                                              message.from_user.last_name,
                                                              str(message.from_user.id), message.text))


def tr_w(words) -> str:  # Перевод
    leng_code = detect(words)
    if leng_code == 'mk':
        return 'Не удалось распознат язык'
    return Translator().translate(words, dest='en').text if leng_code == 'ru' \
        else Translator().translate(words, dest='ru').text


def rend_d() -> bool:  # Рандомный True False
    return True if randint(1, 100) < 20 else False


def hi_r(data: str) -> bool:  # Фильтруем рейтинг
    return True if data == 'r' or 'pg-13' or 'pg' else False
