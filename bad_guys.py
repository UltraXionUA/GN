#!/home/ultraxion/GNBot/GN/.venv/bin/activate
#!/usr/bin/ python3.8
# -*- coding: utf-8 -*-
"""Parser file for GNBot"""
from Config_GNBot.config import bot
from funcs import log
import db


# <<< Bag guys >>
def send_bad_guy() -> None:
    """
    .. notes:: Select most active users un group
    :return: None
    """
    log('Send bad guy is done', 'info')
    for chat_id, users in db.get_bad_guy().items():
        text = '🎉<b>Пидор' + f"{'ы' if len(users) > 1 else ''}" + ' дня</b>🎉\n' + ''.join(f"🎊💙<i>{db.get_from(user['id'], 'Users_name')}</i>💙🎊\n" for user in users) + f'Прийми{"те" if len(users) > 1 else ""} наши поздравления👍'
        try:
            msg = bot.send_message(chat_id, text, parse_mode='HTML')
            bot.pin_chat_message(msg.chat.id, msg.message_id, disable_notification=True)
            db.set_pin_bad_gays(chat_id)
        except Exception:
            log('Error in bad guy', 'error')
    db.reset_users()


def unpin_bag_guys() -> None:
    for chat_id in db.get_pin_bad_gays():
        try:
            bot.unpin_chat_message(chat_id.decode('utf-8'))
        except Exception:
            log('Can\'t unpin bad_guy message', 'warning')
# <<< End bag guys >>