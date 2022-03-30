from __future__ import print_function
import hashlib
import importlib
import json
import logging
import os
import sys

from hashlib import sha1
from os.path import isfile
from os.path import join

import requests
import six

from saml2 import md
from saml2 import saml
from saml2 import samlp
from saml2 import xmldsig
from saml2 import xmlenc
from saml2 import SAMLError
from saml2 import BINDING_HTTP_REDIRECT
from saml2 import BINDING_HTTP_POST
from saml2 import BINDING_SOAP

from saml2.httpbase import HTTPBase
from saml2.extension.idpdisc import BINDING_DISCO
from saml2.extension.idpdisc import DiscoveryResponse
from saml2.md import EntitiesDescriptor
from saml2.mdie import to_dict
from saml2.s_utils import UnsupportedBinding
from saml2.s_utils import UnknownSystemEntity
from saml2.sigver import split_len
from saml2.validate import valid_instance
from saml2.time_util import valid
from saml2.time_util import instant
from saml2.time_util import add_duration
from saml2.time_util import before
from saml2.time_util import str_to_time
from saml2.validate import NotValid
from saml2.sigver import security_context
from saml2.extension.mdattr import NAMESPACE as NS_MDATTR
from saml2.extension.mdattr import EntityAttributes
from saml2.extension.algsupport import NAMESPACE as NS_ALGSUPPORT
from saml2.extension.algsupport import SigningMethod, DigestMethod
from saml2.extension.mdui import NAMESPACE as NS_MDUI
from saml2.extension.mdui import UIInfo
from saml2.extension.mdui import DisplayName
from saml2.extension.mdui import Description
from saml2.extension.mdui import InformationURL
from saml2.extension.mdui import PrivacyStatementURL
from saml2.extension.mdui import Logo


logger = logging.getLogger(__name__)

classnames = {
    "mdattr_entityattributes": "{ns}&{tag}".format(
        ns=NS_MDATTR, tag=EntityAttributes.c_tag
    ),
    "algsupport_signing_method": "{ns}&{tag}".format(ns=NS_ALGSUPPORT, tag=SigningMethod.c_tag),
    "algsupport_digest_method": "{ns}&{tag}".format(ns=NS_ALGSUPPORT, tag=DigestMethod.c_tag),
    "mdui_uiinfo": "{ns}&{tag}".format(ns=NS_MDUI, tag=UIInfo.c_tag),
    "mdui_uiinfo_display_name": "{ns}&{tag}".format(ns=NS_MDUI, tag=DisplayName.c_tag),
    "mdui_uiinfo_description": "{ns}&{tag}".format(ns=NS_MDUI, tag=Description.c_tag),
    "mdui_uiinfo_information_url": "{ns}&{tag}".format(
        ns=NS_MDUI, tag=InformationURL.c_tag
    ),
    "mdui_uiinfo_privacy_statement_url": "{ns}&{tag}".format(
        ns=NS_MDUI, tag=PrivacyStatementURL.c_tag
    ),
    "mdui_uiinfo_logo": "{ns}&{tag}".format(ns=NS_MDUI, tag=Logo.c_tag),
}

ENTITY_CATEGORY = "http://macedir.org/entity-category"
ENTITY_CATEGORY_SUPPORT = "http://macedir.org/entity-category-support"
ASSURANCE_CERTIFICATION = "urn:oasis:names:tc:SAML:attribute:assurance-certification"

SAML_METADATA_CONTENT_TYPE = "application/samlmetadata+xml"
DEFAULT_FRESHNESS_PERIOD = "P0Y0M0DT12H0M0S"



REQ2SRV = {
    # IDP
    "authn_request": "single_sign_on_service",
    "name_id_mapping_request": "name_id_mapping_service",
    # AuthnAuthority
    "authn_query": "authn_query_service",
    # AttributeAuthority
    "attribute_query": "attribute_service",
    # PDP
    "authz_decision_query": "authz_service",
    # AuthnAuthority + IDP + PDP + AttributeAuthority
    "assertion_id_request": "assertion_id_request_service",
    # IDP + SP
    "logout_request": "single_logout_service",
    "manage_name_id_request": "manage_name_id_service",
    "artifact_query": "artifact_resolution_service",
    # SP
    "assertion_response": "assertion_consumer_service",
    "attribute_response": "attribute_consuming_service",
    "discovery_service_request": "discovery_response"
}


class ToOld(Exception):
    pass


class TooOld(ToOld):
    pass


class SourceNotFound(Exception):
    pass


def load_extensions():
    from saml2 import extension
    import pkgutil

    package = extension
    prefix = package.__name__ + "."
    ext_map = {}
    for importer, modname, ispkg in pkgutil.iter_modules(package.__path__,
                                                         prefix):
        module = __import__(modname, fromlist="dummy")
        ext_map[module.NAMESPACE] = module

    return ext_map


def load_metadata_modules():
    mods = {
        saml.NAMESPACE: saml,
        md.NAMESPACE: md,
        xmldsig.NAMESPACE: xmldsig,
        xmlenc.NAMESPACE: xmlenc
    }

    mods.update(load_extensions())
    return mods


def metadata_modules():
    _res = [saml, md, xmldsig, xmlenc]
    _res.extend(list(load_extensions().values()))
    return _res


def destinations(srvs):
    return [s["location"] for s in srvs]


def attribute_requirement(entity, index=None):
    res = {"required": [], "optional": []}
    for acs in entity["attribute_consuming_service"]:
        if index is not None and acs["index"] != index:
            continue

        for attr in acs["requested_attribute"]:
            if "is_required" in attr and attr["is_required"] == "true":
                res["required"].append(attr)
            else:
                res["optional"].append(attr)
    return res


def name(ent, langpref="en"):
    try:
        org = ent["organization"]
    except KeyError:
        return None

    for info in ["organization_display_name",
                 "organization_name",
                 "organization_url"]:
        try:
            for item in org[info]:
                if item["lang"] == langpref:
                    return item["text"]
        except KeyError:
            pass
    return None


def repack_cert(cert):
    part = cert.split("\n")
    if len(part) == 1:
        part = part[0].strip()
        return "\n".join(split_len(part, 64))
    else:
        return "\n".join([s.strip() for s in part])


class MetaData(object):
    def __init__(self, attrc, metadata='', node_name=None,
                 check_validity=True, security=None, **kwargs):
        self.attrc = attrc
        self.metadata = metadata
        self.entity = None
        self.cert = None
        self.to_old = []
        self.node_name = node_name
        self.check_validity = check_validity
        self.security = security

    def items(self):
        '''
        Returns list of items contained in the storage
        '''
        raise NotImplementedError

    def keys(self):
        '''
        Returns keys (identifiers) of items in storage
        '''
        raise NotImplementedError

    def values(self):
        '''
        Returns values of items in storage
        '''
        raise NotImplementedError

    def __len__(self):
        '''
        Returns number of stored items
        '''
        raise NotImplementedError

    def __contains__(self, item):
        '''
        Returns True if the storage contains item
        '''
        raise NotImplementedError

    def __getitem__(self, item):
        '''
        Returns the item specified by the key
        '''
        raise NotImplementedError

    def __setitem__(self, key, value):
        '''
        Sets a key to a value
        '''
        raise NotImplementedError

    def __delitem__(self, key):
        '''
        Removes key from storage
        '''
        raise NotImplementedError

    def do_entity_descriptor(self, entity_descr):
        '''
        #FIXME - Add description
        '''
        raise NotImplementedError

    def parse(self, xmlstr):
        '''
        #FIXME - Add description
        '''
        raise NotImplementedError

    def load(self, *args, **kwargs):
        '''
        Loads the metadata
        '''
        self.parse(self.metadata)

    def service(self, entity_id, typ, service, binding=None):
        """ Get me all services with a specified
        entity ID and type, that supports the specified version of binding.

        :param entity_id: The EntityId
        :param typ: Type of service (idp, attribute_authority, ...)
        :param service: which service that is sought for
        :param binding: A binding identifier
        :return: list of service descriptions.
            Or if no binding was specified a list of 2-tuples (binding, srv)
        """
        raise NotImplementedError

    def ext_service(self, entity_id, typ, service, binding):
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

    def any(self, typ, service, binding=None):
        """
        Return any entity that matches the specification

        :param typ: Type of entity
        :param service:
        :param binding:
        :return:
        """
        res = {}
        for ent in self.keys():
            bind = self.service(ent, typ, service, binding)
            if bind:
                res[ent] = bind

        return res

    def any2(self, typ, service, binding=None):
        """

        :param type:
        :param service:
        :param binding:
        :return:
        """
        res = {}
        for entid, item in self.items():
            hit = False
            try:
                descr = item['{}sso_descriptor'.format(typ)]
            except KeyError:
                continue
            else:
                for desc in descr:
                    try:
                        srvs = desc[service]
                    except KeyError:
                        continue
                    else:
                        for srv in srvs:
                            if srv['binding'] == binding:
                                res[entid] = item
                                hit = True
                                break
                    if hit:
                        break
        return res

    def bindings(self, entity_id, typ, service):
        """
        Get me all the bindings that are registered for a service entity

        :param entity_id:
        :param service:
        :return:
        """
        return self.service(entity_id, typ, service)

    def attribute_requirement(self, entity_id, index=None):
        """ Returns what attributes the SP requires and which are optional
        if any such demands are registered in the Metadata.

        :param entity_id: The entity id of the SP
        :param index: which of the attribute consumer services its all about
            if index=None then return all attributes expected by all
            attribute_consuming_services.
        :return: 2-tuple, list of required and list of optional attributes
        """
        raise NotImplementedError

    def dumps(self):
        return json.dumps(list(self.items()), indent=2)

    def with_descriptor(self, descriptor):
        '''
        Returns any entities with the specified descriptor
        '''
        res = {}
        desc = "%s_descriptor" % descriptor
        for eid, ent in self.items():
            if desc in ent:
                res[eid] = ent
        return res

    def __str__(self):
        return "%s" % self.items()

    def construct_source_id(self):
        raise NotImplementedError

    def entity_categories(self, entity_id):
        res = []
        if "extensions" in self[entity_id]:
            for elem in self[entity_id]["extensions"]["extension_elements"]:
                if elem["__class__"] == classnames["mdattr_entityattributes"]:
                    for attr in elem["attribute"]:
                        res.append(attr["text"])

        return res

    def __eq__(self, other):
        try:
            assert isinstance(other, MetaData)
        except AssertionError:
            return False

        if len(self.entity) != len(other.entity):
            return False

        if set(self.entity.keys()) != set(other.entity.keys()):
            return False

        for key, item in self.entity.items():
            try:
                assert item == other[key]
            except AssertionError:
                return False

        return True

    def certs(self, entity_id, descriptor, use="signing"):
        '''
        Returns certificates for the given Entity
        '''
        ent = self[entity_id]

        def extract_certs(srvs):
            res = []
            for srv in srvs:
                if "key_descriptor" in srv:
                    for key in srv["key_descriptor"]:
                        if "use" in key and key["use"] == use:
                            for dat in key["key_info"]["x509_data"]:
                                cert = repack_cert(
                                    dat["x509_certificate"]["text"])
                                if cert not in res:
                                    res.append(cert)
                        elif not "use" in key:
                            for dat in key["key_info"]["x509_data"]:
                                cert = repack_cert(
                                    dat["x509_certificate"]["text"])
                                if cert not in res:
                                    res.append(cert)

            return res

        if descriptor == "any":
            res = []
            for descr in ["spsso", "idpsso", "role", "authn_authority",
                          "attribute_authority", "pdp"]:
                try:
                    srvs = ent["%s_descriptor" % descr]
                except KeyError:
                    continue

                res.extend(extract_certs(srvs))
        else:
            srvs = ent["%s_descriptor" % descriptor]
            res = extract_certs(srvs)

        return res


class InMemoryMetaData(MetaData):
    def __init__(self, attrc, metadata="", node_name=None,
                 check_validity=True, security=None, **kwargs):
        super(InMemoryMetaData, self).__init__(attrc, metadata=metadata)
        self.entity = {}
        self.security = security
        self.node_name = node_name
        self.entities_descr = None
        self.entity_descr = None
        self.check_validity = check_validity
        try:
            self.filter = kwargs["filter"]
        except KeyError:
            self.filter = None

    def items(self):
        return self.entity.items()

    def keys(self):
        return self.entity.keys()

    def values(self):
        return self.entity.values()

    def __len__(self):
        return len(self.entity)

    def __contains__(self, item):
        return item in self.entity.keys()

    def __getitem__(self, item):
        return self.entity[item]

    def __setitem__(self, key, value):
        self.entity[key] = value

    def __delitem__(self, key):
        del self.entity[key]

    def do_entity_descriptor(self, entity_descr):
        if self.check_validity:
            try:
                if not valid(entity_descr.valid_until):
                    logger.error("Entity descriptor (entity id:%s) too old",
                                 entity_descr.entity_id)
                    self.to_old.append(entity_descr.entity_id)
                    return
            except AttributeError:
                pass

        # have I seen this entity_id before ? If so if log: ignore it
        if entity_descr.entity_id in self.entity:
            print("Duplicated Entity descriptor (entity id: '%s')" %
                  entity_descr.entity_id, file=sys.stderr)
            return

        _ent = to_dict(entity_descr, metadata_modules())
        flag = 0
        # verify support for SAML2
        for descr in ["spsso", "idpsso", "role", "authn_authority",
                      "attribute_authority", "pdp", "affiliation"]:
            _res = []
            try:
                _items = _ent["%s_descriptor" % descr]
            except KeyError:
                continue

            if descr == "affiliation":  # Not protocol specific
                flag += 1
                continue

            for item in _items:
                for prot in item["protocol_support_enumeration"].split(" "):
                    if prot == samlp.NAMESPACE:
                        item["protocol_support_enumeration"] = prot
                        _res.append(item)
                        break
            if not _res:
                del _ent["%s_descriptor" % descr]
            else:
                flag += 1

        if self.filter:
            _ent = self.filter(_ent)
            if not _ent:
                flag = 0

        if flag:
            self.entity[entity_descr.entity_id] = _ent

    def parse(self, xmlstr):
        self.entities_descr = md.entities_descriptor_from_string(xmlstr)

        if not self.entities_descr:
            self.entity_descr = md.entity_descriptor_from_string(xmlstr)
            if self.entity_descr:
                self.do_entity_descriptor(self.entity_descr)
        else:
            try:
                valid_instance(self.entities_descr)
            except NotValid as exc:
                logger.error("Invalid XML message: %s", exc.args[0])
                return

            if self.check_validity:
                try:
                    if not valid(self.entities_descr.valid_until):
                        raise TooOld(
                            "Metadata not valid anymore, it's only valid "
                            "until %s" % (
                                self.entities_descr.valid_until,))
                except AttributeError:
                    pass

            for entity_descr in self.entities_descr.entity_descriptor:
                self.do_entity_descriptor(entity_descr)

    def service(self, entity_id, typ, service, binding=None):
        """ Get me all services with a specified
        entity ID and type, that supports the specified version of binding.

        :param entity_id: The EntityId
        :param typ: Type of service (idp, attribute_authority, ...)
        :param service: which service that is sought for
        :param binding: A binding identifier
        :return: list of service descriptions.
            Or if no binding was specified a list of 2-tuples (binding, srv)
        """
        try:
            srvs = []
            for t in self[entity_id][typ]:
                try:
                    srvs.extend(t[service])
                except KeyError:
                    pass
        except KeyError:
            return None

        if not srvs:
            return srvs

        if binding:
            res = []
            for srv in srvs:
                if srv["binding"] == binding:
                    res.append(srv)
        else:
            res = {}
            for srv in srvs:
                try:
                    res[srv["binding"]].append(srv)
                except KeyError:
                    res[srv["binding"]] = [srv]
        logger.debug("service => %s", res)
        return res

    def attribute_requirement(self, entity_id, index=None):
        """ Returns what attributes the SP requires and which are optional
        if any such demands are registered in the Metadata.

        :param entity_id: The entity id of the SP
        :param index: which of the attribute consumer services its all about
            if index=None then return all attributes expected by all
            attribute_consuming_services.
        :return: 2-tuple, list of required and list of optional attributes
        """
        res = {"required": [], "optional": []}

        try:
            for sp in self[entity_id]["spsso_descriptor"]:
                _res = attribute_requirement(sp, index)
                res["required"].extend(_res["required"])
                res["optional"].extend(_res["optional"])
        except KeyError:
            return None

        return res

    def construct_source_id(self):
        res = {}
        for eid, ent in self.items():
            for desc in ["spsso_descriptor", "idpsso_descriptor"]:
                try:
                    for srv in ent[desc]:
                        if "artifact_resolution_service" in srv:
                            if isinstance(eid, six.string_types):
                                eid = eid.encode('utf-8')
                            s = sha1(eid)
                            res[s.digest()] = ent
                except KeyError:
                    pass

        return res

    def signed(self):
        if self.entities_descr and self.entities_descr.signature:
            return True

        if self.entity_descr and self.entity_descr.signature:
            return True
        else:
            return False

    def parse_and_check_signature(self, txt):
        self.parse(txt)

        if not self.cert:
            return True

        if not self.signed():
            return True

        fallback_name = "{ns}:{tag}".format(
            ns=md.EntitiesDescriptor.c_namespace, tag=md.EntitiesDescriptor.c_tag
        )
        node_name = self.node_name or fallback_name

        return self.security.verify_signature(
            txt, node_name=node_name, cert_file=self.cert
        )


class MetaDataFile(InMemoryMetaData):
    """
    Handles Metadata file on the same machine. The format of the file is
    the SAML Metadata format.
    """

    def __init__(self, attrc, filename=None, cert=None, **kwargs):
        super(MetaDataFile, self).__init__(attrc, **kwargs)
        if not filename:
            raise SAMLError('No file specified.')
        self.filename = filename
        self.cert = cert

    def get_metadata_content(self):
        with open(self.filename, 'rb') as fp:
            return fp.read()

    def load(self, *args, **kwargs):
        _txt = self.get_metadata_content()
        return self.parse_and_check_signature(_txt)


class MetaDataLoader(MetaDataFile):
    """
    Handles Metadata file loaded by a passed in function.
    The format of the file is the SAML Metadata format.
    """

    def __init__(self, attrc, loader_callable, cert=None,
                 security=None, **kwargs):
        super(MetaDataLoader, self).__init__(attrc, **kwargs)
        self.metadata_provider_callable = self.get_metadata_loader(
            loader_callable)
        self.cert = cert
        self.security = security

    @staticmethod
    def get_metadata_loader(func):
        if hasattr(func, '__call__'):
            return func

        i = func.rfind('.')
        module, attr = func[:i], func[i + 1:]
        try:
            mod = importlib.import_module(module)
        except Exception as e:
            raise RuntimeError(
                'Cannot find metadata provider function %s: "%s"' % (func, e))

        try:
            metadata_loader = getattr(mod, attr)
        except AttributeError:
            raise RuntimeError(
                'Module "%s" does not define a "%s" metadata loader' % (
                    module, attr))

        if not hasattr(metadata_loader, '__call__'):
            raise RuntimeError(
                'Metadata loader %s.%s must be callable' % (module, attr))

        return metadata_loader

    def get_metadata_content(self):
        return self.metadata_provider_callable()


class MetaDataExtern(InMemoryMetaData):
    """
    Class that handles metadata store somewhere on the net.
    Accessible by HTTP GET.
    """

    def __init__(self, attrc, url=None, security=None, cert=None,
                 http=None, **kwargs):
        """
        :params attrc:
        :params url: Location of the metadata
        :params security: SecurityContext()
        :params cert: CertificMDloaderate used to sign the metadata
        :params http:
        """
        super(MetaDataExtern, self).__init__(attrc, **kwargs)
        if not url:
            raise SAMLError('URL not specified.')
        else:
            self.url = url

        # No cert is only an error if the metadata is unsigned
        self.cert = cert

        self.security = security
        self.http = http

    def load(self, *args, **kwargs):
        """ Imports metadata by the use of HTTP GET.
        If the fingerprint is known the file will be checked for
        compliance before it is imported.
        """
        response = self.http.send(self.url)
        if response.status_code == 200:
            _txt = response.content
            return self.parse_and_check_signature(_txt)
        else:
            logger.info("Response status: %s", response.status_code)
            raise SourceNotFound(self.url)


class MetaDataMD(InMemoryMetaData):
    """
    Handles locally stored metadata, the file format is the text representation
    of the Python representation of the metadata.
    """

    def __init__(self, attrc, filename, **kwargs):
        super(MetaDataMD, self).__init__(attrc, **kwargs)
        self.filename = filename

    def load(self, *args, **kwargs):
        with open(self.filename) as fp:
            data = json.load(fp)
        for key, item in data:
            self.entity[key] = item


class MetaDataMDX(InMemoryMetaData):
    """
    Uses the MDQ protocol to fetch entity information.
    The protocol is defined at:
    https://datatracker.ietf.org/doc/draft-young-md-query-saml/
    """

    @staticmethod
    def sha1_entity_transform(entity_id):
        entity_id_sha1 = hashlib.sha1(entity_id.encode("utf-8")).hexdigest()
        transform = "{{sha1}}{digest}".format(digest=entity_id_sha1)
        return transform

    def __init__(self, url=None, security=None, cert=None,
                 entity_transform=None, freshness_period=None, **kwargs):
        """
        :params url: mdx service url
        :params security: SecurityContext()
        :params cert: certificate used to check signature of signed metadata
        :params entity_transform: function transforming (e.g. base64,
        sha1 hash or URL quote
        hash) the entity id. It is applied to the entity id before it is
        concatenated with the request URL sent to the MDX server. Defaults to
        sha1 transformation.
        :params freshness_period: a duration in the format described at
        https://www.w3.org/TR/xmlschema-2/#duration
        """
        super(MetaDataMDX, self).__init__(None, **kwargs)
        if not url:
            raise SAMLError('URL for MDQ server not specified.')

        self.url = url.rstrip('/')

        if entity_transform:
            self.entity_transform = entity_transform
        else:
            self.entity_transform = MetaDataMDX.sha1_entity_transform

        self.cert = cert
        self.security = security
        self.freshness_period = freshness_period or DEFAULT_FRESHNESS_PERIOD
        self.expiration_date = {}

        # We assume that the MDQ server will return a single entity
        # described by a single <EntityDescriptor> element. The protocol
        # does allow multiple entities to be returned in an
        # <EntitiesDescriptor> element but we will not currently support
        # that use case since it is unlikely to be leveraged for most
        # flows.
        self.node_name = "{ns}:{tag}".format(
            ns=md.EntityDescriptor.c_namespace, tag=md.EntityDescriptor.c_tag
        )

    def load(self, *args, **kwargs):
        # Do nothing
        pass

    def _fetch_metadata(self, item):
        mdx_url = "{url}/entities/{id}".format(
            url=self.url, id=self.entity_transform(item)
        )

        response = requests.get(mdx_url, headers={"Accept": SAML_METADATA_CONTENT_TYPE})
        if response.status_code != 200:
            error_msg = "Fething {item}: Got response status {status}".format(
                item=item, status=response.status_code
            )
            logger.info(error_msg)
            raise KeyError(error_msg)

        _txt = response.content
        if not self.parse_and_check_signature(_txt):
            error_msg = "Fething {item}: invalid signature".format(
                item=item, status=response.status_code
            )
            logger.info(error_msg)
            raise KeyError(error_msg)

        curr_time = str_to_time(instant())
        self.expiration_date[item] = add_duration(curr_time, self.freshness_period)
        return self.entity[item]

    def _is_metadata_fresh(self, item):
        return before(self.expiration_date[item])

    def __getitem__(self, item):
        if item not in self.entity:
            entity = self._fetch_metadata(item)
        elif not self._is_metadata_fresh(item):
            msg = "Metadata for {} have expired; refreshing metadata".format(item)
            logger.info(msg)
            old_entity = self.entity.pop(item)
            entity = self._fetch_metadata(item)
        else:
            entity = self.entity[item]
        return entity

    def single_sign_on_service(self, entity_id, binding=None, typ="idpsso"):
        if binding is None:
            binding = BINDING_HTTP_REDIRECT
        return self.service(entity_id, "idpsso_descriptor",
                            "single_sign_on_service", binding)


class MetadataStore(MetaData):
    def __init__(self, attrc, config, ca_certs=None,
                 check_validity=True,
                 disable_ssl_certificate_validation=False,
                 filter=None):
        """
        :params attrc:
        :params config: Config()
        :params ca_certs:
        :params disable_ssl_certificate_validation:
        """
        MetaData.__init__(self, attrc, check_validity=check_validity)

        if disable_ssl_certificate_validation:
            self.http = HTTPBase(verify=False, ca_bundle=ca_certs)
        else:
            self.http = HTTPBase(verify=True, ca_bundle=ca_certs)

        self.security = security_context(config)
        self.ii = 0
        self.metadata = {}
        self.check_validity = check_validity
        self.filter = filter
        self.to_old = {}

    def load(self, *args, **kwargs):
        if self.filter:
            _args = {"filter": self.filter}
        else:
            _args = {}

        typ = args[0]
        if typ == "local":
            key = args[1]
            # if library read every file in the library
            if os.path.isdir(key):
                files = [f for f in os.listdir(key) if isfile(join(key, f))]
                for fil in files:
                    _fil = join(key, fil)
                    _md = MetaDataFile(self.attrc, _fil, **_args)
                    _md.load()
                    self.metadata[_fil] = _md
                return
            else:
                # else it's just a plain old file so read it
                _md = MetaDataFile(self.attrc, key, **_args)
        elif typ == "inline":
            self.ii += 1
            key = self.ii
            kwargs.update(_args)
            _md = InMemoryMetaData(self.attrc, args[1])
        elif typ == "remote":
            if "url" not in kwargs:
                raise ValueError("Remote metadata must be structured as a dict containing the key 'url'")
            key = kwargs["url"]
            for _key in ["node_name", "check_validity"]:
                try:
                    _args[_key] = kwargs[_key]
                except KeyError:
                    pass

            if "cert" not in kwargs:
                kwargs["cert"] = ""

            _md = MetaDataExtern(self.attrc,
                                 kwargs["url"], self.security,
                                 kwargs["cert"], self.http, **_args)
        elif typ == "mdfile":
            key = args[1]
            _md = MetaDataMD(self.attrc, args[1], **_args)
        elif typ == "loader":
            key = args[1]
            _md = MetaDataLoader(self.attrc, args[1], **_args)
        elif typ == "mdq":
            if 'url' in kwargs:
                key = kwargs['url']
                url = kwargs['url']
                cert = kwargs.get('cert')
                freshness_period = kwargs.get('freshness_period', None)
                security = self.security
                entity_transform = kwargs.get('entity_transform', None)
                _md = MetaDataMDX(url, security, cert, entity_transform,
                                  freshness_period=freshness_period)
            else:
                key = args[1]
                url = args[1]
                _md = MetaDataMDX(url)
        else:
            raise SAMLError("Unknown metadata type '%s'" % typ)
        _md.load()
        self.metadata[key] = _md

    def imp(self, spec):
        # This serves as a backwards compatibility
        if type(spec) is dict:
            # Old style...
            for key, vals in spec.items():
                for val in vals:
                    if isinstance(val, dict):
                        if not self.check_validity:
                            val["check_validity"] = False
                        self.load(key, **val)
                    else:
                        self.load(key, val)
        else:
            for item in spec:
                try:
                    key = item['class']
                except (KeyError, AttributeError):
                    raise SAMLError("Misconfiguration in metadata %s" % item)
                mod, clas = key.rsplit('.', 1)
                try:
                    mod = importlib.import_module(mod)
                    MDloader = getattr(mod, clas)
                except (ImportError, AttributeError):
                    raise SAMLError("Unknown metadata loader %s" % key)

                # Separately handle MDExtern
                if MDloader == MetaDataExtern:
                    kwargs = {
                        'http': self.http,
                        'security': self.security
                    }
                else:
                    kwargs = {}

                if self.filter:
                    kwargs["filter"] = self.filter

                for key in item['metadata']:
                    # Separately handle MetaDataFile and directory
                    if MDloader == MetaDataFile and os.path.isdir(key[0]):
                        files = [f for f in os.listdir(key[0]) if
                                 isfile(join(key[0], f))]
                        for fil in files:
                            _fil = join(key[0], fil)
                            _md = MetaDataFile(self.attrc, _fil)
                            _md.load()
                            self.metadata[_fil] = _md
                            if _md.to_old:
                                self.to_old[_fil] = _md.to_old
                        return

                    if len(key) == 2:
                        kwargs["cert"] = key[1]

                    _md = MDloader(self.attrc, key[0], **kwargs)
                    _md.load()
                    self.metadata[key[0]] = _md
                    if _md.to_old:
                        self.to_old[key[0]] = _md.to_old

    def service(self, entity_id, typ, service, binding=None):
        known_entity = False
        logger.debug("service(%s, %s, %s, %s)", entity_id, typ, service,
                     binding)
        for key, _md in self.metadata.items():
            srvs = _md.service(entity_id, typ, service, binding)
            if srvs:
                return srvs
            elif srvs is None:
                pass
            else:
                known_entity = True

        if known_entity:
            logger.error("Unsupported binding: %s (%s)", binding, entity_id)
            raise UnsupportedBinding(binding)
        else:
            logger.error("Unknown system entity: %s", entity_id)
            raise UnknownSystemEntity(entity_id)

    def extension(self, entity_id, typ, service):
        for key, _md in self.metadata.items():
            try:
                srvs = _md[entity_id][typ]
            except KeyError:
                continue

            res = []
            for srv in srvs:
                if "extensions" in srv:
                    for elem in srv["extensions"]["extension_elements"]:
                        if elem["__class__"] == service:
                            res.append(elem)
            return res

        return None

    def ext_service(self, entity_id, typ, service, binding=None):
        known_entity = False
        for key, _md in self.metadata.items():
            srvs = _md.ext_service(entity_id, typ, service, binding)
            if srvs:
                return srvs
            elif srvs is None:
                pass
            else:
                known_entity = True

        if known_entity:
            raise UnsupportedBinding(binding)
        else:
            raise UnknownSystemEntity(entity_id)

    def single_sign_on_service(self, entity_id, binding=None, typ="idpsso"):
        # IDP

        if binding is None:
            binding = BINDING_HTTP_REDIRECT
        return self.service(entity_id, "idpsso_descriptor",
                            "single_sign_on_service", binding)

    def name_id_mapping_service(self, entity_id, binding=None, typ="idpsso"):
        # IDP
        if binding is None:
            binding = BINDING_HTTP_REDIRECT
        return self.service(entity_id, "idpsso_descriptor",
                            "name_id_mapping_service", binding)

    def authn_query_service(self, entity_id, binding=None,
                            typ="authn_authority"):
        # AuthnAuthority
        if binding is None:
            binding = BINDING_SOAP
        return self.service(entity_id, "authn_authority_descriptor",
                            "authn_query_service", binding)

    def attribute_service(self, entity_id, binding=None,
                          typ="attribute_authority"):
        # AttributeAuthority
        if binding is None:
            binding = BINDING_HTTP_REDIRECT
        return self.service(entity_id, "attribute_authority_descriptor",
                            "attribute_service", binding)

    def authz_service(self, entity_id, binding=None, typ="pdp"):
        # PDP
        if binding is None:
            binding = BINDING_SOAP
        return self.service(entity_id, "pdp_descriptor",
                            "authz_service", binding)

    def assertion_id_request_service(self, entity_id, binding=None, typ=None):
        # AuthnAuthority + IDP + PDP + AttributeAuthority
        if typ is None:
            raise AttributeError("Missing type specification")
        if binding is None:
            binding = BINDING_SOAP
        return self.service(entity_id, "%s_descriptor" % typ,
                            "assertion_id_request_service", binding)

    def single_logout_service(self, entity_id, binding=None, typ=None):
        # IDP + SP
        if typ is None:
            raise AttributeError("Missing type specification")
        if binding is None:
            binding = BINDING_HTTP_REDIRECT
        return self.service(entity_id, "%s_descriptor" % typ,
                            "single_logout_service", binding)

    def manage_name_id_service(self, entity_id, binding=None, typ=None):
        # IDP + SP
        if binding is None:
            binding = BINDING_HTTP_REDIRECT
        return self.service(entity_id, "%s_descriptor" % typ,
                            "manage_name_id_service", binding)

    def artifact_resolution_service(self, entity_id, binding=None, typ=None):
        # IDP + SP
        if binding is None:
            binding = BINDING_HTTP_REDIRECT
        return self.service(entity_id, "%s_descriptor" % typ,
                            "artifact_resolution_service", binding)

    def assertion_consumer_service(self, entity_id, binding=None, _="spsso"):
        # SP
        if binding is None:
            binding = BINDING_HTTP_POST
        return self.service(entity_id, "spsso_descriptor",
                            "assertion_consumer_service", binding)

    def attribute_consuming_service(self, entity_id, binding=None, _="spsso"):
        # SP
        if binding is None:
            binding = BINDING_HTTP_REDIRECT
        return self.service(entity_id, "spsso_descriptor",
                            "attribute_consuming_service", binding)

    def discovery_response(self, entity_id, binding=None, _="spsso"):
        if binding is None:
            binding = BINDING_DISCO
        return self.ext_service(entity_id, "spsso_descriptor",
                                "%s&%s" % (DiscoveryResponse.c_namespace,
                                           DiscoveryResponse.c_tag),
                                binding)

    def attribute_requirement(self, entity_id, index=None):
        for _md in self.metadata.values():
            if entity_id in _md:
                return _md.attribute_requirement(entity_id, index)

    def keys(self):
        res = []
        for _md in self.metadata.values():
            res.extend(_md.keys())
        return res

    def __getitem__(self, item):
        for _md in self.metadata.values():
            try:
                return _md[item]
            except KeyError:
                pass

        raise KeyError(item)

    def __setitem__(self, key, value):
        self.metadata[key] = value

    def entities(self):
        num = 0
        for _md in self.metadata.values():
            num += len(_md.items())

        return num

    def __len__(self):
        return len(self.metadata)

    def with_descriptor(self, descriptor):
        res = {}
        for _md in self.metadata.values():
            res.update(_md.with_descriptor(descriptor))
        return res

    def name(self, entity_id, langpref="en"):
        for _md in self.metadata.values():
            if entity_id in _md:
                return name(_md[entity_id], langpref)
        return None

    def vo_members(self, entity_id):
        ad = self.__getitem__(entity_id)["affiliation_descriptor"]
        return [m["text"] for m in ad["affiliate_member"]]

    def entity_categories(self, entity_id):
        """
        Get a list of entity categories for an entity id.

        :param entity_id: Entity id
        :return: Entity categories

        :type entity_id: string
        :rtype: [string]
        """
        attributes = self.entity_attributes(entity_id)
        return attributes.get(ENTITY_CATEGORY, [])

    def supported_entity_categories(self, entity_id):
        """
        Get a list of entity category support for an entity id.

        :param entity_id: Entity id
        :return: Entity category support

        :type entity_id: string
        :rtype: [string]
        """
        attributes = self.entity_attributes(entity_id)
        return attributes.get(ENTITY_CATEGORY_SUPPORT, [])

    def assurance_certifications(self, entity_id):
        assurance_certifications = (
            certification
            for name, values in self.entity_attributes(entity_id).items()
            if name == ASSURANCE_CERTIFICATION
            for certification in values
        )
        return assurance_certifications

    def entity_attributes(self, entity_id):
        """
        Get all entity attributes for an entry in the metadata.

        Example return data:

        {'http://macedir.org/entity-category': ['something', 'something2'],
         'http://example.org/saml-foo': ['bar']}

        :param entity_id: Entity id
        :return: dict with keys and value-lists from metadata

        :type entity_id: string
        :rtype: dict
        """
        res = {}
        try:
            ext = self.__getitem__(entity_id)["extensions"]
        except KeyError:
            return res
        for elem in ext["extension_elements"]:
            if elem["__class__"] == classnames["mdattr_entityattributes"]:
                for attr in elem["attribute"]:
                    if attr["name"] not in res:
                        res[attr["name"]] = []
                    res[attr["name"]] += [v["text"] for v in attr[
                        "attribute_value"]]
        return res

    def supported_algorithms(self, entity_id):
        """
        Get all supported algorithms for an entry in the metadata.

        Example return data:

        {'digest_methods': ['http://www.w3.org/2001/04/xmldsig-more#sha224', 'http://www.w3.org/2001/04/xmlenc#sha256'],
         'signing_methods': ['http://www.w3.org/2001/04/xmldsig-more#rsa-sha256']}

        :param entity_id: Entity id
        :return: dict with keys and value-lists from metadata

        :type entity_id: string
        :rtype: dict
        """
        res = {
            'digest_methods': [],
            'signing_methods': []
        }
        try:
            ext = self.__getitem__(entity_id)["extensions"]
        except KeyError:
            return res
        for elem in ext["extension_elements"]:
            if elem["__class__"] == classnames["algsupport_digest_method"]:
                res['digest_methods'].append(elem['algorithm'])
            elif elem["__class__"] == classnames["algsupport_signing_method"]:
                res['signing_methods'].append(elem['algorithm'])
        return res

    def _lookup_elements_by_cls(self, root, cls):
        elements = (
            element
            for uiinfo in root
            for element_key, elements in uiinfo.items()
            if element_key != "__class__"
            for element in elements
            if element.get("__class__") == cls
        )
        return elements

    def _lookup_elements_by_key(self, root, key):
        elements = (
            element
            for uiinfo in root
            for elements in [uiinfo.get(key, [])]
            for element in elements
        )
        return elements

    def mdui_uiinfo(self, entity_id):
        try:
            data = self[entity_id]
        except KeyError:
            data = {}

        descriptor_names = (
            item
            for item in data.keys()
            if item.endswith("_descriptor")
        )
        descriptors = (
            descriptor
            for descriptor_name in descriptor_names
            for descriptor in self[entity_id].get(descriptor_name, [])
        )
        extensions = (
            extension
            for descriptor in descriptors
            for extension in descriptor.get("extensions", {}).get("extension_elements", [])
        )
        uiinfos = (
            extension
            for extension in extensions
            if extension.get("__class__") == classnames["mdui_uiinfo"]
        )
        return uiinfos

    def _mdui_uiinfo_i18n_elements_lookup(self, entity_id, langpref, element_hint, lookup):
        uiinfos = self.mdui_uiinfo(entity_id)
        elements = lookup(uiinfos, element_hint)
        lang_elements = (
            element
            for element in elements
            if langpref is None or element.get("lang") == langpref
        )
        values = (
            value
            for element in lang_elements
            for value in [element.get("text")]
        )
        return values

    def mdui_uiinfo_i18n_element_cls(self, entity_id, langpref, element_cls):
        values = self._mdui_uiinfo_i18n_elements_lookup(
            entity_id, langpref, element_cls, self._lookup_elements_by_cls
        )
        return values

    def mdui_uiinfo_i18n_element_key(self, entity_id, langpref, element_key):
        values = self._mdui_uiinfo_i18n_elements_lookup(
            entity_id, langpref, element_key, self._lookup_elements_by_key
        )
        return values

    def mdui_uiinfo_display_name(self, entity_id, langpref=None):
        cls = classnames["mdui_uiinfo_display_name"]
        values = self.mdui_uiinfo_i18n_element_cls(entity_id, langpref, cls)
        return values

    def mdui_uiinfo_description(self, entity_id, langpref=None):
        cls = classnames["mdui_uiinfo_description"]
        values = self.mdui_uiinfo_i18n_element_cls(entity_id, langpref, cls)
        return values

    def mdui_uiinfo_information_url(self, entity_id, langpref=None):
        cls = classnames["mdui_uiinfo_information_url"]
        values = self.mdui_uiinfo_i18n_element_cls(entity_id, langpref, cls)
        return values

    def mdui_uiinfo_privacy_statement_url(self, entity_id, langpref=None):
        cls = classnames["mdui_uiinfo_privacy_statement_url"]
        values = self.mdui_uiinfo_i18n_element_cls(entity_id, langpref, cls)
        return values

    def mdui_uiinfo_logo(self, entity_id, width=None, height=None):
        uiinfos = self.mdui_uiinfo(entity_id)
        cls = classnames["mdui_uiinfo_logo"]
        elements = self._lookup_elements_by_cls(uiinfos, cls)
        values = (
            element
            for element in elements
            if width is None or element.get("width") == width
            if height is None or element.get("height") == height
        )
        return values

    def contact_person_data(self, entity_id, contact_type=None):
        try:
            data = self[entity_id]
        except KeyError:
            data = {}

        contacts = (
            {
                "contact_type": _contact_type,
                "given_name": contact.get("given_name", {}).get("text", ""),
                "email_address": [
                    address
                    for email in contact.get("email_address", {})
                    for address in [email.get("text")]
                    if address
                ],
            }
            for contact in data.get("contact_person", [])
            for _contact_type in [contact.get("contact_type", "")]
            if contact_type is None or contact_type == _contact_type
        )

        return contacts

    def bindings(self, entity_id, typ, service):
        for _md in self.metadata.values():
            if entity_id in _md.items():
                return _md.bindings(entity_id, typ, service)

        return None

    def __str__(self):
        _str = ["{"]
        for key, val in self.metadata.items():
            _str.append("%s: %s" % (key, val))
        _str.append("}")
        return "\n".join(_str)

    def construct_source_id(self):
        res = {}
        for _md in self.metadata.values():
            res.update(_md.construct_source_id())
        return res

    def items(self):
        res = {}
        for _md in self.metadata.values():
            res.update(_md.items())
        return res.items()

    def _providers(self, descriptor):
        res = []
        for _md in self.metadata.values():
            for ent_id, ent_desc in _md.items():
                if descriptor in ent_desc:
                    if ent_id in res:
                        # print("duplicated entity_id: %s" % res)
                        pass
                    else:
                        res.append(ent_id)
        return res

    def service_providers(self):
        return self._providers("spsso_descriptor")

    def identity_providers(self):
        return self._providers("idpsso_descriptor")

    def attribute_authorities(self):
        return self._providers("attribute_authority")

    def dumps(self, format="local"):
        """
        Dumps the content in standard metadata format or the pysaml2 metadata
        format

        :param format: Which format to dump in
        :return: a string
        """
        if format == "local":
            res = EntitiesDescriptor()
            for _md in self.metadata.values():
                try:
                    res.entity_descriptor.extend(
                        _md.entities_descr.entity_descriptor)
                except AttributeError:
                    res.entity_descriptor.append(_md.entity_descr)

            return "%s" % res
        elif format == "md":
            return json.dumps(self.items(), indent=2)
