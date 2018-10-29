#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
"""
Implements some usefull functions when dealing with validity of
different types of information.
"""
from __future__ import print_function

import calendar
import re
import time
import sys

from datetime import timedelta
from datetime import datetime
import six

TIME_FORMAT = "%Y-%m-%dT%H:%M:%SZ"
TIME_FORMAT_WITH_FRAGMENT = re.compile(
    "^(\d{4,4}-\d{2,2}-\d{2,2}T\d{2,2}:\d{2,2}:\d{2,2})(\.\d*)?Z?$")

# ---------------------------------------------------------------------------
# I'm sure this is implemented somewhere else can't find it now though, so I
# made an attempt.
#Implemented according to
#http://www.w3.org/TR/2001/REC-xmlschema-2-20010502/
#adding-durations-to-dateTimes


def f_quotient(arg0, arg1, arg2=0):
    if arg2:
        return int((arg0 - arg1) / (arg2 - arg1))
    elif not arg0:
        return 0
    else:
        return int(arg0 / arg1)


def modulo(arg0, arg1, arg2=0):
    if arg2:
        return ((arg0 - arg1) % (arg2 - arg1)) + arg1
    else:
        return arg0 % arg1


def maximum_day_in_month_for(year, month):
    return calendar.monthrange(year, month)[1]


D_FORMAT = [
    ("Y", "tm_year"),
    ("M", "tm_mon"),
    ("D", "tm_mday"),
    ("T", None),
    ("H", "tm_hour"),
    ("M", "tm_min"),
    ("S", "tm_sec")
]


def parse_duration(duration):
    # (-)PnYnMnDTnHnMnS
    index = 0
    if duration[0] == '-':
        sign = '-'
        index += 1
    else:
        sign = '+'
    assert duration[index] == "P"
    index += 1

    dic = dict([(typ, 0) for (code, typ) in D_FORMAT if typ])
    dlen = len(duration)

    for code, typ in D_FORMAT:
        #print(duration[index:], code)
        if duration[index] == '-':
            raise Exception("Negation not allowed on individual items")
        if code == "T":
            if duration[index] == "T":
                index += 1
                if index == len(duration):
                    raise Exception("Not allowed to end with 'T'")
            else:
                raise Exception("Missing T")
        elif duration[index] == "T":
            continue
        else:
            try:
                mod = duration[index:].index(code)
                _val = duration[index:index + mod]
                try:
                    dic[typ] = int(_val)
                except ValueError:
                    # smallest value used may also have a decimal fraction
                    if mod + index + 1 == dlen:
                        try:
                            dic[typ] = float(_val)
                        except ValueError:
                            if "," in _val:
                                _val = _val.replace(",", ".")
                                try:
                                    dic[typ] = float(_val)
                                except ValueError:
                                    raise Exception("Not a float")
                            else:
                                raise Exception("Not a float")
                    else:
                        raise ValueError(
                            "Fraction not allowed on other than smallest value")
                index = mod + index + 1
            except ValueError:
                dic[typ] = 0

        if index == dlen:
            break

    return sign, dic


def add_duration(tid, duration):

    (sign, dur) = parse_duration(duration)

    if sign == '+':
        #Months
        temp = tid.tm_mon + dur["tm_mon"]
        month = modulo(temp, 1, 13)
        carry = f_quotient(temp, 1, 13)
        #Years
        year = tid.tm_year + dur["tm_year"] + carry
        # seconds
        temp = tid.tm_sec + dur["tm_sec"]
        secs = modulo(temp, 60)
        carry = f_quotient(temp, 60)
        # minutes
        temp = tid.tm_min + dur["tm_min"] + carry
        minutes = modulo(temp, 60)
        carry = f_quotient(temp, 60)
        # hours
        temp = tid.tm_hour + dur["tm_hour"] + carry
        hour = modulo(temp, 60)
        carry = f_quotient(temp, 60)
        # days
        if dur["tm_mday"] > maximum_day_in_month_for(year, month):
            temp_days = maximum_day_in_month_for(year, month)
        elif dur["tm_mday"] < 1:
            temp_days = 1
        else:
            temp_days = dur["tm_mday"]
        days = temp_days + tid.tm_mday + carry
        while True:
            if days < 1:
                pass
            elif days > maximum_day_in_month_for(year, month):
                days -= maximum_day_in_month_for(year, month)
                carry = 1
            else:
                break
            temp = month + carry
            month = modulo(temp, 1, 13)
            year += f_quotient(temp, 1, 13)

        return time.localtime(time.mktime((year, month, days, hour, minutes,
                                           secs, 0, 0, -1)))
    else:
        pass

# ---------------------------------------------------------------------------


def time_in_a_while(days=0, seconds=0, microseconds=0, milliseconds=0,
                    minutes=0, hours=0, weeks=0):
    """
    format of timedelta:
        timedelta([days[, seconds[, microseconds[, milliseconds[,
                    minutes[, hours[, weeks]]]]]]])
    :return: UTC time
    """
    delta = timedelta(days, seconds, microseconds, milliseconds,
                      minutes, hours, weeks)
    return datetime.utcnow() + delta


def time_a_while_ago(days=0, seconds=0, microseconds=0, milliseconds=0,
                     minutes=0, hours=0, weeks=0):
    """
    format of timedelta:
        timedelta([days[, seconds[, microseconds[, milliseconds[,
                    minutes[, hours[, weeks]]]]]]])
    """
    delta = timedelta(days, seconds, microseconds, milliseconds,
                      minutes, hours, weeks)
    return datetime.utcnow() - delta


def in_a_while(days=0, seconds=0, microseconds=0, milliseconds=0,
               minutes=0, hours=0, weeks=0, format=TIME_FORMAT):
    """
    format of timedelta:
        timedelta([days[, seconds[, microseconds[, milliseconds[,
                    minutes[, hours[, weeks]]]]]]])
    """
    if format is None:
        format = TIME_FORMAT

    return time_in_a_while(days, seconds, microseconds, milliseconds,
                           minutes, hours, weeks).strftime(format)


def a_while_ago(days=0, seconds=0, microseconds=0, milliseconds=0,
                minutes=0, hours=0, weeks=0, format=TIME_FORMAT):
    return time_a_while_ago(days, seconds, microseconds, milliseconds,
                            minutes, hours, weeks).strftime(format)

# ---------------------------------------------------------------------------


def shift_time(dtime, shift):
    """ Adds/deletes an integer amount of seconds from a datetime specification

    :param dtime: The datatime specification
    :param shift: The wanted time shift (+/-)
    :return: A shifted datatime specification
    """
    return dtime + timedelta(seconds=shift)

# ---------------------------------------------------------------------------


def str_to_time(timestr, format=TIME_FORMAT):
    """

    :param timestr:
    :param format:
    :return: UTC time
    """
    if not timestr:
        return 0
    try:
        then = time.strptime(timestr, format)
    except ValueError:  # assume it's a format problem
        try:
            elem = TIME_FORMAT_WITH_FRAGMENT.match(timestr)
        except Exception as exc:
            print("Exception: %s on %s" % (exc, timestr), file=sys.stderr)
            raise
        then = time.strptime(elem.groups()[0] + "Z", TIME_FORMAT)

    return time.gmtime(calendar.timegm(then))


def instant(format=TIME_FORMAT, time_stamp=0):
    if time_stamp:
        return time.strftime(format, time.gmtime(time_stamp))
    else:
        return time.strftime(format, time.gmtime())

# ---------------------------------------------------------------------------


def utc_now():
    return calendar.timegm(time.gmtime())

# ---------------------------------------------------------------------------


def before(point):
    """ True if point datetime specification is before now.

    NOTE: If point is specified it is supposed to be in local time.
    Not UTC/GMT !! This is because that is what gmtime() expects.
    """
    if not point:
        return True

    if isinstance(point, six.string_types):
        point = str_to_time(point)
    elif isinstance(point, int):
        point = time.gmtime(point)

    return time.gmtime() <= point


def after(point):
    """ True if point datetime specification is equal or after now """
    if not point:
        return True
    else:
        return not before(point)


not_before = after

# 'not_on_or_after' is just an obscure name for 'before'
not_on_or_after = before

# a point is valid if it is now or sometime in the future, in other words,
# if it is not before now
valid = before


def utc_time_sans_frac():
    return int("%d" % time.mktime(time.gmtime()))


def later_than(after, before):
    """ True if then is later or equal to that """
    if isinstance(after, six.string_types):
        after = str_to_time(after)
    elif isinstance(after, int):
        after = time.gmtime(after)

    if isinstance(before, six.string_types):
        before = str_to_time(before)
    elif isinstance(before, int):
        before = time.gmtime(before)

    if before is None:
        return True
    if after is None:
        return False
    return after >= before
