
from util.database import *
import meta
from util.classes import BotInstance, bot
from util.functions import try_function
import markups

# bot = BotInstance(token=meta.bot_token)


@try_function
def request_id_event_reminder(message):
    events = events_that_need_reminder()
    if events:
        bot.send_message(message.chat.id,
                         text="Bitte wähle eine Event ID für die du einen Reminder verschicken möchstes "
                              "(Mehrfachwahl möglich):",
                         reply_markup=markups.inline.ask_for_event(command="remind_which_event",
                                                                   events=events))
    else:
        bot.reply_to(message, text="Es stehen keine Rückmeldungen aus.")


@try_function
def send_event_reminder_to_user(to_user, from_user_id, ev):
    username = get_username(from_user_id)
    text = "@{} bittet um Rückmeldung für folgendes Event:\n".format(username) + str(ev)
    bot.send_message(to_user, text=text, reply_markup=markups.selection.new_event_alert())


@try_function
def event_summary_command(message):
    bot.send_message(message.chat.id, text="Bitte wähle einen Termin aus, für den Erinnerungen versendet werden:",
                     reply_markup=markups.inline.ask_for_event(command="event_summary"))


# edit event

@try_function
def edit_event_command(message):
    bot.send_message(message.chat.id, text="Bitte wähle einen Termin aus, den du bearbeiten möchtest:",
                     reply_markup=markups.inline.ask_for_event(command="edit_which_event"))
    return
