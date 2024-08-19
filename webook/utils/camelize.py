import re


def camelize(string):
    s = "".join([word.capitalize() for word in string.split("_")])
    return s[0].lower() + s[1:]


def decamelize(string):
    return re.sub(r"([A-Z])", r"_\1", string).lower()
