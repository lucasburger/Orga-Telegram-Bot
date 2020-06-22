

import util.database as database
import util.functions
from util.classes import BotInstance, CallBackHandler, bot
import meta
import markups
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import json

# bot = BotInstance(token=meta.bot_token)


class ShowTableHandler(CallBackHandler):

    def main(self, initial_message=None, call=None, inline_message=None, **kwargs):

        if inline_message:
            user_id = inline_message.chat.id
        else:
            user_id = (initial_message or call).from_user.id

        if call:
            inline_message = call.message

        if kwargs.get('name', None) is None:
            text = "Welche Tabelle möchtest du anzeigen?"
            tables = database.get_all_tables()
            markup = InlineKeyboardMarkup(row_width=2)
            t = tuple([InlineKeyboardButton(t, callback_data=self.command + json.dumps({'name': t})) for t in tables]
                      + [InlineKeyboardButton("Abbrechen", callback_data="abort")])
            markup.add(*t)

            if inline_message:
                msg = bot.edit_message_text(inline_message=inline_message, text=text, reply_markup=markup)
            else:
                msg = bot.send_message(initial_message.chat.id, text=text, reply_markup=markup)
            self.store[user_id]['inline_message'] = msg
            return

        table = kwargs['name']
        text = util.database.get_table_as_string(table)

        if text is None:
            text = "Die Tabelle ist leer."

        markup = InlineKeyboardMarkup(row_width=1)
        markup.add(InlineKeyboardButton("Zurück", callback_data=self.command + json.dumps({'name': None})))

        bot.edit_message_text(inline_message=inline_message, text=text, reply_markup=markup)


show_table = ShowTableHandler(command='show_table')
