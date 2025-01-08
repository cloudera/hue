# -- encoding: utf-8 --
from __future__ import unicode_literals

import pytest


@pytest.mark.parametrize('locale', ('en', 'fi', 'sv', 'pt-BR'))
def test_babel_render(client, locale):
    """
    Test the middleware and the rendery bits.
    """
    response = client.get('/', HTTP_ACCEPT_LANGUAGE=locale)
    # "Parse" the key-value format
    lines = response.content.decode('utf-8').strip().splitlines()
    content = dict(kv.split('=', 1) for kv in lines)
    # See that we're rendering in the locale we expect
    assert content['language_code'] == locale.lower()
    # check that we could access `babel.Locale.language_name`
    assert content['language_name'] == {
        'en': 'English',
        'fi': 'suomi',
        'sv': 'svenska',
        'pt-BR': 'português',
    }[locale]
    # The rest are not really tested (aside from smoke tests) further;
    # the Babel test suite has taken care of that.
