# -*- coding: utf-8 -*-
"""Control DB file for GNBot"""
from funcs import log
from Config_GNBot import config
import pymysql
import redis


def start_connection():  # Connection to DB
    try:
        connection = pymysql.connect(**config.BD_CONNECT)
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
                groups = user_['supergroup'].split(',')
                for group in groups:
                    if group == str(chat.id):
                        users_groups.append(user_)
                        continue
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
        res = list(cursor.fetchall())
        true_res = []
        if res:
            for en, i in enumerate(res):
                groups = i['supergroup'].split(',')
                if str(chat.id) in groups:
                    true_res.append(i)
    return true_res


def add_user(user, chat=None, connection=None) -> None:
    if connection is None:
        connection = start_connection()
    with connection.cursor() as cursor:
        if cursor.execute(f'SELECT * FROM Users WHERE user_id LIKE \'{user.id}\'') == 0:
            if chat is not None:
                cursor.execute('INSERT INTO Users (`user_id`, `is_bote`, `first_name`, `last_name`, '
                               '`username`, `is_gn`, `supergroup`) VALUE '
                               f'(\'{int(user.id)}\', \'{str(user.is_bot)}\',\'{user.first_name}\','
                               f'\'{user.last_name}\',\'{user.username}\','
                               f' \'{str(True) if str(chat.id) == config.GN_ID else str(False)}\', '
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
                if str(chat.id) == config.GN_ID and cursor.execute(f'SELECT * FROM Users WHERE user_id LIKE {user.id} '
                                                                   f'AND is_gn = \'False\';') == 0:
                    cursor.execute(f'UPDATE Users SET is_gn = \'True\' WHERE user_id LIKE {user.id}')
                    connection.commit()


def check(user_id: str, check_t: str) -> bool:
    connection = start_connection()
    with connection.cursor() as cursor:
        if cursor.execute(f'SELECT * FROM Users WHERE user_id LIKE \'{user_id}\''
                          f'AND {check_t} LIKE \'True\';') == 0:
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


def add_sticker(item_id, emoji, name) -> None:  # Add sticker
    connection = start_connection()
    with connection.cursor() as cursor:
        if cursor.execute(f'SELECT * FROM Stickers WHERE emoji LIKE \'{emoji}\''
                          f'AND set_name LIKE \'{name}\';') == 0 and \
                cursor.execute(f'SELECT * FROM Stickers_gn WHERE emoji LIKE \'{emoji}\''
                               f'AND set_name LIKE \'{name}\';') == 0:
            cursor.execute(f'INSERT INTO `Stickers`(`item_id`, `emoji`, `set_name`) VALUES (\'{item_id}\','
                           f'\'{emoji}\',\'{name}\');')
            connection.commit()
    connection.close()


def random_sticker(gn=False) -> str:  # Random sticker
    connection = start_connection()
    with connection.cursor() as cursor:
        if gn is False:
            cursor.execute('SELECT `item_id` FROM Stickers ORDER BY RAND() LIMIT 1')
        else:
            cursor.execute('SELECT `item_id` FROM Stickers_gn ORDER BY RAND() LIMIT 1')
        result = cursor.fetchone()['item_id']
    connection.close()
    return result


def add_answer(answer: str) -> None:  # Add answer
    connection = start_connection()
    with connection.cursor() as cursor:
        cursor.execute(f'INSERT INTO `Answer`(`answer`) VALUES (\'{answer}\');')
        connection.commit()
    connection.close()


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


def get_answer(word) -> str:  # Get random answer with word
    connection = start_connection()
    with connection.cursor() as cursor:
        cursor.execute(
            f'SELECT answer FROM Word_Answer WHERE word LIKE \'{word}\' ORDER BY RAND() LIMIT 1')
        result = cursor.fetchone()
    connection.close()
    return result['answer']


def get_code(name: str) -> [dict, None]:  # Get all answers
    connection = start_connection()
    with connection.cursor() as cursor:
        cursor.execute(f'SELECT code FROM PasteBin WHERE name LIKE \'{name}\'')
        result = cursor.fetchone()
    connection.close()
    return result

def get_all(type_: str) -> list:
    connection = start_connection()
    with connection.cursor() as cursor:
        if type_ == 'Project_Euler':
            cursor.execute(f'SELECT * FROM {type_} WHERE image_url IS NOT NULL;')
        else:
            cursor.execute(f'SELECT * FROM {type_};')
        result = cursor.fetchall()
    return result

def add_memes(array: list) -> None:  # Add memes
    connection = start_connection()
    with connection.cursor() as cursor:
        for i in array:
            if cursor.execute(f'SELECT * FROM Memes WHERE url LIKE \'{i}\'') != 1:
                cursor.execute(f'INSERT INTO `Memes`(`url`) VALUES (\'{i}\');')
                connection.commit()
    connection.close()


def get_forbidden(type_: str) -> str:
    import random
    r = redis.Redis(host='localhost', port=6379, db=0)
    count_ = r.get(f'len_{type_}')
    return r.get(f'{type_}{random.randint(1, int(count_))}').decode('utf-8')

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

data = """[url=https://ibb.co/QvwWX1K][img]https://i.ibb.co/5hHQ2fR/51.png[/img][/url]
[url=https://ibb.co/NZsRBNZ][img]https://i.ibb.co/kQxZCDQ/52.png[/img][/url]
[url=https://ibb.co/BtTNVpS][img]https://i.ibb.co/G0CTv6b/53.png[/img][/url]
[url=https://ibb.co/hgR6sJw][img]https://i.ibb.co/nwsGrNt/54.png[/img][/url]
[url=https://ibb.co/YQ5gPHZ][img]https://i.ibb.co/zx3dQqJ/55.png[/img][/url]
[url=https://ibb.co/sy3MB26][img]https://i.ibb.co/WgKYT6P/56.png[/img][/url]
[url=https://ibb.co/ChRt41k][img]https://i.ibb.co/J5Dd8Bf/57.png[/img][/url]
[url=https://ibb.co/WtX4G2N][img]https://i.ibb.co/JQTwmsW/58.png[/img][/url]
[url=https://ibb.co/pzs0Sqq][img]https://i.ibb.co/wWb0ftt/59.png[/img][/url]
[url=https://ibb.co/QQSz5Gn][img]https://i.ibb.co/sRxkBrQ/60.png[/img][/url]
[url=https://ibb.co/bN5G5hS][img]https://i.ibb.co/kq2P2nR/61.png[/img][/url]
[url=https://ibb.co/WKGkK0D][img]https://i.ibb.co/x5X15Ym/62.png[/img][/url]
[url=https://ibb.co/j3qVpTw][img]https://i.ibb.co/WB7DT6z/63.png[/img][/url]
[url=https://ibb.co/Mh97ScV][img]https://i.ibb.co/xs36L1j/64.png[/img][/url]
[url=https://ibb.co/VqDLsv5][img]https://i.ibb.co/DRk1Z7T/65.png[/img][/url]
[url=https://ibb.co/pQHbvVp][img]https://i.ibb.co/PM2FZX8/66.png[/img][/url]
[url=https://ibb.co/WcKKQsK][img]https://i.ibb.co/p3XXgnX/67.png[/img][/url]
[url=https://ibb.co/94ryrd5][img]https://i.ibb.co/z24P4tv/68.png[/img][/url]
[url=https://ibb.co/ryQ8hjL][img]https://i.ibb.co/6sy9SMp/69.png[/img][/url]
[url=https://ibb.co/nLY7DK0][img]https://i.ibb.co/87frjQB/70.png[/img][/url]
[url=https://ibb.co/2K4SpNn][img]https://i.ibb.co/pXFQky0/71.png[/img][/url]
[url=https://ibb.co/YWfqGYp][img]https://i.ibb.co/26cfBmg/72.png[/img][/url]
[url=https://ibb.co/bBg7Nzx][img]https://i.ibb.co/85DXP6J/73.png[/img][/url]
[url=https://ibb.co/gSQY1bF][img]https://i.ibb.co/F5cpvkq/74.png[/img][/url]
[url=https://ibb.co/R6p7Lds][img]https://i.ibb.co/yknVL7Z/75.png[/img][/url]
[url=https://ibb.co/LSfjtrM][img]https://i.ibb.co/7vFMWQH/76.png[/img][/url]
[url=https://ibb.co/P17w0Bc][img]https://i.ibb.co/KVMFSC2/77.png[/img][/url]
[url=https://ibb.co/8bdGM83][img]https://i.ibb.co/DY8m4KX/78.png[/img][/url]
[url=https://ibb.co/V3tNBdr][img]https://i.ibb.co/7bXzyH8/79.png[/img][/url]
[url=https://ibb.co/G3DzHY9][img]https://i.ibb.co/prTYhVQ/80.png[/img][/url]
[url=https://ibb.co/MD01B6D][img]https://i.ibb.co/wNmQcsN/81.png[/img][/url]
[url=https://ibb.co/nk1Zd6Q][img]https://i.ibb.co/2KMmVWc/82.png[/img][/url]
[url=https://ibb.co/0FPwM62][img]https://i.ibb.co/SdqLnMy/83.png[/img][/url]
[url=https://ibb.co/ZShWXBY][img]https://i.ibb.co/bFrzms2/84.png[/img][/url]
[url=https://ibb.co/8shtxjN][img]https://i.ibb.co/yP37k8d/85.png[/img][/url]
[url=https://ibb.co/4NTPZbL][img]https://i.ibb.co/F7wgbQ1/86.png[/img][/url]
[url=https://ibb.co/LpByFmx][img]https://i.ibb.co/6sGSMzH/87.png[/img][/url]
[url=https://ibb.co/mS0tHBN][img]https://i.ibb.co/Tr1RHTW/88.png[/img][/url]
[url=https://ibb.co/JC2Hsnt][img]https://i.ibb.co/Yb8hL2Q/89.png[/img][/url]
[url=https://ibb.co/3yGh198][img]https://i.ibb.co/LzbpSXq/90.png[/img][/url]
[url=https://ibb.co/F83FT6H][img]https://i.ibb.co/DwWZ24r/91.png[/img][/url]
[url=https://ibb.co/pP9w1d8][img]https://i.ibb.co/hMt9gVj/92.png[/img][/url]
[url=https://ibb.co/2yR9kqj][img]https://i.ibb.co/vHfFj1J/93.png[/img][/url]
[url=https://ibb.co/KNV8RMr][img]https://i.ibb.co/jV3jBcr/94.png[/img][/url]
[url=https://ibb.co/8YDYBry][img]https://i.ibb.co/NT6T390/95.png[/img][/url]
[url=https://ibb.co/3mWFyxX][img]https://i.ibb.co/0yZ9j0N/96.png[/img][/url]
[url=https://ibb.co/qJ2zYtV][img]https://i.ibb.co/Hh90TW3/97.png[/img][/url]
[url=https://ibb.co/WGng31f][img]https://i.ibb.co/n6rz0Sj/98.png[/img][/url]
[url=https://ibb.co/2PrCg7d][img]https://i.ibb.co/S0gMRXB/99.png[/img][/url]
[url=https://ibb.co/xjL4rnw][img]https://i.ibb.co/C78rSj4/100.png[/img][/url]"""
def set_img():
    import re
    strings = data.split('\n')
    connection = start_connection()
    for en, i in enumerate(strings, 51):
        link = re.search(r'https?://i.ibb.co/.+/\d+.\w+', i).group(0)
        print(en, link)
        with connection.cursor() as cursor:
            cursor.execute(f'UPDATE Project_Euler SET image_url=\'{link}\' WHERE id={en};')
        connection.commit()
    connection.close()


set_img()

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
#         if cursor.execute(f'SELECT * FROM Stickers_gn WHERE set_name LIKE \'{name}\''
#                           f'AND emoji LIKE \'{emoji}\'') != 1:
#             cursor.execute(f'INSERT INTO `Stickers_gn`(`item_id`, `emoji`, `set_name`) VALUES (\'{item_id}\','
#                            f'\'{emoji}\',\'{name}\');')
#             connection.commit()
#     connection.close()
#     logging.info("Отключение от БД")
