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

data = """[url=https://ibb.co/YWjYJ08][img]https://i.ibb.co/kyckzm0/401.png[/img][/url]
[url=https://ibb.co/VY8sG4D][img]https://i.ibb.co/TM5sG3R/402.png[/img][/url]
[url=https://ibb.co/pPYywH8][img]https://i.ibb.co/fSjvF35/403.png[/img][/url]
[url=https://ibb.co/HX4ZD19][img]https://i.ibb.co/GFpmvBr/404.png[/img][/url]
[url=https://ibb.co/HNnbX5w][img]https://i.ibb.co/5YBS2bp/405.png[/img][/url]
[url=https://ibb.co/XxY1vZ5][img]https://i.ibb.co/v4XpKxd/406.png[/img][/url]
[url=https://ibb.co/4YrfLr7][img]https://i.ibb.co/GtSJDS0/407.png[/img][/url]
[url=https://ibb.co/DRbK66K][img]https://i.ibb.co/TgThnnh/408.png[/img][/url]
[url=https://ibb.co/dcxGsq9][img]https://i.ibb.co/LPHnDWw/409.png[/img][/url]
[url=https://ibb.co/D9NWzYB][img]https://i.ibb.co/48ctK2b/410.png[/img][/url]
[url=https://ibb.co/r6JCSMq][img]https://i.ibb.co/mq7Lwtd/411.png[/img][/url]
[url=https://ibb.co/PmVBBjH][img]https://i.ibb.co/3rPttdZ/412.png[/img][/url]
[url=https://ibb.co/zmqSQzZ][img]https://i.ibb.co/hg3KLSV/413.png[/img][/url]
[url=https://ibb.co/zfprS06][img]https://i.ibb.co/Yjm3tq0/414.png[/img][/url]
[url=https://ibb.co/Dr6b3Yc][img]https://i.ibb.co/LNqP4rj/415.png[/img][/url]
[url=https://ibb.co/GHDFy48][img]https://i.ibb.co/phTncBM/416.png[/img][/url]
[url=https://ibb.co/HBT0nBr][img]https://i.ibb.co/rF2g4FZ/417.png[/img][/url]
[url=https://ibb.co/zR88NhW][img]https://i.ibb.co/qs00xML/418.png[/img][/url]
[url=https://ibb.co/0jVJ7M5][img]https://i.ibb.co/pvrX7zq/419.png[/img][/url]
[url=https://ibb.co/8D57HXN][img]https://i.ibb.co/LztZ3vY/420.png[/img][/url]
[url=https://ibb.co/GPFt7X8][img]https://i.ibb.co/q1xWBzc/421.png[/img][/url]
[url=https://ibb.co/V23M11C][img]https://i.ibb.co/Lnv9FFg/422.png[/img][/url]
[url=https://ibb.co/CvXHM8D][img]https://i.ibb.co/3W8CMdQ/423.png[/img][/url]
[url=https://ibb.co/QFr3KvN][img]https://i.ibb.co/ccDSrhF/424.png[/img][/url]
[url=https://ibb.co/0ynh3y8][img]https://i.ibb.co/YBNpGBY/425.png[/img][/url]
[url=https://ibb.co/S0mMkrY][img]https://i.ibb.co/jGwQCR0/426.png[/img][/url]
[url=https://ibb.co/yp7V40v][img]https://i.ibb.co/5kw2KTp/427.png[/img][/url]
[url=https://ibb.co/JvBTHnx][img]https://i.ibb.co/tqm6DBZ/428.png[/img][/url]
[url=https://ibb.co/MSxbk68][img]https://i.ibb.co/V9cdYmH/429.png[/img][/url]
[url=https://ibb.co/Mcqz6g2][img]https://i.ibb.co/dPnNgfW/430.png[/img][/url]
[url=https://ibb.co/ZLWnfRK][img]https://i.ibb.co/r74CQKM/431.png[/img][/url]
[url=https://ibb.co/zxM0W2b][img]https://i.ibb.co/KhP3cs7/432.png[/img][/url]
[url=https://ibb.co/qgjSxVR][img]https://i.ibb.co/DMWJLT7/433.png[/img][/url]
[url=https://ibb.co/0sFphJ1][img]https://i.ibb.co/z67WGfC/434.png[/img][/url]
[url=https://ibb.co/YXqVwr2][img]https://i.ibb.co/r31XNWk/435.png[/img][/url]
[url=https://ibb.co/djQ9700][img]https://i.ibb.co/FmBvnbb/436.png[/img][/url]
[url=https://ibb.co/SNwkfds][img]https://i.ibb.co/rk2Bdc7/437.png[/img][/url]
[url=https://ibb.co/xLwH8QL][img]https://i.ibb.co/LRB5hfR/438.png[/img][/url]
[url=https://ibb.co/0BSV9BG][img]https://i.ibb.co/dbqJpb5/439.png[/img][/url]
[url=https://ibb.co/2sBgh28][img]https://i.ibb.co/D8n5WXG/440.png[/img][/url]
[url=https://ibb.co/MNFpNLb][img]https://i.ibb.co/zfqbfw1/441.png[/img][/url]
[url=https://ibb.co/CWMP5MF][img]https://i.ibb.co/GFtHvtj/442.png[/img][/url]
[url=https://ibb.co/Jv1WPFY][img]https://i.ibb.co/7nfxFN3/443.png[/img][/url]
[url=https://ibb.co/fYFS5xm][img]https://i.ibb.co/wNgLXzD/444.png[/img][/url]
[url=https://ibb.co/grTVbyN][img]https://i.ibb.co/kG81VKj/445.png[/img][/url]
[url=https://ibb.co/MgwB00x][img]https://i.ibb.co/Rgrjwwk/446.png[/img][/url]
[url=https://ibb.co/ZMS3wJt][img]https://i.ibb.co/gRdGX7H/447.png[/img][/url]
[url=https://ibb.co/KWF6N83][img]https://i.ibb.co/NKZx1GH/448.png[/img][/url]
[url=https://ibb.co/Z8g2F7c][img]https://i.ibb.co/J7p3Ggr/449.png[/img][/url]
[url=https://ibb.co/BLXgWGX][img]https://i.ibb.co/9nFqKhF/450.png[/img][/url]
[url=https://ibb.co/Lp0T2qc][img]https://i.ibb.co/ZTfQkwF/451.png[/img][/url]
[url=https://ibb.co/k12CM2D][img]https://i.ibb.co/TLM3rM0/452.png[/img][/url]
[url=https://ibb.co/SxVqr3v][img]https://i.ibb.co/dckng5K/453.png[/img][/url]
[url=https://ibb.co/CHZrgvg][img]https://i.ibb.co/d5qhF6F/454.png[/img][/url]
[url=https://ibb.co/tc5yr2F][img]https://i.ibb.co/92jR54S/455.png[/img][/url]
[url=https://ibb.co/yhFh9zK][img]https://i.ibb.co/VHYH1Fb/456.png[/img][/url]
[url=https://ibb.co/D4wL9G3][img]https://i.ibb.co/jh3HyV7/457.png[/img][/url]
[url=https://ibb.co/XFScpKB][img]https://i.ibb.co/1R8FKPV/458.png[/img][/url]
[url=https://ibb.co/dKDL9jg][img]https://i.ibb.co/j4DWKbR/459.png[/img][/url]
[url=https://ibb.co/d4dk0XZ][img]https://i.ibb.co/KxMVjBn/460.png[/img][/url]
[url=https://ibb.co/kMmYDbR][img]https://i.ibb.co/V3wXCn7/461.png[/img][/url]
[url=https://ibb.co/Lv8sxCD][img]https://i.ibb.co/XVbG7zf/462.png[/img][/url]
[url=https://ibb.co/Rc52p7b][img]https://i.ibb.co/FzP6bn3/463.png[/img][/url]
[url=https://ibb.co/HDk5fPn][img]https://i.ibb.co/zh0qT2G/464.png[/img][/url]
[url=https://ibb.co/HP2R0Rn][img]https://i.ibb.co/VCNbdb2/465.png[/img][/url]
[url=https://ibb.co/Sf0G1xH][img]https://i.ibb.co/QDntqch/466.png[/img][/url]
[url=https://ibb.co/zQT3gRJ][img]https://i.ibb.co/DzHBFCp/467.png[/img][/url]
[url=https://ibb.co/nCCVF3k][img]https://i.ibb.co/Dpp6ZGK/468.png[/img][/url]
[url=https://ibb.co/5LbfFbQ][img]https://i.ibb.co/tDVWXV0/469.png[/img][/url]
[url=https://ibb.co/Tvg5mRX][img]https://i.ibb.co/5MRVBvD/470.png[/img][/url]
[url=https://ibb.co/7yN6m5c][img]https://i.ibb.co/q1FPQfG/471.png[/img][/url]
[url=https://ibb.co/f2dMwKs][img]https://i.ibb.co/VtYV4hs/472.png[/img][/url]
[url=https://ibb.co/2kJnQfC][img]https://i.ibb.co/DRdVySv/473.png[/img][/url]
[url=https://ibb.co/h9pgZq1][img]https://i.ibb.co/zxKm7kH/474.png[/img][/url]
[url=https://ibb.co/F7g4mJ0][img]https://i.ibb.co/7y2tjVR/475.png[/img][/url]
[url=https://ibb.co/pJJnjcg][img]https://i.ibb.co/Fggn429/476.png[/img][/url]
[url=https://ibb.co/b38nhMF][img]https://i.ibb.co/qnPwG3C/477.png[/img][/url]
[url=https://ibb.co/CbPss1W][img]https://i.ibb.co/WkVppxs/478.png[/img][/url]
[url=https://ibb.co/8j55sjJ][img]https://i.ibb.co/dQ22MQS/479.png[/img][/url]
[url=https://ibb.co/Zh4HJBz][img]https://i.ibb.co/0f4BXCy/480.png[/img][/url]
[url=https://ibb.co/KhkY1Vy][img]https://i.ibb.co/H4s0JGg/481.png[/img][/url]
[url=https://ibb.co/47PR9k9][img]https://i.ibb.co/rm42T9T/482.png[/img][/url]
[url=https://ibb.co/hMT7dQQ][img]https://i.ibb.co/rtX7p88/483.png[/img][/url]
[url=https://ibb.co/Z8T6Mb6][img]https://i.ibb.co/Fw7bDdb/484.png[/img][/url]
[url=https://ibb.co/Sd7ZDNY][img]https://i.ibb.co/YyTV42n/485.png[/img][/url]
[url=https://ibb.co/PrfR7B7][img]https://i.ibb.co/nw5THhH/486.png[/img][/url]
[url=https://ibb.co/1nCLpZ6][img]https://i.ibb.co/N30skxS/487.png[/img][/url]
[url=https://ibb.co/GWPzKRR][img]https://i.ibb.co/1r2FDTT/488.png[/img][/url]
[url=https://ibb.co/0CSy5ky][img]https://i.ibb.co/X7gxH9x/489.png[/img][/url]
[url=https://ibb.co/wpzGXNj][img]https://i.ibb.co/ygQv1n7/490.png[/img][/url]
[url=https://ibb.co/xHBMBSS][img]https://i.ibb.co/k1whwgg/491.png[/img][/url]
[url=https://ibb.co/w4hYwB9][img]https://i.ibb.co/NK27mt8/492.png[/img][/url]
[url=https://ibb.co/jHqT4Tj][img]https://i.ibb.co/GFG0P0r/493.png[/img][/url]
[url=https://ibb.co/2v4x4rM][img]https://i.ibb.co/jyXmXYw/494.png[/img][/url]
[url=https://ibb.co/kXnKTzL][img]https://i.ibb.co/x6vhbwn/495.png[/img][/url]
[url=https://ibb.co/Q8RbwzX][img]https://i.ibb.co/0BSDb8Q/496.png[/img][/url]
[url=https://ibb.co/Jr1JKVr][img]https://i.ibb.co/MPv0srP/497.png[/img][/url]
[url=https://ibb.co/cvLKYL3][img]https://i.ibb.co/RSyGjyb/498.png[/img][/url]
[url=https://ibb.co/Wc5cYRf][img]https://i.ibb.co/Bg3gSYB/499.png[/img][/url]
[url=https://ibb.co/ZRj94f6][img]https://i.ibb.co/spf7xgv/500.png[/img][/url]
[url=https://ibb.co/FxF7GRS][img]https://i.ibb.co/GxqPgzK/501.png[/img][/url]
[url=https://ibb.co/zVdJ9bF][img]https://i.ibb.co/yF2Sv5p/502.png[/img][/url]
[url=https://ibb.co/0VZ6Fpb][img]https://i.ibb.co/7NVZRxm/503.png[/img][/url]
[url=https://ibb.co/NLYvhFX][img]https://i.ibb.co/9qYDXpJ/504.png[/img][/url]
[url=https://ibb.co/6tWxskY][img]https://i.ibb.co/C9HZ0fB/505.png[/img][/url]
[url=https://ibb.co/kHNsHBM][img]https://i.ibb.co/X2cr2LV/506.png[/img][/url]
[url=https://ibb.co/jwYRzbF][img]https://i.ibb.co/FY1VXmt/507.png[/img][/url]
[url=https://ibb.co/6JLDk3W][img]https://i.ibb.co/n8tQFHL/508.png[/img][/url]
[url=https://ibb.co/Ybx8KJ0][img]https://i.ibb.co/g6xwXQ4/509.png[/img][/url]
[url=https://ibb.co/WyC3qk3][img]https://i.ibb.co/2tJ6mv6/510.png[/img][/url]
[url=https://ibb.co/qW1Hgtc][img]https://i.ibb.co/LJpTgLc/511.png[/img][/url]
[url=https://ibb.co/nzG7qnB][img]https://i.ibb.co/MMvcyGf/512.png[/img][/url]
[url=https://ibb.co/tDLq4bH][img]https://i.ibb.co/sqWK2Fg/513.png[/img][/url]
[url=https://ibb.co/LSxcYHG][img]https://i.ibb.co/xh1BXd4/514.png[/img][/url]
[url=https://ibb.co/hsySDVs][img]https://i.ibb.co/PxNdwgx/515.png[/img][/url]
[url=https://ibb.co/zP8SPNF][img]https://i.ibb.co/vLsJLDh/516.png[/img][/url]
[url=https://ibb.co/CwqfTtW][img]https://i.ibb.co/vcbSKBD/517.png[/img][/url]
[url=https://ibb.co/Ct0jFh1][img]https://i.ibb.co/VNBF82j/518.png[/img][/url]
[url=https://ibb.co/hLmzgnt][img]https://i.ibb.co/wBzmdbx/519.png[/img][/url]
[url=https://ibb.co/0V04wc7][img]https://i.ibb.co/LhTjG8F/520.png[/img][/url]
[url=https://ibb.co/fHjhRXs][img]https://i.ibb.co/0rHgNnx/521.png[/img][/url]
[url=https://ibb.co/WchsMv3][img]https://i.ibb.co/BgpwQ2P/522.png[/img][/url]
[url=https://ibb.co/kqm7YNb][img]https://i.ibb.co/Yf0CvHn/523.png[/img][/url]
[url=https://ibb.co/jwK2Wr9][img]https://i.ibb.co/wQHXwzZ/524.png[/img][/url]
[url=https://ibb.co/F4FCWKc][img]https://i.ibb.co/whfjLR8/525.png[/img][/url]
[url=https://ibb.co/fxZKtX0][img]https://i.ibb.co/nL4Vfwk/526.png[/img][/url]
[url=https://ibb.co/JzWhyDQ][img]https://i.ibb.co/Vv0KQfm/527.png[/img][/url]
[url=https://ibb.co/hKGTMvq][img]https://i.ibb.co/qRH2nwZ/528.png[/img][/url]
[url=https://ibb.co/yf99r4j][img]https://i.ibb.co/7Yffqkm/529.png[/img][/url]
[url=https://ibb.co/X3QV4bd][img]https://i.ibb.co/WPhs36d/530.png[/img][/url]
[url=https://ibb.co/RSwrSvB][img]https://i.ibb.co/QcwScbC/531.png[/img][/url]
[url=https://ibb.co/TYX3Km2][img]https://i.ibb.co/HBv8Nn4/532.png[/img][/url]
[url=https://ibb.co/y0b6NkY][img]https://i.ibb.co/WnYkHzP/533.png[/img][/url]
[url=https://ibb.co/fMwyQGh][img]https://i.ibb.co/NxBJ7n8/534.png[/img][/url]
[url=https://ibb.co/Brd8JrX][img]https://i.ibb.co/YyYvSyz/535.png[/img][/url]
[url=https://ibb.co/MsM2B6s][img]https://i.ibb.co/6mgnXBm/536.png[/img][/url]
[url=https://ibb.co/P67063h][img]https://i.ibb.co/mcLgc1q/537.png[/img][/url]
[url=https://ibb.co/n1PpYMc][img]https://i.ibb.co/FYHpy4w/538.png[/img][/url]
[url=https://ibb.co/tbgdH22][img]https://i.ibb.co/55m71jj/539.png[/img][/url]
[url=https://ibb.co/NmDKFn7][img]https://i.ibb.co/ZY4xf1N/540.png[/img][/url]
[url=https://ibb.co/HnVLCBj][img]https://i.ibb.co/3B75v4n/541.png[/img][/url]
[url=https://ibb.co/gRtdsh9][img]https://i.ibb.co/3CSvtQd/542.png[/img][/url]
[url=https://ibb.co/HXDkZjx][img]https://i.ibb.co/3kyLKnM/543.png[/img][/url]
[url=https://ibb.co/gwHZKyq][img]https://i.ibb.co/Y8YBs2n/544.png[/img][/url]
[url=https://ibb.co/gTjVfJB][img]https://i.ibb.co/R0vyscV/545.png[/img][/url]
[url=https://ibb.co/0FhD5K5][img]https://i.ibb.co/NmZVRrR/546.png[/img][/url]
[url=https://ibb.co/WDmQ6Cb][img]https://i.ibb.co/9wQJNPF/547.png[/img][/url]
[url=https://ibb.co/vX1md7C][img]https://i.ibb.co/wcyCQ9Z/548.png[/img][/url]
[url=https://ibb.co/0h22z5C][img]https://i.ibb.co/J5ttSZv/549.png[/img][/url]
[url=https://ibb.co/kJW7kRd][img]https://i.ibb.co/KD3PRM1/550.png[/img][/url]
[url=https://ibb.co/gF4dG0N][img]https://i.ibb.co/wrc7TnV/551.png[/img][/url]
[url=https://ibb.co/sPSj3Cn][img]https://i.ibb.co/qnGB1CK/552.png[/img][/url]
[url=https://ibb.co/JzCVZkC][img]https://i.ibb.co/8jXqk8X/553.png[/img][/url]
[url=https://ibb.co/NCn7W1b][img]https://i.ibb.co/8s4XPzt/554.png[/img][/url]
[url=https://ibb.co/K6BJZC7][img]https://i.ibb.co/kKztnY0/555.png[/img][/url]
[url=https://ibb.co/BT6TCvW][img]https://i.ibb.co/KVsVrB4/556.png[/img][/url]
[url=https://ibb.co/vXY9ZrM][img]https://i.ibb.co/mN8p6YP/557.png[/img][/url]
[url=https://ibb.co/48ntGW2][img]https://i.ibb.co/7ndC5vQ/558.png[/img][/url]
[url=https://ibb.co/20zqvBr][img]https://i.ibb.co/j9ChyFY/559.png[/img][/url]
[url=https://ibb.co/T4ft9DN][img]https://i.ibb.co/2v9dG0p/560.png[/img][/url]
[url=https://ibb.co/XW0bHw1][img]https://i.ibb.co/kGbxZdj/561.png[/img][/url]
[url=https://ibb.co/X39PBvW][img]https://i.ibb.co/612Shfy/562.png[/img][/url]
[url=https://ibb.co/YBJrWXx][img]https://i.ibb.co/1GBSnMk/563.png[/img][/url]
[url=https://ibb.co/PDRchsY][img]https://i.ibb.co/y4D6ymR/564.png[/img][/url]
[url=https://ibb.co/ZBx01KF][img]https://i.ibb.co/QPM4jnT/565.png[/img][/url]
[url=https://ibb.co/NLrFfdF][img]https://i.ibb.co/zSFmCTm/566.png[/img][/url]
[url=https://ibb.co/Q8M4Y0b][img]https://i.ibb.co/TKtsPyv/567.png[/img][/url]
[url=https://ibb.co/N1GbK5p][img]https://i.ibb.co/DGjTQhk/568.png[/img][/url]
[url=https://ibb.co/7gfpkG5][img]https://i.ibb.co/cbB8YNH/569.png[/img][/url]
[url=https://ibb.co/RN4XJxD][img]https://i.ibb.co/3vYxPDC/570.png[/img][/url]
[url=https://ibb.co/L69PhpT][img]https://i.ibb.co/VDMNpBF/571.png[/img][/url]
[url=https://ibb.co/qFV2pJx][img]https://i.ibb.co/0VvzrsQ/572.png[/img][/url]
[url=https://ibb.co/NLtMgD8][img]https://i.ibb.co/8jNHnvW/573.png[/img][/url]
[url=https://ibb.co/BgxBmn6][img]https://i.ibb.co/zSYZ162/574.png[/img][/url]
[url=https://ibb.co/ZYSMRmT][img]https://i.ibb.co/dLt5sgK/575.png[/img][/url]
[url=https://ibb.co/DYpr2LD][img]https://i.ibb.co/5kFKH2W/576.png[/img][/url]
[url=https://ibb.co/Wp22wnG][img]https://i.ibb.co/5xRRyTG/577.png[/img][/url]
[url=https://ibb.co/PNHSR54][img]https://i.ibb.co/W6JTQcF/578.png[/img][/url]
[url=https://ibb.co/f1ybRYg][img]https://i.ibb.co/kHwpng7/579.png[/img][/url]
[url=https://ibb.co/D4tJmZd][img]https://i.ibb.co/K6XPBJn/580.png[/img][/url]
[url=https://ibb.co/2K3sfgn][img]https://i.ibb.co/NY2mHZV/581.png[/img][/url]
[url=https://ibb.co/WHQrnSM][img]https://i.ibb.co/vcbN12T/582.png[/img][/url]
[url=https://ibb.co/TPZrVcV][img]https://i.ibb.co/MPb9YnY/583.png[/img][/url]
[url=https://ibb.co/0VjRMpM][img]https://i.ibb.co/4gZnTwT/584.png[/img][/url]
[url=https://ibb.co/dDPnLzx][img]https://i.ibb.co/4p8BY53/585.png[/img][/url]
[url=https://ibb.co/jLDcn91][img]https://i.ibb.co/vJk70CK/586.png[/img][/url]
[url=https://ibb.co/cwYvjdp][img]https://i.ibb.co/QkDc4Gq/587.png[/img][/url]
[url=https://ibb.co/vjB5w6x][img]https://i.ibb.co/QKcBb3F/588.png[/img][/url]
[url=https://ibb.co/qpCrZ7c][img]https://i.ibb.co/HqCHJBb/589.png[/img][/url]
[url=https://ibb.co/stbJWSb][img]https://i.ibb.co/XVjkYBj/590.png[/img][/url]
[url=https://ibb.co/NL39T8d][img]https://i.ibb.co/CntbPk3/591.png[/img][/url]
[url=https://ibb.co/2tw8cJZ][img]https://i.ibb.co/r6gb59d/592.png[/img][/url]
[url=https://ibb.co/mhz4PLb][img]https://i.ibb.co/c2TQsGk/593.png[/img][/url]
[url=https://ibb.co/L9VS892][img]https://i.ibb.co/HG57VGk/594.png[/img][/url]
[url=https://ibb.co/PQcGRKR][img]https://i.ibb.co/gVSZGNG/595.png[/img][/url]
[url=https://ibb.co/TRwksk0][img]https://i.ibb.co/WFH6L6z/596.png[/img][/url]
[url=https://ibb.co/0mXNWtn][img]https://i.ibb.co/mbBsY8R/597.png[/img][/url]
[url=https://ibb.co/xS8v54D][img]https://i.ibb.co/KjzZy1X/598.png[/img][/url]
[url=https://ibb.co/HKBJ3PR][img]https://i.ibb.co/51G7wjC/599.png[/img][/url]
[url=https://ibb.co/ZgcYFbd][img]https://i.ibb.co/myhX2PJ/600.png[/img][/url]
[url=https://ibb.co/X59yg48][img]https://i.ibb.co/vdbsGBY/601.png[/img][/url]
[url=https://ibb.co/nBBjt8Q][img]https://i.ibb.co/DYYQTgw/602.png[/img][/url]
[url=https://ibb.co/18xLMFQ][img]https://i.ibb.co/3BH7vgd/603.png[/img][/url]
[url=https://ibb.co/hyfCthh][img]https://i.ibb.co/0ctQd88/604.png[/img][/url]
[url=https://ibb.co/Xjhh2JF][img]https://i.ibb.co/vV77wzL/605.png[/img][/url]
[url=https://ibb.co/D4QDMnb][img]https://i.ibb.co/nrjs1S0/606.png[/img][/url]
[url=https://ibb.co/Wz6JyHF][img]https://i.ibb.co/z2rvRmb/607.png[/img][/url]
[url=https://ibb.co/XJ9Rmtv][img]https://i.ibb.co/NYXBwKH/608.png[/img][/url]
[url=https://ibb.co/80XpMtJ][img]https://i.ibb.co/37kq1Qw/609.png[/img][/url]
[url=https://ibb.co/9WBkZFm][img]https://i.ibb.co/vkf6X7C/610.png[/img][/url]
[url=https://ibb.co/bb1wVH9][img]https://i.ibb.co/nPrdy3J/611.png[/img][/url]
[url=https://ibb.co/zPgbjrv][img]https://i.ibb.co/DwFkst2/612.png[/img][/url]
[url=https://ibb.co/nbTy7Sx][img]https://i.ibb.co/ZV3rBCq/613.png[/img][/url]
[url=https://ibb.co/vPcf2MZ][img]https://i.ibb.co/Z8fvybW/614.png[/img][/url]
[url=https://ibb.co/1ZBC2mq][img]https://i.ibb.co/H7RcgHz/615.png[/img][/url]
[url=https://ibb.co/3Bvdrg9][img]https://i.ibb.co/m60TDfV/616.png[/img][/url]
[url=https://ibb.co/HhrpwTG][img]https://i.ibb.co/vXJvy4L/617.png[/img][/url]
[url=https://ibb.co/2kKhVQ7][img]https://i.ibb.co/ZMTX4P6/618.png[/img][/url]
[url=https://ibb.co/JWYqNvP][img]https://i.ibb.co/5XQkdrV/619.png[/img][/url]
[url=https://ibb.co/F66MHKH][img]https://i.ibb.co/jhh2JTJ/620.png[/img][/url]
[url=https://ibb.co/kG8fkcH][img]https://i.ibb.co/3TNqGhr/621.png[/img][/url]
[url=https://ibb.co/j80BfbG][img]https://i.ibb.co/tHjkKQc/622.png[/img][/url]
[url=https://ibb.co/vh4rSq7][img]https://i.ibb.co/5khzP4N/623.png[/img][/url]
[url=https://ibb.co/pL5MjXx][img]https://i.ibb.co/wzjPh6R/624.png[/img][/url]
[url=https://ibb.co/z4K13Qk][img]https://i.ibb.co/9rRJxcM/625.png[/img][/url]
[url=https://ibb.co/1rTghPH][img]https://i.ibb.co/y6q9GZL/626.png[/img][/url]
[url=https://ibb.co/wgKZ21x][img]https://i.ibb.co/F3Bkdtj/627.png[/img][/url]
[url=https://ibb.co/M22L3zc][img]https://i.ibb.co/p00p9Hf/628.png[/img][/url]
[url=https://ibb.co/s5f20fn][img]https://i.ibb.co/RhF9xFf/629.png[/img][/url]
[url=https://ibb.co/QrKY3Xw][img]https://i.ibb.co/Wg2B4sJ/630.png[/img][/url]
[url=https://ibb.co/ft8hs9r][img]https://i.ibb.co/GksKq9C/631.png[/img][/url]
[url=https://ibb.co/dDbsbF6][img]https://i.ibb.co/BB4H4bj/632.png[/img][/url]
[url=https://ibb.co/N9Dftxd][img]https://i.ibb.co/wSG8ByF/633.png[/img][/url]
[url=https://ibb.co/09986MD][img]https://i.ibb.co/C99NY71/634.png[/img][/url]
[url=https://ibb.co/GcvFk38][img]https://i.ibb.co/xJS3G8B/635.png[/img][/url]
[url=https://ibb.co/CtbdDNJ][img]https://i.ibb.co/pPfD5GW/636.png[/img][/url]
[url=https://ibb.co/84Lv81h][img]https://i.ibb.co/cXSfT4m/637.png[/img][/url]
[url=https://ibb.co/ZNBGs1S][img]https://i.ibb.co/g6Sm1Fd/638.png[/img][/url]
[url=https://ibb.co/FmhZvMG][img]https://i.ibb.co/VJLnyZX/639.png[/img][/url]
[url=https://ibb.co/30CNKtj][img]https://i.ibb.co/55R8ZqS/640.png[/img][/url]
[url=https://ibb.co/1sZJCt4][img]https://i.ibb.co/bH1R4MG/641.png[/img][/url]
[url=https://ibb.co/4tHH2Bc][img]https://i.ibb.co/PjddMBR/642.png[/img][/url]
[url=https://ibb.co/9pNpM2Y][img]https://i.ibb.co/j8T8pG4/643.png[/img][/url]
[url=https://ibb.co/6sZFhtP][img]https://i.ibb.co/NY3KhNj/644.png[/img][/url]
[url=https://ibb.co/KVYrD3S][img]https://i.ibb.co/sshVCMz/645.png[/img][/url]
[url=https://ibb.co/XS6YNjZ][img]https://i.ibb.co/2gRZmW7/646.png[/img][/url]
[url=https://ibb.co/9tq9TC9][img]https://i.ibb.co/VmvWSPW/647.png[/img][/url]
[url=https://ibb.co/ZJypvqL][img]https://i.ibb.co/0XPR1HD/648.png[/img][/url]
[url=https://ibb.co/7n4p9x2][img]https://i.ibb.co/bsJvfjz/649.png[/img][/url]
[url=https://ibb.co/p20gpW7][img]https://i.ibb.co/JnBNPx1/650.png[/img][/url]
[url=https://ibb.co/R6fSJ9B][img]https://i.ibb.co/kDjyPx9/651.png[/img][/url]
[url=https://ibb.co/wRhjgFz][img]https://i.ibb.co/9NHSgkr/652.png[/img][/url]
[url=https://ibb.co/4JKmxjW][img]https://i.ibb.co/SJ5spKN/653.png[/img][/url]
[url=https://ibb.co/swtbfmS][img]https://i.ibb.co/7WbjfYc/654.png[/img][/url]
[url=https://ibb.co/kg2kbWT][img]https://i.ibb.co/273mVfr/655.png[/img][/url]
[url=https://ibb.co/R2YN2m6][img]https://i.ibb.co/CBm6BZ9/656.png[/img][/url]
[url=https://ibb.co/6YL7hpG][img]https://i.ibb.co/2qH12LR/657.png[/img][/url]
[url=https://ibb.co/Kx0J6Qm][img]https://i.ibb.co/RTvq2M7/658.png[/img][/url]
[url=https://ibb.co/NyxcFmd][img]https://i.ibb.co/wzy5dwF/659.png[/img][/url]
[url=https://ibb.co/1zNxHWn][img]https://i.ibb.co/tL65yrh/660.png[/img][/url]
[url=https://ibb.co/59HD5Yx][img]https://i.ibb.co/X4RBzyk/661.png[/img][/url]
[url=https://ibb.co/bsfDffn][img]https://i.ibb.co/2vbHbbB/662.png[/img][/url]
[url=https://ibb.co/J79hyFr][img]https://i.ibb.co/zRzk7HP/663.png[/img][/url]
[url=https://ibb.co/dbRJh66][img]https://i.ibb.co/TKsqCRR/664.png[/img][/url]
[url=https://ibb.co/BjKfYz4][img]https://i.ibb.co/sQJgXm5/665.png[/img][/url]
[url=https://ibb.co/LhkQ3XB][img]https://i.ibb.co/7NYgqdB/666.png[/img][/url]
[url=https://ibb.co/sQn2CY9][img]https://i.ibb.co/1K1LMWG/667.png[/img][/url]
[url=https://ibb.co/MGs6BbK][img]https://i.ibb.co/ZYVm23v/668.png[/img][/url]
[url=https://ibb.co/qkVS3K4][img]https://i.ibb.co/FgCrL2f/669.png[/img][/url]
[url=https://ibb.co/2gQV4j9][img]https://i.ibb.co/hDjQzK6/670.png[/img][/url]
[url=https://ibb.co/jZ2mzXH][img]https://i.ibb.co/M54rf09/671.png[/img][/url]
[url=https://ibb.co/Hz13fhX][img]https://i.ibb.co/G2BN4HF/672.png[/img][/url]
[url=https://ibb.co/h2sGmY6][img]https://i.ibb.co/kqKLSm7/673.png[/img][/url]
[url=https://ibb.co/8PdWXkK][img]https://i.ibb.co/L9JLvKk/674.png[/img][/url]
[url=https://ibb.co/bF2MD2K][img]https://i.ibb.co/nBnNtnL/675.png[/img][/url]
[url=https://ibb.co/J2xJsfs][img]https://i.ibb.co/pZWFLtL/676.png[/img][/url]
[url=https://ibb.co/QMfd0qr][img]https://i.ibb.co/FzKVpfg/677.png[/img][/url]
[url=https://ibb.co/sRscQYG][img]https://i.ibb.co/3dSVWZq/678.png[/img][/url]
[url=https://ibb.co/pXv0bzx][img]https://i.ibb.co/88DKN50/679.png[/img][/url]
[url=https://ibb.co/X5NMsds][img]https://i.ibb.co/DMsTC6C/680.png[/img][/url]
[url=https://ibb.co/TMHY0Cx][img]https://i.ibb.co/hFKLdqJ/681.png[/img][/url]
[url=https://ibb.co/g7jzyyL][img]https://i.ibb.co/BPzqLL5/682.png[/img][/url]
[url=https://ibb.co/P4cWKh8][img]https://i.ibb.co/4M8SzTx/683.png[/img][/url]
[url=https://ibb.co/5R3Hkx4][img]https://i.ibb.co/1mNWMJQ/684.png[/img][/url]
[url=https://ibb.co/2n137CL][img]https://i.ibb.co/7YdtJZT/685.png[/img][/url]
[url=https://ibb.co/5Wgq5mH][img]https://i.ibb.co/KjpC9dv/686.png[/img][/url]
[url=https://ibb.co/X5HcNfS][img]https://i.ibb.co/94PQzms/687.png[/img][/url]
[url=https://ibb.co/JQCQjcM][img]https://i.ibb.co/SrJrw69/688.png[/img][/url]
[url=https://ibb.co/S5B3j4N][img]https://i.ibb.co/pbdL7B2/689.png[/img][/url]
[url=https://ibb.co/rvn9zc1][img]https://i.ibb.co/Bw8kQrS/690.png[/img][/url]
[url=https://ibb.co/kXY3WjS][img]https://i.ibb.co/M7q83rC/691.png[/img][/url]
[url=https://ibb.co/F3R0Hyk][img]https://i.ibb.co/dM8LmVs/692.png[/img][/url]
[url=https://ibb.co/xCbbBkv][img]https://i.ibb.co/X2PPKQB/693.png[/img][/url]
[url=https://ibb.co/d5JrQmg][img]https://i.ibb.co/z4HrS6J/694.png[/img][/url]
[url=https://ibb.co/PY0n8cD][img]https://i.ibb.co/9vSLjbZ/695.png[/img][/url]
[url=https://ibb.co/W67G19L][img]https://i.ibb.co/bPYQnhk/696.png[/img][/url]
[url=https://ibb.co/yBTM37j][img]https://i.ibb.co/n82VWtJ/697.png[/img][/url]
[url=https://ibb.co/QJkxkqg][img]https://i.ibb.co/MgfJfjv/698.png[/img][/url]
[url=https://ibb.co/pWpgqdq][img]https://i.ibb.co/TK5Zyty/699.png[/img][/url]"""

def set_img():
    import re
    strings = data.split('\n')
    connection = start_connection()
    for en, i in enumerate(strings, 401):
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
