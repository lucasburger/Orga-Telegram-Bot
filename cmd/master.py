# cmd.master

from cmd.cmd_handler import master_cmd


@master_cmd
def master_menu(t):
    return t in ['mastermenu', 'mastermenue']


@master_cmd
def listtables(t):
    return t in ['listtables', 'zeigetabellen']


@master_cmd
def show_table(t):
    return t in ['showtable', 'zeigetabelle']


@master_cmd
def remove_event(t):
    return t in ['removeevent', 'terminentfernen', 'terminloeschen']


@master_cmd
def remove_survey(t):
    return t in ['removesurvey']


@master_cmd
def remove_user(t):
    return t in ['removeuser', 'entfernefrichtle']

@master_cmd
def new_admin(t):
    return t in ['newadmin', 'neueradmin']


@master_cmd
def remove_admin(t):
    return t in ['removeadmin', 'entferneadmin']


@master_cmd
def sql_command(t):
    return t in ['sqlcommand']


@master_cmd
def manage_members_menu(t):
    return t in ['managemembers']


@master_cmd
def new_invite_link(t):
    return 'invitelink' in t


@master_cmd
def calculator(t):
    return 'calculator' in t
