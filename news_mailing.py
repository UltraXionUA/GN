#!/home/ultraxion/GNBot/GN/.venv/bin/activate
#!/usr/bin/ python3.8
# -*- coding: utf-8 -*-
"""Parser file for GNBot"""
from telebot.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from funcs import log, clear_link, clear_date
from Config_GNBot.config import API, bot
from collections import defaultdict
from urllib import request, error
import requests
import db
import re

# <<< News_mailing >>
daily_news_data = defaultdict(list)
daily_news_msg = defaultdict(Message)


def send_daily_news() -> None:
    global daily_news_data, daily_news_msg
    for group in db.get_id_from_where('Setting', 'news_mailing', 'On'):
        setting = db.get_from(group['id'], 'Setting')
        try:
            daily_news_data[group['id']] = requests.get('https://' + f'newsapi.org/v2/top-headlines?country='
                                             f'{"us" if setting["news"] == "Us" else "ua" if setting["news"] == "Ua" else "ru"}'
                                             f'&pageSize=10&apiKey={API["News"]["Api_Key"]}').json()['articles']
            daily_news_msg[group['id']] = bot.send_photo(group['id'], API['News']['image'])
        except Exception:
            log('Error in daily news', 'error')
        else:
            send_news(0, group['id'])


def send_news(index: int, chat_id: str) -> None:
    global daily_news_msg, daily_news_data
    keyboard = InlineKeyboardMarkup()
    keyboard.add(
        InlineKeyboardButton(text="⬅️️", callback_data=f"daily_news_move_to {index - 1 if index > 0 else 'pass'}"),
        InlineKeyboardButton(text="➡️", callback_data=f"daily_news_move_to "
                                                      f"{index + 1 if index < len(daily_news_data[chat_id]) - 1 else 'pass'}"))
    if daily_news_data[chat_id][index]['urlToImage'] is None or daily_news_data[chat_id][index]['urlToImage'] == '' \
            or daily_news_data[chat_id][index]['description'] is None:
        daily_news_data[chat_id].pop(index)
        send_news(index, chat_id)
        return
    else:
        try:
            if requests.get(daily_news_data[chat_id][index]["url"]).ok:
                keyboard.add(InlineKeyboardButton('Читать', url=daily_news_data[chat_id][index]["url"]))
        except (requests.exceptions.ConnectionError, requests.exceptions.MissingSchema):
            pass
        try:
            if requests.get(daily_news_data[chat_id][index]['urlToImage']).ok:
                req = request.Request(daily_news_data[chat_id][index]['urlToImage'], method='HEAD')
                f = request.urlopen(req)
                if f.headers['Content-Length'] is not None:
                    if int(f.headers['Content-Length']) > 5242880:
                        daily_news_data[chat_id].pop(index)
                        send_news(index, chat_id)
                        return
                else:
                    daily_news_data[chat_id].pop(index)
                    send_news(index, chat_id)
                    return
            else:
                daily_news_data[chat_id].pop(index)
                send_news(index, chat_id)
                return
        except (requests.exceptions.ConnectionError, requests.exceptions.MissingSchema, error.URLError,
                UnicodeEncodeError):
            daily_news_data[chat_id].pop(index)
            send_news(index, chat_id)
            return
        except IndexError:
            log('Index Error in daily news', 'warning')
        bot.edit_message_media(chat_id=chat_id, message_id=daily_news_msg[chat_id].message_id,
                               media=InputMediaPhoto(daily_news_data[chat_id][index]['urlToImage'],
                                                     caption=f"<b>{clear_link(daily_news_data[chat_id][index]['title'])}</b>"
                                                             f"\n\n{clear_link(daily_news_data[chat_id][index]['description'])}"
                                                             f"\n\n<i>{clear_date(daily_news_data[chat_id][index]['publishedAt'])}</i>",
                                                     parse_mode='HTML'), reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: re.fullmatch(r'^daily_news_move_to\s\d+$', call.data))
def next_news_query(call):
    index = int(call.data.split()[1])
    if 0 <= index < len(daily_news_data[str(call.message.chat.id)]) - 1:
        bot.answer_callback_query(call.id, f'Вы выбрали стр.{index + 1}')
        send_news(index, str(call.message.chat.id))
    else:
        bot.answer_callback_query(call.id, '⛔️')


@bot.callback_query_handler(func=lambda call: re.match(r'daily_news_move_to\spass', call.data))
def pass_query(call):
    bot.answer_callback_query(call.id, '⛔️')
# <<< End news_mailing >>