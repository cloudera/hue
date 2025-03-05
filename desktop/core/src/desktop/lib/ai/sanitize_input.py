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


def validate_input(input, user_input_max_length, chars_to_remove):
    validate_user_input_max_length(input, user_input_max_length)
    cleaned_input = user_input_trim_whitespaces(input)
    cleaned_input = user_input_character_remover(cleaned_input, chars_to_remove)
    return cleaned_input
