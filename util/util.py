


def convert_from_database(d):
    if isinstance(d, list):
        return [convert_from_database(list_item) for list_item in d]

    if not isinstance(d, dict):
        return d
    try:
        d.pop("_id")
    except KeyError:
        pass

    d = {convert_keys(k): convert_from_database(v) for k, v in d.items()}
    return d


def convert_keys(k):
    if k[0] == "_":
        return int(k[1:])
    else:
        try:
            return int(k)
        except:
            return k


def convert(func):
    def wrapped(*args, **kwargs):
        r = func(*args, **kwargs)
        return convert_from_database(r)

    return wrapped


def convert_to_database(d):
    if isinstance(d, list):
        return [convert_to_database(list_item) for list_item in d]

    if not isinstance(d, dict):
        return d
    try:
        d.pop("_id")
    except KeyError:
        pass

    d = {reconvert_keys(k): convert_to_database(v) for k, v in d.items()}
    return d


def reconvert_keys(k):
    if isinstance(k, int):
        return f"_{k}"
    else:
        return k
        