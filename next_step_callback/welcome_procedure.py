

import util.database as database
import util.functions
from util.classes import BotInstance, CallBackHandler, Frichtle, bot
import meta
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import json
import markups

# bot = BotInstance(token=meta.bot_token)


class WelcomeProcedureHandler(CallBackHandler):

    def main(self, initial_message=None, user_message=None, call=None, inline_message=None, **kwargs):

        if initial_message:
            f = Frichtle.from_user(initial_message.from_user)
            user_id = f.user_id
            self.store[user_id]['new_frichtle'] = f

        else:
            if inline_message:
                user_id = inline_message.chat.id
            else:
                user_id = (initial_message or user_message or call).from_user.id
            f = self.store[user_id]['new_frichtle']

        text = "Hallo {},\n\n".format(f.first_name)

        if user_message:
            bot.delete_message(chat_id=user_message.chat.id, message_id=user_message.message_id)

        if call:
            inline_message = call.message

        if inline_message is None:
            inline_message = self.store[user_id]['inline_message']

        if 'abort' in kwargs.keys():
            del self.store[user_id]
            bot.edit_message_text(inline_message=inline_message, text="Der Vorgang wurde abgebrochen und deine angegebenen Daten wurden gelöscht. Falls du möchtest, starte bitte erneut über den Einladungslink.\nLieben Gruß\nLucas")

        if 'done' in kwargs.keys() and kwargs.get('done'):
            util.database.add_frichtle(self.store[user_id]['new_frichtle'])
            bot.edit_message_text(inline_message=inline_message, text="Okay, du wurdest gespeichert und wirst jetzt zum Hauptmenü weitergeleitet.")
            bot.send_message(chat_id=user_id, text="Hauptmenü", reply_markup=markups.menu.main(user_id=user_id))
            return

        if initial_message:
            text += "Du hast folgenden Namen in Telegram hinterlegt:\n{} {}\nMöchtest du einen anderen Namen eingeben, mit dem dich andere sehen können? Ein Name, unter dem man dich erkennt wäre sehr hilfreich 😉".format(f.first_name, f.last_name)
            markup = InlineKeyboardMarkup(row_width=2)
            buttons = [InlineKeyboardButton(text="Ja, bitte", callback_data=self.command + json.dumps({'name_okay': False})),
                       InlineKeyboardButton(text="Nein, passt", callback_data=self.command + json.dumps({'name_okay': True}))]
            markup.add(*tuple(buttons))
            if inline_message:
                msg = bot.edit_message_text(inline_message=inline_message, text=text, reply_markup=markup)
            else:
                msg = bot.send_message(initial_message.chat.id, text=text, reply_markup=markup)
            self.store[user_id]['inline_message'] = msg
            return

        if not kwargs.get('name_okay'):
            text += "Okay, bitte gib einen anderen Namen ein:"
            msg = bot.edit_message_text(inline_message=self.store[user_id]['inline_message'],
                                        text=text)
            bot.register_next_step_handler(msg, self.change_name_reply)
            return

        if kwargs.get('instr', None) is None:
            text += "Bitte wähle dein Instrument?"
            markup = InlineKeyboardMarkup(row_width=2)
            buttons = [InlineKeyboardButton(text=instr, callback_data=self.command + json.dumps({'instr': instr}))
                       for instr in meta.instruments]
            markup.add(*tuple(buttons))
            bot.edit_message_text(text=text, inline_message=inline_message, reply_markup=markup)
            return
        else:
            self.store[user_id]['new_frichtle'].instrument = kwargs.get('instr')

        if not kwargs.get('done', False):
            text += "Die folgenden Daten werden in einer verschlüsselten Datenbank abgelegt. Dieser Bot steht in keiner direkten Verbindung zum Verein und umgeht deshalb jegliche Richtlinien der DSGVO. Bei Fragen zur Datenspeicherung, kannst du jederzeit Lucas (@LucasBurger) anschreiben.\n\n"
            text += "Zusammenfassung:\n{}\n\nEinverstanden?".format(self.store[user_id]['new_frichtle'].get_detail_str())
            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton(text="Instrument ändern", callback_data=self.command + json.dumps({'instr': None})))
            markup.add(InlineKeyboardButton(text="Name ändern",
                                            callback_data=self.command + json.dumps({'name_okay': False})))
            markup.add(InlineKeyboardButton(text="Einverstanden!",
                                            callback_data=self.command + json.dumps({'done': True})))
            bot.edit_message_text(text=text, inline_message=inline_message, reply_markup=markup)

        return

    def change_name_reply(self, message):
        user_id = message.from_user.id
        s = message.text.split()
        first_name = s[0]
        if len(s) == 2:
            last_name = s[1]
        elif len(s) > 2:
            last_name = " ".join(s[1:])
        else:
            last_name = ''

        self.store[user_id]['new_frichtle'].first_name = first_name
        self.store[user_id]['new_frichtle'].last_name = last_name
        self.store[user_id]['data']['name_okay'] = True

        self.__call__(user_message=message)


welcome_procedure = WelcomeProcedureHandler(command='welcome', vault_file='')
