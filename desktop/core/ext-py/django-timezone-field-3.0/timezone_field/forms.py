import pytz
from django.core.exceptions import ValidationError
from django import forms


class TimeZoneFormField(forms.TypedChoiceField):
    def __init__(self, *args, **kwargs):

        def coerce_to_pytz(val):
            try:
                return pytz.timezone(val)
            except pytz.UnknownTimeZoneError:
                raise ValidationError("Unknown time zone: '%s'" % val)

        defaults = {
            'coerce': coerce_to_pytz,
            'choices': [
                (tz, tz.replace('_', ' ')) for tz in pytz.common_timezones
            ],
            'empty_value': None,
        }
        defaults.update(kwargs)
        super(TimeZoneFormField, self).__init__(*args, **defaults)
