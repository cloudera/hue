import re

from bs4 import BeautifulSoup


def validate_user_input_max_length(input, max_length):
    if len(input) > max_length:
        raise ValueError(f"Invalid input : Maximum allowed length of user input is {max_length} characters, but got {len(input)}.")

    return "Valid input"


def user_input_trim_whitespaces(input):
    input = re.sub(r'[ ]+', ' ', input)
    input = re.sub(r'\n\s*\n+', '\n', input)
    return input.strip()


# doesn't work for unicode lanugages - chinese , spanish etc.
def user_input_character_remover(input, chars_to_remove):
    return input.translate(str.maketrans('', '', chars_to_remove.encode().decode('unicode_escape')))


def user_input_banned_keyphrase_checker(input, banned_keyphrases):
    keyphrases = set(map(str.lower, banned_keyphrases or []))
    input_lower = input.lower()
    for word in keyphrases:
        if word in input_lower:
            raise ValueError(f"Invalid input: Found banned keyphrase '{word}' in '{input}'")

    return "Valid Input"


def user_input_banned_regex_checker(input, banned_regex):
    match = re.search(banned_regex, input)
    if match:
        matched_substring = match.group(0)
        raise ValueError(f"Invalid input: Found banned pattern substring '{matched_substring}' in '{input}'")
    return "Valid input"


def user_input_check_html(input):
    return re.sub(r'<(.*?)>', r'&lt;\1&gt;', input)


def validate_input(input, user_input_max_length, chars_to_remove, banned_keyphrases, banned_regex, html_block):
    validate_user_input_max_length(input, user_input_max_length)
    cleaned_input = user_input_trim_whitespaces(input)
    cleaned_input = user_input_character_remover(cleaned_input, chars_to_remove)
    if banned_keyphrases[0]:
        user_input_banned_keyphrase_checker(cleaned_input, banned_keyphrases)
    if banned_regex:
        user_input_banned_regex_checker(cleaned_input, banned_regex)
    if html_block:
        cleaned_input = user_input_check_html(cleaned_input)
    return cleaned_input
