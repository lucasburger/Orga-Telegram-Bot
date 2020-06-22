
from util.database import *
import meta
from util.classes import BotInstance, bot
from util.functions import try_function
import util
import markups
# bot = BotInstance(token=meta.bot_token)
instruments = meta.instruments

STORE = {}


@try_function
def show_which_table(message):
    bot.reply_to(message, text="Wähle Tabelle:", reply_markup=markups.inline.show_which_table(get_all_tables()))


@try_function
def appoint_admin_command(message):
    frichtle = get_frichtle()
    non_admin = list(filter(lambda f: f.admin == 0, frichtle))
    if len(non_admin) == 0:
        bot.reply_to(message=message, text="Es gibt keine Frichtle, die nicht Admin sind.")
    else:
        bot.send_message(message.chat.id,
                         text="Bitte wähle einen neuen Admin:",
                         reply_markup=markups.inline.ask_for_frichtle(command="appoint_admin", frichtle=non_admin))


@try_function
def process_admin_appoint(call):
    cmd_split = call.data.split(":")
    user_id = int(cmd_split[2])
    make_admin(user_id)
    text = "{} mit user_id {} wurde zum Admin ernannt.".format(get_username(user_id), user_id)
    bot.edit_message_text(text=text, chat_id=call.message.chat.id, message_id=call.message.message_id,
                          reply_markup=None)


@try_function
def remove_admin_command(message):
    frichtle = get_frichtle()
    admins = list(filter(lambda f: f.admin == 1, frichtle))
    admins = list(filter(lambda f: f.user_id != meta.lucas_user_id, admins))
    if len(admins) == 0:
        bot.reply_to(message=message, text="Es gibt keine Frichtle, die Admin sind.")
    else:
        bot.send_message(message.chat.id,
                         text="Bitte wähle einen Admin, den du entfernen möchtest:",
                         reply_markup=markups.inline.ask_for_frichtle(command="remove_admin", frichtle=admins))


@try_function
def process_admin_remove(call):
    cmd_split = call.data.split(":")
    user_id = int(cmd_split[2])
    remove_admin(user_id)
    text = "{} mit user_id {} wurde als Admin entfernt.".format(get_username(user_id), user_id)
    bot.edit_message_text(text=text, chat_id=call.message.chat.id, message_id=call.message.message_id,
                          reply_markup=None)


@try_function
def remove_user_command(message):
    frichtle = get_frichtle()
    not_me = list(filter(lambda f: f.user_id != meta.lucas_user_id, frichtle))
    if len(not_me) == 0:
        bot.reply_to(message=message, text="Es gibt keine Frichtle, außer dir.")
    else:
        bot.send_message(message.chat.id,
                         text="Bitte wähle ein Mitgleid, das du entfernen möchtest:",
                         reply_markup=markups.inline.ask_for_frichtle(command="remove_user", frichtle=not_me))


@try_function
def process_user_remove(call):
    cmd_split = call.data.split(":")
    user_id = int(cmd_split[2])
    text = "{} mit user_id {} wurde als User entfernt.".format(get_username(user_id), user_id)
    remove_frichtle(user_id)
    bot.edit_message_text(text=text, chat_id=call.message.chat.id, message_id=call.message.message_id)


@try_function
def remove_which_event(message):
    bot.send_message(message.chat.id, text="Bitte wähle ein Event aus:",
                     reply_markup=markups.inline.ask_for_event(command="remove_which_event"))


@try_function
def remove_event_sure(call):
    event_id = call.data.split(":")[2]
    chat_id = call.message.chat.id
    event = util.database.get_event(event_id)
    if event is None:
        text = "Okay, beendet."
        bot.edit_message_text(text=text, chat_id=chat_id, message_id=call.message.message_id)
        return
    bot.edit_message_text(text="Bist du sicher, dass du '{}' entfernen möchtest?".format(event.description),
                          chat_id=chat_id, message_id=call.message.message_id,
                          reply_markup=markups.inline.yesno_remove_event(event))


@try_function
def remove_event(call):
    chat_id = call.message.chat.id
    event_id = call.data.split(":")[2]
    result = util.database.remove_event(event_id=event_id)
    if result:
        text = "Der Termin wurde erfolgreich entfernt."
    else:
        text = "Es ist etwas schiefgegangen."

    bot.edit_message_text(chat_id=chat_id, message_id=call.message.message_id, text=text)


@try_function
def remove_which_survey(message):
    bot.send_message(message.chat.id, text="Bitte wähle eine Umfrage aus:",
                     reply_markup=markups.inline.ask_for_survey(command="remove_which_survey"))


@try_function
def remove_survey_sure(call):
    survey_id = call.data.split(":")[2]
    chat_id = call.message.chat.id
    survey = util.database.get_survey(survey_id)
    if survey is None:
        text = "Okay, beendet."
        bot.edit_message_text(text=text, chat_id=chat_id, message_id=call.message.message_id)
        return
    bot.edit_message_text(text="Bist du sicher, dass du '{}' entfernen möchtest?".format(survey.description),
                          chat_id=chat_id, message_id=call.message.message_id,
                          reply_markup=markups.inline.yesno_remove_survey(survey))
