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

data = """[url=https://ibb.co/ynMNKhh][img]https://i.ibb.co/1fp0Bss/201.png[/img][/url]
[url=https://ibb.co/022pt25][img]https://i.ibb.co/pww6ywq/202.png[/img][/url]
[url=https://ibb.co/0ZJ2txQ][img]https://i.ibb.co/828scHX/203.png[/img][/url]
[url=https://ibb.co/tcVHHCY][img]https://i.ibb.co/q9TDD1m/204.png[/img][/url]
[url=https://ibb.co/bXp55qh][img]https://i.ibb.co/x6VqqPv/205.png[/img][/url]
[url=https://ibb.co/RYZQZ0H][img]https://i.ibb.co/mb1h1qz/206.png[/img][/url]
[url=https://ibb.co/qy2cXkp][img]https://i.ibb.co/zntBjGZ/207.png[/img][/url]
[url=https://ibb.co/tpKB1Pc][img]https://i.ibb.co/JjtnSF2/208.png[/img][/url]
[url=https://ibb.co/5vGKZmG][img]https://i.ibb.co/TRYWy6Y/209.png[/img][/url]
[url=https://ibb.co/KWDhGms][img]https://i.ibb.co/HqC42XP/210.png[/img][/url]
[url=https://ibb.co/rkN2RKb][img]https://i.ibb.co/VV5Yc0H/211.png[/img][/url]
[url=https://ibb.co/xhVV0ND][img]https://i.ibb.co/XXmmgqb/212.png[/img][/url]
[url=https://ibb.co/6sBFkY2][img]https://i.ibb.co/tCXD9BS/213.png[/img][/url]
[url=https://ibb.co/5hczSdD][img]https://i.ibb.co/3mh8jwX/214.png[/img][/url]
[url=https://ibb.co/hc93nRb][img]https://i.ibb.co/xYLxcSW/215.png[/img][/url]
[url=https://ibb.co/L629xnX][img]https://i.ibb.co/Qn1YPr3/216.png[/img][/url]
[url=https://ibb.co/h1QPfS7][img]https://i.ibb.co/2YVDNTn/217.png[/img][/url]
[url=https://ibb.co/Jz68wWn][img]https://i.ibb.co/khbzsVK/218.png[/img][/url]
[url=https://ibb.co/C9JrgqW][img]https://i.ibb.co/YdDrm6b/219.png[/img][/url]
[url=https://ibb.co/D8mrvNJ][img]https://i.ibb.co/dLXmVST/220.png[/img][/url]
[url=https://ibb.co/JQkkMw4][img]https://i.ibb.co/jR441P2/221.png[/img][/url]
[url=https://ibb.co/6F79r5S][img]https://i.ibb.co/gJLqmC8/222.png[/img][/url]
[url=https://ibb.co/7K1r2Cn][img]https://i.ibb.co/1TmR8Qr/223.png[/img][/url]
[url=https://ibb.co/qNbFN8q][img]https://i.ibb.co/0CPVCL4/224.png[/img][/url]
[url=https://ibb.co/4FnvCsP][img]https://i.ibb.co/S64YHQR/225.png[/img][/url]
[url=https://ibb.co/vd3cvYK][img]https://i.ibb.co/dpPfJgz/226.png[/img][/url]
[url=https://ibb.co/vdS2tN3][img]https://i.ibb.co/n1FhWX7/227.png[/img][/url]
[url=https://ibb.co/9hp1gBh][img]https://i.ibb.co/tzHvKnz/228.png[/img][/url]
[url=https://ibb.co/KrYG14p][img]https://i.ibb.co/crPvmfS/229.png[/img][/url]
[url=https://ibb.co/vqCPh7x][img]https://i.ibb.co/kBV8JRg/230.png[/img][/url]
[url=https://ibb.co/17bXGgz][img]https://i.ibb.co/mbSy5jN/231.png[/img][/url]
[url=https://ibb.co/kDHpxKs][img]https://i.ibb.co/FYx9K6L/232.png[/img][/url]
[url=https://ibb.co/bdWC5Bn][img]https://i.ibb.co/vzwT4P8/233.png[/img][/url]
[url=https://ibb.co/16Pg4WJ][img]https://i.ibb.co/RysFJw4/234.png[/img][/url]
[url=https://ibb.co/CPgnJDZ][img]https://i.ibb.co/Hh6rN3s/235.png[/img][/url]
[url=https://ibb.co/M84YNPB][img]https://i.ibb.co/N1P8YWT/236.png[/img][/url]
[url=https://ibb.co/n3tX49J][img]https://i.ibb.co/dbxNXFY/237.png[/img][/url]
[url=https://ibb.co/GkyPddb][img]https://i.ibb.co/Y8mjNNq/238.png[/img][/url]
[url=https://ibb.co/Y7RRDMy][img]https://i.ibb.co/HDFFNsx/239.png[/img][/url]
[url=https://ibb.co/QJBqggP][img]https://i.ibb.co/kGnr774/240.png[/img][/url]
[url=https://ibb.co/sVz5k6L][img]https://i.ibb.co/FDCsN0G/241.png[/img][/url]
[url=https://ibb.co/ZBgd2r2][img]https://i.ibb.co/jywhJYJ/242.png[/img][/url]
[url=https://ibb.co/rkvyvKP][img]https://i.ibb.co/8MX8Xn3/243.png[/img][/url]
[url=https://ibb.co/w7yB1hg][img]https://i.ibb.co/Qk9pGvQ/244.png[/img][/url]
[url=https://ibb.co/5K4kgRp][img]https://i.ibb.co/Sfyc43Y/245.png[/img][/url]
[url=https://ibb.co/4KrjK2h][img]https://i.ibb.co/ydj8dpH/246.png[/img][/url]
[url=https://ibb.co/0B5Q4cc][img]https://i.ibb.co/28J5Vyy/247.png[/img][/url]
[url=https://ibb.co/CzyhZrF][img]https://i.ibb.co/c19DHmd/248.png[/img][/url]
[url=https://ibb.co/ByLfLtR][img]https://i.ibb.co/jyh8hTF/249.png[/img][/url]
[url=https://ibb.co/3cJHr0N][img]https://i.ibb.co/QM5Gb6N/250.png[/img][/url]
[url=https://ibb.co/ZfVVJmD][img]https://i.ibb.co/WH663tJ/251.png[/img][/url]
[url=https://ibb.co/dKcK6Wy][img]https://i.ibb.co/LpPp6kf/252.png[/img][/url]
[url=https://ibb.co/dGc3pLJ][img]https://i.ibb.co/vZBrdQv/253.png[/img][/url]
[url=https://ibb.co/3CG8J0B][img]https://i.ibb.co/NyQk4LZ/254.png[/img][/url]
[url=https://ibb.co/ts5wL1R][img]https://i.ibb.co/FwtkHdp/255.png[/img][/url]
[url=https://ibb.co/3rPkf8f][img]https://i.ibb.co/LksvQqQ/256.png[/img][/url]
[url=https://ibb.co/dPbWYn3][img]https://i.ibb.co/x1mCTVc/257.png[/img][/url]
[url=https://ibb.co/H23y096][img]https://i.ibb.co/1njN341/258.png[/img][/url]
[url=https://ibb.co/MSZ1031][img]https://i.ibb.co/6wrtCft/259.png[/img][/url]
[url=https://ibb.co/LYK750S][img]https://i.ibb.co/bQt9J61/260.png[/img][/url]
[url=https://ibb.co/4NPzjBF][img]https://i.ibb.co/C0hgnxw/261.png[/img][/url]
[url=https://ibb.co/C9FpT5P][img]https://i.ibb.co/X5TfvZY/262.png[/img][/url]
[url=https://ibb.co/3vrR4nr][img]https://i.ibb.co/dtWmjRW/263.png[/img][/url]
[url=https://ibb.co/8B7Rm21][img]https://i.ibb.co/z54Lmbq/264.png[/img][/url]
[url=https://ibb.co/G5yNNh8][img]https://i.ibb.co/KrdSS1f/265.png[/img][/url]
[url=https://ibb.co/K6pF2BT][img]https://i.ibb.co/p2BJfNY/266.png[/img][/url]
[url=https://ibb.co/sjMxT5F][img]https://i.ibb.co/dBzCNbQ/267.png[/img][/url]
[url=https://ibb.co/RTd3FFN][img]https://i.ibb.co/yF7699p/268.png[/img][/url]
[url=https://ibb.co/zJngFwR][img]https://i.ibb.co/6BnS85P/269.png[/img][/url]
[url=https://ibb.co/bLGRzQ6][img]https://i.ibb.co/vmMvZVc/270.png[/img][/url]
[url=https://ibb.co/pRVm77h][img]https://i.ibb.co/TbjCffW/271.png[/img][/url]
[url=https://ibb.co/gdr6MzF][img]https://i.ibb.co/m0RSC6F/272.png[/img][/url]
[url=https://ibb.co/mt1gTnL][img]https://i.ibb.co/6bVLwK3/273.png[/img][/url]
[url=https://ibb.co/y8JDQLH][img]https://i.ibb.co/19x3mHF/274.png[/img][/url]
[url=https://ibb.co/gjCM5r8][img]https://i.ibb.co/98j9Fp0/275.png[/img][/url]
[url=https://ibb.co/cDg6LSW][img]https://i.ibb.co/t8mqXT0/276.png[/img][/url]
[url=https://ibb.co/bX5k8Dy][img]https://i.ibb.co/pdjS95s/277.png[/img][/url]
[url=https://ibb.co/GnCjLhq][img]https://i.ibb.co/ck2dHmj/278.png[/img][/url]
[url=https://ibb.co/H4wh54F][img]https://i.ibb.co/yPv4HPf/279.png[/img][/url]
[url=https://ibb.co/wsZVrRS][img]https://i.ibb.co/M6yr5sc/280.png[/img][/url]
[url=https://ibb.co/LZVsbKH][img]https://i.ibb.co/0GHz85v/281.png[/img][/url]
[url=https://ibb.co/QNMfMzZ][img]https://i.ibb.co/SnBPBW2/282.png[/img][/url]
[url=https://ibb.co/vqpy3sf][img]https://i.ibb.co/qjKqN0h/283.png[/img][/url]
[url=https://ibb.co/qkDrtbX][img]https://i.ibb.co/D51Rx3s/284.png[/img][/url]
[url=https://ibb.co/bPFx0JR][img]https://i.ibb.co/6m82MBJ/285.png[/img][/url]
[url=https://ibb.co/842QS9J][img]https://i.ibb.co/S70Z9B2/286.png[/img][/url]
[url=https://ibb.co/vsgC5zK][img]https://i.ibb.co/5YtXDcf/287.png[/img][/url]
[url=https://ibb.co/XJChC5h][img]https://i.ibb.co/mzcLcyL/288.png[/img][/url]
[url=https://ibb.co/Dzzkhk6][img]https://i.ibb.co/mbbtktY/289.png[/img][/url]
[url=https://ibb.co/dKvfwqp][img]https://i.ibb.co/3hbT9qF/290.png[/img][/url]
[url=https://ibb.co/C77nBYS][img]https://i.ibb.co/XsszXKG/291.png[/img][/url]
[url=https://ibb.co/J76vZPY][img]https://i.ibb.co/bBwstn4/292.png[/img][/url]
[url=https://ibb.co/d0zBpgg][img]https://i.ibb.co/hRtsdff/293.png[/img][/url]
[url=https://ibb.co/pRZ5ZMF][img]https://i.ibb.co/nnftfYJ/294.png[/img][/url]
[url=https://ibb.co/94xYQh9][img]https://i.ibb.co/rpByD3G/295.png[/img][/url]
[url=https://ibb.co/dgGGtMM][img]https://i.ibb.co/7422QCC/296.png[/img][/url]
[url=https://ibb.co/yQ9n3T1][img]https://i.ibb.co/vjFxt5G/297.png[/img][/url]
[url=https://ibb.co/MZJg7Wm][img]https://i.ibb.co/HB9Kq1j/298.png[/img][/url]
[url=https://ibb.co/gt4ZHDz][img]https://i.ibb.co/xzFqPMJ/299.png[/img][/url]
[url=https://ibb.co/GcGPjr9][img]https://i.ibb.co/NZfYzGr/300.png[/img][/url]
[url=https://ibb.co/5RQvKC1][img]https://i.ibb.co/YL580JN/301.png[/img][/url]
[url=https://ibb.co/k6kgFyg][img]https://i.ibb.co/cXMcdvc/302.png[/img][/url]
[url=https://ibb.co/BV6fc5D][img]https://i.ibb.co/rGpQFRP/303.png[/img][/url]
[url=https://ibb.co/cgQ3Hr0][img]https://i.ibb.co/znZxY4p/304.png[/img][/url]
[url=https://ibb.co/F70n8wL][img]https://i.ibb.co/HgxXGzf/305.png[/img][/url]
[url=https://ibb.co/nL8dNMF][img]https://i.ibb.co/HHpwfTj/306.png[/img][/url]
[url=https://ibb.co/q7gGfV8][img]https://i.ibb.co/17XV5jN/307.png[/img][/url]
[url=https://ibb.co/NLRrbgD][img]https://i.ibb.co/4jk23wv/308.png[/img][/url]
[url=https://ibb.co/JpzyqNf][img]https://i.ibb.co/B6grGmX/309.png[/img][/url]
[url=https://ibb.co/wp5bMd2][img]https://i.ibb.co/Dw0651j/310.png[/img][/url]
[url=https://ibb.co/RjFT8vd][img]https://i.ibb.co/vXF49wR/311.png[/img][/url]
[url=https://ibb.co/3NRYM48][img]https://i.ibb.co/58KxnGz/312.png[/img][/url]
[url=https://ibb.co/grf9WVT][img]https://i.ibb.co/8mfsxc5/313.png[/img][/url]
[url=https://ibb.co/gtm9ntV][img]https://i.ibb.co/0Ym2wYt/314.png[/img][/url]
[url=https://ibb.co/2MwRhZc][img]https://i.ibb.co/C9q48PV/315.png[/img][/url]
[url=https://ibb.co/RpzXdg8][img]https://i.ibb.co/svyTzg7/316.png[/img][/url]
[url=https://ibb.co/7JwCj96][img]https://i.ibb.co/fYhFqcP/317.png[/img][/url]
[url=https://ibb.co/b58pZgd][img]https://i.ibb.co/HTkmsDg/318.png[/img][/url]
[url=https://ibb.co/XY0DgmX][img]https://i.ibb.co/fD695mM/319.png[/img][/url]
[url=https://ibb.co/sqvFrPd][img]https://i.ibb.co/M7DRLhx/320.png[/img][/url]
[url=https://ibb.co/wNJwnHW][img]https://i.ibb.co/tMZx0fs/321.png[/img][/url]
[url=https://ibb.co/RhL0rNM][img]https://i.ibb.co/1sHqyMp/322.png[/img][/url]
[url=https://ibb.co/t8m2R49][img]https://i.ibb.co/yWfk2Xr/323.png[/img][/url]
[url=https://ibb.co/x71RGNL][img]https://i.ibb.co/fxkPtsF/324.png[/img][/url]
[url=https://ibb.co/R3MfWK1][img]https://i.ibb.co/YcKmGS6/325.png[/img][/url]
[url=https://ibb.co/jfkHcDV][img]https://i.ibb.co/F34nSzs/326.png[/img][/url]
[url=https://ibb.co/cFnGYWm][img]https://i.ibb.co/FwTSHQP/327.png[/img][/url]
[url=https://ibb.co/ngbsjR9][img]https://i.ibb.co/NVs6K75/328.png[/img][/url]
[url=https://ibb.co/L8pxFKV][img]https://i.ibb.co/Cz0bcLR/329.png[/img][/url]
[url=https://ibb.co/d2wcHCq][img]https://i.ibb.co/cFSvsfH/330.png[/img][/url]
[url=https://ibb.co/qRT30kn][img]https://i.ibb.co/RCRkhzS/331.png[/img][/url]
[url=https://ibb.co/N6c2hF8][img]https://i.ibb.co/bgc5h6S/332.png[/img][/url]
[url=https://ibb.co/kh0jjgx][img]https://i.ibb.co/BgjbbVt/333.png[/img][/url]
[url=https://ibb.co/yNVmHdy][img]https://i.ibb.co/10bYF7q/334.png[/img][/url]
[url=https://ibb.co/hRpwd5C][img]https://i.ibb.co/pvC5KDn/335.png[/img][/url]
[url=https://ibb.co/K0TJnDv][img]https://i.ibb.co/Bz09kGM/336.png[/img][/url]
[url=https://ibb.co/vZr7q8w][img]https://i.ibb.co/KFQMhH0/337.png[/img][/url]
[url=https://ibb.co/1mWDck7][img]https://i.ibb.co/kSCRZt5/338.png[/img][/url]
[url=https://ibb.co/7N6QCXx][img]https://i.ibb.co/WpY056N/339.png[/img][/url]
[url=https://ibb.co/FBMpQKx][img]https://i.ibb.co/64xQKmn/340.png[/img][/url]
[url=https://ibb.co/cY4mQfJ][img]https://i.ibb.co/bbcfXw1/341.png[/img][/url]
[url=https://ibb.co/tq71HN4][img]https://i.ibb.co/x1pr2cD/342.png[/img][/url]
[url=https://ibb.co/M7FyCVk][img]https://i.ibb.co/GRzf52Q/343.png[/img][/url]
[url=https://ibb.co/VMwjHGy][img]https://i.ibb.co/8PYKzw3/344.png[/img][/url]
[url=https://ibb.co/W2vzsJV][img]https://i.ibb.co/G5QMFSH/345.png[/img][/url]
[url=https://ibb.co/sWGb01Q][img]https://i.ibb.co/2ZQWDMP/346.png[/img][/url]
[url=https://ibb.co/R7NNsVx][img]https://i.ibb.co/yVppZbw/347.png[/img][/url]
[url=https://ibb.co/JtkZQM1][img]https://i.ibb.co/pwXqy97/348.png[/img][/url]
[url=https://ibb.co/F5s7pFh][img]https://i.ibb.co/n73kpFw/349.png[/img][/url]
[url=https://ibb.co/6HDWjsp][img]https://i.ibb.co/bsNKcdy/350.png[/img][/url]
[url=https://ibb.co/GpNTznM][img]https://i.ibb.co/YQwZHPd/351.png[/img][/url]
[url=https://ibb.co/YBXX6Z0][img]https://i.ibb.co/yFppDS4/352.png[/img][/url]
[url=https://ibb.co/z4JVzc5][img]https://i.ibb.co/QKdv4Bc/353.png[/img][/url]
[url=https://ibb.co/mScNmnM][img]https://i.ibb.co/Ws2VQrY/354.png[/img][/url]
[url=https://ibb.co/gDFMgdB][img]https://i.ibb.co/GV3vP9b/355.png[/img][/url]
[url=https://ibb.co/w0W2JMw][img]https://i.ibb.co/r76Xb4c/356.png[/img][/url]
[url=https://ibb.co/G7SXLLV][img]https://i.ibb.co/hszkjjK/357.png[/img][/url]
[url=https://ibb.co/6DL4X9f][img]https://i.ibb.co/p453hV9/358.png[/img][/url]
[url=https://ibb.co/VNCNd3F][img]https://i.ibb.co/cv8vPxW/359.png[/img][/url]
[url=https://ibb.co/tsq7Dxr][img]https://i.ibb.co/SnthBdC/360.png[/img][/url]
[url=https://ibb.co/jDNC2kp][img]https://i.ibb.co/6FMKx0d/361.png[/img][/url]
[url=https://ibb.co/x2cWBq2][img]https://i.ibb.co/2FLxC3F/362.png[/img][/url]
[url=https://ibb.co/Gcqbzqz][img]https://i.ibb.co/18kwFkF/363.png[/img][/url]
[url=https://ibb.co/Pz1gkd6][img]https://i.ibb.co/wrp4tfz/364.png[/img][/url]
[url=https://ibb.co/sbFzz9p][img]https://i.ibb.co/rFZNN2K/365.png[/img][/url]
[url=https://ibb.co/0MSDHmX][img]https://i.ibb.co/jM26nb5/366.png[/img][/url]
[url=https://ibb.co/RQGLNHR][img]https://i.ibb.co/3S5tvhg/367.png[/img][/url]
[url=https://ibb.co/cJWGM6r][img]https://i.ibb.co/kKLRk4S/368.png[/img][/url]
[url=https://ibb.co/WVgfvBQ][img]https://i.ibb.co/2Zgd3cw/369.png[/img][/url]
[url=https://ibb.co/Gk3qnvW][img]https://i.ibb.co/pZrSbvf/370.png[/img][/url]
[url=https://ibb.co/pPc2zb2][img]https://i.ibb.co/g7NyTmy/371.png[/img][/url]
[url=https://ibb.co/G2nY3Xj][img]https://i.ibb.co/Xsj0k9T/372.png[/img][/url]
[url=https://ibb.co/spYTfDQ][img]https://i.ibb.co/HL8cSMY/373.png[/img][/url]
[url=https://ibb.co/bXYfY0L][img]https://i.ibb.co/QMh5hgn/374.png[/img][/url]
[url=https://ibb.co/NjPmxTJ][img]https://i.ibb.co/J74yn3G/375.png[/img][/url]
[url=https://ibb.co/vjtLvfr][img]https://i.ibb.co/MCXP5Kj/376.png[/img][/url]
[url=https://ibb.co/Sr33nkG][img]https://i.ibb.co/YZLLk5w/377.png[/img][/url]
[url=https://ibb.co/9cgKdWY][img]https://i.ibb.co/wBgG246/378.png[/img][/url]
[url=https://ibb.co/mHGj9P0][img]https://i.ibb.co/4j7q802/379.png[/img][/url]
[url=https://ibb.co/Ldd6f0k][img]https://i.ibb.co/CKKvFw1/380.png[/img][/url]
[url=https://ibb.co/fnb1dMS][img]https://i.ibb.co/rcg72kt/381.png[/img][/url]
[url=https://ibb.co/FWVv5qM][img]https://i.ibb.co/0XtNCVS/382.png[/img][/url]
[url=https://ibb.co/wCscvWx][img]https://i.ibb.co/K7wK1q3/383.png[/img][/url]
[url=https://ibb.co/fpHc8V1][img]https://i.ibb.co/mq4xvrD/384.png[/img][/url]
[url=https://ibb.co/zX3GmFG][img]https://i.ibb.co/gS0zrdz/385.png[/img][/url]
[url=https://ibb.co/khN3qgw][img]https://i.ibb.co/WcmDBWM/386.png[/img][/url]
[url=https://ibb.co/LQq75ks][img]https://i.ibb.co/mvYW8DP/387.png[/img][/url]
[url=https://ibb.co/r4znY5W][img]https://i.ibb.co/f4ymfrc/388.png[/img][/url]
[url=https://ibb.co/1nsBxtV][img]https://i.ibb.co/268RB12/389.png[/img][/url]
[url=https://ibb.co/Rjqsmvw][img]https://i.ibb.co/1zkP5vW/390.png[/img][/url]
[url=https://ibb.co/g3wpXwK][img]https://i.ibb.co/6mbxpbC/391.png[/img][/url]
[url=https://ibb.co/GWMNNjp][img]https://i.ibb.co/F5YCCt3/392.png[/img][/url]
[url=https://ibb.co/cFRcCN5][img]https://i.ibb.co/vPfxQJ5/393.png[/img][/url]
[url=https://ibb.co/H4QGdF3][img]https://i.ibb.co/h9v2f7w/394.png[/img][/url]
[url=https://ibb.co/M1vhfd5][img]https://i.ibb.co/pK7PQqr/395.png[/img][/url]
[url=https://ibb.co/K2zbzB8][img]https://i.ibb.co/pfrbrNk/396.png[/img][/url]
[url=https://ibb.co/DQZx9jz][img]https://i.ibb.co/TtsV4NY/397.png[/img][/url]
[url=https://ibb.co/94HgHvC][img]https://i.ibb.co/rp202t1/398.png[/img][/url]
[url=https://ibb.co/xfGTsjg][img]https://i.ibb.co/dL6Yc2p/399.png[/img][/url]
[url=https://ibb.co/ZVRSvYd][img]https://i.ibb.co/9NmhBVn/400.png[/img][/url]"""

def set_img():
    import re
    strings = data.split('\n')
    connection = start_connection()
    for en, i in enumerate(strings, 201):
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
