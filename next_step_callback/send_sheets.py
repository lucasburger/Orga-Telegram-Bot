

from util.classes import BotInstance, CallBackHandler, bot
import meta
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import json
from copy import copy

# bot = BotInstance(token=meta.bot_token)


class SendSheetsHandler(CallBackHandler):

    def main(self, initial_message=None, call=None, inline_message=None, **kwargs):

        if inline_message:
            user_id = inline_message.chat.id
        else:
            user_id = (initial_message or call).from_user.id

        if call:
            inline_message = call.message

        if kwargs.get('typ', None) is None:
            text = "Bitte wähle aus:"
            markup = InlineKeyboardMarkup(row_width=1)
            markup.add(InlineKeyboardButton(text="Schritte",
                                            callback_data=self.command + json.dumps({'typ': "s"})))
            markup.add(InlineKeyboardButton(text="Märsche",
                                            callback_data=self.command + json.dumps({'typ': "m"})))
            markup.add(InlineKeyboardButton(text="Bühnenstücke",
                                            callback_data=self.command + json.dumps({'typ': "b"})))
            markup.add(InlineKeyboardButton("Beenden", callback_data="end"))
            if inline_message:
                msg = bot.edit_message_text(inline_message=inline_message, text=text, reply_markup=markup)
            else:
                msg = bot.send_message(initial_message.chat.id, text=text, reply_markup=markup)
            self.store[user_id]['inline_message'] = msg
            return

        typ = {"s": "Schritte", "m": "Maersche", "b": "Buehnenstuecke"}[kwargs['typ']]

        if kwargs.get('sheet_id', None) is None:
            noten = copy(meta.noten[typ])
            for i, n in enumerate(noten):
                v = n[0]
                v = v.replace("ae", "ä")
                v = v.replace("ue", "ü")
                v = v.replace("oe", "ö")
                v = v.replace("_", " ")
                noten[i] = (v, noten[i][1])

            markup = InlineKeyboardMarkup(row_width=1)
            buttons = list(InlineKeyboardButton(text=n[0],
                                                callback_data=self.command + json.dumps({'sheet_id': n[1]}))
                           for n in noten)
            markup.add(*tuple(buttons))
            markup.add(InlineKeyboardButton("Zurück", callback_data=self.command + json.dumps({'typ': None})))
            bot.edit_message_text(text="Bitte wähle aus:", inline_message=inline_message, reply_markup=markup)

            return

        noten = meta.noten[typ]
        for l in noten:
            if l[1] == kwargs['sheet_id']:
                name = l[0]
                break

        noten_path = meta.noten_path.format(typ=typ, name=name)

        bot.delete_message(message=inline_message)

        bot.send_document(chat_id=inline_message.chat.id, data=open(noten_path, "rb"), caption="Bitteschön!")


send_sheets = SendSheetsHandler(command='send_sheets')
