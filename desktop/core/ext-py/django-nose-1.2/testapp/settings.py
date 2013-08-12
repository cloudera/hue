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

SECRET_KEY = 'ssshhhh'
