# -*- coding: utf-8 -*-
import config
import pymysql
import logging


def start_connection():  # Подключиться к базе данных.
    # try:
    connection = pymysql.connect(**config.BD_CONNECT)
    logging.info("Успешное подклчение к БД!")
    return connection
    # except pymysql.err.OperationalError:
    #     raise ConnectionError('Ошибка подключения к БД!')


def get_joke() -> dict:  # Рандомная шутка
    connection = start_connection()
    with connection.cursor() as cursor:
        cursor.execute('SELECT `setup`, `panchline` FROM Joke ORDER BY RAND() LIMIT 1')  # Выполнить команду запроса.
        result = cursor.fetchall()[0]  # cursor.fetch()[0][0] for online database
    connection.close()
    logging.info("Отключение от БД")
    return result


def change_karma(username, action):  # Изменение кармы
    connection = start_connection()
    with connection.cursor() as cursor:
        if cursor.execute(f'SELECT * FROM Users WHERE username LIKE \'{username}\'') != 0:
            cursor.execute(f'SELECT `karma` FROM `Users` WHERE `username` = \'{username}\';')
            karma = cursor.fetchall()[0]['karma']
            if action == '+':
                karma += 10
            else:
                karma -= 10
            cursor.execute(f'UPDATE `Users` SET `karma` = \'{karma}\' WHERE `username` = \'{username}\';')
            connection.commit()
    connection.close()
    logging.info("Отключение от БД")
    return karma


def add_user_to_db(user_id, is_bote, first_name, last_name, username):  # Добавить пользователя в бд
    connection = start_connection()
    with connection.cursor() as cursor:
        if cursor.execute(f'SELECT * FROM Users WHERE user_id LIKE \'{user_id}\''
                          f'AND username LIKE \'{username}\';') == 0:
            cursor.execute(f'INSERT INTO `Users`(`user_id`, `is_bote`, `first_name`, `last_name`, `username`) VALUES '
                           f'(\'{user_id}\', \'{str(is_bote)}\',\'{first_name}\',\'{last_name}\',\'{username}\');')
            connection.commit()
    connection.close()
    logging.info("Отключение от БД")


def random_gn_sticker() -> str:  # Рандомный стикер ГН
    connection = start_connection()
    with connection.cursor() as cursor:
        cursor.execute('SELECT `item_id` FROM Stickers_gn ORDER BY RAND() LIMIT 1')  # Выполнить команду запроса.
        result = cursor.fetchall()[0]['item_id']  # cursor.fetch()[0][0] for online database
    connection.close()
    logging.info("Отключение от БД")
    return result


def add_sticker(item_id, emoji, name):  # Добавить стикер
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


def random_sticker() -> str:  # Рандомный стикер
    connection = start_connection()
    with connection.cursor() as cursor:
        cursor.execute('SELECT `item_id` FROM Stickers ORDER BY RAND() LIMIT 1')  # Выполнить команду запроса.
        result = cursor.fetchall()[0][0]  # cursor.fetch()[0][0] for online database
    connection.close()
    logging.info("Отключение от БД")
    return result


def add_answer(answer):  # Добавить ответ
    connection = start_connection()
    with connection.cursor() as cursor:
        cursor.execute(f'INSERT INTO `Answer`(`answer`) VALUES (\'{answer}\');')
        connection.commit()
    connection.close()
    logging.info("Отключение от БД")


def get_simple_answer() -> str:  # Рандомный ответ
    connection = start_connection()
    with connection.cursor() as cursor:
        cursor.execute(
            f'SELECT `answer` FROM Answer ORDER BY RAND() LIMIT 1')
        result = cursor.fetchall()[0][0]
    connection.close()
    logging.info("Отключение от БД")
    return result


def add_to_db(word, answer):  # Добавить слово ответ
    connection = start_connection()
    with connection.cursor() as cursor:
        cursor.execute(f'INSERT INTO `Word_Answer`(`word`, `answer`) VALUES (\'{word}\', \'{answer}\');')
        connection.commit()
    connection.close()
    logging.info("Отключение от БД")


def get_answer(word) -> str:  # Получить ответ
    connection = start_connection()
    with connection.cursor() as cursor:
        cursor.execute(
            f'SELECT `answer` FROM Word_Answer WHERE word LIKE \'{word}\' ORDER BY RAND() LIMIT 1')
        result = cursor.fetchall()[0][0]
    connection.close()
    logging.info("Отключение от БД")
    return result


def get_all_word() -> list:  # Получить все ответы
    connection = start_connection()
    with connection.cursor() as cursor:
        cursor.execute(
            f'SELECT `word` FROM Word_Answer')
        result = set(x[0].lower() for x in cursor.fetchall())
    connection.close()
    logging.info("Отключение от БД")
    return list(result)


def random_meme() -> str:  # Рандомный мем
    connection = start_connection()
    with connection.cursor() as cursor:
        cursor.execute('SELECT `url` FROM Memes ORDER BY RAND() LIMIT 1')  # Выполнить команду запроса.
        result = cursor.fetchall()[0][0]  # cursor.fetch()[0][0] for online database
    connection.close()
    logging.info("Отключение от БД")
    return result


def add_memes(array):  # Добавить мемы
    connection = start_connection()
    with connection.cursor() as cursor:
        for i in array:
            if cursor.execute(f'SELECT * FROM Memes WHERE url LIKE \'{i}\'') != 1:
                cursor.execute(f'INSERT INTO `Memes`(`url`) VALUES (\'{i}\');')
                connection.commit()
    connection.close()
    logging.info("Отключение от БД")

# def add_gn_sticker(item_id, emoji, name):  # Добавить стикер в гн
#     connection = start_connection()
#     with connection.cursor() as cursor:
#         if cursor.execute(f'SELECT * FROM Stickers_gn WHERE item_id LIKE \'{item_id}\'') != 1 :
#             cursor.execute(f'INSERT INTO `Stickers_gn`(`item_id`, `emoji`, `set_name`) VALUES (\'{item_id}\','
#                            f'\'{emoji}\',\'{name}\');')
#             connection.commit()
#     connection.close()
#     logging.info("Отключение от БД")
