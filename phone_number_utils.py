import re

def is_valid_number(string):
    pattern = r'^(\+381|0)[67]\d{8}$'
    return bool(re.match(pattern, string))

def extract_phone_number(text):
    # Remove non-digit characters from the text
    cleaned_text = re.sub(r'\D', '', text)

    # Check if the cleaned text matches the phone number pattern
    if re.match(r'^(\+)?\d{10,15}$', cleaned_text):
        return cleaned_text

    return None