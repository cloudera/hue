# -*- coding: utf-8 -*-

from __future__ import absolute_import

import pickle
import sys

import pytest

import thriftpy2

PICKLED_BYTES = b"\x80\x02caddressbook_thrift\nPerson\nq\x00)\x81q\x01}q\x02(X\x04\x00\x00\x00nameq\x03X\x03\x00\x00\x00Bobq\x04X\x06\x00\x00\x00phonesq\x05NX\n\x00\x00\x00created_atq\x06Nub."  # noqa


def test_import_hook():
    ab_1 = thriftpy2.load("addressbook.thrift")
    print("Load file succeed.")
    assert ab_1.DEFAULT_LIST_SIZE == 10

    try:
        import addressbook_thrift as ab  # noqa
    except ImportError:
        print("Import hook not installed.")

    thriftpy2.install_import_hook()

    import addressbook_thrift as ab_2
    print("Magic import succeed.")
    assert ab_2.DEFAULT_LIST_SIZE == 10


def test_load():
    ab_1 = thriftpy2.load("addressbook.thrift")
    ab_2 = thriftpy2.load("addressbook.thrift",
                          module_name="addressbook_thrift")

    assert ab_1.__name__ == "addressbook"
    assert ab_2.__name__ == "addressbook_thrift"

    # load without module_name can't do pickle
    with pytest.raises(pickle.PicklingError):
        pickle.dumps(ab_1.Person(name='Bob'))

    # load with module_name set and it can be pickled
    person = ab_2.Person(name='Bob')
    assert person == pickle.loads(pickle.dumps(person))


def test_load_module():
    ab = thriftpy2.load_module("addressbook_thrift")
    assert ab.__name__ == "addressbook_thrift"
    assert sys.modules["addressbook_thrift"] == ab

    # note we can import after load_module
    import addressbook_thrift as ab2
    assert ab2 == ab


def test_duplicate_loads():
    # multiple loads with same module_name returns the same module
    ab_1 = thriftpy2.load("addressbook.thrift",
                          module_name="addressbook_thrift")
    ab_2 = thriftpy2.load("./addressbook.thrift",
                          module_name="addressbook_thrift")
    assert ab_1 == ab_2


def test_tpayload_pickle():
    ab = thriftpy2.load_module("addressbook_thrift")

    person = ab.Person(name="Bob")
    person_2 = pickle.loads(PICKLED_BYTES)

    assert person == person_2
