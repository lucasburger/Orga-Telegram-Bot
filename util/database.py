
from util.classes import Frichtle, Event, Survey
import meta
import json
import os
from pymongo import MongoClient
from telebot import logger
import telebot


class OwnUser(telebot.types.User):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        f = get_frichtle(user_id=self.id)
        if f:
            self.exist = True
            self.is_admin = is_admin(self.id)
            self.is_master = is_master(self.id)
        else:
            self.exist = self.is_admin = self.is_master = False


telebot.types.User = OwnUser

event_col_names = meta.event_col_names

client = MongoClient("192.168.178.50", 27017)

db = client.frichtle_bot


def add_frichtle(f):

    try:
        db.users.insert_one(f.to_json())
    except Exception as e:
        print(e)

    db.events.update_many({}, {"$set": {f"attendance._{f.user_id}": 1}})

    for s in db.surveys.find():
        for i in range(len(s["questions"])):
            db.surveys.update_one({"_id": s["_id"]}, {"$set": {f"questions.{i}.results._{f.user_id}": None}})

    logger.info(f"Added Frichtle " + str(f))

    return


def update_frichtle(user_id, **kwargs):
    db.users.update_one({"user_id": user_id}, kwargs)
    logger.info(f"Updated {user_id}: " + " ".join(["{}={}".format(k, v) for k, v in kwargs.items()]))
    return


def get_frichtle(return_json=False, **kwargs):

    frichtle = list(db.users.find(kwargs))

    if len(frichtle) == 0:
        return

    if return_json:
        return frichtle

    if len(kwargs) == 0 or len(frichtle) > 1:
        return [Frichtle.from_json(f) for f in frichtle]
    else:
        return Frichtle.from_json(frichtle[0])


def exist_frichtle(user_id):

    return db.users.find({"user_id": user_id}) is not None


def remove_frichtle(user_id):
    try:
        frichtle = Frichtle.from_json(db.users.find_one({"user_id": user_id}))
        str_rep = str(frichtle)
        db.users.delete_one({"user_id": user_id})
    except Exception:
        str_rep = ""

    events = list(db.events.find())
    for e in events:
        e["attendance"].pop(f"_{user_id}", None)
        db.events.update_one({"event_id": e["event_id"]}, {"$set": {"attendance": e["attendance"]}})

    surveys = list(db.surveys.find())
    for s in surveys:
        for q in s["questions"]:
            q["results"].pop(f"_{user_id}", None)
        db.surveys.update_one({"survey_id": s["survey_id"]}, {"$set": {"questions": s["questions"]}})

    if str_rep != "":
        logger.info(f"Removed Frichtle " + str_rep)

    return


def get_from_all_frichtle(info):

    return [f[info] for f in db.users.find()]


def get_username(user_id):
    return db.users.find_one({"_id": user_id})["username"]


def get_user_id(username):
    return db.users.find_one({"username": username})["_id"]


def is_admin(user_id):
    return db.users.find_one({"_id": user_id})["admin"]


def is_master(user_id):
    return db.users.find_one({"_id": user_id})["master"]


def make_admin(user_id):
    db.users.update_one({"_id": user_id}, {"$set": {"admin": True}})
    logger.info("Made " + str(user_id) + " an admin.")


def remove_admin(user_id):
    db.users.update_one({"_id": user_id}, {"$set": {"admin": False}})
    logger.info("Removed " + str(user_id) + " as admin.")


def remove_master(user_id):
    db.users.update_one({"_id": user_id}, {"$set": {"master": False}})


def get_instrument(user_id):
    return db.users.find_one({"_id": user_id})["instrument"]


def set_instrument(user_id, instrument):
    db.users.update_one({"_id": user_id}, {"$set": {"instrument": instrument}})
    logger.info(f"Set instrument={instrument} for " + user_id)


def is_active(event_id=None):
    return db.events.find_one({"_id": event_id})["active"]


def set_attendance_to_event(event_id, user_id, att):
    if att not in [1, 2, 3]:
        return
    db.events.update_one({"_id": event_id}, {"$set": {f"attendance._{user_id}": att}})
    f = get_frichtle(user_id=user_id)
    logger.info(f"Set attendance={att} for " + f.name + " for event " + event_id)
    return


def check_attendance(user_id, event_id):
    return db.events.find_one({"_id": event_id})["attendance"][f"_{user_id}"]


def add_event(ev):
    ev.attendance = {k: 1 for k in get_from_all_frichtle(info="user_id")}
    ev = ev.to_json()
    ev["_id"] = ev["event_id"]
    db.events.insert_one(ev)
    logger.info("Added Event: {}".format(str(ev).replace("\n", ";")))
    return


def exist_event_id(event_id):
    return db.events.find_one({"_id": event_id}) is not None


def get_new_event_id():
    base = meta.event_id_base
    i = 1
    while exist_event_id(base.format(i)):
        i += 1
    return base.format(i)


def get_event(event_id=None, incl_cancel=False):

    if event_id:
        return Event.from_json(list(db.events.find_one({"_id": event_id}))[0])
    else:
        events = [Event.from_json(e) for e in db.events.find()]
        if not incl_cancel:
            events = [e for e in events if e.active]

        events.sort(key=lambda r: r.get_start_time())
        return events


def events_that_need_reminder():
    return [Event.from_json(e) for e in db.events.find() if 1 in e["attendance"].values()]


def get_event_attendance(event_id=None, event=None):
    if not event_id:
        event_id = event.event_id

    att = db.events.find_one({"_id": event_id})["attendance"]
    att = {int(k.replace("_", "")): v for k, v in att.items()}
    frichtle = {f.user_id: f.to_json() for f in get_frichtle()}
    event_dict = [{"user_id": k, "attendance": v, "instrument": frichtle[k]["instrument"]} for k, v in att.items()]

    return event_dict


def get_events_from_user(user_id, attendance=None):
    if attendance is None:
        attendance = [3, 2, 1]
    if isinstance(attendance, int):
        attendance = [attendance]

    events = [{'ev': Event.from_json(e), 'att': e["attendance"][f"_{user_id}"]} for e in db.events.find()]
    events = list(filter(lambda e: e['att'] in attendance, events))
    return events


def cancel_event(event_id=None, ev=None):
    if event_id is None:
        event_id = ev.event_id

    event = db.events.find_one({"_id": event_id})
    new_attendance = {k: (-1)*v for k, v in event["attendance"].items()}
    db.events.update_one({"_id": event_id}, {"$set": {"active": False, "attendance": new_attendance}})

    logger.info(f"Canceled Event: {event['description']}")
    return


def remove_event(event_id=None, ev=None):
    if event_id is None:
        event_id = ev.event_id

    event = db.events.find_one_and_delete({"_id": event_id})
    if event:
        logger.info(f"Removed Event: {event['description']}")

    return


def remove_survey(survey_id=None, survey=None):
    if survey_id is None:
        survey_id = survey.survey_id

    survey = db.survey.find_one_and_delete({"_id": survey_id})
    if survey:
        logger.info(f"Removed Survey: {survey['description']}")

    return


def get_survey(survey_id=None):
    if survey_id is None:
        s = [Survey.from_json(survey) for survey in db.surveys.find()]
        if not isinstance(s, list):
            s = [s]
        return s
    else:
        return Survey.from_json(db.surveys.find_one({"_id": survey_id}))


def exist_survey_id(survey_id):
    return db.surveys.find_one({"_id": survey_id}) is not None


def get_new_survey_id(surveys=None):
    base = meta.survey_id_base
    i = 1
    while exist_survey_id(base.format(i)):
        i += 1
    return base.format(i)


def add_survey(survey):

    for q in survey.questions:
        q["results"] = {f"_{k}": None for k in get_from_all_frichtle(info="user_id")}
    survey["_id"] = survey["survey_id"]
    db.surveys.insert_one(survey.to_json())

    logger.info("Saved Survey: {}".format(str(survey).replace("\n", ";")))

    return


def surveys_that_need_reminder():
    surveys = [Survey.from_json(s) for s in db.surveys.find()]
    return [s for s in surveys if None in s.results.values()]


def get_survey_result(survey_id=None):

    survey = db.surveys.find_one({"_id": survey_id})

    return [
        {"user_id": int(k.replace("_", "")), "answers": [q["results"][k] for q in survey["questions"]]}
        for k in survey["questions"][0]["results"].keys()
    ]


def set_response_to_survey(survey_id, user_id, response):
    survey = get_survey(survey_id=survey_id)
    for i, q in enumerate(survey["questions"]):
        db.surveys.update_one({"_id": survey_id}, {"$set": {f"questions.{i}.results._{user_id}": response}})

    return


def check_survey_response(user_id, survey_id):
    return get_survey(survey_id).results[user_id]


def get_all_tables():
    return ["frichtle", "event", "survey"]


def get_table_as_string(table):
    content = db[table].find()
    content = [{k: v for k, v in c.items() if k != "_id"} for c in content]
    return json.dumps(content, indent=4)
