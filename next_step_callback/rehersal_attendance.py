import util.database as database
import util.functions
from util.classes import BotInstance, CallBackHandler, bot
import meta
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import json
import re
import datetime

# bot = BotInstance(token=meta.bot_token)


def check_email(email):
    EMAIL_REGEX = re.compile(r"[^@]+@[^@]+\.[^@]+")
    return EMAIL_REGEX.match(email)


class RehersalAttendanceHandler(CallBackHandler):

    def main(self, initial_message=None, user_message=None, call=None, inline_message=None, **kwargs):

        if inline_message:
            user_id = inline_message.chat.id
        else:
            user_id = (initial_message or user_message or call).from_user.id

        if initial_message:
            d = initial_message.text.replace('_probe', '').strip()
            self.store[user_id]['data']['date'] = d

        if call:
            inline_message = call.message

        if self.store[user_id].get('frichtle') is None:
            #self.store[user_id]['frichtle'] = util.database.get_frichtle()
            self.store[user_id]['frichtle'] = util.classes.fake_frichtle.copy()

        if self.store[user_id].get('set_frichtle') is None:
            self.store[user_id]['set_frichtle'] = []

        if len(self.store[user_id]['set_frichtle']) > 0:
            self.store[user_id]['set_frichtle'] = sorted(self.store[user_id]['set_frichtle'], key=lambda f: f.first_name)
            text = "Ausgewählte Frichtle:\n" + "\n".join([f.get_inline_str() for f in self.store[user_id]['set_frichtle']])
            text += "\n\n"
        else:
            text = ""

        if not kwargs.get('done', False):
            if kwargs.get('register') is None:
                text += "Wähle Register aus:"
                markup = InlineKeyboardMarkup(row_width=1)
                buttons = list(InlineKeyboardButton(text=r, callback_data=self.command + json.dumps({'register': r}))
                               for r in meta.registers.keys())
                markup.add(*tuple(buttons))
                markup.add(InlineKeyboardButton("Fertig", callback_data=self.command + json.dumps({'done': True})))
                markup.add(InlineKeyboardButton("Abbrechen", callback_data="abort"))
                if inline_message:
                    msg = bot.edit_message_text(inline_message=inline_message, text=text, reply_markup=markup)
                else:
                    msg = bot.send_message(initial_message.chat.id, text=text, reply_markup=markup)
                self.store[user_id]['inline_message'] = msg
                return

            if kwargs.get('user_id') is None:
                text += "Wähle Frichtle aus {} aus:".format(kwargs['register'])
                register_instruments = meta.registers[kwargs['register']]
                register_frichtle = list(filter(lambda f: f.instrument in register_instruments, self.store[user_id]['frichtle']))
                markup = InlineKeyboardMarkup(row_width=1)
                buttons = list(InlineKeyboardButton(text=f.get_inline_str(), callback_data=self.command + json.dumps({'user_id': f.user_id}))
                               for f in register_frichtle)
                markup.add(*tuple(buttons))
                markup.add(InlineKeyboardButton("Zurück", callback_data=self.command + json.dumps({'register': None})))
                if inline_message:
                    msg = bot.edit_message_text(inline_message=inline_message, text=text, reply_markup=markup)
                else:
                    msg = bot.send_message(initial_message.chat.id, text=text, reply_markup=markup)
                self.store[user_id]['inline_message'] = msg
                return

        if kwargs.get('done') is None:
            f = list(filter(lambda f: f.user_id == kwargs['user_id'], self.store[user_id]['frichtle']))[0]
            self.store[user_id]['frichtle'].pop(self.store[user_id]['frichtle'].index(f))
            self.store[user_id]['set_frichtle'].append(f)
            self.store[user_id]['data'].pop('user_id')
            self.__call__(inline_message=inline_message)
            return

        if kwargs.get('email') is None:
            text = "Okay, gib deine Email Adresse ein:\nFalls du keine Email erhalten möchtest, gib '0' ein."
            msg = bot.edit_message_text(inline_message=inline_message, text=text)
            bot.register_next_step_handler(msg, self.process_email)
            return

        if kwargs.get('send') is None:
            if kwargs['email'] == '':
                text += "Keine Email angegeben."
                button_text = "Speichern"
            else:
                text += "Email Adresse: {}".format(kwargs['email'])
                button_text = "Senden"
            markup = InlineKeyboardMarkup(row_width=2)
            markup.add(InlineKeyboardButton(text=button_text, callback_data=self.command + json.dumps({'send': True})),
                       InlineKeyboardButton(text="Zurück", callback_data=self.command + json.dumps({'send': False,
                                                                                                    'done': False})))
            if inline_message:
                msg = bot.edit_message_text(inline_message=inline_message, text=text, reply_markup=markup)
            else:
                msg = bot.send_message(initial_message.chat.id, text=text, reply_markup=markup)
            self.store[user_id]['inline_message'] = msg
            return

        if kwargs.get('send'):
            util.functions.save_rehersal_attendance(frichtle=self.store[user_id]['set_frichtle'],
                                                    date=self.store[user_id]['data']['date'])

            if '@' in kwargs.get('email'):
                email_text = util.functions.rehersal_email_text(frichtle=self.store[user_id]['set_frichtle'])
                subject = "Anwesenheit Probe {}".format(self.store[user_id]['data']['date'])
                success = util.functions.send_email(email=kwargs.get('email', 'Keine Email'),
                                                    subject=subject, text=email_text)

                if success:
                    text = "Okay, Email wurde gesendet. Anwesenheit abgeschlossen."
                else:
                    text = "Die Email konnte nicht versandt werden."
            else:
                text = "Es wurde keine Email versandt."

            text += "\nDie Anwesenheit wurde lokal gespeichert."
            bot.edit_message_text(inline_message=inline_message, text=text)
            return
        else:
            self.store[user_id]['done'] = False
            self.__call__(inline_message=inline_message)
        return

    def process_email(self, message):
        user_id = message.from_user.id
        if message.text == '0':
            self.store[user_id]['data']['email'] = ''
            bot.delete_message(message=message)
            self.__call__(user_message=message)
        elif check_email(message.text):
            self.store[user_id]['data']['email'] = message.text
            bot.delete_message(message=message)
            self.__call__(user_message=message)
        else:
            text = "Die Email wurde nicht erkannt. Bitte versuche es erneut:"
            bot.delete_message(message=message)
            msg = bot.edit_message_text(inline_message=self.store[user_id]['inline_message'], text=text)
            bot.register_next_step_handler(msg, self.process_email)

        return


rehersal_attendance = RehersalAttendanceHandler(command='reh_att')

