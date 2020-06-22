
from util.database import execute_sql_command
from util.classes import BotInstance, bot
import markups
import meta

# bot = BotInstance(token=meta.bot_token)


def sql_command(message):
    msg = bot.send_message(message.chat.id, text="BEFEHLEINGABE:\n'0' um zu beenden\n'hints' für Befehle")
    bot.register_next_step_handler(msg, process_command)


def process_command(message):
    if message.text == "0":
        bot.send_message(message.chat.id, text="Command Eingabe beendet.", reply_markup=markups.menu.master())
        return
    elif message.text == "hints":
        bot.send_message(message.chat.id, text=meta.sql_command_hints)
    else:
        success, res = execute_sql_command(message.text)
        if success:
            if res:
                text = res
            else:
                text = "<NO RETURN VALUE>"
            bot.reply_to(message, text=text)
        else:
            bot.reply_to(message, text="ERROR: " + res)

    sql_command(message)
