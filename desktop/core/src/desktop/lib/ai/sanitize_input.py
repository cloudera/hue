def validate_user_input_max_length(input, max_length):
    if len(input) > max_length:
        raise ValueError(f"Prompt length exceeds limit : Maximum allowed length is {max_length} characters, but got {len(input)}.")

    return "Valid prompt"


def validate_input(input, user_input_max_length):
    validate_user_input_max_length(input, user_input_max_length)
