# -*- coding: utf-8 -*-

"""This file is a demo for what the dynamiclly generated code would be like.
"""

from thriftpy2.thrift import (
    TPayload,
    TException,
    TType,
)

from container import MixItem


DEFAULT_LIST_SIZE = 10


class PhoneType(object):
    MOBILE = 0
    HOME = 1
    WORK = 2


class PhoneNumber(TPayload):
    thrift_spec = {
        1: (TType.I32, "type", PhoneType, False),
        2: (TType.STRING, "number", False),
        3: (TType.STRUCT, "mix_item", MixItem, False),
    }
    default_spec = [("type", None), ("number", None), ("mix_item", None)]


class Person(TPayload):
    thrift_spec = {
        1: (TType.STRING, "name", False),
        2: (TType.LIST, "phones", (TType.STRUCT, PhoneNumber)),
        4: (TType.I32, "created_at", False),
    }
    default_spec = [("name", None), ("phones", None), ("created_at", None)]


class AddressBook(TPayload):
    thrift_spec = {
        1: (TType.MAP, "people",
            (TType.STRING, (TType.STRUCT, Person)))
    }
    default_spec = [("people", None)]


class PersonNotExistsError(TException):
    thrift_spec = {
        1: (TType.STRING, "message", False)
    }
    default_spec = [("message", None)]


class AddressBookService(object):
    thrift_services = [
        "ping",
        "hello",
        "add",
        "remove",
        "get",
        "book",
        "get_phonenumbers",
        "get_phones",
        "sleep",
    ]

    class ping_args(TPayload):
        thrift_spec = {}
        default_spec = []

    class ping_result(TPayload):
        thrift_spec = {}
        default_spec = []

    class hello_args(TPayload):
        thrift_spec = {
            1: (TType.STRING, "name"),
        }
        default_spec = [("name", None)]

    class hello_result(TPayload):
        thrift_spec = {
            0: (TType.STRING, "success"),
        }
        default_spec = [("success", None)]

    class add_args(TPayload):
        thrift_spec = {
            1: (TType.STRUCT, "person", Person),
        }
        default_spec = [("person", None)]

    class add_result(TPayload):
        thrift_spec = {
            0: (TType.BOOL, "success"),
        }
        default_spec = [("success", None)]

    class remove_args(TPayload):
        thrift_spec = {
            1: (TType.STRING, "name"),
        }
        default_spec = [("name", None)]

    class remove_result(TPayload):
        thrift_spec = {
            0: (TType.BOOL, "success"),
            1: (TType.STRUCT, "not_exists", PersonNotExistsError)
        }
        default_spec = [("success", None), ("not_exists", None)]

    class get_args(TPayload):
        thrift_spec = {
            1: (TType.STRING, "name"),
        }
        default_spec = [("name", None)]

    class get_result(TPayload):
        thrift_spec = {
            0: (TType.STRUCT, "success", Person),
            1: (TType.STRUCT, "not_exists", PersonNotExistsError)
        }
        default_spec = [("success", None), ("not_exists", None)]

    class book_args(TPayload):
        thrift_spec = {}
        default_spec = []

    class book_result(TPayload):
        thrift_spec = {
            0: (TType.STRUCT, "success", AddressBook),
        }
        default_spec = [("success", None)]

    class get_phonenumbers_args(TPayload):
        thrift_spec = {
            1: (TType.STRING, "name"),
            2: (TType.I32, "count"),
        }
        default_spec = [("name", None), ("count", None)]

    class get_phonenumbers_result(TPayload):
        thrift_spec = {
            0: (TType.LIST, "success", (TType.STRUCT)),
        }
        default_spec = [("success", None)]

    class get_phones_args(TPayload):
        thrift_spec = {
            1: (TType.STRING, "name"),
        }
        default_spec = [("name", None)]

    class get_phones_result(TPayload):
        thrift_spec = {
            0: (TType.MAP, "success", (TType.I32, TType.STRING)),
        }
        default_spec = [("success", None)]

    class sleep_args(TPayload):
        thrift_spec = {
            1: (TType.I16, "ms"),
        }
        default_spec = []

    class sleep_result(TPayload):
        thrift_spec = {
            0: (TType.BOOL, "success"),
        }
        default_spec = [("success", None)]
