from hashlib import sha1
import logging

from pymongo import MongoClient
from pymongo.mongo_replica_set_client import MongoReplicaSetClient
import pymongo.uri_parser
import pymongo.errors
from saml2.eptid import Eptid
from saml2.mdstore import InMemoryMetaData
from saml2.s_utils import PolicyError

from saml2.ident import code, IdentDB, Unknown
from saml2.mdie import to_dict, from_dict

from saml2 import md
from saml2 import saml
from saml2.extension import mdui
from saml2.extension import idpdisc
from saml2.extension import dri
from saml2.extension import mdattr
from saml2.extension import ui
import xmldsig
import xmlenc


ONTS = {
    saml.NAMESPACE: saml,
    mdui.NAMESPACE: mdui,
    mdattr.NAMESPACE: mdattr,
    dri.NAMESPACE: dri,
    ui.NAMESPACE: ui,
    idpdisc.NAMESPACE: idpdisc,
    md.NAMESPACE: md,
    xmldsig.NAMESPACE: xmldsig,
    xmlenc.NAMESPACE: xmlenc
}

__author__ = 'rolandh'

logger = logging.getLogger(__name__)


class CorruptDatabase(Exception):
    pass


def context_match(cfilter, cntx):
    # TODO
    return True


class SessionStorageMDB(object):
    """ Session information is stored in a MongoDB database"""

    def __init__(self, database="", collection="assertion", **kwargs):
        db = _mdb_get_database(database, **kwargs)
        self.assertion = db[collection]

    def store_assertion(self, assertion, to_sign):
        name_id = assertion.subject.name_id
        nkey = sha1(code(name_id)).hexdigest()

        doc = {
            "name_id_key": nkey,
            "assertion_id": assertion.id,
            "assertion": to_dict(assertion, ONTS.values(), True),
            "to_sign": to_sign
        }

        _ = self.assertion.insert(doc)

    def get_assertion(self, cid):
        res = []
        for item in self.assertion.find({"assertion_id": cid}):
            res.append({"assertion": from_dict(item["assertion"], ONTS, True),
                        "to_sign": item["to_sign"]})
        if len(res) == 1:
            return res[0]
        elif res is []:
            return None
        else:
            raise SystemError("More then one assertion with the same ID")

    def get_assertions_by_subject(self, name_id=None, session_index=None,
                                  requested_context=None):
        """

        :param name_id: One of name_id or key can be used to get the authn
            statement
        :param session_index: If match against a session index should be done
        :param requested_context: Authn statements should match a specific
            authn context
        :return:
        """
        result = []
        key = sha1(code(name_id)).hexdigest()
        for item in self.assertion.find({"name_id_key": key}):
            assertion = from_dict(item["assertion"], ONTS, True)
            if session_index or requested_context:
                for statement in assertion.authn_statement:
                    if session_index:
                        if statement.session_index == session_index:
                            result.append(assertion)
                            break
                    if requested_context:
                        if context_match(requested_context,
                                         statement.authn_context):
                            result.append(assertion)
                            break
            else:
                result.append(assertion)
        return result

    def remove_authn_statements(self, name_id):
        logger.debug("remove authn about: %s" % name_id)
        key = sha1(code(name_id)).hexdigest()
        for item in self.assertion.find({"name_id_key": key}):
            self.assertion.remove(item["_id"])

    def get_authn_statements(self, name_id, session_index=None,
                             requested_context=None):
        """

        :param name_id:
        :param session_index:
        :param requested_context:
        :return:
        """
        return [k.authn_statement for k in self.get_assertions_by_subject(
            name_id, session_index, requested_context)]


class IdentMDB(IdentDB):
    def __init__(self, database="", collection="ident", domain="",
                 name_qualifier=""):
        IdentDB.__init__(self, None, domain, name_qualifier)
        self.mdb = MDB(database=database, collection=collection)
        self.mdb.primary_key = "user_id"

    def in_store(self, _id):
        if [x for x in self.mdb.get(ident_id=_id)]:
            return True
        else:
            return False

    def create_id(self, nformat, name_qualifier="", sp_name_qualifier=""):
        _id = self._create_id(nformat, name_qualifier, sp_name_qualifier)
        while self.in_store(_id):
            _id = self._create_id(nformat, name_qualifier, sp_name_qualifier)
        return _id

    def store(self, ident, name_id):
        self.mdb.store(ident, name_id=to_dict(name_id, ONTS.values(), True))

    def find_nameid(self, userid, nformat=None, sp_name_qualifier=None,
                    name_qualifier=None, sp_provided_id=None, **kwargs):
        # reset passed for compatibility kwargs for next usage
        kwargs = {}
        if nformat:
            kwargs["name_format"] = nformat
        if sp_name_qualifier:
            kwargs["sp_name_qualifier"] = sp_name_qualifier
        if name_qualifier:
            kwargs["name_qualifier"] = name_qualifier
        if sp_provided_id:
            kwargs["sp_provided_id"] = sp_provided_id

        res = []
        for item in self.mdb.get(userid, **kwargs):
            res.append(from_dict(item["name_id"], ONTS, True))
        return res

    def find_local_id(self, name_id):
        cnid = to_dict(name_id, ONTS.values(), True)
        for item in self.mdb.get(name_id=cnid):
            return item[self.mdb.primary_key]
        return None

    def remove_remote(self, name_id):
        cnid = to_dict(name_id, ONTS.values(), True)
        self.mdb.remove(name_id=cnid)

    def handle_name_id_mapping_request(self, name_id, name_id_policy):
        _id = self.find_local_id(name_id)
        if not _id:
            raise Unknown("Unknown entity")

        if name_id_policy.allow_create == "false":
            raise PolicyError("Not allowed to create new identifier")

        # else create and return a new one
        return self.construct_nameid(_id, name_id_policy=name_id_policy)

    def close(self):
        pass


#------------------------------------------------------------------------------
class MDB(object):
    primary_key = "mdb"

    def __init__(self, database, collection, **kwargs):
        _db = _mdb_get_database(database, **kwargs)
        self.db = _db[collection]

    def store(self, value, **kwargs):
        if value:
            doc = {self.primary_key: value}
        else:
            doc = {}
        doc.update(kwargs)
        _ = self.db.insert(doc)

    def get(self, value=None, **kwargs):
        if value is not None:
            doc = {self.primary_key: value}
            doc.update(kwargs)
            return [item for item in self.db.find(doc)]
        elif kwargs:
            return [item for item in self.db.find(kwargs)]

    def remove(self, key=None, **kwargs):
        if key is None:
            if kwargs:
                for item in self.db.find(kwargs):
                    self.db.remove(item["_id"])
        else:
            doc = {self.primary_key: key}
            doc.update(kwargs)
            for item in self.db.find(doc):
                self.db.remove(item["_id"])

    def keys(self):
        for item in self.db.find():
            yield item[self.primary_key]

    def items(self):
        for item in self.db.find():
            _key = item[self.primary_key]
            del item[self.primary_key]
            del item["_id"]
            yield _key, item

    def __contains__(self, key):
        doc = {self.primary_key: key}
        res = [item for item in self.db.find(doc)]
        if not res:
            return False
        else:
            return True

    def reset(self):
        self.db.drop()


def _mdb_get_database(uri, **kwargs):
    """
    Helper-function to connect to MongoDB and return a database object.

    The `uri' argument should be either a full MongoDB connection URI string,
    or just a database name in which case a connection to the default mongo
    instance at mongodb://localhost:27017 will be made.

    Performs explicit authentication if a username is provided in a connection
    string URI, since PyMongo does not always seem to do that as promised.

    :params database: name as string or (uri, name)
    :returns: pymongo database object
    """
    if not "tz_aware" in kwargs:
        # default, but not forced
        kwargs["tz_aware"] = True

    connection_factory = MongoClient
    _parsed_uri = {}

    try:
        _parsed_uri = pymongo.uri_parser.parse_uri(uri)
    except pymongo.errors.InvalidURI:
        # assume URI to be just the database name
        db_name = uri
        _conn = MongoClient()
        pass
    else:
        if "replicaset" in _parsed_uri["options"]:
            connection_factory = MongoReplicaSetClient
        db_name = _parsed_uri.get("database", "pysaml2")
        _conn = connection_factory(uri, **kwargs)

    _db = _conn[db_name]

    if "username" in _parsed_uri:
        _db.authenticate(
            _parsed_uri.get("username", None),
            _parsed_uri.get("password", None)
        )

    return _db


#------------------------------------------------------------------------------
class EptidMDB(Eptid):
    def __init__(self, secret, database="", collection="eptid"):
        Eptid.__init__(self, secret)
        self.mdb = MDB(database, collection)
        self.mdb.primary_key = "eptid_key"

    def __getitem__(self, key):
        res = self.mdb.get(key)
        if not res:
            raise KeyError(key)
        elif len(res) == 1:
            return res[0]["eptid"]
        else:
            raise CorruptDatabase("Found more than one EPTID document")

    def __setitem__(self, key, value):
        _ = self.mdb.store(key, **{"eptid": value})


#------------------------------------------------------------------------------

def protect(dic):
    res = {}
    for key, val in dic.items():
        key = key.replace(".", "__")
        if isinstance(val, basestring):
            pass
        elif isinstance(val, dict):
            val = protect(val)
        elif isinstance(val, list):
            li = []
            for va in val:
                if isinstance(va, basestring):
                    pass
                elif isinstance(va, dict):
                    va = protect(va)
                    # I don't think lists of lists will appear am I wrong ?
                li.append(va)
            val = li
        res[key] = val
    return res


def unprotect(dic):
    res = {}
    for key, val in dic.items():
        if key == "__class__":
            pass
        else:
            key = key.replace("__", ".")
        if isinstance(val, basestring):
            pass
        elif isinstance(val, dict):
            val = unprotect(val)
        elif isinstance(val, list):
            li = []
            for va in val:
                if isinstance(va, basestring):
                    pass
                elif isinstance(val, dict):
                    va = unprotect(va)
                li.append(va)
            val = li
        res[key] = val
    return res


def export_mdstore_to_mongo_db(mds, database, collection, sub_collection=""):
    mdb = MDB(database, collection, sub_collection=sub_collection)
    mdb.reset()
    mdb.primary_key = "entity_id"
    for key, desc in mds.items():
        kwargs = {
            "entity_description": protect(desc),
        }
        mdb.store(key, **kwargs)


class MetadataMDB(InMemoryMetaData):
    def __init__(self, onts, attrc, database="", collection=""):
        super(MetadataMDB, self).__init__(onts, attrc)
        self.mdb = MDB(database, collection)
        self.mdb.primary_key = "entity_id"

    def _ext_service(self, entity_id, typ, service, binding):
        try:
            srvs = self[entity_id][typ]
        except KeyError:
            return None

        if not srvs:
            return srvs

        res = []
        for srv in srvs:
            if "extensions" in srv:
                for elem in srv["extensions"]["extension_elements"]:
                    if elem["__class__"] == service:
                        if elem["binding"] == binding:
                            res.append(elem)

        return res

    def load(self):
        pass

    def items(self):
        for key, item in self.mdb.items():
            yield key, unprotect(item["entity_description"])

    def keys(self):
        return self.mdb.keys()

    def values(self):
        for key, item in self.mdb.items():
            yield unprotect(item["entity_description"])

    def __contains__(self, item):
        return item in self.mdb

    def __getitem__(self, item):
        res = self.mdb.get(item)
        if not res:
            raise KeyError(item)
        elif len(res) == 1:
            return unprotect(res[0]["entity_description"])
        else:
            raise CorruptDatabase("More then one document with key %s" % item)

    def bindings(self, entity_id, typ, service):
        pass
