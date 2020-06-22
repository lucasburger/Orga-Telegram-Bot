

import util.database as database
import util.functions
from util.classes import BotInstance, CallBackHandler, bot
import meta
import markups
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import json

# bot = BotInstance(token=meta.bot_token)


class CancelEventHandler(CallBackHandler):

    def main(self, initial_message=None, user_message=None, call=None, inline_message=None, **kwargs):

        if inline_message:
            user_id = inline_message.chat.id
        else:
            user_id = (initial_message or user_message or call).from_user.id

        if call:
            inline_message = call.message

        if 'event_id' not in kwargs.keys():
            text = "Wähle einen Termin aus, den du absagen möchtest:"
            markup = InlineKeyboardMarkup(row_width=1)
            buttons = list(InlineKeyboardButton(text=e.get_inline_str(),
                                                callback_data=self.command + json.dumps({'event_id': e.event_id}))
                           for e in database.get_event())
            markup.add(*tuple(buttons))
            markup.add(InlineKeyboardButton("Abbrechen", callback_data="abort"))
            msg = bot.send_message(initial_message.chat.id, text=text, reply_markup=markup)
            self.store[user_id]['inline_message'] = msg
            return

        if 'sure' not in kwargs.keys():
            event = database.get_event(event_id=kwargs.get('event_id'))
            text = "Bist du sicher, dass du folgenden Termin absagen möchtest?\n\n" + event.get_detail_str()
            markup = InlineKeyboardMarkup(row_width=2)
            markup.add(InlineKeyboardButton(text="Ja", callback_data=self.command + json.dumps({'sure': True})),
                       InlineKeyboardButton(text="Nein", callback_data=self.command + json.dumps({'sure': False})))
            markup.add(InlineKeyboardButton(text="Abbrechen", callback_data="abort"))
            bot.edit_message_text(inline_message=inline_message, text=text, reply_markup=markup)
            return

        if 'send_notice' not in kwargs.keys():
            if not kwargs.get('sure'):
                text = "Schade, dann ist wohl etwas schiefgegangen... Bitte versuche es ggfs erneut."
                markup = None
            else:
                event = database.get_event(event_id=kwargs.get('event_id'))
                text = "Okay, der Termin wurde abgesagt.\n" \
                       "Möchtest du alle wissen lassen, dass der Termin abgesagt wurde?"
                markup = InlineKeyboardMarkup(row_width=2)
                markup.add(InlineKeyboardButton(text="Ja", callback_data=self.command + json.dumps({'send_notice': True})),
                           InlineKeyboardButton(text="Nein", callback_data=self.command + json.dumps({'send_notice': False})))
                markup.add(InlineKeyboardButton(text="Abbrechen", callback_data="abort"))

            bot.edit_message_text(inline_message=inline_message, text=text, reply_markup=markup)

            return

        if not kwargs.get('send_notice'):
            text = "Okay, es werden keine Nachrichten versandt."
        else:
            text = "Okay, es wurden Nachrichten an alle versandt."
            util.functions.send_cancel_event_notice(who_cancel=user_id, event_id=kwargs['event_id'])

        bot.edit_message_text(inline_message=inline_message, text=text)
        self.store[user_id] = dict()
        self.store[user_id]['data'] = dict()
        self.store[user_id]['inline_message'] = None
        return


cancel_event = CancelEventHandler(command='cancel_event')
