
import json

summary_function_dict = {"free": lambda x: ""}

character_widths = {
    "M": 3
}


def register(name):
    def wrapper(func):
        summary_function_dict[name] = func
        return func
    return wrapper


def format_key_value_pairs(item_dict, key_space=8, value_space=6):

    return "\n".join([f"{k}: {v}" for k, v in item_dict.items()])


@register("list")
def summary_list(survey):

    q = survey.questions[0]

    aggregate_count = {k: 0 for k in q["answers"]}

    for k in aggregate_count.keys():
        for answer in q["results"].values():
            if answer == k:
                aggregate_count[answer] += 1

    return format_key_value_pairs(aggregate_count)


@register("count")
def summary_count(survey):

    q = list(survey.questions[0]["results"].values())

    q = [qq for qq in q if qq is not None]

    return "Gesamt: {}".format(sum(q))


@register("number_and_string")
def summary_number_and_string(survey):

    for q in survey.questions:
        if isinstance(q["answers"], list):
            strings = q["answers"]
            results_string = q["results"]
        elif q["answers"] == "count":
            results_count = q["results"]

    aggregate_count = {k: 0 for k in strings}

    for k in aggregate_count.keys():
        for user_id, count in results_count.items():
            if results_string[user_id] == k:
                aggregate_count[k] += count

    return format_key_value_pairs(aggregate_count)
