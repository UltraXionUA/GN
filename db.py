# -*- coding: utf-8 -*-
"""Control DB file for GNBot"""
from Config_GNBot.config import GN_ID, GN_Stickers, BD_CONNECT
from funcs import log
import pymysql
import redis
import random


def start_connection():  # Connection to DB
    try:
        connection = pymysql.connect(**BD_CONNECT)
        return connection
    except pymysql.err.OperationalError:
        log('Ошибка подключения к БД!', 'error')


def get_user(user, chat) -> dict:
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
    connection = start_connection()
    with connection.cursor() as cursor:
        cursor.execute(f'SELECT * FROM Users WHERE is_bote = \'False\' AND supergroup IS NOT NULL ORDER BY karma DESC')
        res = cursor.fetchall()
        true_res = []
        if res:
            for en, i in enumerate(res):
                if str(chat.id) in i['supergroup'].split(','):
                    true_res.append(i)
    return true_res


def add_user(user, chat=None, connection=None) -> None:
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
                if cursor.execute(f'SELECT * FROM Users WHERE user_id LIKE {user.id} '
                                                                   f'AND supergroup IS NULL;') != 0:
                    cursor.execute(f'UPDATE Users SET supergroup = \'{chat.id},\' WHERE user_id LIKE {user.id};')
                    connection.commit()
                elif cursor.execute(f'SELECT * FROM Users WHERE user_id LIKE \'{user.id}\' '
                                                                       f'AND supergroup IS NOT NULL;') != 0:
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
    connection = start_connection()
    with connection.cursor() as cursor:
        cursor.execute(f'SELECT * FROM Users WHERE supergroup IS NOT NULL;')
        res = cursor.fetchall()
        if chat_id is None:
            for user in res:
                cursor.execute(f'UPDATE Users SET daily={user["karma"]} WHERE id={user["id"]};')
                connection.commit()
        else:
            for user in res:
                 for group in user['supergroup'].split(','):
                     if group == chat_id:
                         cursor.execute(f'UPDATE Users SET daily={user["karma"]} WHERE id={user["id"]};')
                         connection.commit()
    connection.close()


def get_bad_guy():
    connection = start_connection()
    with connection.cursor() as cursor:
        cursor.execute(f'SELECT * FROM Users WHERE supergroup IS NOT NULL AND is_bote=\'False\';')
        res = cursor.fetchall()
    connection.close()
    groups = set()
    for user in res:
        for group in user['supergroup'].split(','):
            if group != '':
                groups.add(group)
    users = []
    for user in res:
        for group_u in user['supergroup'].split(','):
            for group in groups:
                if group == group_u:
                    users.append({'id': user['id'], 'group': group_u, 'karma': user['karma'], 'daily': user['daily'],
                                 'first_name': user['first_name'], 'last_name': user['last_name']})
    bag_guys = {}
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
    r = redis.Redis(host='localhost', port=6379, db=2)
    r.set(chat_id, message_id)

def get_pin_bag_guys() -> list:
    r = redis.Redis(host='localhost', port=6379, db=2)
    return [{'chat_id': id_.decode('utf-8'), 'message_id': r.get(id_.decode('utf-8'))} for id_ in r.keys()]


def get_setting(chat_id: str) -> dict:
    connection = start_connection()
    with connection.cursor() as cursor:
        cursor.execute(f'SELECT * FROM Setting WHERE id=\'{chat_id}\';')
        res = cursor.fetchone()
    connection.close()
    return res

def change_setting(chat_id: str, method: str, status: str) -> None:
    connection = start_connection()
    with connection.cursor() as cursor:
        if method == 'bad_guy' and status == 'on':
            reset_users(chat_id)
        cursor.execute(f'UPDATE Setting SET `{method}`=\'{status.title()}\' WHERE id LIKE \'{chat_id}\'')
        connection.commit()
    connection.close()


def check(user_id: str, check_t: str) -> bool:
    connection = start_connection()
    with connection.cursor() as cursor:
        if cursor.execute(f'SELECT * FROM Users WHERE user_id LIKE \'{user_id}\' AND {check_t} LIKE \'True\';') == 0:
            return False
        else:
            return True


def change_karma(user, chat, action: list, exp: int) -> dict:  # Change Karma
    connection = start_connection()
    with connection.cursor() as cursor:
        add_user(user, chat, connection)
        cursor.execute(f'SELECT `karma` FROM `Users` WHERE `user_id` = {user.id};')
        karma = cursor.fetchone()['karma']
        if action[0] == '+':
            karma += len(action) * exp
        else:
            karma -= len(action) * exp
        cursor.execute(f'UPDATE `Users` SET `karma` = \'{karma}\' WHERE `username` = \'{user.username}\';')
        connection.commit()
    connection.close()
    return karma


def add_sticker(id_, emoji, name) -> None:  # Add sticker
    connection = start_connection()
    with connection.cursor() as cursor:
        if cursor.execute(f'SELECT * FROM Stickers WHERE `set_name`=\'{name}\' AND emoji=\'{emoji}\';') == 0:
            cursor.execute(f'INSERT INTO `Stickers`(`item_id`, `emoji`, `set_name`) VALUES (\'{id_}\','
                               f'\'{emoji}\',\'{name}\');')
            connection.commit()
    connection.close()

def random_sticker(gn=False) -> str:  # Random sticker
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
    result = cursor.fetchone()
    connection.close()
    return result['item_id']


def ban_user(user: str) -> None:  # Ban user
    connection = start_connection()
    with connection.cursor() as cursor:
        cursor.execute(f'INSERT INTO `BlackList` (`user_id`) VALUES (\'{user}\');')
        connection.commit()
    connection.close()


def check_ban_user(user: str) -> None:  # Ban user
    connection = start_connection()
    with connection.cursor() as cursor:
        if cursor.execute(f'SELECT * FROM `BlackList` WHERE user_id LIKE \'{user}\';') == 0:
            return True
        else:
            return False


def get_code(name: str) -> [dict, None]:
    connection = start_connection()
    with connection.cursor() as cursor:
        cursor.execute(f'SELECT code FROM PasteBin WHERE name LIKE \'{name}\'')
        result = cursor.fetchone()
    connection.close()
    return result

def get_all(type_: str) -> list:
    connection = start_connection()
    with connection.cursor() as cursor:
        cursor.execute(f'SELECT * FROM {type_};')
        result = cursor.fetchall()
    return result

def add_memes(array: list) -> None:  # Add memes
    connection = start_connection()
    count = 0
    with connection.cursor() as cursor:
        for i in array:
            if cursor.execute(f'SELECT * FROM Memes WHERE url LIKE \'{i}\'') != 1:
                count += 1
                cursor.execute(f'INSERT INTO `Memes`(`url`) VALUES (\'{i}\');')
                connection.commit()
    log(f'Мемов добавлено: {count}', 'info')
    connection.close()


def get_forbidden(type_: str) -> str:
    r = redis.Redis(host='localhost', port=6379, db=0)
    return r.get(f'{type_}{random.randint(1, int(r.get(f"len_{type_}")))}').decode('utf-8')

def get_doc(id_: str) -> str:
    connection = start_connection()
    with connection.cursor() as cursor:
        cursor.execute(f'SELECT other FROM Project_Euler WHERE id={id_};')
        result = cursor.fetchone()
    return result['other']


def get_task_answer(id_: str) -> str:
    connection = start_connection()
    with connection.cursor() as cursor:
        cursor.execute(f'SELECT answer FROM Logic_Tasks WHERE id={id_};')
        result = cursor.fetchone()
    return result['answer']

def get_answer() -> str:
    r = redis.Redis(host='localhost', port=6379, db=1)
    answer = r.get(f'answer{random.randint(1, int(r.get("len_answer")))}').decode('utf-8')
    return answer[1:] if answer[0] == '.' else answer

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
