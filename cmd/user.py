# cmd.user.py

from cmd.cmd_handler import user_cmd


@user_cmd
def event(text):
    return text in ['termin', 'termine', 'event']


@user_cmd
def frichtle(t):
    return t in ['members', 'frichtle', 'mitglieder']


@user_cmd
def surveys(t):
    return t in ['umfragen']


@user_cmd
def help(t):
    return t in ['help', 'hilfe']


@user_cmd
def main_menu(t):
    return t in ['hauptmenue', 'mainmenu', "macheichspaeter..."]


@user_cmd
def zusagen(t):
    return t in ['meinezusagen', 'zusagen']


@user_cmd
def absagen(t):
    return t in ['meineabsagen', 'absagen']


@user_cmd
def ausstehende_rueckmeldungen(t):
    return t in ['ausstehenderueckmeldungen']


@user_cmd
def all_events(t):
    return t in ['zeigealletermine', 'alletermine', 'alleterminemitdetails']


@user_cmd
def all_surveys(t):
    return t in ['zeigealleumfragen', 'alleumfragen', 'alleumfragenmitdetails']


@user_cmd
def unanswered_surveys(t):
    return t in ['unbeantworteteumfragen']
