
import markups
from util.classes import BotInstance, Event, Survey, bot
import meta
from telebot.types import Message, CallbackQuery
import util.database as util_db
from util.survey_summaries import summary_function_dict

from requests.exceptions import ConnectionError

from telebot import logger

# bot = BotInstance(token=meta.bot_token)


def try_function(func):
    def new_func(*args, **kwargs):
        return func(*args, **kwargs)
        try:
            return func(*args, **kwargs)
        except ConnectionResetError:
            logger.exception("Couldn't catch ConnectionResetError:")
            pass
        except ConnectionError:
            logger.exception("Couldn't catch ConnectionError:")
            pass
        except Exception as e:
            caught = False
            for a in args:
                if isinstance(a, Message):
                    chat_id = a.chat.id
                    username = a.from_user.username
                    user_id = a.from_user.id
                    caught = True
                    bot.send_message(chat_id, text=meta.error_text,
                                     reply_markup=markups.menu.main(user_id))
                elif isinstance(a, CallbackQuery):
                    bot.edit_message_reply_markup(call=a, reply_markup=None)
                    bot.edit_message_text(text=meta.error_text, call=a, reply_markup=None)
                    username = a.from_user.username
                    user_id = a.from_user.id
                    caught = True

                if caught:
                    bot.send_message(meta.lucas_chat_id,
                                     "Bei @{} ist folgender Fehler in der Funktion {} aufgetreten:\n"
                                     .format(username, func.__name__) + str(e),
                                     reply_markup=markups.menu.main(user_id))
                    logger.exception("Caught Exception:")
                    break

            return
    return new_func


@try_function
def goto_main_menu(message=None):
    chat_id = message.chat.id
    user_id = message.from_user.id
    bot.send_message(chat_id, text=message.text, reply_markup=markups.menu.main(user_id))
    return


@try_function
def goto_manage_events_menu(message=None, chat_id=None):
    if chat_id is None:
        chat_id = message.chat.id
    bot.send_message(chat_id, text="Termine verwalten", reply_markup=markups.menu.manage_events())
    return


@try_function
def goto_events_menu(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, text="Termine", reply_markup=markups.menu.events())
    return


@try_function
def goto_survey_menu(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, text="Umfragen", reply_markup=markups.menu.surveys())
    return


@try_function
def goto_master_menu(message):
    bot.send_message(message.chat.id, text="Mastermenü", reply_markup=markups.menu.master())
    return


@try_function
def get_event_summary(event_id=None, event=None, detail=False, **kwargs):
    if event is not None:
        event_id = event.event_id
    else:
        event = util_db.get_event(event_id)

    summary = util_db.get_event_attendance(event_id)
    x1 = len(list(filter(lambda x: x['attendance'] == 3, summary)))
    x0 = len(list(filter(lambda x: x['attendance'] == 2, summary)))
    x_1 = len(list(filter(lambda x: x['attendance'] == 1, summary)))
    att = {'Beschreibung': str(event),
           'Zusagen': x1, 'Absagen': x0, 'Ausstehend': x_1}
    for instr in meta.registers.values():
        for i in instr:
            att[i] = get_attendance_from_instrument(summary, i)

    text = meta.event_summary_template.format(**att)

    if detail:
        for f in util_db.get_frichtle():
            res = '\n'
            for res in summary:
                if res['user_id'] == f.user_id:
                    r = res['attendance']
                    if r == 3:
                        res = "Ja"
                    elif r == 2:
                        res = "Nein"
                    else:
                        res = "Keine Rückmeldung"
                    break
            if res != '':
                text += "{}: {}\n".format(f.get_inline_str(), res)

    return text

    return meta.event_summary_template.format(**att)


def get_attendance_from_instrument(summary, instrument=None):
    if instrument is None:
        l = summary
    else:
        l = list(filter(lambda x: x['instrument'] == instrument, summary))
    x1 = len(list(filter(lambda x: x['attendance'] == 3, l)))
    x0 = len(list(filter(lambda x: x['attendance'] == 2, l)))
    x_1 = len(list(filter(lambda x: x['attendance'] == 1, l)))
    return str(x1) + " / " + str(x0) + " / " + str(x_1)


@try_function
def send_cancel_event_notice(who_cancel, event_id):
    frichtle = util_db.get_frichtle()
    ev = util_db.get_event(event_id=event_id)
    name = util_db.get_username(who_cancel).get_inline_str()
    text = "Benachrichtigung:\n{} hat folgenden Termin abgesagt:\n".format(name) + str(ev)
    for user_id in [f.user_id for f in frichtle]:
        if user_id == who_cancel:
            continue
        bot.send_message(chat_id=user_id, text=text)


@try_function
def send_event_edit_notice(who_edit, event_id):
    frichtle = util_db.get_frichtle()
    ev = util_db.get_event(event_id=event_id)
    name = util_db.get_frichtle(user_id=who_edit).get_inline_str()
    text = "Benachrichtigung:\n{} hat folgenden Termin bearbeitet. Bitte überprüfe, ob deine Zu- oder Absage noch stimmt:\n"\
        .format(name) + str(ev)
    for user_id in [f.user_id for f in frichtle]:
        if user_id == who_edit:
            continue
        bot.send_message(user_id, text=text)


@try_function
def send_reminder_for(from_user_id, _id=None):
    if _id[:2] == 'su':
        l = util_db.get_survey(survey_id=_id)
    elif _id[:2] == 'ev':
        l = util_db.get_event(event_id=_id)

    frichtle = util_db.get_frichtle()
    username = util_db.get_frichtle(user_id=from_user_id).get_inline_str()
    for f in frichtle:
        if f.user_id == from_user_id:
            continue
        if isinstance(l, Survey):
            needs = util_db.check_survey_response(user_id=f.user_id, survey_id=_id) == None
            markup = markups.selection.new_survey_alert()
            text = "{} bittet um Rückmeldung für folgende Umfrage:\n".format(username) + str(l)
        elif isinstance(l, Event):
            needs = util_db.check_attendance(user_id=f.user_id, event_id=_id) == 1
            markup = markups.selection.new_event_alert()
            text = "{} bittet um Rückmeldung für folgenden Termin:\n".format(username) + str(l)
        else:
            needs = False

        if needs:
            bot.send_message(f.user_id, text=text, reply_markup=markup)
        logger.info("Send reminder for: {}".format(str(l).replace("\n", ";")))
    return


@try_function
def get_survey_summary(survey_id=None, survey=None, detail=False, **kwargs):
    if survey is not None:
        survey_id = survey.survey_id
    else:
        survey = util_db.get_survey(survey_id)

    unanswered = sum([(1 if s is None else 0) for s in survey.results.values()])
    text = meta.survey_summary_template.format(details=survey.get_detail_str(), unanswered=unanswered)

    text += "\n" + summary_function_dict[survey.summary_function](survey) + "\n"

    if detail:
        frichtle = util_db.get_frichtle(return_json=True)
        det = '\n*Antworten*:\n'
        for user_id, res in survey.results.items():
            if res is None:
                res = "Keine Rückmeldung."
            det += "{}: {}\n".format(frichtle[user_id]["name"], res)

        text += det

    return text


def send_new_event_alert(event, by):
    text = "{} hat einen neuen Termin erstellt:\n".format(by.get_inline_str()) + str(event) + "\nBitte gehe in die '/termine' Sektion, um zu- oder abzusagen."
    for user_id in util_db.get_from_all_frichtle('user_id'):
        if user_id == by.user_id:
            continue
        bot.send_message(user_id, text, reply_markup=markups.selection.new_event_alert())


def send_new_survey_alert(survey, by):
    text = "{} hat eine neue Umfrage erstellt:\n".format(by.get_inline_str()) + str(survey) + "\nBitte gehe in die '/Umfragen' Sektion, um zu antworten."
    for user_id in util_db.get_from_all_frichtle('user_id'):
        if user_id == by.user_id:
            continue
        bot.send_message(user_id, text, reply_markup=markups.selection.new_survey_alert())
