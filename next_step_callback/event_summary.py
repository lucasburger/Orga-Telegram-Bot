import util.database as database
import util.functions
from util.classes import BotInstance, CallBackHandler, bot
import meta
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import json

# bot = BotInstance(token=meta.bot_token)


class EventSummaryHandler(CallBackHandler):

    def main(self, initial_message=None, user_message=None, call=None, inline_message=None, **kwargs):

        if inline_message:
            user_id = inline_message.chat.id
        else:
            user_id = (initial_message or user_message or call).from_user.id

        if call:
            inline_message = call.message

        buttons = []
        markup = None

        events = util.database.get_event()

        if len(events) == 0:
            bot.reply_to(initial_message, text="Es gibt aktuell keine Termine.")
            return

        if kwargs.get('event_id') is None:
            text = "Wähle einen Termin aus:"
            markup = InlineKeyboardMarkup(row_width=1)
            buttons = list(InlineKeyboardButton(text=s.get_inline_str(),
                                                callback_data=self.command + json.dumps({'event_id': s.event_id}))
                           for s in database.get_event())
            markup.add(*tuple(buttons))
            markup.add(InlineKeyboardButton("Beenden", callback_data="end"))
            if inline_message:
                msg = bot.edit_message_text(inline_message=inline_message, text=text, reply_markup=markup)
            else:
                msg = bot.send_message(initial_message.chat.id, text=text, reply_markup=markup)
            self.store[user_id]['inline_message'] = msg
            return

        event = util.database.get_event(event_id=kwargs['event_id'])
        text = util.functions.get_event_summary(**kwargs)

        if not kwargs.get('detail', False):
            # erinnerung
            if kwargs['event_id'] in [s.event_id for s in util.database.events_that_need_reminder()] and \
                    not self.store[user_id].get('sent_reminder', False):
                buttons.append(InlineKeyboardButton(text="Erinnern", callback_data=self.command + json.dumps({'remind': True})))
            # detail
            if not kwargs.get('detail', False) and any(s['attendance'] >= 2 for s in util.database.get_event_attendance(event=event)):
                buttons.append(InlineKeyboardButton(text="Details", callback_data=self.command + json.dumps({'detail': True})))

            # back button
            if kwargs.get('detail', False):
                dump = {'detail': False}
            else:
                dump = {'event_id': None}

            buttons.append(InlineKeyboardButton(text="Zurück", callback_data=self.command + json.dumps(dump)))

            markup = InlineKeyboardMarkup(row_width=2)
            markup.add(*tuple(buttons))

        if kwargs.get('remind', False):
            util.functions.send_reminder_for(from_user_id=user_id, _id=kwargs['event_id'])
            self.store[user_id]['sent_reminder'] = True
            text = "Es wurden Erinnerungen versandt."
            dump = {'remind': False, 'detail': False}

            markup = InlineKeyboardMarkup(row_width=1)
            markup.add(InlineKeyboardButton(text="Zurück", callback_data=self.command + json.dumps(dump)))

        if markup is None and kwargs['detail']:
            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton(text="Zurück", callback_data=self.command + json.dumps({'detail': False})))

        if inline_message:
            msg = bot.edit_message_text(inline_message=inline_message, text=text, reply_markup=markup)
        else:
            msg = bot.send_message(initial_message.chat.id, text=text, reply_markup=markup)
        self.store[user_id]['inline_message'] = msg
        return


event_summary = EventSummaryHandler(command='event_summary')
