import logging

from hashlib import sha1

from saml2.ident import code_binary

from saml2 import md
from saml2 import saml
from saml2.extension import mdui
from saml2.extension import idpdisc
from saml2.extension import dri
from saml2.extension import mdattr
from saml2.extension import ui
from saml2 import xmldsig
from saml2 import xmlenc


__author__ = 'rolandh'

logger = logging.getLogger(__name__)


def context_match(cfilter, cntx):
    # TODO
    return True

# The key to the stored authn statement is placed encrypted in the cookie


class SessionStorage(object):
    """ In memory storage of session information """

    def __init__(self):
        self.db = {"assertion": {}, "authn": {}}
        self.assertion = self.db["assertion"]
        self.authn = self.db["authn"]

    def store_assertion(self, assertion, to_sign):
        self.assertion[assertion.id] = (assertion, to_sign)
        key = sha1(code_binary(assertion.subject.name_id)).hexdigest()
        try:
            self.authn[key].append(assertion.authn_statement)
        except KeyError:
            self.authn[key] = [assertion.authn_statement]

    def get_assertion(self, cid):
        return self.assertion[cid]

    def get_authn_statements(self, name_id, session_index=None,
                             requested_context=None):
        """

        :param name_id:
        :param session_index:
        :param requested_context:
        :return:
        """
        result = []
        key = sha1(code_binary(name_id)).hexdigest()
        try:
            statements = self.authn[key]
        except KeyError:
            logger.info("Unknown subject %s", name_id)
            return []

        for statement in statements:
            if session_index:
                if statement.session_index != session_index:
                    continue
            if requested_context:
                if not context_match(requested_context,
                                     statement[0].authn_context):
                    continue
            result.append(statement)

        return result

    def remove_authn_statements(self, name_id):
        logger.debug("remove authn about: %s", name_id)
        nkey = sha1(code_binary(name_id)).hexdigest()

        del self.authn[nkey]
