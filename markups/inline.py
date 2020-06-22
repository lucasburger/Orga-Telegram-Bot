
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from util.database import get_event, get_survey, get_frichtle
import meta
import json


# Remove survey ##############


def remove_which_survey():
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    for s in get_survey():
        markup.add(InlineKeyboardButton(s.get_inline_str(), callback_data="remove_which_survey:" + s.survey_id))

    return markup


def yesno_remove_survey(survey):
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(InlineKeyboardButton("Ja", callback_data="cb:remove_survey:" + str(survey.survey_id)),
               InlineKeyboardButton("Nein", callback_data="abort"))
    return markup


def yesno_edit_event_okay():
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(InlineKeyboardButton("Ja", callback_data="cb:edit_event_okay:yes"),
               InlineKeyboardButton("Nein", callback_data="cb:edit_event_okay:no"))
    return markup

# Remove event ##############


def remove_which_event():
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    for e in get_event():
        markup.add(InlineKeyboardButton(e.get_inline_str(), callback_data="remove_which_event:" + e.event_id))

    return markup


def yesno_remove_event(event):
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(InlineKeyboardButton("Ja", callback_data="cb:remove_event:" + str(event.event_id)),
               InlineKeyboardButton("Nein", callback_data="abort"))
    return markup


# Cancel event ##############


def cancel_which_event():
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    for e in get_event():
        markup.add(InlineKeyboardButton(e.get_inline_str(), callback_data="cb:cancel_which_event:" + e.event_id))

    return markup


def yesno_cancel_event(event):
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(InlineKeyboardButton("Ja", callback_data="cb:cancel_event:1:" + event.event_id),
               InlineKeyboardButton("Nein", callback_data="cb:cancel_event:0:" + event.event_id))
    return markup


def yesno_send_cancel_event_alert(event_id):
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(InlineKeyboardButton("Ja", callback_data="cb:send_cancel_event_alert:1:" + event_id),
               InlineKeyboardButton("Nein", callback_data="cb:send_cancel_event_alert:0:" + event_id))
    return markup


# Remind event #############


def remind_which_event(events):
    markup = InlineKeyboardMarkup(row_width=2)
    for e in events:
        markup.add(InlineKeyboardButton(e.get_inline_str(), callback_data="cb:send_event_reminder:" + e.event_id))
    markup.add(InlineKeyboardButton(text="Für alle Events", callback_data="cb:send_event_reminder"))
    markup.add(InlineKeyboardButton(text="Abbrechen", callback_data="abort"))
    return markup


# Attend Event ##########

def attendance_which_event(events):
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    for e in [event['ev'] for event in events]:
        markup.add(InlineKeyboardButton(e.get_inline_str(), callback_data="cb:attend_which_event:" + e.event_id))

    return markup


def yesno_attend_event(event):
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(InlineKeyboardButton("Ja", callback_data="cb:attend_event:1:" + event.event_id),
               InlineKeyboardButton("Nein", callback_data="cb:attend_event:0:" + event.event_id))
    markup.row(InlineKeyboardButton("Weiß noch nicht", callback_data="cb:attend_event:-1:" + event.event_id))
    return markup


def send_reminder_for_all_events_button():
    return InlineKeyboardButton("Für alle Termine", callback_data="cb:send_event_reminder:all")


def send_reminder_for_all_surveys_button():
    return InlineKeyboardButton("Für alle Umfragen", callback_data="cb:send_survey_reminder:all")


def ask_for_event_or_survey():
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(InlineKeyboardButton("Event", callback_data="cb:remind_event"),
               InlineKeyboardButton("Umfrage", callback_data="cb:remind_survey"))
    markup.row(InlineKeyboardButton(text="Abbrechen", callback_data="abort"))
    return markup

# summary event #############


def ask_for_event(command, events=None, extra_buttons=None):
    if events is None:
        events = get_event()
    markup = InlineKeyboardMarkup(row_width=1)
    command = "cb:" + command + ":"
    if events is None:
        return
    for e in events:
        markup.add(InlineKeyboardButton(e.get_inline_str(), callback_data=command+e.event_id))
    if extra_buttons:
        for b in extra_buttons:
            markup.add(b)
    markup.add(InlineKeyboardButton("Abbrechen", callback_data="abort"))
    return markup


# summary survey

def ask_for_survey(command, surveys=None, extra_buttons=None):
    if surveys is None:
        surveys = get_survey()
    markup = InlineKeyboardMarkup(row_width=1)
    command = "cb:" + command + ":"
    if isinstance(surveys, list) and len(surveys) == 0:
        return
    for s in surveys:
        markup.add(InlineKeyboardButton(s.get_inline_str(), callback_data=command+s.survey_id))
    if extra_buttons:
        for b in extra_buttons:
            markup.add(b)

    markup.add(InlineKeyboardButton("Abbrechen", callback_data="abort"))
    return markup


def survey_response(survey):
    markup = InlineKeyboardMarkup(row_width=2)
    command_base = "cb:respond_survey:" + survey.survey_id + ":{}"
    last_button = InlineKeyboardButton("Abbrechen", callback_data=command_base.format('back'))
    l = len(survey.answers) - 1
    i = 0
    while i + 1 <= l:
        a, b = survey.answers[i], survey.answers[i + 1]
        ca, cb = command_base.format(survey.answers[i]), command_base.format(survey.answers[i+1])
        markup.add(InlineKeyboardButton(a, callback_data=ca), InlineKeyboardButton(b, callback_data=cb))
        i += 2
    if i == l:
        a, ca = survey.answers[i], command_base.format(survey.answers[i])
        markup.add(InlineKeyboardButton(a, callback_data=ca), last_button)
    else:
        markup.add(last_button)

    return markup


def edit_survey_response(survey):
    markup = InlineKeyboardMarkup(row_width=2)
    command_base = "cb:edit_survey_response:" + survey.survey_id + ":{}"
    last_button = InlineKeyboardButton("Abbrechen", callback_data=command_base.format('back'))
    l = len(survey.answers) - 1
    i = 0
    while i + 1 <= l:
        a, b = survey.answers[i], survey.answers[i + 1]
        ca, cb = command_base.format(survey.answers[i]), command_base.format(survey.answers[i+1])
        markup.add(InlineKeyboardButton(a, callback_data=ca), InlineKeyboardButton(b, callback_data=cb))
        i += 2
    if i == l:
        a, ca = survey.answers[i], command_base.format(survey.answers[i])
        markup.add(InlineKeyboardButton(a, callback_data=ca), last_button)
    else:
        markup.add(last_button)

    return markup


def send_survey_reminder_for_all_button():
    return InlineKeyboardButton("Für alle Termine", callback_data="cb:send_survey_reminder:all")


# edit event #############

def edit_event_property(event_id):
    markup = InlineKeyboardMarkup(row_width=2)
    props_disp = meta.event_col_names_display[:-1]
    props = meta.event_col_names[:-2]
    command_base = "cb:edit_event:" + event_id + ":{}"
    last_button = InlineKeyboardButton("Bearbeiten beenden", callback_data=command_base.format('back'))
    l = len(props) - 1
    i = 0
    while i + 1 <= l:
        a, b = props_disp[i], props_disp[i + 1]
        ca, cb = command_base.format(props[i]), command_base.format(props[i+1])
        markup.add(InlineKeyboardButton(a, callback_data=ca), InlineKeyboardButton(b, callback_data=cb))
        i += 2
    if i == l:
        a, ca = props_disp[i], command_base.format(props[i])
        markup.add(InlineKeyboardButton(a, callback_data=ca), last_button)
    else:
        markup.add(last_button)

    return markup


def ask_for_frichtle(command, frichtle=None, extra_buttons=None):
    if frichtle is None:
        frichtle = get_frichtle()
    markup = InlineKeyboardMarkup(row_width=1)
    command = "cb:" + command + ":"
    if isinstance(frichtle, list) and len(frichtle) == 0:
        return
    for f in frichtle:
        markup.add(InlineKeyboardButton(f.get_inline_str(), callback_data=command+str(f.user_id)))
    if extra_buttons:
        for b in extra_buttons:
            markup.add(b)
    markup.add(InlineKeyboardButton("Beenden", callback_data="abort"))
    return markup


# show table ###########

def show_which_table(tables):
    markup = InlineKeyboardMarkup(row_width=2)
    t = tuple([InlineKeyboardButton(t, callback_data="cb:show_table:" + t) for t in tables] + [InlineKeyboardButton("Beenden", callback_data="abort")])
    markup.add(*t)
    return markup


# show_event_back ####
def show_event_back():
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(InlineKeyboardButton("Zurück", callback_data="cb:show_event_back"))
    return markup


def show_survey_edit_or_back(survey_id):
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(InlineKeyboardButton("Ändern", callback_data="cb:edit_which_survey_response:{}".format(survey_id)),
               InlineKeyboardButton("Zurück", callback_data="cb:show_survey_back"))
    return markup


def event_summary_back():
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(InlineKeyboardButton("Zurück", callback_data="cb:event_summary_back"))
    return markup


def survey_summary_back():
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(InlineKeyboardButton("Zurück", callback_data="cb:survey_summary_back"))
    return markup


def show_numbers(command, return_name='num', question=0, page=1):

    markup = InlineKeyboardMarkup(row_width=3)
    l = []
    for i in range(1, 10):
        num = i+(page-1)*9
        l.append(InlineKeyboardButton(str(num), callback_data=command + json.dumps({return_name: [question, num]})))

    if page == 1:
        l.append(InlineKeyboardButton("Abbrechen", callback_data="abort"))
        l.append(InlineKeyboardButton("Mehr", callback_data=command + json.dumps({'page': page + 1})))
    else:
        l.append(InlineKeyboardButton("Weniger", callback_data=command + json.dumps({'page': page - 1})))
        l.append(InlineKeyboardButton("Abbruch", callback_data="abort"))
        if page < 10:
            l.append(InlineKeyboardButton("Mehr", callback_data=command + json.dumps({'page': page + 1})))

    markup.add(*tuple(l))
    return markup
