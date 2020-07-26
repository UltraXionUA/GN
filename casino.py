#!/home/ultraxion/GNBot/GN/.venv/bin/activate
#!/usr/bin/ python3.8
# -*- coding: utf-8 -*-
"""Casino file for GNBot"""
from telebot.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from funcs import log, get_bid_size, get_color
from datetime import datetime as dt, timedelta
from collections import defaultdict
from threading import Thread
from threading import Timer
from Config_GNBot.config import bot
import random
import time
import re
import db


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
        for num in nums[start: -1 if start > 22 else start + 10]:
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