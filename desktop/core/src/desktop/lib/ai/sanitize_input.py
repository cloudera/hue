import re


def validate_user_input_max_length(input, max_length):
    if len(input) > max_length:
        raise ValueError(f"Prompt length exceeds limit : Maximum allowed length is {max_length} characters, but got {len(input)}.")

    return "Valid prompt"


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


def validate_input(input, user_input_max_length, chars_to_remove, banned_keyphrases):
    validate_user_input_max_length(input, user_input_max_length)
    cleaned_input = user_input_trim_whitespaces(input)
    cleaned_input = user_input_character_remover(cleaned_input, chars_to_remove)
    if banned_keyphrases[0]:
        user_input_banned_keyphrase_checker(input, banned_keyphrases)
    return cleaned_input
