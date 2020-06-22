
import logging
import os
import json
from datetime import datetime as dt
from util.classes import BotInstance, PWManager, bot, Frichtle
import time
import util
import next_step_callback
import next_step_message
import functions_master
import functions_user
import welcome_procedure
import markups
import meta
import cmd
from telebot import logger, formatter
from telebot.apihelper import send_message
import traceback
import requests

logger.setLevel(logging.DEBUG)

log_info = os.path.join("Logs", "Log_Info.log")
log_debug = os.path.join("Logs", "Log_Debug.log")

info_handler = logging.FileHandler(filename=log_info)
info_handler.setFormatter(formatter)
info_handler.setLevel(logging.INFO)
logger.addHandler(info_handler)

debug_handler = logging.FileHandler(filename=log_debug)
debug_handler.setFormatter(formatter)
debug_handler.setLevel(logging.DEBUG)
logger.addHandler(debug_handler)

logger.removeHandler(logger.handlers[0])
logger.info("=====================================================================")
logger.info("================Restart {}===================".format(dt.now()))
logger.info("=====================================================================")

pw_manager = PWManager()


@bot.message_handler(commands=['start', 'Start'])
def f001(message):
    welcome_procedure.welcome_user(message)


@bot.message_handler(func=cmd.user.help)
def f002(message): functions_user.show_help(message)


@bot.message_handler(func=cmd.user.event)
def f003(message): next_step_callback.show_event.show_event(initial_message=message)


@bot.message_handler(func=cmd.user.surveys)
def f004(message): next_step_callback.show_survey.show_survey(initial_message=message)


@bot.message_handler(func=cmd.user.frichtle)
def f005(message): functions_user.show_users(message)


@bot.message_handler(func=cmd.user.main_menu)
def f006(message): util.functions.goto_main_menu(message)


# Admin Functions ##############


@bot.message_handler(func=cmd.admin.admin_menu)
def f007(message): bot.send_message(message.chat.id, text=message.text, reply_markup=markups.menu.admin())


@bot.message_handler(func=cmd.admin.new_event)
def f008(message): next_step_message.new_event.new_event(initial_message=message)


@bot.message_handler(func=cmd.admin.manage_events)
def f009(message): bot.send_message(message.chat.id, text=message.text, reply_markup=markups.menu.manage_events())


@bot.message_handler(func=cmd.admin.edit_event)
def f010(message): next_step_callback.edit_event.edit_event(initial_message=message)


@bot.message_handler(func=cmd.admin.event_summary)
def f011(message): next_step_callback.event_summary.event_summary(initial_message=message)


@bot.message_handler(func=cmd.admin.cancel_event)
def f012(message): next_step_callback.cancel_event.cancel_event(initial_message=message)


@bot.message_handler(func=cmd.admin.send_reminder)
def f013(message): next_step_callback.send_reminder.send_reminder(initial_message=message)


@bot.message_handler(func=cmd.admin.manage_surveys)
def f014(message): bot.send_message(message.chat.id, text=message.text, reply_markup=markups.menu.manage_surveys())


@bot.message_handler(func=cmd.admin.new_survey)
def f015(message): next_step_message.new_survey.new_survey(initial_message=message)


@bot.message_handler(func=cmd.admin.survey_summary)
def f016(message): next_step_callback.survey_summary.survey_summary(initial_message=message)


# Master Functions ##############


@bot.message_handler(func=cmd.master.show_table)
def f017(message): next_step_callback.show_table.show_table(initial_message=message)


@bot.message_handler(func=cmd.master.sql_command)
def f018(message): next_step_message.sql_command.sql_command(message)


@bot.message_handler(func=cmd.master.remove_event)
def f019(message): functions_master.remove_which_event(message)


@bot.message_handler(func=cmd.master.remove_survey)
def f020(message): functions_master.remove_which_survey(message)


@bot.message_handler(func=cmd.master.new_admin)
def f021(message): functions_master.appoint_admin_command(message)


@bot.message_handler(func=cmd.master.remove_admin)
def f022(message): functions_master.remove_admin_command(message)


@bot.message_handler(func=cmd.master.remove_user)
def f023(message): functions_master.remove_user_command(message)


@bot.message_handler(func=cmd.master.master_menu)
def f024(message): util.functions.goto_master_menu(message)


@bot.message_handler(func=cmd.master.manage_members_menu)
def f025(message): bot.send_message(message.chat.id, text=message.text, reply_markup=markups.menu.manage_members())


@bot.message_handler(func=cmd.master.new_invite_link)
def f026(message): bot.reply_to(message, text=meta.invite_link_base + pw_manager.generate())


@bot.message_handler(func=lambda m: (m.text[:4] == "exec" and m.from_user.id == meta.lucas_user_id))
def f040(message):
    t = message.text

    t = t.replace("exec", "").strip()
    try:
        for table in ["frichtle", "events", "surveys"]:
            if t[:len(table)] == table:
                file_name = f"vault/{table}.json"

                with open(file_name, "r") as f:
                    exec(f"{table} = json.load(f)")

                exec(t.replace(",", "\""))

                with open(file_name, "w") as f:
                    exec(f"json.dump({table}, f, indent=4)")

                bot.reply_to(message, text="Successful.")

                break
        else:
            exec(t)

    except Exception as e:
        bot.reply_to(message, text=str(e))


# try:
#     exec(message.text)
#     print(locals())
# except Exception as e:
#     print(e)


# Callback Handlers #############


# @bot.callback_query_handler(func=cmd.callback.survey_summary_back)
# def f027(call): next_step_callback.survey_summary.start_survey_summary(bot_message=call.message)


# @bot.callback_query_handler(func=cmd.callback.summary_which_survey)
# def f028(call): next_step_callback.survey_summary.summary_which_survey(call)


@bot.callback_query_handler(func=cmd.callback.appoint_admin)
def f029(call): functions_master.process_admin_appoint(call)


@bot.callback_query_handler(func=cmd.callback.remove_admin)
def f030(call): functions_master.process_admin_remove(call)


@bot.callback_query_handler(func=cmd.callback.remove_user)
def f031(call): functions_master.process_user_remove(call)


@bot.callback_query_handler(func=cmd.callback.remove_which_event)
def f032(call): functions_master.remove_event_sure(call)


@bot.callback_query_handler(func=cmd.callback.remove_event)
def f033(call): functions_master.remove_event(call)


@bot.callback_query_handler(func=cmd.callback.remove_which_survey)
def f034(call): functions_master.remove_survey_sure(call)


@bot.callback_query_handler(func=cmd.callback.remove_survey)
def f035(call): functions_master.remove_survey(call)


def abort_action(call):
    bot.edit_message_text(call=call, text="Okay, die Aktion wurde abgebrochen.")


def end_action(call):
    bot.edit_message_text(call=call, text="Okay, beendet.")


@bot.callback_query_handler(func=cmd.callback.command)
def f036(call):
    command = call.data.split(";")[0]
    if command == 'abort':
        abort_action(call)
        return
    elif command == 'end':
        end_action(call)
        return
    func = util.classes.callback_commands[command]
    func(call=call)
    return


def main():
    logger.info("Bot started.")
    try:
        bot.polling(none_stop=True)
    finally:
        logger.info("Bot stopped.")


if __name__ == '__main__':

    try:
        main()
        print('Bot finished.')
    except KeyboardInterrupt:
        quit()
    except Exception as e:
        content = "The FrichtleOrganiser Bot crashed.\n\nError:\n\n{}".format(traceback.format_exc())
        send_message(token=meta.bot_token, chat_id=meta.lucas_chat_id, text=content)
