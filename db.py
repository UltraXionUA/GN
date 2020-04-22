# -*- coding: utf-8 -*-
"""Control DB file for GNBot"""
from funcs import log
import config
import pymysql
import logging


def start_connection():  # Connection to DB
    try:
        connection = pymysql.connect(**config.BD_CONNECT)
        return connection
    except pymysql.err.OperationalError:
        log('Ошибка подключения к БД!', 'error')


def get_stat(chat) -> list:
    connection = start_connection()
    with connection.cursor() as cursor:
        cursor.execute(f'SELECT * FROM Users WHERE supergroup LIKE \'{chat.id}\' ORDER BY karma DESC')
        res = cursor.fetchall()
    return res


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
                               f' \'{str(True) if str(chat.id) == "-1001339129150" else str(False)}\', '
                               f'\'{str(chat.id)}\');')
            else:
                cursor.execute('INSERT INTO Users (`user_id`, `is_bote`, `first_name`, `last_name`, '
                               '`username`) VALUE '
                               f'(\'{int(user.id)}\', \'{str(user.is_bot)}\',\'{user.first_name}\','
                               f'\'{user.last_name}\',\'{user.username}\');')
            connection.commit()
        else:
            if chat is not None:
                cursor.execute(f'UPDATE Users SET supergroup = {chat.id} WHERE user_id LIKE {user.id}')
                if str(chat.id) == "-1001339129150":
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
                          f'AND supergroup LIKE \'-1001339129150\'') == 0:
            return False
        else:
            return True


def change_karma(user, chat, action) -> dict:  # Change Karma
    connection = start_connection()
    with connection.cursor() as cursor:
        add_user(user, chat, connection)
        cursor.execute(f'SELECT `karma` FROM `Users` WHERE `username` = \'{user.username}\';')
        karma = cursor.fetchone()['karma']
        if action[0] == '+':
            karma += len(action) * 10
        else:
            karma -= len(action) * 10
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
    logging.info("Отключение от БД")
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
    logging.info("Отключение от БД")


def random_sticker() -> str:  # Random sticker
    connection = start_connection()
    with connection.cursor() as cursor:
        cursor.execute('SELECT `item_id` FROM Stickers ORDER BY RAND() LIMIT 1')
        result = cursor.fetchone()['item_id']
    connection.close()
    logging.info("Отключение от БД")
    return result


def add_answer(answer) -> None:  # Add answer
    connection = start_connection()
    with connection.cursor() as cursor:
        cursor.execute(f'INSERT INTO `Answer`(`answer`) VALUES (\'{answer}\');')
        connection.commit()
    connection.close()
    logging.info("Отключение от БД")


def get_simple_answer() -> str:  # Get random answer
    connection = start_connection()
    with connection.cursor() as cursor:
        cursor.execute(
            f'SELECT `answer` FROM Answer ORDER BY RAND() LIMIT 1')
        result = cursor.fetchone()['answer']
    connection.close()
    logging.info("Отключение от БД")
    return result


def add_to_db(word, answer) -> None:  # Add word and answer
    connection = start_connection()
    with connection.cursor() as cursor:
        cursor.execute(f'INSERT INTO `Word_Answer`(`word`, `answer`) VALUES (\'{word}\', \'{answer}\');')
        connection.commit()
    connection.close()
    logging.info("Отключение от БД")


def get_answer(word) -> str:  # Get random answer with word
    connection = start_connection()
    with connection.cursor() as cursor:
        cursor.execute(
            f'SELECT answer FROM Word_Answer WHERE word LIKE \'{word}\' ORDER BY RAND() LIMIT 1')
        result = cursor.fetchone()['answer']
    connection.close()
    logging.info("Отключение от БД")
    return result


def get_all_word() -> list:  # Get all answers
    connection = start_connection()
    with connection.cursor() as cursor:
        cursor.execute(f'SELECT `word` FROM Word_Answer')
        result = set(x['word'].lower() for x in cursor.fetchall())
    connection.close()
    logging.info("Отключение от БД")
    return list(result)


def get_code(name: str) -> [dict, None]:  # Get all answers
    connection = start_connection()
    with connection.cursor() as cursor:
        cursor.execute(f'SELECT code FROM PasteBin WHERE name LIKE \'{name}\'')
        result = cursor.fetchone()
    connection.close()
    logging.info("Отключение от БД")
    return result


def random_meme() -> str:  # Random meme
    connection = start_connection()
    with connection.cursor() as cursor:
        cursor.execute('SELECT `url` FROM Memes ORDER BY RAND() LIMIT 1')  # Выполнить команду запроса.
        result = cursor.fetchone()['url']
    connection.close()
    logging.info("Отключение от БД")
    return result


def add_memes(array) -> None:  # Add memes
    connection = start_connection()
    with connection.cursor() as cursor:
        for i in array:
            if cursor.execute(f'SELECT * FROM Memes WHERE url LIKE \'{i}\'') != 1:
                cursor.execute(f'INSERT INTO `Memes`(`url`) VALUES (\'{i}\');')
                connection.commit()
    connection.close()
    logging.info("Отключение от БД")


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
