

import util.database as database
import util.functions
from util.classes import BotInstance, CallBackHandler, bot
import meta
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import json

# bot = BotInstance(token=meta.bot_token)


class CloseSurveyHandler(CallBackHandler):

    def main(self, initial_message=None, user_message=None, call=None, inline_message=None, **kwargs):

        if inline_message:
            user_id = inline_message.chat.id
        else:
            user_id = (initial_message or user_message or call).from_user.id

        if call:
            inline_message = call.message

        surveys = util.database.get_survey()

        if len(surveys) == 0:
            bot.reply_to(initial_message, text="Es gibt keine Umfragen.")
            return

        if 'survey_id' not in kwargs.keys():
            text = "Wähle eine Umfrage aus, die du schließen möchtest:"
            markup = InlineKeyboardMarkup(row_width=1)
            buttons = list(InlineKeyboardButton(text=s.get_inline_str(),
                                                callback_data=self.command + json.dumps({'survey_id': s.survey_id}))
                           for s in surveys)
            markup.add(*tuple(buttons))
            markup.add(InlineKeyboardButton("Abbrechen", callback_data="abort"))
            msg = bot.send_message(initial_message.chat.id, text=text, reply_markup=markup)
            self.store[user_id]['inline_message'] = msg
            return

        if 'sure' not in kwargs.keys():
            survey = database.get_survey(survey_id=kwargs.get('survey_id'))
            text = "Bist du sicher, dass du folgende Umfrage schließen möchtest?\n\n" + survey.get_detail_str()
            markup = InlineKeyboardMarkup(row_width=2)
            markup.add(InlineKeyboardButton(text="Ja", callback_data=self.command + json.dumps({'sure': True})),
                       InlineKeyboardButton(text="Nein", callback_data=self.command + json.dumps({'sure': False})))
            markup.add(InlineKeyboardButton(text="Abbrechen", callback_data="abort"))
            bot.edit_message_text(inline_message=inline_message, text=text, reply_markup=markup)
            return

        if not kwargs['sure']:
            text = "Schade, dann ist wohl etwas schiefgegangen... Bitte versuche es ggfs erneut."
        else:
            text = "Okay, die Umfrage wurde geschlossen. Antworten können nicht mehr geändert werden."
            util.database.close_survey(survey_id=kwargs['survey_id'])

        bot.edit_message_text(inline_message=inline_message, text=text)
        self.store[user_id] = dict()
        self.store[user_id]['data'] = dict()
        self.store[user_id]['inline_message'] = None
        return


close_survey = CloseSurveyHandler(command='close_survey')
