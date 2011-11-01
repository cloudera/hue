# -*- coding: utf-8 -*-
#
# Copyright (C) 2007 Edgewall Software
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution. The terms
# are also available at http://babel.edgewall.org/wiki/License.
#
# This software consists of voluntary contributions made by many
# individuals. For the exact contribution history, see the revision
# history and logs, available at http://babel.edgewall.org/log/.

from django.conf import settings
from django.template import Library
from django.utils.translation import to_locale
try:
    from pytz import timezone
except ImportError:
    timezone = None

from babeldjango.middleware import get_current_locale

babel = __import__('babel', {}, {}, ['core', 'support'])
Format = babel.support.Format
Locale = babel.core.Locale

register = Library()

def _get_format():
    locale = get_current_locale()
    if not locale:
        locale = Locale.parse(to_locale(settings.LANGUAGE_CODE))
    if timezone:
        tzinfo = timezone(settings.TIME_ZONE)
    else:
        tzinfo = None
    return Format(locale, tzinfo)

def datefmt(date=None, format='medium'):
    return _get_format().date(date, format=format)
datefmt = register.filter(datefmt)

def datetimefmt(datetime=None, format='medium'):
    return _get_format().datetime(datetime, format=format)
datetimefmt = register.filter(datetimefmt)

def timefmt(time=None, format='medium'):
    return _get_format().time(time, format=format)
timefmt = register.filter(timefmt)

def numberfmt(number):
    return _get_format().number(number)
numberfmt = register.filter(numberfmt)

def decimalfmt(number, format=None):
    return _get_format().decimal(number, format=format)
decimalfmt = register.filter(decimalfmt)

def currencyfmt(number, currency):
    return _get_format().currency(number, currency)
currencyfmt = register.filter(currencyfmt)

def percentfmt(number, format=None):
    return _get_format().percent(number, format=format)
percentfmt = register.filter(percentfmt)

def scientificfmt(number):
    return _get_format().scientific(number)
scientificfmt = register.filter(scientificfmt)
