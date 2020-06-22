from markups import inline
from markups import menu
from markups import selection
from telebot.types import ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton
import json


def remove():
    return ReplyKeyboardRemove(selective=False)


def show_numbers(command_base=None, page=1):
    if command_base is None:
        command_base = 'cb:'
    markup = InlineKeyboardMarkup(row_width=3)
    l = []
    for i in range(1, 10):
        l.append(InlineKeyboardButton(str(i+(page-1)*9), callback_data=command_base.format(i*page)))

    if page == 1:
        l.append(InlineKeyboardButton('', callback_data="cb:"))
        l.append(InlineKeyboardButton("Abbruch", callback_data="abort"))
        l.append(InlineKeyboardButton("Mehr", callback_data="show_numbers;" + json.dumps({'page': 2})))
    else:
        l.append(InlineKeyboardButton('Weniger', callback_data="show_numbers;" + json.dumps({'page': page-1})))
        l.append(InlineKeyboardButton("Abbruch", callback_data="abort"))
        l.append(InlineKeyboardButton("Mehr", callback_data="show_numbers;" + json.dumps({'page': page+1})))

    markup.add(*tuple(l))
    return markup
