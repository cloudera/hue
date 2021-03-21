from django.conf import settings

from testproject import settings as testproject_settings


def pytest_configure():
    settings.configure(**vars(testproject_settings))
