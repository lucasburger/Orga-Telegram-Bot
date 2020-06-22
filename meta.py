
import os
import json


db = '.vault/frichtle_bot.db'
bot_token = 'XXXXXXXXXX'

invite_link_base = 't.me/Frichtle_bot?start='

registers = json.load(open('metadata/registers.json'))

instruments = []
for i in registers.values():
    instruments.extend(i)
instruments = sorted(instruments)


dresses = json.load(open('metadata/dresses.json'))

frichtle_col_names = ('name', 'username', 'instrument',
                      'user_id', 'admin', 'master')
frichtle_col_types = {'name': str, 'username': str, 'instrument': str,
                      'user_id': int, 'admin': int, 'master': int}

event_col_names = ['start_time', 'end_time', 'location', 'meeting_point', 'description', 'long_description', 'dress', 'event_id', 'active']
event_col_names_display = ['Start', 'Ende', 'Ort', 'Treffpunkt', 'Kurze Beschreibung', 'Ausführliche Beschreibung', 'Outfit']

event_col_names_hints = json.load(open('metadata/event_col_names_hints.json', 'r'))

survey_col_names = ['description', 'question', 'answers', 'survey_id', 'active']
survey_col_names_display = ['Beschreibung', 'Frage', 'Antwort']

survey_col_names_hints = {
    'answers': "Gib die Antwortmöglichkeiten mit Komma (,) getrennt ein.\nFalls du eine Zahl als Antwort haben möchtest, antworte mit 'Zahl'.\nFalls jeder eine eigene Antwort schreiben darf, antworte 'Frei'."}

lucas_chat_id = 123456789
lucas_user_id = 123456789

help_message_user = help_message_master = help_message_admin = "Hier hast du nochmals die Anleitung als PDF. Sonst frage gegebenenfalls Lucas (@LucasBurger) 😁."

error_text = open('metadata/error_text.txt', 'r').read()


event_id_base = "ev{:02d}"
survey_id_base = "su{:02d}"


new_event_guide = open('metadata/new_event_guide.txt', 'r').read()
event_summary_template = open('metadata/event_summary_template.txt', 'r').read()

max_len = 0
for instr in registers.values():
    for i in instr:
        max_len = max(max_len, len(i))

for r, instr in registers.items():
    event_summary_template += "*" + r + "*:\n"
    for i in instr:
        event_summary_template += "{i: <{w}}: {{{j}}}\n".format(i=i, j=i, w=max_len)
    event_summary_template += "\n"


new_survey_guide = open('metadata/new_survey_guide.txt', 'r').read()
survey_summary_template = open('metadata/survey_summary_template.txt', 'r').read()

attend_event_answers = json.load(open('metadata/attend_event_answers.json', 'r'))
sql_command_hints = open('metadata/sql_command_hints.txt', 'r').read()
email_template = open('metadata/email_template.txt', 'r').read()
what_is_saved_from_me_template = open('metadata/what_is_saved_from_me_template.txt', 'r').read()


help_pdf_filename = os.path.abspath("DummyPDF.pdf")
