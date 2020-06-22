# everything that is needed
import telebot
import meta
import re
import random
import string
from datetime import datetime, timedelta
import json
from util.util import convert_from_database, convert_to_database
import copy


DATEFORMAT = "%Y-%m-%dT%H:%M:%S.%f"


class PWManager(object):

    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(PWManager, cls).__new__(cls)

        return cls._instance

    def __init__(self):
        self.file_name = 'vault/.passwords.json'

        try:
            with open(self.file_name, 'r') as fp:
                self.pw = json.load(fp)
        except FileNotFoundError:
            self.pw = {}
            with open(self.file_name, 'w') as fp:
                json.dump(self.pw, fp, indent=4)

    def generate(self):

        for key, value in self.pw.items():
            if (datetime.strptime(value, DATEFORMAT)-datetime.now()).total_seconds() > 72000:
                return key

        new_pw = ''.join(random.choice(string.ascii_lowercase) for _ in range(20))
        self.pw[new_pw] = (datetime.now() + timedelta(days=1)).strftime(DATEFORMAT)

        with open(self.file_name, 'w') as fp:
            json.dump(self.pw, fp)

        return new_pw

    def check_password(self, x):
        if x in self.pw.keys():
            if datetime.strptime(self.pw[x], DATEFORMAT) > datetime.now():
                return True
        return False


class Frichtle:

    @classmethod
    def from_json(cls, js):

        js = convert_from_database(js)
        if "user_id" not in js.keys():
            return [cls.from_json(v) for v in js.values()]

        f = Frichtle()
        f.name = js.get("name", "")
        f.user_id = js.get("user_id", 0)
        f.username = js.get("username", "")
        f.instrument = js.get("instrument", "")
        f.admin = js.get("admin", False)
        f.master = js.get("master", False)
        return f

    def to_json(self):
        js = {
            "name": self.name,
            "user_id": self.user_id,
            "username": self.username,
            "instrument": self.instrument,
            "admin": self.admin,
            "master": self.master
        }
        return js

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __str__(self):
        return str(self.to_json())

    def get_inline_str(self):
        s = self.name
        if self.username is not None:
            s += " (@" + self.username + ")"
        return s


class Event:
    date_format = "%d.%m.%y %H:%M"
    hour_format = "%H:%M"
    _start_time = None
    _end_time = None
    location = None
    meeting_point = None
    long_description = None
    dress = None

    @classmethod
    def from_json(cls, js):

        js = convert_from_database(js)

        if "start_time" not in js.keys():
            return [cls.from_json(v) for v in js.values()]

        e = Event()
        e.event_id = js.get("event_id")
        e.start_time = js.get("start_time", "")
        e.end_time = js.get("end_time", "")
        e.location = js.get("location", "?")
        e.meeting_point = js.get("meeting_point", "?")
        e.description = js.get("description", "")
        e.long_description = js.get("long_description", "")
        e.dress = js.get("dress", "?")
        e.active = js.get("active", True)
        e.attendance = js.get("attendance", {})
        return e

    def to_json(self):
        js = {
            "event_id": self.event_id,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "location": self.location,
            "meeting_point": self.meeting_point,
            "description": self.description,
            "long_description": self.long_description,
            "dress": self.dress,
            "active": self.active,
            "attendance": self.attendance
        }
        return convert_to_database(js)

    def __init__(self):
        self.start_time = "01.01.00 00:00"
        self.end_time = None
        self.location = '?'
        self.description = '?'
        self.meeting_point = '?'
        self.long_description = None
        self.dress = '?'
        self.active = True
        self.attendance = []

    def str_rep(self):
        s = ""
        s += self.start_time

        if self._end_time:
            s += "-"
            if self._start_time.day == self._end_time.day:
                s += self._end_time.strftime(self.hour_format)
            else:
                s += self._end_time.strftime(self.date_format)

        s = s + ": " + self.description + " in " + self.location

        s += ", Treffpunkt: " + self.meeting_point

        if self.dress is not None:
            s += ", Outfit: " + self.dress
        return s

    def __str__(self):
        return self.str_rep()

    def get_inline_str(self):
        return self._start_time.strftime("%d.%m.") + ": " + self.description

    def get_detail_str(self):
        s = self.__str__()
        if self.long_description:
            s += "\nWeitere Details:\n" + self.long_description
        return s

    def get_start_time(self):
        return self._start_time

    def get_end_time(self):
        return self._end_time

    @property
    def start_time(self):
        if self._start_time:
            return self._start_time.strftime(self.date_format)
        else:
            return ''

    @property
    def end_time(self):
        if self._end_time:
            return self._end_time.strftime(self.date_format)
        else:
            return ''

    @start_time.setter
    def start_time(self, x):
        if isinstance(x, datetime):
            self._start_time = x
        elif isinstance(x, str):
            self._start_time = datetime.strptime(x, self.date_format)

    @end_time.setter
    def end_time(self, x):
        if isinstance(x, datetime):
            self._end_time = x
        elif isinstance(x, str):
            self._end_time = datetime.strptime(x, self.date_format)

    @property
    def id(self):
        return self.event_id


class Survey:
    description = None
    questions = []
    creator = None
    survey_id = None

    _base_questions = [{"question": "?",
                        "answers": "free"}]

    @classmethod
    def from_db(cls, tuple_list):
        for t in tuple_list:
            returncls = Survey()
            for i, v in enumerate(meta.survey_col_names):
                setattr(returncls, v, t[i])
            yield returncls

    @classmethod
    def from_json(cls, js):

        js = convert_from_database(js)
        if "questions" not in js.keys():
            return [cls.from_json(v) for v in js.values()]

        s = Survey()
        s.survey_id = js.get("survey_id")
        s.description = js.get("description")
        s.questions = js.get("questions")
        s.summary_function = js.get("summary_function", None)
        s.creator = js.get("creator")
        s.active = js.get("active", True)
        return s

    def to_json(self):
        js = {
            "survey_id": self.survey_id,
            "description": self.description,
            "questions": self.questions,
            "summary_function": self.summary_function,
            "creator": self.creator,
            "active": self.active
        }
        return convert_to_database(js)

    def str_rep(self, question=None):
        s = "Beschreibung: " + self.description
        if len(self.questions) > 1 and question is None:
            s += "\nFragen:\n"
            s += "\n".join([f" {c+1}.) " + q["question"] for c, q in enumerate(self.questions)])
        elif len(self.questions) > 1 and question is not None:
            s += "\n" + self.questions[question]["question"]
        elif len(self.questions) == 1:
            s += "\n" + self.questions[0]["question"]

        return s

    def __str__(self):
        return self.str_rep()

    def get_inline_str(self):
        return self.description

    def get_detail_str(self, question=None):
        return self.str_rep(question=question)

    @property
    def results(self):
        r = {}
        for k in self.questions[0]["results"].keys():
            a = []
            for q in self.questions:
                if q["results"][k] is None:
                    r[k] = None
                    break
                else:
                    a.append(str(q["results"][k]))
            else:
                r[k] = " ".join(a)

        return r

    @property
    def id(self):
        return self.survey_id


class BotInstance(telebot.TeleBot):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(BotInstance, cls).__new__(cls)

        return cls._instance

    def edit_message_reply_markup(self, *args, call=None, **kwargs):
        if call is not None:
            kwargs['chat_id'] = call.message.chat.id
            kwargs['message_id'] = call.message.message_id

        return super().edit_message_reply_markup(*args, **kwargs)

    def edit_message_text(self, *args, call=None, inline_message=None, **kwargs):
        if call is not None:
            kwargs['chat_id'] = call.message.chat.id
            kwargs['message_id'] = call.message.message_id

        if inline_message is not None:
            kwargs['inline_message_id'] = inline_message.message_id
            kwargs['chat_id'] = inline_message.chat.id
            kwargs['message_id'] = inline_message.message_id

        if "*" in kwargs.get('text', ""):
            if 'parse_mode' not in kwargs.keys():
                kwargs['parse_mode'] = 'Markdown'

        return super().edit_message_text(*args, **kwargs)

    def send_message(self, *args, **kwargs):

        if "*" in kwargs.get('text', ""):
            if 'parse_mode' not in kwargs.keys():
                kwargs['parse_mode'] = 'Markdown'

        return super().send_message(*args, **kwargs)

    def reply_to(self, *args, **kwargs):

        if "*" in kwargs.get('text', ""):
            if 'parse_mode' not in kwargs.keys():
                kwargs['parse_mode'] = 'Markdown'

        return super().reply_to(*args, **kwargs)

    def delete_message(self, *args, message=None, **kwargs):
        if message is not None:
            kwargs['chat_id'] = message.chat.id
            kwargs['message_id'] = message.message_id
        return super().delete_message(**kwargs)


bot = BotInstance(token=meta.bot_token, threaded=False)


callback_commands = {}


def to_json(d):
    if type(d) == dict:
        for key, value in d.items():
            d[key] = to_json(value)
    else:
        if isinstance(d, telebot.types.Message):
            return json.dumps(d.json)
        else:
            try:
                return json.dumps(d)
            except:
                pass
    return d


def from_json(d):
    if type(d) == dict:
        for key, value in d.items():
            try:
                d[key] = telebot.types.Message.de_json(value)
            except:
                d[key] = from_json(value)
    return d


class CallBackHandler(object):

    def __init__(self, command, vault_file=None):
        if vault_file is None:
            vault_file = 'vault/.{}_save.json'.format(command)
        self.vault_file = vault_file
        try:
            self.store = self.load_from_file(vault_file)
        except:
            self.store = {}
        self.command = command + ';'
        callback_commands[command] = self

    @staticmethod
    def save_to_file(vault_file, d):
        with open(vault_file, 'w') as f:
            json.dump(to_json(d), f)
        return

    @staticmethod
    def load_from_file(vault_file):
        try:
            with open(vault_file, 'r') as f:
                d = json.load(f)
        except FileNotFoundError:
            d = None
        if d is not None:
            try:
                return from_json(d)
            except:
                pass
        else:
            d = dict()

        return d

    @staticmethod
    def load_data(call):
        s = call.data.split(";")
        try:
            ret = json.loads(s[1])
        except:
            ret = dict()
        return ret

    def __call__(self, initial_message=None, user_message=None, call=None):

        user_id = (initial_message or user_message or call).from_user.id

        if user_id not in self.store.keys() or initial_message:
            self.store[user_id] = dict()
            self.store[user_id]['data'] = dict()
            self.store[user_id]['inline_message'] = None

        if initial_message:
            inline = self.store[user_id].get('inline_message', None)
            if inline:
                bot.edit_message_text(inline_message=inline, text="Nachricht nicht mehr verfügbar.")

        if call:
            last_inline = self.store[user_id].get('inline_message', None)
            if last_inline and call.message.message_id != last_inline.message_id:
                bot.edit_message_text(inline_message=last_inline, text="Nachricht nicht mehr verfügbar.")
            else:
                self.store[user_id]['data'].update(self.load_data(call))
            self.store[user_id]['inline_message'] = call.message
            inline_message = call.message
        else:
            inline_message = self.store[user_id].get('inline_message', None)

        self.main(initial_message=initial_message, user_message=user_message, inline_message=inline_message, call=call,
                  **self.store[user_id]['data'])

        try:
            self.save_to_file(vault_file=self.vault_file, d=copy.deepcopy(self.store))
        except:
            pass

    def main(self, *args, **kwargs):
        raise NotImplementedError
