import pytest

from desktop.lib.ai.sanitize_input import *


def test_validate_user_input_max_length_valid():

    assert validate_user_input_max_length("short input", 20) == "Valid input"


def test_validate_user_input_max_length_exceeds():
    with pytest.raises(ValueError, match=r"Invalid input : Maximum allowed length of user input is 10 characters, but got 14."):
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


@pytest.mark.parametrize(
"input_text, banned_keyphrases, expected",
[
    ("This is a safe input", ["banned"],
     "Valid Input"),
    ("This contains a banned word", ["banned"],
      pytest.raises(ValueError, match="Invalid input: Found banned keyphrase 'banned' in 'This contains a banned word'")),
    ("Another forbidden no space, term", ["space"],
      pytest.raises(ValueError, match="Invalid input: Found banned keyphrase 'space' in 'Another forbidden no space, term'")),
    ("Case Insensitive BAN", ["ban"],
      pytest.raises(ValueError, match="Invalid input: Found banned keyphrase 'ban' in 'Case Insensitive BAN'")),
    ("No banned words here", [],
      "Valid Input"),
    ("Special characters #@!", ["special"],
      pytest.raises(ValueError, match="Invalid input: Found banned keyphrase 'special' in 'Special characters #@!'")),
    ("PartialMatch", ["match"],
      pytest.raises(ValueError, match="Invalid input: Found banned keyphrase 'match' in 'PartialMatch'")),
    ("Multiple banned words here", ["banned", "words"],
      pytest.raises(ValueError, match="Invalid input: Found banned keyphrase (?:'banned'|'words') in 'Multiple banned words here'")),
    ("Space seperated banned words", ["banned words"],
    pytest.raises(ValueError, match="Invalid input: Found banned keyphrase ('banned words') in 'Space seperated banned words'")),
]
)
def test_user_input_banned_keywords_checker(input_text, banned_keyphrases, expected):
    if isinstance(expected, str):
        assert user_input_banned_keyphrase_checker(input_text, banned_keyphrases) == expected
    else:
        with expected:
            user_input_banned_keyphrase_checker(input_text, banned_keyphrases)


@pytest.mark.parametrize(
    "input, banned_regex, expected_output, expected_exception",
    [
        ("invalid_input", r"invalid", None, ValueError),

        ("valid_input", r"invalid", "Valid input", None),

        ("123abc", r"123|xyz", None, ValueError),

        ("bad_input#", r"#", None, ValueError),
    ]
)
def test_user_input_banned_regex_checker(input, banned_regex, expected_output, expected_exception):
    if expected_exception:
        with pytest.raises(expected_exception):
            user_input_banned_regex_checker(input, banned_regex)
    else:
        result = user_input_banned_regex_checker(input, banned_regex)
        assert result == expected_output


@pytest.mark.parametrize(
    "input_str, expected_output", [
        ("<div>Hello</div>", "&lt;div&gt;Hello&lt;/div&gt;"),
        ("Hello", "Hello"),
        ("<div><p>Hello</p></div>", "&lt;div&gt;&lt;p&gt;Hello&lt;/p&gt;&lt;/div&gt;"),
        ("", ""),
        ("a<b", "a<b"),
        ("<div>a<b and c>d</div>", "&lt;div&gt;a&lt;b and c&gt;d&lt;/div&gt;"),
        ("<a href='test.html'>a<b;</a>", "&lt;a href='test.html'&gt;a&lt;b;</a&gt;")
    ]
)
def test_user_input_check_html(input_str, expected_output):
    assert user_input_check_html(input_str) == expected_output
