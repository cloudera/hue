#!/usr/bin/env python

import calendar
import datetime
import time
from saml2.time_util import f_quotient, modulo, parse_duration, add_duration
from saml2.time_util import str_to_time, instant, valid, in_a_while
from saml2.time_util import before, after, not_before, not_on_or_after


def test_f_quotient():
    assert f_quotient(0, 3) == 0
    assert f_quotient(1, 3) == 0
    assert f_quotient(2, 3) == 0
    assert f_quotient(3, 3) == 1
    assert f_quotient(3.123, 3) == 1


def test_modulo():
    assert modulo(-1, 3) == 2
    assert modulo(0, 3) == 0
    assert modulo(1, 3) == 1
    assert modulo(2, 3) == 2
    assert modulo(3, 3) == 0
    x = 3.123
    assert modulo(3.123, 3) == x - 3


def test_f_quotient_2():
    for i in range(1, 13):
        assert f_quotient(i, 1, 13) == 0
    assert f_quotient(13, 1, 13) == 1
    assert f_quotient(13.123, 1, 13) == 1


def test_modulo_2():
    assert modulo(0, 1, 13) == 12
    for i in range(1, 13):
        assert modulo(i, 1, 13) == i
    assert modulo(13, 1, 13) == 1
    #x = 0.123
    #assert modulo(13+x, 1, 13) == 1+x


def test_parse_duration():
    (sign, d) = parse_duration("P1Y3M5DT7H10M3.3S")
    assert sign == "+"
    assert d['tm_sec'] == 3.3
    assert d['tm_mon'] == 3
    assert d['tm_hour'] == 7
    assert d['tm_mday'] == 5
    assert d['tm_year'] == 1
    assert d['tm_min'] == 10


def test_parse_duration2():
    (sign, d) = parse_duration("PT30M")
    assert sign == "+"
    assert d['tm_sec'] == 0
    assert d['tm_mon'] == 0
    assert d['tm_hour'] == 0
    assert d['tm_mday'] == 0
    assert d['tm_year'] == 0
    assert d['tm_min'] == 30


PATTERNS = {
    "P3Y6M4DT12H30M5S": {'tm_sec': 5, 'tm_hour': 12, 'tm_mday': 4,
                         'tm_year': 3, 'tm_mon': 6, 'tm_min': 30},
    "P23DT23H": {'tm_sec': 0, 'tm_hour': 23, 'tm_mday': 23, 'tm_year': 0,
                 'tm_mon': 0, 'tm_min': 0},
    "P4Y": {'tm_sec': 0, 'tm_hour': 0, 'tm_mday': 0, 'tm_year': 4,
            'tm_mon': 0, 'tm_min': 0},
    "P1M": {'tm_sec': 0, 'tm_hour': 0, 'tm_mday': 0, 'tm_year': 0,
            'tm_mon': 1, 'tm_min': 0},
    "PT1M": {'tm_sec': 0, 'tm_hour': 0, 'tm_mday': 0, 'tm_year': 0,
             'tm_mon': 0, 'tm_min': 1},
    "P0.5Y": {'tm_sec': 0, 'tm_hour': 0, 'tm_mday': 0, 'tm_year': 0.5,
              'tm_mon': 0, 'tm_min': 0},
    "P0,5Y": {'tm_sec': 0, 'tm_hour': 0, 'tm_mday': 0, 'tm_year': 0.5,
              'tm_mon': 0, 'tm_min': 0},
    "PT36H": {'tm_sec': 0, 'tm_hour': 36, 'tm_mday': 0, 'tm_year': 0,
              'tm_mon': 0, 'tm_min': 0},
    "P1DT12H": {'tm_sec': 0, 'tm_hour': 12, 'tm_mday': 1, 'tm_year': 0,
                'tm_mon': 0, 'tm_min': 0}
}


def test_parse_duration_n():
    for dur, _val in PATTERNS.items():
        (sign, d) = parse_duration(dur)
        assert d == _val

def test_add_duration_1():
    #2000-01-12T12:13:14Z	P1Y3M5DT7H10M3S	2001-04-17T19:23:17Z    
    t = add_duration(str_to_time("2000-01-12T12:13:14Z"), "P1Y3M5DT7H10M3S")
    assert t.tm_year == 2001
    assert t.tm_mon == 4
    assert t.tm_mday == 17
    assert t.tm_hour == 19
    assert t.tm_min == 23
    assert t.tm_sec == 17


def test_add_duration_2():
    #2000-01-12 PT33H   2000-01-13
    t = add_duration(str_to_time("2000-01-12T00:00:00Z"), "PT33H")
    assert t.tm_year == 2000
    assert t.tm_mon == 1
    assert t.tm_mday == 14
    assert t.tm_hour == 9
    assert t.tm_min == 0
    assert t.tm_sec == 0


def test_str_to_time():
    t = calendar.timegm(str_to_time("2000-01-12T00:00:00Z"))
    #TODO: Find all instances of time.mktime(.....)
    #t = time.mktime(str_to_time("2000-01-12T00:00:00Z"))
    #assert t == 947631600.0
    #TODO: add something to show how this time was arrived at
    # do this as an external method in the 
    assert t == 947635200
    # some IdPs omit the trailing Z, and SAML spec is unclear if it is actually required
    t = calendar.timegm(str_to_time("2000-01-12T00:00:00"))
    assert t == 947635200

def test_instant():
    inst = str_to_time(instant())
    now = time.gmtime()

    assert now >= inst


def test_valid():
    assert valid("2000-01-12T00:00:00Z") == False
    current_year = datetime.datetime.today().year
    assert valid("%d-01-12T00:00:00Z" % (current_year + 1)) == True
    this_instance = instant()
    time.sleep(1)
    assert valid(this_instance) is False  # unless on a very fast machine :-)
    soon = in_a_while(seconds=10)
    assert valid(soon) == True


def test_timeout():
    soon = in_a_while(seconds=1)
    time.sleep(2)
    assert valid(soon) == False


def test_before():
    current_year = datetime.datetime.today().year
    assert before("%d-01-01T00:00:00Z" % (current_year - 1)) == False
    assert before("%d-01-01T00:00:00Z" % (current_year + 1)) == True


def test_after():
    current_year = datetime.datetime.today().year
    assert after("%d-01-01T00:00:00Z" % (current_year + 1)) == False
    assert after("%d-01-01T00:00:00Z" % (current_year - 1)) == True


def test_not_before():
    current_year = datetime.datetime.today().year
    assert not_before("%d-01-01T00:00:00Z" % (current_year + 1)) == False
    assert not_before("%d-01-01T00:00:00Z" % (current_year - 1)) == True


def test_not_on_or_after():
    current_year = datetime.datetime.today().year
    assert not_on_or_after("%d-01-01T00:00:00Z" % (current_year + 1)) == True
    assert not_on_or_after("%d-01-01T00:00:00Z" % (current_year - 1)) == False


if __name__ == "__main__":
    test_str_to_time()
