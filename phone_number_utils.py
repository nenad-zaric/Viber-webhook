import re

def is_phone_number(string):
    pattern = r'^(\+381|0)[67]\d{8}$'
    return bool(re.match(pattern, string))

def clean_number(number):
    number = number.replace("-", "").replace("/", "").replace(" ", "")
    return number