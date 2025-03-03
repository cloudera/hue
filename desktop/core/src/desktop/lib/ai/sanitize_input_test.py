import pytest

from desktop.lib.ai.sanitize_input import validate_input, validate_user_input_max_length


def test_validate_user_input_max_length_valid():

    assert validate_user_input_max_length("short input", 20) == "Valid prompt"


def test_validate_user_input_max_length_exceeds():
    with pytest.raises(ValueError, match=r"Prompt length exceeds limit : Maximum allowed length is 10 characters, but got 14."):
        validate_user_input_max_length("exceeds length", 10)


def test_validate_input_valid():
    assert validate_input("valid input", 15) is None


def test_validate_input_exceeds():
    with pytest.raises(ValueError, match=r"Prompt length exceeds limit : Maximum allowed length is 5 characters, but got 14."):
        validate_input("too long input", 5)
