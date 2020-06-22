

import util.database as database
import util.functions
from util.classes import BotInstance, CallBackHandler, bot
import meta
import markups
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import json

# bot = BotInstance(token=meta.bot_token)


class ShowSurveyHandler(CallBackHandler):

    def main(self, initial_message=None, user_message=None, call=None, inline_message=None, **kwargs):

        if inline_message:
            user_id = inline_message.chat.id
        else:
            user_id = (initial_message or user_message or call).from_user.id

        surveys = util.database.get_survey()

        if len(surveys) == 0:
            bot.reply_to(message=initial_message, text="Es gibt aktuell keine Umfragen.")
            del self.store[user_id]
            return

        if call:
            inline_message = call.message

        if user_message:
            bot.delete_message(chat_id=user_message.chat.id, message_id=user_message.message_id)

        if kwargs.get('survey_id', None) is None:
            text = "Welche Umfrage möchtest du anzeigen?"

            buttons = []
            for s in surveys:
                if util.database.check_survey_response(user_id=user_id, survey_id=s.survey_id) is None:
                    replace = "Unbeantwortet: "
                else:
                    replace = ""
                buttons.append(InlineKeyboardButton(text=s.get_inline_str().replace("Umfrage: ", replace),
                                                    callback_data=self.command +
                                                    json.dumps({'survey_id': s.survey_id})))
            markup = InlineKeyboardMarkup(row_width=1)
            markup.add(*tuple(buttons))
            markup.add(InlineKeyboardButton("Beenden", callback_data="end"))

            if inline_message:
                msg = bot.edit_message_text(inline_message=inline_message, text=text, reply_markup=markup)
            else:
                msg = bot.send_message(initial_message.chat.id, text=text, reply_markup=markup)
            self.store[user_id]['inline_message'] = msg
            return

        survey = util.database.get_survey(survey_id=kwargs['survey_id'])

        if kwargs.get('edit', None) is None:
            text = survey.get_detail_str()
            res = survey.results[user_id]
            buttons = []
            if res is None:
                text += "\n\nDu hast noch nicht geantwortet."
                buttons.append(InlineKeyboardButton(text="Jetzt antworten",
                                                    callback_data=self.command + json.dumps({'edit': True})))
            else:
                text += "\n\nDu hast mit '{}' geantwortet".format(res)
                if survey.active:
                    buttons.append(InlineKeyboardButton(text="Ändern",
                                                        callback_data=self.command + json.dumps({'edit': True})))
            if not survey.active:
                text += "\nDie Umfrage ist geschlossen."
            buttons.append(InlineKeyboardButton(text="Zurück", callback_data=self.command + json.dumps({'survey_id': None})))

            markup = InlineKeyboardMarkup(row_width=2)
            markup.add(*tuple(buttons))
            bot.edit_message_text(inline_message=inline_message, text=text, reply_markup=markup)
            return

        if kwargs["edit"] and self.store[user_id]["data"].get("response", None) is None:
            self.store[user_id]["data"]["response"] = [None] * len(survey.questions)

        res = kwargs.pop("res", None)
        if res is not None:
            self.store[user_id]["data"]["response"][res[0]] = res[1]

        i = 0
        while i < len(survey.questions):
            if self.store[user_id]["data"]["response"][i] is None:
                break
            i += 1

        if i < len(survey.questions):
            text = survey.get_detail_str(question=i) + "\n\nWie lautet deine Antwort?"
            if isinstance(survey.questions[i]["answers"], list):
                buttons = []
                for r in survey.questions[i]["answers"]:
                    buttons.append(InlineKeyboardButton(text=r, callback_data=self.command + json.dumps({'res': [i, r]})))
                markup = InlineKeyboardMarkup(row_width=2)
                markup.add(*tuple(buttons),
                           InlineKeyboardButton(text="Zurück", callback_data=self.command + json.dumps({'edit': None})))
            elif survey.questions[i]["answers"].lower() == 'count':
                page = kwargs.get('page', 1)
                markup = markups.inline.show_numbers(command=self.command, return_name='res', question=i, page=page)
            else:
                # free reply
                text = survey.get_detail_str() + "\n\nOkay, gib deine Antwort ein:"
                msg = bot.edit_message_text(inline_message=inline_message, text=text)
                bot.register_next_step_handler(msg, self.survey_reply, question=i)
                return

            if i < len(survey.questions):
                bot.edit_message_text(inline_message=inline_message, text=text, reply_markup=markup)
                return

        util.database.set_response_to_survey(survey_id=kwargs['survey_id'], user_id=user_id, response=self.store[user_id]["data"]["response"])

        final_answer = " ".join([str(r) for r in self.store[user_id]["data"]["response"]])

        text = f"\n\nDu hast mit '{final_answer}' geantwortet."

        text += "\n Wähle neue Umfrage aus:"

        buttons = []
        for s in surveys:
            if util.database.check_survey_response(user_id=user_id, survey_id=s.survey_id) == '':
                replace = "Unbeantwortet: "
            else:
                replace = ""
            buttons.append(InlineKeyboardButton(text=s.get_inline_str().replace("Umfrage: ", replace),
                                                callback_data=self.command +
                                                json.dumps({'survey_id': s.survey_id})))
        markup = InlineKeyboardMarkup(row_width=1)
        markup.add(*tuple(buttons))
        markup.add(InlineKeyboardButton("Beenden", callback_data="end"))

        self.store[user_id]['data'].update({'survey_id': None, 'edit': None, 'res': None, "response": None})

        bot.edit_message_text(inline_message=inline_message, text=text, reply_markup=markup)

    def survey_reply(self, message, question=0):
        user_id = message.from_user.id
        # survey_id = self.store[user_id]['data']['survey_id']
        self.store[user_id]["data"]["response"][question] = message.text
        # util.database.set_response_to_survey(survey_id=survey_id, user_id=user_id, response=message.text)
        # self.store[user_id]['data'].pop('edit')
        self.__call__(user_message=message)


show_survey = ShowSurveyHandler(command='show_survey')
