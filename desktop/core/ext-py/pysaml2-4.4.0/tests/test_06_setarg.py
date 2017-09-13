from saml2 import saml
from saml2.saml import Subject
from saml2.samlp import Response
from saml2.argtree import set_arg, add_path, is_set
from saml2.argtree import find_paths

__author__ = 'roland'


def test_path():
    result = find_paths(Subject, 'in_response_to')

    assert result == [
        ['subject_confirmation', 'subject_confirmation_data', 'in_response_to']]

    result = find_paths(Response, 'in_response_to')

    assert result == [
        ['assertion', 'subject', 'subject_confirmation',
         'subject_confirmation_data', 'in_response_to'],
        ['in_response_to']
    ]


def test_set_arg():
    r = set_arg(Subject, 'in_response_to', '123456')

    assert r == [{'subject_confirmation': {
        'subject_confirmation_data': {'in_response_to': '123456'}}}]


def test_multi():
    t = {}
    t = add_path(t, ['subject_confirmation','method',saml.SCM_BEARER])
    add_path(t['subject_confirmation'],
             ['subject_confirmation_data','in_response_to','1234'])

    assert t == {
        'subject_confirmation': {
            'subject_confirmation_data': {'in_response_to': '1234'},
            'method': 'urn:oasis:names:tc:SAML:2.0:cm:bearer'}
    }


def test_is_set():
    t = {}
    t = add_path(t, ['subject_confirmation','method',saml.SCM_BEARER])
    add_path(t['subject_confirmation'],
             ['subject_confirmation_data','in_response_to','1234'])

    assert is_set(t, ['subject_confirmation','method'])
    assert is_set(t, ['subject_confirmation', 'subject_confirmation_data',
                      'receiver']) is False
