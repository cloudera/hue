"""Custom runner to test overriding runner."""
from django_nose import NoseTestSuiteRunner


class CustomNoseTestSuiteRunner(NoseTestSuiteRunner):
    """Custom test runner, to test overring runner."""
