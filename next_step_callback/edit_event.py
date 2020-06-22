

import util.database as database
import util.functions
from util.classes import BotInstance, CallBackHandler, bot
import meta
import markups
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import json

# bot = BotInstance(token=meta.bot_token)


class EditEventHandler(CallBackHandler):

    def main(self, initial_message=None, user_message=None, call=None, inline_message=None, **kwargs):

        if inline_message:
            user_id = inline_message.chat.id
        else:
            user_id = (initial_message or user_message or call).from_user.id

        if user_message:
            bot.delete_message(chat_id=user_message.chat.id, message_id=user_message.message_id)

        if call:
            inline_message = call.message

        if kwargs.get('event_id', None) is None:
            text = "Wähle einen Termin aus, den du bearbeiten möchtest:"
            markup = InlineKeyboardMarkup(row_width=1)
            buttons = list(InlineKeyboardButton(text=e.get_inline_str(),
                                                callback_data=self.command + json.dumps({'event_id': e.event_id}))
                           for e in database.get_event())
            markup.add(*tuple(buttons))
            markup.add(InlineKeyboardButton("Abbrechen", callback_data="abort"))
            if inline_message:
                msg = bot.edit_message_text(inline_message=inline_message, text=text, reply_markup=markup)
            else:
                msg = bot.send_message(initial_message.chat.id, text=text, reply_markup=markup)
            self.store[user_id]['inline_message'] = msg
            return
        else:
            event = database.get_event(event_id=kwargs['event_id'])
            text = "Du bearbeitest folgenden Termin:\n" + event.get_detail_str() + "\n\n"

        if kwargs.get('property', None) is None:
            text += "Was möchtest du bearbeiten?"
            markup = InlineKeyboardMarkup(row_width=2)
            buttons = []
            for i, v in enumerate(meta.event_col_names_display):
                buttons.append(InlineKeyboardButton(text=v,
                                                    callback_data=self.command +
                                                                  json.dumps({'property': meta.event_col_names[i]})))
            buttons.append(InlineKeyboardButton("Zurück", callback_data=self.command + json.dumps({'event_id': None})))
            buttons.append(InlineKeyboardButton(text="Abbrechen", callback_data="abort"))
            markup.add(*tuple(buttons))
            bot.edit_message_text(text=text, inline_message=inline_message, reply_markup=markup)
            return

        if kwargs['property'] == "dress":
            if kwargs.get('new_value') is None:
                text += "Okay, bitte wähle ein Outfit:"
                markup = InlineKeyboardMarkup(row_width=2)
                markup.add(*tuple([InlineKeyboardButton(text=s, callback_data=self.command + json.dumps(
                    {'new_value': s}
                )) for s in meta.dresses] +
                                  [InlineKeyboardButton(text="Zurück", callback_data=self.command +
                                                                                     json.dumps({'property': None, 'new_value': None}))]))
                bot.edit_message_text(text=text, inline_message=inline_message, reply_markup=markup)
            else:
                event = util.database.get_event(event_id=self.store[user_id]['data']['event_id'])
                event.dress = kwargs.pop('new_value')
                util.database.save_event(ev=event)
                self.store[user_id]['data'].pop('new_value')
                self.store[user_id]['data'].pop('property')
                self.__call__(call=call)
            return

        elif 'new_value' not in kwargs.keys():
            prop_display = meta.event_col_names_display[meta.event_col_names.index(kwargs.get('property'))]
            text += "Okay, gib einen neuen Wert für '{}' ein:".format(prop_display)
            hint = meta.event_col_names_hints.get(kwargs['property'])
            if hint is not None:
                text += "\n{}".format(hint)
            msg = bot.edit_message_text(inline_message=inline_message, text=text)
            bot.register_next_step_handler(msg, self.edit_property_reply)
            return

        if 'sure' not in kwargs.keys():
            # send sure reply markup
            event = database.get_event(event_id=kwargs.get('event_id'))
            setattr(event, kwargs.get('property'), kwargs.get('new_value'))
            text = "Der bearbeitete Termin ist jetzt:\n" + event.get_detail_str() + "\n\nSoll er gespeichert werden?"
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
                setattr(event, kwargs.get('property'), kwargs.get('new_value'))
                database.save_event(event)
                text = "Okay, die Änderungen wurden gespeichert.\n" \
                       "Möchtest du alle wissen lassen, dass sich der Termin geändert hat?"
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
            util.functions.send_event_edit_notice(who_edit=user_id, event_id=kwargs.get('event_id'))

        bot.edit_message_text(inline_message=inline_message, text=text)
        self.store[user_id] = dict()
        self.store[user_id]['data'] = dict()
        self.store[user_id]['inline_message'] = None

        return

    def edit_property_reply(self, message):
        user_id = message.from_user.id
        event = database.get_event(event_id=self.store[user_id]['data']['event_id'])
        prop = self.store[user_id]['data']['property']
        try:
            setattr(event, prop, message.text)
            self.store[user_id]['data']['new_value'] = message.text
        except ValueError:
            text = "Der neue Wert wurde nicht erkannt."
            markup = markups.menu.manage_events()
            bot.send_message(message.chat.id, text=text, reply_markup=markup)
            return
        self.__call__(user_message=message)


edit_event = EditEventHandler(command='edit_event')
