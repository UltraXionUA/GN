# -*- coding: utf-8 -*-
"""Control DB file for GNBot"""
from funcs import log
import Config_GNBot.config
import pymysql


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


def get_stat(chat) -> list:  # -1001339129150
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


def get_all_jokes() -> list:  # All Joke
    connection = start_connection()
    with connection.cursor() as cursor:
        cursor.execute('SELECT `setup`, `panchline` FROM Joke')
        result = cursor.fetchall()
    connection.close()
    return result


def check_user(user_id: str) -> bool:
    connection = start_connection()
    with connection.cursor() as cursor:
        if cursor.execute(f'SELECT * FROM Users WHERE user_id LIKE \'{user_id}\''
                          f'AND is_gn LIKE \'True\';') == 0:
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


def random_gn_sticker() -> str:  # Random sticker from GN
    connection = start_connection()
    with connection.cursor() as cursor:
        cursor.execute('SELECT `item_id` FROM Stickers_gn ORDER BY RAND() LIMIT 1')
        result = cursor.fetchone()['item_id']
    connection.close()
    return result


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


def random_sticker() -> str:  # Random sticker
    connection = start_connection()
    with connection.cursor() as cursor:
        cursor.execute('SELECT `item_id` FROM Stickers ORDER BY RAND() LIMIT 1')
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


def get_all_answers() -> list:  # Get random answer
    connection = start_connection()
    with connection.cursor() as cursor:
        cursor.execute(
            f'SELECT answer FROM Answer;')
        result = cursor.fetchall()
    connection.close()
    return result


def get_answer(word) -> str:  # Get random answer with word
    connection = start_connection()
    with connection.cursor() as cursor:
        cursor.execute(
            f'SELECT answer FROM Word_Answer WHERE word LIKE \'{word}\' ORDER BY RAND() LIMIT 1')
        result = cursor.fetchone()['answer']
    connection.close()
    return result


def get_code(name: str) -> [dict, None]:  # Get all answers
    connection = start_connection()
    with connection.cursor() as cursor:
        cursor.execute(f'SELECT code FROM PasteBin WHERE name LIKE \'{name}\'')
        result = cursor.fetchone()
    connection.close()
    return result


def get_all_memes() -> list:  # Random meme
    connection = start_connection()
    with connection.cursor() as cursor:
        cursor.execute('SELECT `url` FROM Memes;')  # Выполнить команду запроса.
        result = cursor.fetchall()
    connection.close()
    return result


def add_memes(array: list) -> None:  # Add memes
    connection = start_connection()
    with connection.cursor() as cursor:
        for i in array:
            if cursor.execute(f'SELECT * FROM Memes WHERE url LIKE \'{i}\'') != 1:
                cursor.execute(f'INSERT INTO `Memes`(`url`) VALUES (\'{i}\');')
                connection.commit()
    connection.close()


def get_hentai(type_: str) -> dict:
    connection = start_connection()
    with connection.cursor() as cursor:
        cursor.execute(f'SELECT `url` FROM {type_} ORDER BY rand() LIMIT 1;')
        result = cursor.fetchone()
    return result


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
