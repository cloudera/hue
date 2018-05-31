#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")

    from django.core.management import execute_from_command_line
    from django.conf import settings

    if '--no-migrations' in sys.argv:
        settings.SOUTH_TESTS_MIGRATE=False
        sys.argv.remove('--no-migrations')
    execute_from_command_line(sys.argv)
