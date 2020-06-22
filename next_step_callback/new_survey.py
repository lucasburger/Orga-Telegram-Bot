

import util.database as database
import util.functions
from util.classes import BotInstance, CallBackHandler, Survey, bot
import meta
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import json

# bot = BotInstance(token=meta.bot_token)


class NewSurveyHandler(CallBackHandler):

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
            bot.reply_to(initial_message, text=meta.new_survey_guide)

        if kwargs.get('done', False):
            # send sure reply markup
            if kwargs.get('sure') is None:
                survey = self.store[user_id]['survey']
                text = "Die Umfrage lautet:\n" + survey.get_detail_str() + "\n\nSoll sie gespeichert werden?"
                markup = InlineKeyboardMarkup(row_width=2)
                markup.add(InlineKeyboardButton(text="Ja", callback_data=self.command + json.dumps({'sure': True})),
                           InlineKeyboardButton(text="Nein", callback_data=self.command + json.dumps({'sure': None,
                                                                                                      'done': None})))
                bot.edit_message_text(inline_message=inline_message, text=text, reply_markup=markup)
                return

            if not kwargs['sure']:
                self.store[user_id]['data'].pop('done')
                self.store[user_id]['data'].pop('sure')
                self.__call__(call=call)
                return

            if kwargs.get('send_notice') is None:
                if not kwargs.get('sure'):
                    self.store[user_id]['property'] = None
                    self.__call__(call=call)
                    return
                else:
                    survey = self.store[user_id]['survey']
                    database.add_survey(survey)
                    text = "Okay, die Umfrage wurde erstellt.\n" \
                           "Möchtest du alle wissen lassen, sodass sie reagieren können?"
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
                util.functions.send_new_survey_alert(by=util.database.get_frichtle(user_id=user_id),
                                                     survey=self.store[user_id]['survey'])

            bot.edit_message_text(inline_message=inline_message, text=text)
            self.store[user_id] = dict()
            self.store[user_id]['data'] = dict()
            self.store[user_id]['inline_message'] = None

            return

        if kwargs.get('property') is None:
            s = self.store[user_id].get('survey', Survey())
            s.survey_id = util.database.get_new_survey_id()
            self.store[user_id]['survey'] = s

            text = "Aktuell sieht die Umfrage folgendermaßen aus:\n" + s.get_detail_str() + "\n\nBitte wähle aus, um zu Daten einzugeben:"
            markup = InlineKeyboardMarkup(row_width=2)
            buttons = []
            for i, v in enumerate(meta.survey_col_names_display):
                buttons.append(InlineKeyboardButton(text=v,
                                                    callback_data=self.command +
                                                    json.dumps({'property': meta.survey_col_names[i]})))
            buttons.append(InlineKeyboardButton(text="Fertig", callback_data=self.command + json.dumps({'done': True,
                                                                                                        'property': None})))
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

        prop_display = meta.survey_col_names_display[meta.survey_col_names.index(kwargs.get('property'))]
        text = "Okay, gib '{}' ein:".format(prop_display)
        hint = meta.survey_col_names_hints.get(kwargs['property'])
        if hint is not None:
            text += "\n{}".format(hint)
        msg = bot.edit_message_text(inline_message=inline_message, text=text)
        bot.register_next_step_handler(msg, self.property_reply)

        return

    def property_reply(self, message):
        user_id = message.from_user.id
        survey = self.store[user_id]['survey']
        prop = self.store[user_id]['data'].pop('property')
        try:
            setattr(survey, prop, message.text)
        except:
            pass  # TODO handle errors when new survey property not valid
        self.__call__(user_message=message)


new_survey = NewSurveyHandler(command='new_survey')
