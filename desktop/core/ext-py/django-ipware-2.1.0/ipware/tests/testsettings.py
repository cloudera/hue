DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    },
}
SECRET_KEY = "un33k"
INSTALLED_APPS = ['ipware']
MIDDLEWARE_CLASSES = []

# Version 1 support
IPWARE_TRUSTED_PROXY_LIST = ['177.139.233.100']
