
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from util.database import is_admin, is_master


def main(user_id=None):
    markup = ReplyKeyboardMarkup(row_width=2)
    markup.add(KeyboardButton("❓ Hilfe ❓"), KeyboardButton("🏷 Umfragen"))
    markup.add(KeyboardButton("📅 Termine"), KeyboardButton("👥 Frichtle"))
    if user_id is not None and is_admin(user_id):
        markup.row(KeyboardButton("Admin Menü"))
    if user_id is not None and is_master(user_id):
        markup.row(KeyboardButton("Master Menü"))
    return markup


def admin():
    markup = ReplyKeyboardMarkup(row_width=2)
    markup.add(KeyboardButton("📆 Terminzusammenfassung"), KeyboardButton("ℹ️ Umfrageergebnis"))
    markup.row(KeyboardButton("🔙 Hauptmenü"))
    return markup


def admin_old():
    markup = ReplyKeyboardMarkup(row_width=2)
    markup.add(KeyboardButton("📆 Termine verwalten"), KeyboardButton("🏷 Umfragen verwalten"))
    markup.add(KeyboardButton("🔔 Erinnerung senden"), KeyboardButton("🔙 Hauptmenü"))
    return markup


def reminder():
    markup = ReplyKeyboardMarkup(row_width=2)
    markup.add(KeyboardButton("Erinnerung für Event"), KeyboardButton("Erinnerung für Umfrage"))
    markup.row(KeyboardButton("Admin Menü"))
    return markup


def events():
    markup = ReplyKeyboardMarkup(row_width=2)
    markup.add(KeyboardButton("🎭 Alle Termine mit Details"), KeyboardButton("⁉️ Ausstehende Rückmeldungen"))
    markup.add(KeyboardButton("✅ Meine Zusagen"), KeyboardButton("❌ Meine Absagen"))
    markup.row(KeyboardButton("Hauptmenü"))
    return markup


def manage_events():
    markup = ReplyKeyboardMarkup(row_width=2)
    markup.add(KeyboardButton("🆕 Neuer Termin"), KeyboardButton("🔄 Termin bearbeiten"))
    markup.add(KeyboardButton("ℹ️ Terminzusammenfassung"), KeyboardButton("⏹ Termin absagen"))
    markup.row(KeyboardButton("🔙 Admin Menü"))
    return markup


def surveys():
    markup = ReplyKeyboardMarkup(row_width=2)
    markup.add(KeyboardButton("📊 Alle Umfragen"), KeyboardButton("⁉️ Unbeantwortete Umfragen"))
    markup.row(KeyboardButton("Hauptmenü"))
    return markup


def manage_surveys():
    markup = ReplyKeyboardMarkup(row_width=2)
    markup.add(KeyboardButton("🆕 Neue Umfrage"), KeyboardButton("ℹ️ Umfrageergebnis"))
    markup.row(KeyboardButton("🔙 Admin Menü"))
    return markup


def master():
    markup = ReplyKeyboardMarkup(row_width=2)
    markup.row(KeyboardButton("📝 Show Table"))
    # markup.add(KeyboardButton("📝 Show Table"), KeyboardButton("SQL Command"))
    markup.add(KeyboardButton("Manage Members"), KeyboardButton("Remove Event")),
    markup.row(KeyboardButton("Remove Survey"), KeyboardButton("🔙 Main Menu"))
    return markup


def manage_members():
    markup = ReplyKeyboardMarkup(row_width=2)
    markup.add(KeyboardButton("🆕 New Admin"), KeyboardButton("🚷 Remove Admin"))
    markup.add(KeyboardButton("🚷 Remove User"), KeyboardButton("Invite Link"))
    markup.row(KeyboardButton("🔙 Master Menü"))
    return markup
