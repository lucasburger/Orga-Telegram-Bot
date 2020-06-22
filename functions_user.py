
from util.database import *
import meta
from util.classes import BotInstance, bot
from util.functions import try_function

# bot = BotInstance(token=meta.bot_token)


@try_function
def show_help(message):
    if is_master(user_id=message.from_user.id):
        text = meta.help_message_master
    elif is_admin(user_id=message.from_user.id):
        text = meta.help_message_admin
    else:
        text = meta.help_message_user

    help_file = open(meta.help_pdf_filename, 'rb')
    bot.send_document(chat_id=message.chat.id, data=help_file, caption=text)
    help_file.close()


@try_function
def show_users(message, reply=True):
    frichtle = get_frichtle()
    if not isinstance(frichtle, list):
        frichtle = [frichtle]
    s = ""
    for f in frichtle:
        s += f.get_inline_str()
        if f.master:
            s += " (Master)"
        elif f.admin:
            s += " (Admin)"
        s += "\n"
    if reply:
        bot.reply_to(message, s)
    else:
        bot.send_message(message.chat.id, text=s)


@try_function
def show_instrument(message):
    instrument = get_instrument(message.from_user.id)
    if instrument == 'Passiv':
        text = 'Du bist passives Mitglied.'
    else:
        text = 'Du spielst {}'.format(instrument)
    bot.reply_to(message, text)
