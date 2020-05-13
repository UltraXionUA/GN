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

data = """[url=https://ibb.co/9mD4Rtv][img]https://i.ibb.co/DPJM3pb/101.png[/img][/url]
[url=https://ibb.co/SJ7kg59][img]https://i.ibb.co/x38nbXR/102.png[/img][/url]
[url=https://ibb.co/0qNnP0k][img]https://i.ibb.co/JnLcXYN/103.png[/img][/url]
[url=https://ibb.co/WBrQNKk][img]https://i.ibb.co/kqLpVc4/104.png[/img][/url]
[url=https://ibb.co/J71cy6q][img]https://i.ibb.co/2t9FsVS/105.png[/img][/url]
[url=https://ibb.co/qgrCqS5][img]https://i.ibb.co/dp5tCTg/106.png[/img][/url]
[url=https://ibb.co/QdcDLdy][img]https://i.ibb.co/BNPnbN0/107.png[/img][/url]
[url=https://ibb.co/9chrKVm][img]https://i.ibb.co/YPXLny4/108.png[/img][/url]
[url=https://ibb.co/6wN6nCF][img]https://i.ibb.co/W5sSxJf/109.png[/img][/url]
[url=https://ibb.co/xMVRs0x][img]https://i.ibb.co/646fZxj/110.png[/img][/url]
[url=https://ibb.co/cLFfXJw][img]https://i.ibb.co/Ry0r42N/111.png[/img][/url]
[url=https://ibb.co/1bLbgfz][img]https://i.ibb.co/mSGSjCN/112.png[/img][/url]
[url=https://ibb.co/KG0Scy0][img]https://i.ibb.co/VNj50Bj/113.png[/img][/url]
[url=https://ibb.co/n6NbVY5][img]https://i.ibb.co/PFvNbPf/114.png[/img][/url]
[url=https://ibb.co/93xHPz8][img]https://i.ibb.co/DgBfdsV/115.png[/img][/url]
[url=https://ibb.co/h7Jy5Z3][img]https://i.ibb.co/2n1y2sG/116.png[/img][/url]
[url=https://ibb.co/jwM07Cc][img]https://i.ibb.co/7pWM73w/117.png[/img][/url]
[url=https://ibb.co/Wz8BZZN][img]https://i.ibb.co/Lgj9mmD/118.png[/img][/url]
[url=https://ibb.co/9rHtXxb][img]https://i.ibb.co/bK5Jh4s/119.png[/img][/url]
[url=https://ibb.co/HdXsb6J][img]https://i.ibb.co/WtswMZT/120.png[/img][/url]
[url=https://ibb.co/R7NcRZW][img]https://i.ibb.co/nRBjxZS/121.png[/img][/url]
[url=https://ibb.co/gSV0d24][img]https://i.ibb.co/GWTZ96H/122.png[/img][/url]
[url=https://ibb.co/L9xGtb5][img]https://i.ibb.co/9ybMTzt/123.png[/img][/url]
[url=https://ibb.co/qrFSn4X][img]https://i.ibb.co/vjvFBrg/124.png[/img][/url]
[url=https://ibb.co/rH1wGKT][img]https://i.ibb.co/kXWSgVk/125.png[/img][/url]
[url=https://ibb.co/M1RWJg3][img]https://i.ibb.co/T0HpNwF/126.png[/img][/url]
[url=https://ibb.co/Y32Vdwr][img]https://i.ibb.co/qdB2gVZ/127.png[/img][/url]
[url=https://ibb.co/sQDNkMz][img]https://i.ibb.co/82RfTSt/128.png[/img][/url]
[url=https://ibb.co/xh72vfV][img]https://i.ibb.co/SN36Tdq/129.png[/img][/url]
[url=https://ibb.co/SsnhMfr][img]https://i.ibb.co/QbN2TDd/130.png[/img][/url]
[url=https://ibb.co/3FwbqDc][img]https://i.ibb.co/8xJwpW9/131.png[/img][/url]
[url=https://ibb.co/gSjBh4v][img]https://i.ibb.co/0CDdvsB/132.png[/img][/url]
[url=https://ibb.co/sqkC8wR][img]https://i.ibb.co/dD1t82M/133.png[/img][/url]
[url=https://ibb.co/p4L0ZNt][img]https://i.ibb.co/QYKbnh2/134.png[/img][/url]
[url=https://ibb.co/2NHPs5X][img]https://i.ibb.co/WtjFPsS/135.png[/img][/url]
[url=https://ibb.co/1bBYvJk][img]https://i.ibb.co/fQZV1Gs/136.png[/img][/url]
[url=https://ibb.co/3Fv0S5M][img]https://i.ibb.co/DMY7wP8/137.png[/img][/url]
[url=https://ibb.co/2sDGw78][img]https://i.ibb.co/7RwsHJg/138.png[/img][/url]
[url=https://ibb.co/dP3ZBgH][img]https://i.ibb.co/y6M20Sx/139.png[/img][/url]
[url=https://ibb.co/dfJDLQ2][img]https://i.ibb.co/D1gQ87C/140.png[/img][/url]
[url=https://ibb.co/w6D9Ygc][img]https://i.ibb.co/0JPgQ2s/141.png[/img][/url]
[url=https://ibb.co/0Zh2RK2][img]https://i.ibb.co/P4wjvMj/142.png[/img][/url]
[url=https://ibb.co/swfH7tJ][img]https://i.ibb.co/3N3zKkY/143.png[/img][/url]
[url=https://ibb.co/Jjnn3gT][img]https://i.ibb.co/LdSSNHy/144.png[/img][/url]
[url=https://ibb.co/hM28rW8][img]https://i.ibb.co/n0Qk4ck/145.png[/img][/url]
[url=https://ibb.co/BzjGTHN][img]https://i.ibb.co/Ss0cVDr/146.png[/img][/url]
[url=https://ibb.co/P1QrVBr][img]https://i.ibb.co/KVw58C5/147.png[/img][/url]
[url=https://ibb.co/x3F5Ryp][img]https://i.ibb.co/8XY8SJW/148.png[/img][/url]
[url=https://ibb.co/Zf3xGsM][img]https://i.ibb.co/8mJ9N37/149.png[/img][/url]
[url=https://ibb.co/hM7bt4F][img]https://i.ibb.co/59MmfSh/150.png[/img][/url]
[url=https://ibb.co/Krx3yLj][img]https://i.ibb.co/RDTVHBp/151.png[/img][/url]
[url=https://ibb.co/ZJyC4HW][img]https://i.ibb.co/N3wzD1Z/152.png[/img][/url]
[url=https://ibb.co/zhjPTzB][img]https://i.ibb.co/XZNFrqK/153.png[/img][/url]
[url=https://ibb.co/6XpHpds][img]https://i.ibb.co/bbysyfd/154.png[/img][/url]
[url=https://ibb.co/3CBWTH3][img]https://i.ibb.co/mc6tR7j/155.png[/img][/url]
[url=https://ibb.co/sK8g8tk][img]https://i.ibb.co/WkmHmsq/156.png[/img][/url]
[url=https://ibb.co/D4QJFT4][img]https://i.ibb.co/K6WPgS6/157.png[/img][/url]
[url=https://ibb.co/jHkjvkQ][img]https://i.ibb.co/JCjSRjG/158.png[/img][/url]
[url=https://ibb.co/7N9ZvkH][img]https://i.ibb.co/PzSPxDR/159.png[/img][/url]
[url=https://ibb.co/8DPVbYb][img]https://i.ibb.co/wNp17c7/160.png[/img][/url]
[url=https://ibb.co/f4m3F4p][img]https://i.ibb.co/3BtxdBN/161.png[/img][/url]
[url=https://ibb.co/rk4CJQB][img]https://i.ibb.co/b1zSn64/162.png[/img][/url]
[url=https://ibb.co/59dsWzp][img]https://i.ibb.co/xsyzSc9/163.png[/img][/url]
[url=https://ibb.co/9gqDwSW][img]https://i.ibb.co/LRCFQH1/164.png[/img][/url]
[url=https://ibb.co/3p2hJ3w][img]https://i.ibb.co/x1W54ky/165.png[/img][/url]
[url=https://ibb.co/wrFhGHy][img]https://i.ibb.co/VpcYnyV/166.png[/img][/url]
[url=https://ibb.co/kmJPc3m][img]https://i.ibb.co/bbFGdHb/167.png[/img][/url]
[url=https://ibb.co/tmTdM2K][img]https://i.ibb.co/HFfJDP4/168.png[/img][/url]
[url=https://ibb.co/HThwyTL][img]https://i.ibb.co/jkJ0Yk9/169.png[/img][/url]
[url=https://ibb.co/T8mjM8w][img]https://i.ibb.co/58Bph81/170.png[/img][/url]
[url=https://ibb.co/h7TpC8w][img]https://i.ibb.co/kHPYMcv/171.png[/img][/url]
[url=https://ibb.co/6s19S6L][img]https://i.ibb.co/ThbjGzd/172.png[/img][/url]
[url=https://ibb.co/25FqFSQ][img]https://i.ibb.co/b7616FZ/173.png[/img][/url]
[url=https://ibb.co/zsmsC9H][img]https://i.ibb.co/tBHBnjP/174.png[/img][/url]
[url=https://ibb.co/Qp9Py0t][img]https://i.ibb.co/Kb62TnS/175.png[/img][/url]
[url=https://ibb.co/qFK960m][img]https://i.ibb.co/k6j0Z3q/176.png[/img][/url]
[url=https://ibb.co/vdHY4Wp][img]https://i.ibb.co/VCtmYGR/177.png[/img][/url]
[url=https://ibb.co/xCvdNrQ][img]https://i.ibb.co/K0ZSJ8H/178.png[/img][/url]
[url=https://ibb.co/s2F5cTm][img]https://i.ibb.co/zrS8C3n/179.png[/img][/url]
[url=https://ibb.co/TKhJ3wb][img]https://i.ibb.co/DGKm218/180.png[/img][/url]
[url=https://ibb.co/xCpX7G0][img]https://i.ibb.co/yfwdQ51/181.png[/img][/url]
[url=https://ibb.co/zxhXzsm][img]https://i.ibb.co/9g9b7np/182.png[/img][/url]
[url=https://ibb.co/Z1ZWtvw][img]https://i.ibb.co/CsrhN4X/183.png[/img][/url]
[url=https://ibb.co/1m2fqRr][img]https://i.ibb.co/sV3vwsK/184.png[/img][/url]
[url=https://ibb.co/V9n4Kmk][img]https://i.ibb.co/zx9vkJt/185.png[/img][/url]
[url=https://ibb.co/M80Qy46][img]https://i.ibb.co/s5YzpGH/186.png[/img][/url]
[url=https://ibb.co/fdZ2KHs][img]https://i.ibb.co/3mV78cn/187.png[/img][/url]
[url=https://ibb.co/DLnJvK6][img]https://i.ibb.co/cxdBZTp/188.png[/img][/url]
[url=https://ibb.co/fCjtKPg][img]https://i.ibb.co/XzcpdvQ/189.png[/img][/url]
[url=https://ibb.co/ZYXfCkY][img]https://i.ibb.co/Hx4KQkx/190.png[/img][/url]
[url=https://ibb.co/rxpBCQs][img]https://i.ibb.co/sK1T0gH/191.png[/img][/url]
[url=https://ibb.co/6H9XQ3v][img]https://i.ibb.co/T4jWyVK/192.png[/img][/url]
[url=https://ibb.co/cw0Rq5v][img]https://i.ibb.co/BGbvkDP/193.png[/img][/url]
[url=https://ibb.co/g64kQNP][img]https://i.ibb.co/FnHRc20/194.png[/img][/url]
[url=https://ibb.co/Wy98Ttq][img]https://i.ibb.co/BZDW1Nd/195.png[/img][/url]
[url=https://ibb.co/kSg94zS][img]https://i.ibb.co/VqWQgbq/196.png[/img][/url]
[url=https://ibb.co/93dcWdk][img]https://i.ibb.co/prkbdkB/197.png[/img][/url]
[url=https://ibb.co/QQm3fN7][img]https://i.ibb.co/mTzVGqr/198.png[/img][/url]
[url=https://ibb.co/RH4Vjwt][img]https://i.ibb.co/2KYfZ4R/199.png[/img][/url]
[url=https://ibb.co/92h6d5D][img]https://i.ibb.co/sQCnXYf/200.png[/img][/url]"""

def set_img():
    import re
    strings = data.split('\n')
    connection = start_connection()
    for en, i in enumerate(strings, 101):
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
