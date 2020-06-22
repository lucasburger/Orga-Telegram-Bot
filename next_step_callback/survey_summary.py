
import util.database as database
import util.functions
from util.classes import BotInstance, CallBackHandler, bot
import meta
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import json

# bot = BotInstance(token=meta.bot_token)


class SurveySummaryHandler(CallBackHandler):

    def main(self, initial_message=None, user_message=None, call=None, inline_message=None, **kwargs):

        if inline_message:
            user_id = inline_message.chat.id
        else:
            user_id = (initial_message or user_message or call).from_user.id

        if call:
            inline_message = call.message

        buttons = []
        markup = None

        surveys = util.database.get_survey()

        if len(surveys) == 0:
            bot.reply_to(initial_message, text="Es gibt aktuell keine Umfragen.")
            return

        if kwargs.get('survey_id') is None:
            text = "Wähle eine Umfrage aus:"
            markup = InlineKeyboardMarkup(row_width=1)
            buttons = list(InlineKeyboardButton(text=s.get_inline_str(),
                                                callback_data=self.command + json.dumps({'survey_id': s.survey_id}))
                           for s in database.get_survey())
            markup.add(*tuple(buttons))
            markup.add(InlineKeyboardButton("Beenden", callback_data="end"))
            if inline_message:
                msg = bot.edit_message_text(inline_message=inline_message, text=text, reply_markup=markup)
            else:
                msg = bot.send_message(initial_message.chat.id, text=text, reply_markup=markup)
            self.store[user_id]['inline_message'] = msg
            return

        survey = util.database.get_survey(survey_id=kwargs['survey_id'])

        text = util.functions.get_survey_summary(**kwargs)

        if not kwargs.get('detail', False):
            # erinnerung
            if kwargs['survey_id'] in [s.survey_id for s in util.database.surveys_that_need_reminder()] and \
                    not self.store[user_id].get('sent_reminder', False):
                buttons.append(InlineKeyboardButton(text="Erinnern", callback_data=self.command + json.dumps({'remind': True})))
            # detail
            if not kwargs.get('detail', False) and any(s is not None for s in survey.results.values()):
                buttons.append(InlineKeyboardButton(text="Details", callback_data=self.command + json.dumps({'detail': True})))

            # back button
            if kwargs.get('detail', False):
                dump = {'detail': False}
            else:
                dump = {'survey_id': None}

            buttons.append(InlineKeyboardButton(text="Zurück", callback_data=self.command + json.dumps(dump)))

            markup = InlineKeyboardMarkup(row_width=2)
            markup.add(*tuple(buttons))

        if kwargs.get('remind', False):
            util.functions.send_reminder_for(from_user_id=user_id, _id=kwargs['survey_id'])
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


survey_summary = SurveySummaryHandler(command='survey_summary')
