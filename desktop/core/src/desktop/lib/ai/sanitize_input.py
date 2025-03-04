import re


def validate_user_input_max_length(input, max_length):
    if len(input) > max_length:
        raise ValueError(f"Prompt length exceeds limit : Maximum allowed length is {max_length} characters, but got {len(input)}.")

    return "Valid prompt"


def user_input_trim_whitespaces(input):
    input = re.sub(r'[ ]+', ' ', input)
    input = re.sub(r'\n\s*\n+', '\n', input)
    return input.strip()


def validate_input(input, user_input_max_length):
    validate_user_input_max_length(input, user_input_max_length)
    cleaned_input = user_input_trim_whitespaces(input)
    return cleaned_input
