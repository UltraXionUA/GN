# -*- coding: utf-8 -*-
"""Control DB file for GNBot"""
from Config_GNBot.config import GN_ID, GN_Stickers, BD_CONNECT
from funcs import log
import pymysql
import redis
import random


def start_connection():
    """
    .. notes:: Funk to connect to MySQL DB
    :return: connection
    :rtype: connection: pymysql.connect
    """
    try:
        connection = pymysql.connect(**BD_CONNECT)
        return connection
    except pymysql.err.OperationalError:
        log('Ошибка подключения к БД!', 'error')


def get_user(user, chat) -> [dict, int or bool, bool]:
    """
    :param user
    :param chat
    :return: user, en
    :rtype: user: dict, en: int
    :return: False, False
    :rtype: False: bool, False: bool
    .. notes:: Get some user
    """
    connection = start_connection()
    with connection.cursor() as cursor:
        cursor.execute(f'SELECT * FROM Users ORDER BY karma DESC;')
        all_users = cursor.fetchall()
        users_groups = []
        for en, user_ in enumerate(all_users):
            if user_['supergroup'] is None:
                all_users.pop(en)
            else:
                for group in user_['supergroup'].split(','):
                    if group == str(chat.id):
                        users_groups.append(user_)
        if users_groups:
            for en, user_ in enumerate(users_groups, 1):
                if user_['user_id'] == user.id:
                    return user_, en
        else:
            return False, False
    connection.close()


def get_stat(chat) -> list:
    """
    :param chat
    :return: user_list
    :rtype: user_list: list
    .. notes:: get stats users in some group
    """
    connection = start_connection()
    with connection.cursor() as cursor:
        cursor.execute(f'SELECT * FROM Users WHERE is_bote = \'False\' AND supergroup IS NOT NULL ORDER BY karma DESC')
        return [i for i in cursor.fetchall() if str(chat.id) in i['supergroup'].split(',')]


def add_user(user, chat=None, connection=None) -> None:
    """
    :param user
    :param chat
    :param connection
    :return: None
    .. notes:: add or update user to DB
    """
    if connection is None:
        connection = start_connection()
    with connection.cursor() as cursor:
        if chat is not None:
            if cursor.execute(f'SELECT * FROM Setting WHERE id=\'{chat.id}\';') == 0:
                cursor.execute(f'INSERT INTO `Setting`(`id`) VALUES (\'{chat.id}\');')
                connection.commit()
        else:
            if cursor.execute(f'SELECT * FROM Setting WHERE id=\'{user.id}\';') == 0:
                cursor.execute(f'INSERT INTO `Setting`(`id`) VALUES (\'{user.id}\');')
                connection.commit()
        if cursor.execute(f'SELECT * FROM Users WHERE user_id LIKE \'{user.id}\'') == 0:
            if chat is not None:
                cursor.execute('INSERT INTO Users (`user_id`, `is_bote`, `first_name`, `last_name`, '
                               '`username`, `is_gn`, `supergroup`) VALUE '
                               f'(\'{int(user.id)}\', \'{str(user.is_bot)}\',\'{user.first_name}\','
                               f'\'{user.last_name}\',\'{user.username}\','
                               f' \'{str(True) if str(chat.id) == GN_ID else str(False)}\', '
                               f'\'{str(chat.id)},\');')
            else:
                cursor.execute('INSERT INTO Users (`user_id`, `is_bote`, `first_name`, `last_name`, '
                               '`username`) VALUE '
                               f'(\'{int(user.id)}\', \'{str(user.is_bot)}\',\'{user.first_name}\','
                               f'\'{user.last_name}\',\'{user.username}\');')
            connection.commit()
        else:
            cursor.execute(f'SELECT * FROM Users WHERE user_id LIKE {user.id}')
            user_db = cursor.fetchone()
            if user_db['first_name'] != user.first_name:
                cursor.execute(f'UPDATE Users SET first_name=\'{user.first_name}\' WHERE user_id LIKE {user.id};')
                connection.commit()
            if user_db['last_name'] != user.last_name:
                cursor.execute(f'UPDATE Users SET last_name=\'{user.last_name}\' WHERE user_id LIKE {user.id};')
                connection.commit()
            if user_db['username'] != user.username:
                cursor.execute(f'UPDATE Users SET username=\'{user.username}\' WHERE user_id LIKE {user.id};')
                connection.commit()
            if chat is not None:
                if cursor.execute(f'SELECT * FROM Users WHERE user_id LIKE {user.id} AND supergroup IS NULL;') != 0:
                    cursor.execute(f'UPDATE Users SET supergroup = \'{chat.id},\' WHERE user_id LIKE {user.id};')
                    connection.commit()
                elif cursor.execute(f'SELECT * FROM Users WHERE user_id LIKE \'{user.id}\' AND supergroup IS NOT NULL;') != 0:
                    cursor.execute(f'SELECT * FROM Users WHERE user_id LIKE \'{user.id}\';')
                    res = cursor.fetchone()
                    if str(chat.id) not in res['supergroup'].split(','):
                        cursor.execute(f'UPDATE Users SET supergroup = \'{res["supergroup"] + str(chat.id)},\''
                                       f' WHERE user_id LIKE {user.id};')
                        connection.commit()
                if str(chat.id) == GN_ID and cursor.execute(f'SELECT * FROM Users WHERE user_id LIKE {user.id} '
                                                                   f'AND is_gn = \'False\';') == 0:
                    cursor.execute(f'UPDATE Users SET is_gn = \'True\' WHERE user_id LIKE {user.id}')
                    connection.commit()


def reset_users(chat_id=None) -> None:
    """
    :param chat_id
    :type chat_id: str
    :return: None
    .. notes:: reset users daily karma
    """
    connection = start_connection()
    with connection.cursor() as cursor:
        cursor.execute(f'SELECT * FROM Users WHERE supergroup IS NOT NULL;')
        if chat_id is None:
            for user in cursor.fetchall():
                cursor.execute(f'UPDATE Users SET daily={user["karma"]} WHERE id={user["id"]};')
                connection.commit()
        else:
            for user in cursor.fetchall():
                 for group in user['supergroup'].split(','):
                     if group == chat_id:
                         cursor.execute(f'UPDATE Users SET daily={user["karma"]} WHERE id={user["id"]};')
                         connection.commit()
    connection.close()


def get_bad_guy() -> dict:
    """
    :return: dict_bag_guys
    :rtype: dict_bag_guys: dict
    .. notes:: get bad guys for all super groups
    """
    connection = start_connection()
    groups, users, bag_guys = set(), [], {}
    with connection.cursor() as cursor:
        cursor.execute(f'SELECT * FROM Users WHERE supergroup IS NOT NULL AND is_bote=\'False\';')
        res = cursor.fetchall()
    for user in res:
        for group in user['supergroup'].split(','):
            if group != '':
                groups.add(group)
    for user in res:
        for group_u in user['supergroup'].split(','):
            for group in groups:
                if group == group_u:
                    users.append(
                        {'id': user['id'], 'group': group_u, 'karma': user['karma'], 'daily': user['daily'],
                         'first_name': user['first_name'], 'last_name': user['last_name']})
    for group in groups:
        for user in users:
            if user['group'] == group:
                if  user['group'] not in bag_guys:
                    bag_guys[group] = [user]
                elif bag_guys[group][0]['karma'] - bag_guys[group][0]['daily'] > user['karma'] - user['daily']:
                    bag_guys[group].clear()
                    bag_guys[group].append(user)
                elif bag_guys[group][0]['karma'] - bag_guys[group][0]['daily'] == user['karma'] - user['daily']:
                    bag_guys[group].append(user)
    return bag_guys


def save_pin_bag_guys(chat_id: str, message_id: str) -> None:
    """
    :param chat_id
    :type chat_id: str
    :param message_id
    :type message_id: str
    :return: None
    .. notes:: save pins id's
    """
    r = redis.Redis(host='localhost', port=6379, db=2)
    r.set(chat_id, message_id)

def get_pin_bag_guys() -> list:
    """
    :return: list_pins
    :rtype: list_pins: list
    .. notes:: get pin's messages
    """
    r = redis.Redis(host='localhost', port=6379, db=2)
    return [{'chat_id': id_.decode('utf-8'), 'message_id': r.get(id_.decode('utf-8'))} for id_ in r.keys()]


def get_setting(chat_id: str) -> dict:
    """
    :param: chat_id
    :type: chat_id: str
    :return: list_pins
    :rtype: list_pins: list
    .. notes:: get setting from group
    """
    connection = start_connection()
    with connection.cursor() as cursor:
        cursor.execute(f'SELECT * FROM Setting WHERE id=\'{chat_id}\';')
        return cursor.fetchone()


def change_setting(chat_id: str, method: str, status: str) -> None:
    """
    :param: chat_id
    :type: chat_id: str
    :param: method
    :type: method: str
    :param: status
    :type: status: str
    :return: None
    .. notes:: change some setting in group
    """
    connection = start_connection()
    with connection.cursor() as cursor:
        if method == 'bad_guy' and status == 'on':
            reset_users(chat_id)
        cursor.execute(f'UPDATE Setting SET `{method}`=\'{status.title()}\' WHERE id LIKE \'{chat_id}\'')
        connection.commit()
    connection.close()


def check(user_id: str, check_t: str) -> bool:
    """
    :param: user_id
    :type: user_id: str
    :param: check_t
    :type: check_t: str
    :rtype: bool
    .. notes:: check user in DB
    """
    connection = start_connection()
    with connection.cursor() as cursor:
        return False if cursor.execute(f'SELECT * FROM Users WHERE user_id LIKE \'{user_id}\' AND {check_t} LIKE \'True\';') == 0 else True


def change_karma(user, chat, action: list, exp: int) -> dict:
    """
    :param: user
    :param: action
    :type: action: list
    :param: exp
    :type: exp: int
    :type: check_t: str
    :return karma
    :rtype: karma: dict
    .. notes:: change and get back karma of some users
    """
    connection = start_connection()
    with connection.cursor() as cursor:
        cursor.execute(f'SELECT `karma` FROM `Users` WHERE `user_id` = {user.id};')
        karma = cursor.fetchone()['karma'] + len(action) * exp if action[0] == '+' else - len(action) * exp
        cursor.execute(f'UPDATE `Users` SET `karma` = \'{karma}\' WHERE `username` = \'{user.username}\';')
        connection.commit()
    return karma


def add_sticker(id_, emoji, name) -> None:
    """
    :param: id_
    :param: emoji
    :param: name
    :return None
    .. notes:: add new sticker to DB
    """
    connection = start_connection()
    with connection.cursor() as cursor:
        if cursor.execute(f'SELECT * FROM Stickers WHERE `set_name`=\'{name}\' AND emoji=\'{emoji}\';') == 0:
            cursor.execute(f'INSERT INTO `Stickers`(`item_id`, `emoji`, `set_name`) VALUES (\'{id_}\','
                               f'\'{emoji}\',\'{name}\');')
            connection.commit()
    connection.close()

def random_sticker(gn=False) -> str:
    """
    :param: gn
    :type: gn: bool
    :return sticker_id
    :rtype: sticker_id: str
    .. notes:: get random sticker from DB
    """
    connection = start_connection()
    with connection.cursor() as cursor:
        if gn is False:
            cursor.execute(f'SELECT * FROM Stickers WHERE `set_name`!=\'{GN_Stickers[0]}\' AND'
                           f'`set_name`!=\'{GN_Stickers[1]}\' AND `set_name`!=\'{GN_Stickers[2]}\' AND'
                           f'`set_name`!=\'{GN_Stickers[3]}\' ORDER BY RAND() LIMIT 1')
        else:
            cursor.execute(f"SELECT `item_id` FROM Stickers WHERE `set_name`"
                           f"=\'{random.choice(GN_Stickers)}\'"
                           f" ORDER BY RAND() LIMIT 1")
        return cursor.fetchone()['item_id']



def ban_user(user: str) -> None:
    """
    :param: user
    :type: user: str
    :return None
    .. notes:: ban some user in group
    """
    connection = start_connection()
    with connection.cursor() as cursor:
        cursor.execute(f'INSERT INTO `BlackList` (`user_id`) VALUES (\'{user}\');')
        connection.commit()
    connection.close()


def check_ban_user(user: str) -> bool:
    """
    :param: user
    :type: user: str
    :return sticker_id
    :rtype: bool
    .. notes:: Check baned user or not
    """
    connection = start_connection()
    with connection.cursor() as cursor:
        return True if cursor.execute(f'SELECT * FROM `BlackList` WHERE user_id LIKE \'{user}\';') == 0 else False


def get_code(name: str) -> [dict, None]:
    """
    :param: name
    :type: name: str
    :return code
    :rtype: code: dict or None
    .. notes:: Get code of programming lang
    """
    connection = start_connection()
    with connection.cursor() as cursor:
        cursor.execute(f'SELECT code FROM PasteBin WHERE name LIKE \'{name}\'')
        return cursor.fetchone()


def del_meme(meme_id: str) -> None:
    """
    :param: meme_id
    :type: meme_id: str
    :return None
    .. notes:: Delete meme from DB (for admins)
    """
    connection = start_connection()
    with connection.cursor() as cursor:
        cursor.execute(f'DELETE FROM Memes WHERE id={meme_id}')
        connection.commit()
    connection.close()

def get_all(type_: str) -> list:
    """
    :param: type_
    :type: type_: str
    :rtype list
    .. notes:: get all {some thing} from DB
    """
    connection = start_connection()
    with connection.cursor() as cursor:
        cursor.execute(f'SELECT * FROM {type_};')
        return cursor.fetchall()


def add_memes(data_memes: list) -> None:
    """
    :param: data_memes
    :type: data_memes: list
    :rtype None
    .. notes:: Add new memes from daily parser
    """
    connection = start_connection()
    with connection.cursor() as cursor:
        for en, meme in enumerate([meme for meme in data_memes if cursor.execute(f'SELECT * FROM Memes WHERE url LIKE \'{meme}\'') == 0], 1):
            cursor.execute(f'INSERT INTO `Memes`(`url`) VALUES (\'{meme}\');')
            connection.commit()
        else:
            log(f'Мемов добавлено: {en}', 'info')
    connection.close()


def get_forbidden(type_: str) -> str:
    """
    :param: type_
    :type: type_: str
    :return forbidden
    :rtype forbidden: str
    .. notes:: get random forbidden
    """
    r = redis.Redis(host='localhost', port=6379, db=0)
    return r.get(f'{type_}{random.randint(1, int(r.get(f"len_{type_}")))}').decode('utf-8')

def get_doc(id_: str) -> str:
    """
    :param: id_
    :type: id_: str
    :return doc
    :rtype doc: str
    .. notes:: get document from some task of Project Euler
    """
    connection = start_connection()
    with connection.cursor() as cursor:
        cursor.execute(f'SELECT other FROM Project_Euler WHERE id={id_};')
        return cursor.fetchone()['other']


def get_task_answer(id_: str) -> str:
    """
   :param: id_
   :type: id_: str
   :return task_answer
   :rtype task_answer: str
   .. notes:: get answer from Logic Task
   """
    connection = start_connection()
    with connection.cursor() as cursor:
        cursor.execute(f'SELECT answer FROM Logic_Tasks WHERE id={id_};')
        return cursor.fetchone()['answer']


def get_answer() -> str:
    """
    :return bot_answer
    :rtype bot_answer: str
    .. notes:: get random bot answer from DB
    """
    r = redis.Redis(host='localhost', port=6379, db=1)
    return r.get(f'answer{random.randint(1, int(r.get("len_answer")))}').decode('utf-8')


# def add_answers():
#     import re
#     data = []
#     with open('answer_databse.txt', 'r') as f:
#         for en, i in enumerate(f.readlines(), 1):
#             try:
#                 answer = i.split("\\")[1].replace('\n', '')
#                 if re.match(r'^=+', answer) or re.match(r'^⚡+', answer) or len(answer) > 499:
#                     continue
#                 else:
#                     if answer[0] == '.':
#                         answer = answer[1:]
#                     answer = re.sub(r'=+', '', answer)
#                     answer = re.sub(r'⚡+', '', answer)
#                     data.append(answer)
#             except IndexError:
#                 continue
#     connection = start_connection()
#     with connection.cursor() as cursor:
#         for en, i in enumerate(set(data), 1):
#             if en % 1000 == 0:
#                 print(en)
#             word = i.replace('\'', '\\\'')
#             cursor.execute(f"INSERT INTO `Answer`(`answer`) VALUES (\'{word}\');")
#             connection.commit()
#     connection.close()
#     print('finish')
#
# def add_to_redis():
#     connection = start_connection()
#     with connection.cursor() as cursor:
#         cursor.execute(f'SELECT answer FROM Answer;')
#         res = cursor.fetchall()
#     r = redis.Redis(host='localhost', port=6379, db=1)
#     r.set(f'len_answer', len(res))
#     print(len(res))
#     for en, i in enumerate(res, 1):
#         if en % 1000 == 0:
#             print(en)
#         r.set('answer' + str(en), i['answer'])
#     print('finish')
#
# add_answers()
# add_to_redis()

# def set_img():
#     import re
#     strings = data.split('\n')
#     connection = start_connection()
#     for en, i in enumerate(strings, 51):
#         link = re.search(r'https?://i.ibb.co/.+/\d+.\w+', i).group(0)
#         print(en, link)
#         with connection.cursor() as cursor:
#             cursor.execute(f'UPDATE Project_Euler SET image_url=\'{link}\' WHERE id={en};')
#         connection.commit()
#     connection.close()
#
#
# set_img()

# def set_eluler(data: list) -> None:
#     connection = start_connection()
#     with connection.cursor() as cursor:
#         if data:
#             for i in data:
#                 cursor.execute(f'INSERT INTO `Project_Euler`(`name`, `url`) VALUES (\'{str(i["name"])}\', \'{str(i["url"])}\');')
#                 connection.commit()
#             connection.close()

# def add_to_redis(data: list, type_: str):
#     r = redis.Redis(host='localhost', port=6379, db=0)
#     r.set(f'len_{type_}', len(data))
#     print(len(data))
#     for en, i in enumerate(data, 1):
#         r.set(type_ + str(en), i['url'])
#     print('finish')

# def get_all():
#     connection = start_connection()
#     with connection.cursor() as cursor:
#         cursor.execute(f'SELECT * FROM Lolis;')
#         result = cursor.fetchall()
#         add_to_redis(result, 'loli')
#         cursor.execute(f'SELECT * FROM Hentai;')
#         result = cursor.fetchall()
#         add_to_redis(result, 'hentai')
#         cursor.execute(f'SELECT * FROM Girls;')
#         result = cursor.fetchall()
#         add_to_redis(result, 'girls')
#
# get_all()


# def add_logic_tasks(tasks: dict) -> None:
#     connection = start_connection()
#     with connection.cursor() as cursor:
#         for i, q in tasks.items():
#             print(i, '\n', q, '\n\n')
#             cursor.execute(f'INSERT INTO `Logic_Tasks`(`question`, `answer`) VALUES (\'{i}\', \'{q}\');')
#             connection.commit()
#         connection.close()


# def add_girls(girls: list) -> None:
#     connection = start_connection()
#     with connection.cursor() as cursor:
#         if girls:
#             for i in girls:
#                 cursor.execute(f'INSERT INTO `Girls`(`url`) VALUES (\'{i}\');')
#                 connection.commit()
#             connection.close()

# def add_lolis(lolis: list) -> None:
#     connection = start_connection()
#     with connection.cursor() as cursor:
#         if lolis:
#             for i in lolis:
#                 cursor.execute(f'INSERT INTO `Lolis`(`url`) VALUES (\'{i}\');')
#                 connection.commit()
#             connection.close()


# def add_gn_sticker(item_id, emoji, name):  # Add stickers from GN
#     connection = start_connection()
#     with connection.cursor() as cursor:
#             cursor.execute(f'INSERT INTO `Stickers_gn`(`item_id`, `emoji`, `set_name`) VALUES (\'{item_id}\','
#                            f'\'{emoji}\',\'{name}\');')
#             connection.commit()
#     connection.close()
