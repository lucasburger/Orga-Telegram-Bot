

import util.database as database
import util.functions
from util.classes import BotInstance, CallBackHandler, Event, bot
import meta
import markups
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import json

# bot = BotInstance(token=meta.bot_token)


class NewEventHandler(CallBackHandler):

    def main(self, initial_message=None, user_message=None, call=None, inline_message=None, **kwargs):

        if inline_message:
            user_id = inline_message.chat.id
        else:
            user_id = (initial_message or user_message or call).from_user.id

        if user_message:
            bot.delete_message(chat_id=user_message.chat.id, message_id=user_message.message_id)

        if call:
            inline_message = call.message

        if initial_message:
            bot.reply_to(initial_message, text=meta.new_event_guide)

        if kwargs.get('done', False):
            # send sure reply markup
            if kwargs.get('sure') is None:
                event = self.store[user_id]['event']
                text = "Der Termin ist lautet:\n" + event.get_detail_str() + "\n\nSoll er gespeichert werden?"
                markup = InlineKeyboardMarkup(row_width=2)
                markup.add(InlineKeyboardButton(text="Ja", callback_data=self.command + json.dumps({'sure': True})),
                           InlineKeyboardButton(text="Nein", callback_data=self.command + json.dumps({'sure': False})))
                markup.add(InlineKeyboardButton(text="Zurück", callback_data=self.command + json.dumps({'done': None,
                                                                                                        'property': None})))
                bot.edit_message_text(inline_message=inline_message, text=text, reply_markup=markup)
                return

            if kwargs.get('send_notice') is None:
                if not kwargs.get('sure'):
                    self.store[user_id]['property'] = None
                    self.__call__(call=call)
                    return
                else:
                    event = self.store[user_id]['event']
                    database.save_event(event)
                    text = "Okay, der Termin wurde erstellt.\n" \
                           "Möchtest du alle wissen lassen, sodass sie zu oder absagen können?"
                    markup = InlineKeyboardMarkup(row_width=2)
                    markup.add(
                        InlineKeyboardButton(text="Ja", callback_data=self.command + json.dumps({'send_notice': True})),
                        InlineKeyboardButton(text="Nein",
                                             callback_data=self.command + json.dumps({'send_notice': False})))

                bot.edit_message_text(inline_message=inline_message, text=text, reply_markup=markup)
                return
            if not kwargs.get('send_notice'):
                text = "Okay, es werden keine Nachrichten versandt."
            else:
                text = "Okay, es wurden Nachrichten an alle versandt."
                util.functions.send_new_event_alert(by=util.database.get_frichtle(user_id=user_id),
                                                    event=self.store[user_id]['event'])

            bot.edit_message_text(inline_message=inline_message, text=text)
            self.store[user_id] = dict()
            self.store[user_id]['data'] = dict()
            self.store[user_id]['inline_message'] = None

            return

        if kwargs.get('property') is None:
            e = self.store[user_id].get('event', Event())
            e.event_id = util.database.get_new_event_id()
            self.store[user_id]['event'] = e

            text = "Aktuell sieht der Termin folgendermaßen aus:\n" + e.get_detail_str() + "\n\nBitte wähle aus, um zu Daten einzugeben:"
            markup = InlineKeyboardMarkup(row_width=2)
            buttons = []
            for i, v in enumerate(meta.event_col_names_display):
                buttons.append(InlineKeyboardButton(text=v,
                                                    callback_data=self.command +
                                                    json.dumps({'property': meta.event_col_names[i]})))
            buttons.append(InlineKeyboardButton(text="Fertig", callback_data=self.command + json.dumps({'done': True,
                                                                                                        'property': ''})))
            buttons.append(InlineKeyboardButton(text="Abbrechen", callback_data="abort"))
            markup.add(*tuple(buttons))

            if inline_message:
                msg = bot.edit_message_text(inline_message=inline_message, text=text, reply_markup=markup)
            elif call:
                msg = bot.edit_message_text(call=call, text=text, reply_markup=markup)
            else:
                msg = bot.send_message(initial_message.chat.id, text=text, reply_markup=markup)
            self.store[user_id]['inline_message'] = msg
            return

        if kwargs['property'] == "dress":
            if kwargs.get('value') is None:
                text = "Okay, bitte wähle ein Outfit:"
                markup = InlineKeyboardMarkup(row_width=2)
                markup.add(*tuple([InlineKeyboardButton(text=s, callback_data=self.command + json.dumps(
                    {'value': s}
                )) for s in meta.dresses] +
                    [InlineKeyboardButton(text="Zurück", callback_data=self.command +
                                          json.dumps({'property': None, 'value': None}))]))
                bot.edit_message_text(text=text, inline_message=inline_message, reply_markup=markup)
            else:
                event = self.store[user_id]['event']
                event.dress = kwargs.pop('value')
                self.store[user_id]['data'].pop('value')
                self.store[user_id]['data'].pop('property')
                self.__call__(call=call)
            return

        else:
            prop_display = meta.event_col_names_display[meta.event_col_names.index(kwargs.get('property'))]
            text = "Okay, gib '{}' ein:".format(prop_display)
            hint = meta.event_col_names_hints.get(kwargs['property'])
            if hint is not None:
                text += "\n{}".format(hint)
            msg = bot.edit_message_text(inline_message=inline_message, text=text)
            bot.register_next_step_handler(msg, self.property_reply)
            return

    def property_reply(self, message):
        user_id = message.from_user.id
        event = self.store[user_id]['event']
        prop = self.store[user_id]['data'].pop('property')
        try:
            setattr(event, prop, message.text)
        except ValueError:
            pass  # TODO handle errors when new event property not valid
        self.__call__(user_message=message)


new_event = NewEventHandler(command='new_event')
