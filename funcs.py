# -*- coding: utf-8 -*-
"""Function file for GNBot"""
from datetime import datetime as dt
from googletrans import Translator
from langdetect import detect
from random import randint
import logging
import re


logging.basicConfig(filename="logger.log", level=logging.INFO, filemode='w')  # Turn on logger


def log(message, type_l=None) -> None:
    """
    :param message
    :type message: telebot.types.Message
    :param type_l
    :type type_l: str
    :return: None
    .. seealso:: logging all actions
    """
    def get_info():
        return "<!-------!> " + str(dt.now().strftime("%Y-%m-%d-%H.%M.%S")) + " <!-------!>\n " \
                                                                              f"Сообщение от {message.from_user.first_name}" \
                                                                              f"{message.from_user.last_name} " \
                                                                              f"(id = {str(message.from_user.id)})\n" \
                                                                              f"\'{message.text}\'"
    if type(message) is not str:
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
        logging.info(f'{message}  {str(dt.now().strftime("%Y-%m-%d-%H.%M.%S"))}')


def get_weather_emoji(code: str) -> str:
    """
    :param code
    :type code: str
    :return: emoji
    :rtype: emoji: str
    .. seealso:: get emoji by weather code
    """
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
    """
    :param data
    :type data: str
    :return: day
    :rtype: day: str
    .. seealso:: get day by data timestamp
    """
    for num, day in {1: 'ПН', 2: 'ВТ', 3: 'СР', 4: 'ЧТ', 5: 'ПТ', 6: 'СБ', 7: 'ВС'}.items():
        if num == dt.strptime(data, '%Y-%m-%d').isoweekday():
            return day
    else:
        log('Wrong day of week', 'warning')


def sec_to_time(seconds: int) -> str:
    """
    :param seconds
    :type seconds: str
    :return: time
    :rtype: time: str
    .. seealso:: convert seconds to minutes
    """
    minutes = int(seconds / 60)
    if minutes < 10:
        minutes = '0' + str(minutes)
    sec = int(seconds % 60)
    if sec == 0:
        sec = '00'
    elif sec < 10:
        sec = '0' + str(sec)
    return f"{minutes}:{sec}"


def tr_w(sentence: str) -> str:
    """
   :param sentence
   :type sentence: str
   :return: tr_word
   :rtype: tr_word: str
   .. seealso:: detect lang of sentence and translate them
   """
    leng_code = detect(sentence)
    return Translator().translate(sentence, dest='en').text if leng_code == 'ru' else 'Не удалось распознать язык⛔️' \
        if leng_code == 'mk' else Translator().translate(sentence, dest='ru').text


def clear_link(sentence: str) -> str:
    """
    :param sentence
    :type sentence: str
    :return: clear_sentence
    :rtype: clear_sentence: str
    .. seealso:: clear some text from links and wrong symbols
    """
    clear_sentence = re.sub(r'https?://.*[\r\n]*|[www.]?\w+\-?\w+\.\w.', '', sentence, flags=re.MULTILINE)
    clear_sentence = re.sub(r'\s+', ' ', clear_sentence, flags=re.MULTILINE)
    clear_sentence = re.sub(r'(\s-\s+m)?', '', clear_sentence, flags=re.MULTILINE)
    return re.sub(r'&\w+;', ' ', clear_sentence, flags=re.MULTILINE)



def clear_date(date: str) -> str:
    """
    :param date
    :type date: str
    :return: clear_date
    :rtype: clear_date: str
    .. seealso:: clear some date from wrong symbols
    """
    clear_date = re.sub('T', ' ', date)
    return re.sub('Z', '', clear_date)


def rend_d(percent: int) -> bool:
    """
    :param percent
    :type percent: int
    :rtype: bool
    .. seealso:: get True or False by percent
    """
    return True if randint(1, 100) <= percent else False


def hi_r(rating: str) -> bool:
    """
    :param rating
    :type rating: str
    :rtype: bool
    .. seealso:: correctness rating check
    """
    return True if rating == 'r' or 'pg-13' or 'pg' else False
