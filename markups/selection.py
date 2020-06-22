
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
import meta


def dress():
    markup = ReplyKeyboardMarkup(one_time_keyboard=True)
    for d in meta.dresses:
        markup.add(KeyboardButton(d))
    return markup


def new_event_alert():
    markup = ReplyKeyboardMarkup(one_time_keyboard=True, row_width=2)
    markup.add(KeyboardButton("📅 Termine"))
    markup.add(KeyboardButton("Mache ich später..."))
    return markup


def new_survey_alert():
    markup = ReplyKeyboardMarkup(one_time_keyboard=True, row_width=2)
    markup.add(KeyboardButton("🏷 Umfragen"))
    markup.add(KeyboardButton("Mache ich später..."))
    return markup


def yesno():
    markup = ReplyKeyboardMarkup(row_width=2, one_time_keyboard=True)
    markup.add(KeyboardButton("Ja"), KeyboardButton("Nein"))
    return markup


def instrument():
    markup = ReplyKeyboardMarkup(row_width=2)
    for instr in meta.instruments:
        markup.add(KeyboardButton(instr))
    return markup


def edit_which_event_property():
    markup = ReplyKeyboardMarkup(row_width=2)
    last_button = KeyboardButton("Bearbeiten beenden")
    ll = meta.event_col_names_display
    l = len(ll) - 2
    i = 0
    while i+1 <= l:
        a, b = ll[i], ll[i+1]
        markup.add(KeyboardButton(a), KeyboardButton(b))
        i += 2
    if i == l:
        markup.add(KeyboardButton(ll[i]), last_button)
    else:
        markup.add(last_button)

    return markup
