# command handler


import re


def remove_emoji(text):
    return emoji_pattern.sub(r'', text)


emoji_pattern = re.compile("["
                           u"\U0001F600-\U0001F64F"  # emoticons
                           u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                           u"\U0001F680-\U0001F6FF"  # transport & map symbols
                           u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                           u"\U00000800-\U0001F5FF"
                           "]+", flags=re.UNICODE)


def user_cmd(func):
    def return_func(message):
        if not message.from_user.exist:
            return 0
        if message.text != "" and message.text is not None:
            t = remove_emoji(message.text).lower()
        else:
            return 0
        if t[0] == "/":
            t = t[1:]
        t = t.replace("ü", "ue")
        t = t.replace("ä", "ae")
        t = t.replace("ö", "oe")
        t = t.replace(" ", "")
        return func(t)
    return return_func


def admin_cmd(func):
    def return_func(message):
        if not message.from_user.is_admin:
            return 0
        return user_cmd(func)(message)
    return return_func


def master_cmd(func):
    def return_func(message):
        if not message.from_user.is_master:
            return 0
        return user_cmd(func)(message)
    return return_func


def callback_cmd(func):
    def return_func(callback):
        t = callback.data.split(":")
        if t[0] != "cb":
            return 0
        return func(t[1])
    return return_func


def new_callback_cmd(func):
    def return_func(callback):
        t = callback.data.split(";")
        if len(t) == 1:
            return 0
        return func(t[1])
    return return_func
