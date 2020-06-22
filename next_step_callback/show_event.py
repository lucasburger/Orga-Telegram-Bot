

import util.database as database
import util.functions
from util.classes import BotInstance, CallBackHandler, bot
import meta
import markups
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import json

# bot = BotInstance(token=meta.bot_token)


class ShowEventHandler(CallBackHandler):

    def main(self, initial_message=None, call=None, inline_message=None, **kwargs):

        if inline_message:
            user_id = inline_message.chat.id
        else:
            user_id = (initial_message or call).from_user.id

        if call:
            inline_message = call.message

        if kwargs.get('att', None) is None:
            text = "Welche Termine möchtest du anzeigen?"
            markup = InlineKeyboardMarkup(row_width=1)
            markup.add(InlineKeyboardButton(text="Ausstehende Rückmeldungen",
                                            callback_data=self.command + json.dumps({'att': 1})))
            markup.add(InlineKeyboardButton(text="Meine Zusagen",
                                            callback_data=self.command + json.dumps({'att': 3})))
            markup.add(InlineKeyboardButton(text="Meine Absagen",
                                            callback_data=self.command + json.dumps({'att': 2})))
            markup.add(InlineKeyboardButton("Beenden", callback_data="end"))
            if inline_message:
                msg = bot.edit_message_text(inline_message=inline_message, text=text, reply_markup=markup)
            else:
                msg = bot.send_message(initial_message.chat.id, text=text, reply_markup=markup)
            self.store[user_id]['inline_message'] = msg
            return

        if kwargs.get('event_id', None) is None:
            events = [d['ev'] for d in util.database.get_events_from_user(user_id=user_id, attendance=kwargs['att'])]
            if len(events) > 0:
                text = "Wähle aus, um den Termin anzuzeigen:"
            else:
                text = "Keine entsprechenden Termine gefunden."

            markup = InlineKeyboardMarkup(row_width=1)
            buttons = list(InlineKeyboardButton(text=e.get_inline_str(),
                                                callback_data=self.command + json.dumps({'event_id': e.event_id}))
                           for e in events)
            markup.add(*tuple(buttons))
            markup.add(InlineKeyboardButton("Zurück", callback_data=self.command + json.dumps({'att': None})))
            bot.edit_message_text(text=text, inline_message=inline_message, reply_markup=markup)

            return

        event = util.database.get_event(event_id=kwargs['event_id'])

        if kwargs.get('edit', None) is None:
            text = event.get_detail_str()
            text += "\nDu hast {}"
            markup_text = "Ändern"
            if kwargs['att'] == 3:
                text = text.format("ZUGESAGT.")
            elif kwargs['att'] == 2:
                text = text.format("ABGESAGT.")
            elif kwargs['att'] == 1:
                text = text.format("noch keine Rückmeldung gegeben.")
                markup_text = "Rückmeldung geben"

            markup = InlineKeyboardMarkup(row_width=2)
            markup.add(InlineKeyboardButton(text=markup_text, callback_data=self.command + json.dumps({'edit': True})),
                       InlineKeyboardButton(text="Zurück", callback_data=self.command + json.dumps({'event_id': None})))
            bot.edit_message_text(inline_message=inline_message, text=text, reply_markup=markup)
            return

        text = "Kommst du zu folgendem Event?\n" + event.get_detail_str()

        if kwargs.get('att_new', None) is None:
            # send sure reply markup
            markup = InlineKeyboardMarkup(row_width=2)
            markup.add(InlineKeyboardButton(text="Ja", callback_data=self.command + json.dumps({'att_new': 3})),
                       InlineKeyboardButton(text="Nein", callback_data=self.command + json.dumps({'att_new': 2})),
                       InlineKeyboardButton(text="Weiß doch nicht", callback_data=self.command + json.dumps({"att_new": 1})),
                       InlineKeyboardButton(text="Zurück", callback_data=self.command + json.dumps({'edit': None})))
            bot.edit_message_text(inline_message=inline_message, text=text, reply_markup=markup)
            return

        util.database.set_attendance_to_event(event_id=kwargs['event_id'], user_id=user_id, att=kwargs['att_new'])

        if kwargs['att_new'] == 3:
            text = "\n\nDu hast ZUGESAGT."
        elif kwargs['att_new'] == 2:
            text = "\n\nDu hast ABGESAGT."
        elif kwargs['att_new'] == 1:
            text = "\n\nDeine Rückmeldung wurde entfernt."

        text += "\n Wähle neuen Termin aus:"

        events = [e['ev'] for e in util.database.get_events_from_user(user_id=user_id, attendance=kwargs['att'])]
        markup = InlineKeyboardMarkup(row_width=1)
        buttons = list(InlineKeyboardButton(text=e.get_inline_str(),
                                            callback_data=self.command + json.dumps({'event_id': e.event_id}))
                       for e in events)
        markup.add(*tuple(buttons))
        markup.add(InlineKeyboardButton("Zurück", callback_data=self.command + json.dumps({'att': None})))

        self.store[user_id]['data'].update({'event_id': None, 'att_new': None, 'edit': None})

        bot.edit_message_text(inline_message=inline_message, text=text, reply_markup=markup)


show_event = ShowEventHandler(command='show_event')
