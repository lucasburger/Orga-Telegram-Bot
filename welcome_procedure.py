
import util.database as db
import meta
from util.classes import BotInstance, PWManager, bot, Frichtle
from util.functions import try_function
import markups

pw_manager = PWManager()


@try_function
def welcome_user(message):
    if db.exist_frichtle(message.from_user.id):
        bot.send_message(message.chat.id, 'Willkommen zurück. \nWie du diesen Bot benutzt, erfährst du von '
                                          '@LucasBurger oder in der Hilfe Sektion.',
                         reply_markup=markups.menu.main(message.from_user.id))
    else:
        if pw_manager.check_password(message.text.replace("/start ", "")):
            welcome(message)


@try_function
def welcome(message):
    new_frichtle = Frichtle.from_json({"user_id": message.from_user.id,
                                       "admin": False,
                                       "master": False,
                                       "name": "Neuling",
                                       "username": message.from_user.username})

    if new_frichtle.user_id == meta.lucas_user_id:
        new_frichtle.admin = True
        new_frichtle.master = True

    if new_frichtle.username is not None:
        text = 'Willkommen @{} beim Frichtle Bot!'.format(new_frichtle.username)
    else:
        text = "Willkommen beim Frichtle Bot!"

    bot.reply_to(message, text)
    db.add_frichtle(new_frichtle)
    msg = bot.send_message(message.chat.id,
                           text="Bitte gib deinen Namen, unter dem dich die anderen erkennen: 😉",)
    bot.register_next_step_handler(msg, process_name_reply)


@try_function
def process_name_reply(message):

    new_name = message.text
    db.update_frichtle(user_id=message.from_user.id, name=new_name)

    msg = bot.send_message(message.chat.id, text=f"Vielen Dank {new_name}.\nWähle dein Instrument:?",
                           reply_markup=markups.selection.instrument())
    bot.register_next_step_handler(msg, process_instrument_reply)


@try_function
def process_instrument_reply(message):
    mid = message.chat.id
    text = message.text

    if text in meta.instruments:
        db.set_instrument(message.from_user.id, text)
        text = "Instrument wurde gespeichert."
    else:
        db.remove_frichtle(message.from_user.id)
        bot.send_message(message.chat.id, text="Instrument wurde nicht erkannt.\n"
                                               "Vorgang abgebrochen. Zum Neustart, bitte erneut den Link verwenden.")
        return

    f = db.get_frichtle(user_id=message.from_user.id)
    bot.send_message(meta.lucas_chat_id, "{} ist dem FrichtleBot beigetreten.".format(f.get_inline_str()))

    bot.send_message(mid, text=text + " Du wirst zum Hauptmenü weitergeleitet.",
                     reply_markup=markups.menu.main(message.from_user.id))
