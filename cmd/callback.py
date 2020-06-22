
from cmd.cmd_handler import callback_cmd

from util.classes import callback_commands


@callback_cmd
def abort(t):
    return t in ["abort_action", "abort"]


@callback_cmd
def remove_which_event(t):
    return t == "remove_which_event"


@callback_cmd
def remove_event(t):
    return t == "remove_event"


@callback_cmd
def remove_which_survey(t):
    return t == "remove_which_survey"


@callback_cmd
def remove_survey(t):
    return t == "remove_survey"


@callback_cmd
def cancel_which_event(t):
    return t == "cancel_which_event"


@callback_cmd
def cancel_event(t):
    return t == "cancel_event"


@callback_cmd
def send_cancel_event_alert(t):
    return t == "send_cancel_event_alert"


@callback_cmd
def edit_which_event(t):
    return t == "edit_which_event"


@callback_cmd
def edit_event(t):
    return t == "edit_event"


@callback_cmd
def edit_event_okay(t):
    return t == "edit_event_okay"


@callback_cmd
def attend_which_event(t):
    return t == "attend_which_event"


@callback_cmd
def attend_event(t):
    return t == "attend_event"


@callback_cmd
def show_event(t):
    return t == "show_event"


@callback_cmd
def show_event_back(t):
    return t == "show_event_back"


@callback_cmd
def summary_which_event(t):
    return t == "summary_which_event"


@callback_cmd
def event_summary_back(t):
    return t == "event_summary_back"


@callback_cmd
def send_reminder_for_event(t):
    return t == "send_event_reminder"


@callback_cmd
def send_reminder_for_survey(t):
    return t == "send_survey_reminder"


@callback_cmd
def send_reminder_back(t):
    return t in ["send_survey_reminder_back", "send_event_reminder_back"]


@callback_cmd
def respond_which_survey(t):
    return t == "respond_which_survey"


@callback_cmd
def respond_survey(t):
    return t == "respond_survey"


@callback_cmd
def show_survey(t):
    return t == "show_survey"


@callback_cmd
def edit_which_survey_response(t):
    return t == "edit_which_survey_response"


@callback_cmd
def edit_survey_response(t):
    return t == "edit_survey_response"


@callback_cmd
def show_survey_back(t):
    return t == "show_survey_back"


@callback_cmd
def summary_which_survey(t):
    return t == "summary_which_survey"


@callback_cmd
def survey_summary_back(t):
    return t == "survey_summary_back"


@callback_cmd
def show_table(t):
    return t == "show_table"


@callback_cmd
def appoint_admin(t):
    return t == "appoint_admin"


@callback_cmd
def remove_admin(t):
    return t == "remove_admin"


@callback_cmd
def remove_user(t):
    return t == "remove_user"


@callback_cmd
def remind_event(t):
    return t == "remind_event"


@callback_cmd
def remind_survey(t):
    return t == "remind_survey"


@callback_cmd
def show_numbers(t):
    return t == "show_numbers"


def command(call):
    t = call.data.split(";")
    return t[0] in callback_commands.keys() or t[0] in ['abort', 'end']
