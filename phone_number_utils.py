import re

def is_valid_number(string):
    pattern = r'^(\+381|0)[67]\d{7,8}$'
    try:
        return bool(re.match(pattern, string))
    except:
        return False


def extract_phone_number(string):
    # Remove any non-digit characters except '+'
    cleaned_string = re.sub(r'[^+\d]|(?<=\+)\+', '', string)

    # Check if the cleaned string matches the phone number pattern
    if re.match(r'^\+?\d{9,15}$', cleaned_string):
        return cleaned_string

    return None


def to_local_format(text):
    if text.startswith("+381"):
        text = "0" + text[4:]
        return text
