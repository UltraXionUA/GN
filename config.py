#!/home/UltraXionUA/.virtualenvs/myvirtualenv/bin/python3.8

# -*- coding: utf-8 -*-
"""Configuration file for GNBot"""
import pymysql.cursors
from telebot import TeleBot

#ssh ultraxion@94.103.89.221

#sudo mysql -u root -p Bot_DB -h localhost

#source /home/ultraxion/GNBot/GN/.venv/bin/activate
#sudo systemctl start tgbot
#sudo systemctl enable tgbot
#sudo systemctl stopcat ~/.ssh/id_rsa.pub tgbot


TOKEN = '1077848786:AAHfMrRKadc3Plo14rpE7dPJJC3bVbbVod0'  # Release bot TOKEN
TEST_TOKEN = '839168325:AAGtBUzQoqdPSSHPWUeo4K9Onxxnclv96sA'  # Test bot TOKEN

bot = TeleBot(TOKEN)

PAYMENT_TOKEN = '635983722:LIVE:i7814191795'

GN_ID = '-1001339129150'
GNBot_ID = '1077848786'
Admin_ID = '698667021'

# API
API = {'API_Weather': 'https://' + 'api.weatherbit.io/v2.0/forecast/daily?'
                       'city=CityName&lang=ru&units=M&days=16&key=71e00e889c4045a2b1f09cd4ccad1102',
       'API_Gif': 'https://' + 'api.giphy.com/v1/gifs/random?api_key=mHVzi8lTLfPjh2qIAoXcN8P8QLeVRlvh&' \
                               'tag=weapons, cars, girls, funny, cats, sex, drugs, programming, anime, hentai' \
                               'guns, gaming, science, memes'
                               '&rating=R',
       'API_Meme': 'https://' + 'meme-api.herokuapp.com/gimme',
       'API_Deezer': 'https://' + 'api.deezer.com/search/',
       'AUDD_data': {'url': 'None',
                     'return': 'deezer',
                     'api_token': 'e80cb21e8b4bc33ca36f4a1db75708ed'
                     },
       'AUDD': 'https://' + 'api.audd.io/',
       'PasteBin': {'URL': 'http://' + 'pastebin.com/api/api_post.php',
                    'DevApi': '2d13a3dcd3657d8d7a64d3ea12dfbaf5',
                    'UserApi': 'eaaf7366142b140c579a72a63b1a1d9c'
                    },
       'News': {'Api_Key': '891aeb67feff4c8c96156b04f541d0e0',
                'URL': 'http://' + 'newsapi.org/v2/top-headlines?category=Method&country=ru&pageSize=100&apiKey=',
                'image': 'https://' + 'st.depositphotos.com/1152339/1972/i/450/depositphotos_19723583-stock-photo-news-concept-news-on-digital.jpg'},
       'QRCode': {'Create': 'https://' + 'api.qrserver.com/v1/create-qr-code/?data=DATA&'
                                         'size=1000x1000&bgcolor=f00&margin=30&qzone=2&format=jpeg',
                  'Read': 'https://' + 'api.qrserver.com/v1/read-qr-code/?fileurl=FILE&outputformat=json'}
       }

URLS = {'logo': 'https://' + 'i.redd.it/6mfq9bv5u5n31.png',
        'memes': ['https://' + 'www.reddit.com/r/Pikabu/search?q=flair%3AМем&restrict_sr=1&sort=new'],
        'torrent': {'search': 'http://' + 'gtorrent.ru/?do=search&subaction=search&story=',
                    'download': 'https://' + 'gtorrent.ru/engine/download.php?id=',
                    'main': 'http://' + 'gtorrent.ru',
                    'name': 'GTorrent.ru'},
        'torrent2': {'search': 'https://' + 'gamestracker.org/search/?q=TEXT&t=1',
                     'main': 'https://' + 'gamestracker.org',
                     'name': 'Gamestracker.org'},
        'torrent3':  {'search': 'http://' + 'rutor.info/search/',
                      'download': 'http://' + 'd.rutor.info/download/',
                      'main': 'http://' + 'rutor.info',
                      'name': 'Rutor.info'},
        'loli': {'main': 'https://' + 'gazo-kore.com',
                 'search': 'https://' + 'gazo-kore.com/images/search?type=4&id=66&page='}

        }


# BD_CONNECT = {'unix_socket': '/Applications/MAMP/tmp/mysql/mysql.sock',  # Local DB
#               'user': 'root',
#               'password': 'root',
#               'db': 'Bot_DB',
#               'charset': 'utf8mb4',
#               'cursorclass': pymysql.cursors.DictCursor
#               }

BD_CONNECT = {'user': 'root',  # host
              'password': '25813123321',
              'host': 'localhost',
              'db': 'Bot_DB',
              'charset': 'utf8mb4',
              'cursorclass': pymysql.cursors.DictCursor
              }

# BD_CONNECT = {'user': 'UltraXionUA',  # Python Anywhere DB
#               'password': 'DB25813123321',
#               'host': 'UltraXionUA.mysql.pythonanywhere-services.com',
#               'database': 'UltraXionUA$test',
#               'cursorclass': pymysql.cursors.DictCursor
#               }

# https://api.telegram.org/bot1077848786:AAHfMrRKadc3Plo14rpE7dPJJC3bVbbVod0/sendMessage  # To add autoposting
# {"chat_id":"-1001339129150","text":" {{Url}}"}



