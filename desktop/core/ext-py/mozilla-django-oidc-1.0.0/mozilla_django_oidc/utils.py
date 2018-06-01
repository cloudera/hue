from django import VERSION
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


def import_from_settings(attr, *args):
    """
    Load an attribute from the django settings.

    :raises:
        ImproperlyConfigured
    """
    try:
        if args:
            return getattr(settings, attr, args[0])
        return getattr(settings, attr)
    except AttributeError:
        raise ImproperlyConfigured('Setting {0} not found'.format(attr))


def absolutify(request, path):
    """Return the absolute URL of a path."""
    return request.build_absolute_uri(path)


# Computed once, reused in every request
_less_than_django_1_10 = VERSION < (1, 10)


def is_authenticated(user):
    """return True if the user is authenticated.

    This is necessary because in Django 1.10 the `user.is_authenticated`
    stopped being a method and is now a property.
    Actually `user.is_authenticated()` actually works, thanks to a backwards
    compat trick in Django. But in Django 2.0 it will cease to work
    as a callable method.
    """
    if _less_than_django_1_10:
        return user.is_authenticated()
    return user.is_authenticated
