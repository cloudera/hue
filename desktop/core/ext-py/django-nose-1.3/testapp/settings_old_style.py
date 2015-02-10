DATABASES = {
    'default': {
        'NAME': 'django_master',
        'ENGINE': 'django.db.backends.sqlite3',
    }
}

INSTALLED_APPS = (
    'django_nose',
)

TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'
TEST_RUNNER = 'django_nose.run_tests'

SECRET_KEY = 'sssshhh'
