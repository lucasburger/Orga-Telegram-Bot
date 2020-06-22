

import util.database as database
import util.functions
from util.classes import BotInstance, CallBackHandler, bot
import meta
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import json

# bot = BotInstance(token=meta.bot_token)


class SendReminderHandler(CallBackHandler):

    def main(self, initial_message=None, user_message=None, call=None, inline_message=None, **kwargs):

        if inline_message:
            user_id = inline_message.chat.id
        else:
            user_id = (initial_message or user_message or call).from_user.id

        if call:
            inline_message = call.message

        if kwargs.get('id', None) is None:
            text = "Bitte wähle aus, für was du eine Erinnerung versenden möchtest:"
            events = util.database.events_that_need_reminder()
            surveys = util.database.surveys_that_need_reminder()

            markup = InlineKeyboardMarkup(row_width=1)
            buttons = list(InlineKeyboardButton(text=e.get_inline_str(),
                                                callback_data=self.command + json.dumps({'id': e.id}))
                           for e in events)
            buttons += list(InlineKeyboardButton(text="Umfrage: " + s.get_inline_str(),
                                                 callback_data=self.command + json.dumps({'id': s.id}))
                            for s in surveys)

            markup.add(*tuple(buttons))
            markup.add(InlineKeyboardButton("Abbrechen", callback_data="abort"))
            if inline_message:
                msg = bot.edit_message_text(inline_message=inline_message, text=text, reply_markup=markup)
            else:
                msg = bot.send_message(initial_message.chat.id, text=text, reply_markup=markup)
            self.store[user_id]['inline_message'] = msg
            return
        else:
            text = "Okay, es wurden Erinnerungen versendet"
            bot.edit_message_text(inline_message=inline_message, text=text)
            util.functions.send_reminder_for(from_user_id=user_id, id=kwargs['id'])


send_reminder = SendReminderHandler(command='send_reminder')
