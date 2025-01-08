import os

import pkg_resources
from django.core.management import call_command

TEST_LOCALE_DIR = pkg_resources.resource_filename(
    'testproject', 'locale'
)


def test_babel_compilemessages():
    call_command(
        'babel',
        'compilemessages',
        '-l', 'fi',
    )
    # Assert that the .mo file was created by attempting to delete it.
    os.unlink(
        os.path.join(TEST_LOCALE_DIR, 'fi', 'LC_MESSAGES', 'django.mo')
    )


def test_babel_makemessages():
    call_command(
        'babel',
        'makemessages',
        '-l', 'en',
        '-F', pkg_resources.resource_filename(__name__, 'babel.cfg'),
    )
    # See that the expected files get populated with the discovered message
    for path in [
        os.path.join(TEST_LOCALE_DIR, 'django.pot'),
        os.path.join(TEST_LOCALE_DIR, 'en', 'LC_MESSAGES', 'django.po'),
    ]:
        with open(path) as infp:
            assert '"This could be translated."' in infp.read()
        os.unlink(path)  # clean up
