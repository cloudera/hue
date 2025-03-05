import pytest

from desktop.lib.ai.sanitize_input import *


def test_validate_user_input_max_length_valid():

    assert validate_user_input_max_length("short input", 20) == "Valid prompt"


def test_validate_user_input_max_length_exceeds():
    with pytest.raises(ValueError, match=r"Prompt length exceeds limit : Maximum allowed length is 10 characters, but got 14."):
        validate_user_input_max_length("exceeds length", 10)


@pytest.mark.parametrize("input_text, expected_output", [
    ("Hello  World", "Hello World"),
    ("  Leading and trailing spaces  ", "Leading and trailing spaces"),


    ("Hello\n\n\nWorld", "Hello\nWorld"),
    ("Hello\n  \n  \nWorld", "Hello\nWorld"),
    ("\n\n\nHello\n\n\nWorld\n\n", "Hello\nWorld"),

    ("   Hello   \n   World   ", "Hello \n World"),
    ("Hello \n    World", "Hello \n World"),

    ("", ""),
    ("    ", ""),
    ("\n\n\n", ""),
    (" \n  \n   ", ""),
])
def test_user_input_trim_whitespaces(input_text, expected_output):
    assert user_input_trim_whitespaces(input_text) == expected_output


@pytest.mark.parametrize("input_text, chars_to_remove, expected_output", [
    ("hello world", "l", "heo word"),
    ("abcdef", "bdf", "ace"),

    ("hello", "xyz", "hello"),
    ("unchanged text", "", "unchanged text"),

    ("", "abc", ""),
    ("abcdef", "", "abcdef"),
    ("aaaa", "a", ""),

    ("hello, \n\rworld!", "\n,!", "hello \rworld"),
    ("(123) 456-7890", "()-", "123 4567890"),

    ("123 456 789", " ", "123456789"),
    ("2024-03-05", "-03", "2245"),

])
def test_user_input_character_remover(input_text, chars_to_remove, expected_output):
    assert user_input_character_remover(input_text, chars_to_remove) == expected_output
