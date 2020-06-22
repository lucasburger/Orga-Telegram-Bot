# cmd.admin

from cmd.cmd_handler import admin_cmd


@admin_cmd
def admin_menu(t):
    return t in ['admin', 'adminmenue']


@admin_cmd
def new_event(t):
    return t in ['neuertermin', 'newevent']


@admin_cmd
def manage_events(t):
    return t in ['termineverwalten', 'manageevents']


@admin_cmd
def edit_event(t):
    return t in ['terminbearbeiten', 'editevent']


@admin_cmd
def event_summary(t):
    return t in ['terminzusammenfassung', 'summaryevent', 'eventsummary']


@admin_cmd
def cancel_event(t):
    return t in ['cancelevent', 'terminabsagen', 'eventabsagen']


@admin_cmd
def send_reminder(t):
    return t in ['sendreminder', 'erinnerungsenden', 'erinnerungversenden']


@admin_cmd
def remind_event(t):
    return t in ['erinnerungfürevent']


@admin_cmd
def remind_survey(t):
    return t in ['erinnerungfürumfrage']


@admin_cmd
def manage_surveys(t):
    return t in ['umfragenverwalten']


@admin_cmd
def new_survey(t):
    return t in ['neueumfrage']


@admin_cmd
def survey_summary(t):
    return t in ['umfrageergebnis']
