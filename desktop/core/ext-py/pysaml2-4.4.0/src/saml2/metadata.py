#!/usr/bin/env python
from saml2.algsupport import algorithm_support_in_metadata
from saml2.md import AttributeProfile
from saml2.sigver import security_context
from saml2.config import Config
from saml2.validate import valid_instance
from saml2.time_util import in_a_while
from saml2.extension import mdui
from saml2.extension import idpdisc
from saml2.extension import shibmd
from saml2.extension import mdattr
from saml2.saml import NAME_FORMAT_URI
from saml2.saml import AttributeValue
from saml2.saml import Attribute
from saml2.attribute_converter import from_local_name
from saml2 import md, SAMLError
from saml2 import BINDING_HTTP_POST
from saml2 import BINDING_HTTP_REDIRECT
from saml2 import BINDING_SOAP
from saml2 import samlp
from saml2 import class_name

from saml2 import xmldsig as ds
import six

from saml2.sigver import pre_signature_part

from saml2.s_utils import factory
from saml2.s_utils import rec_factory
from saml2.s_utils import sid

__author__ = 'rolandh'

NSPAIR = {
    "saml2p": "urn:oasis:names:tc:SAML:2.0:protocol",
    "saml2": "urn:oasis:names:tc:SAML:2.0:assertion",
    "soap11": "http://schemas.xmlsoap.org/soap/envelope/",
    "meta": "urn:oasis:names:tc:SAML:2.0:metadata",
    "xsi": "http://www.w3.org/2001/XMLSchema-instance",
    "ds": "http://www.w3.org/2000/09/xmldsig#",
    "shibmd": "urn:mace:shibboleth:metadata:1.0",
    "md": "urn:oasis:names:tc:SAML:2.0:metadata",
}

DEFAULTS = {
    "want_assertions_signed": "true",
    "authn_requests_signed": "false",
    "want_authn_requests_signed": "true",
    "want_authn_requests_only_with_valid_cert": "false",
}

ORG_ATTR_TRANSL = {
    "organization_name": ("name", md.OrganizationName),
    "organization_display_name": ("display_name", md.OrganizationDisplayName),
    "organization_url": ("url", md.OrganizationURL)
}

MDNS = '"urn:oasis:names:tc:SAML:2.0:metadata"'
bMDNS = b'"urn:oasis:names:tc:SAML:2.0:metadata"'
XMLNSXS = " xmlns:xs=\"http://www.w3.org/2001/XMLSchema\""
bXMLNSXS = b" xmlns:xs=\"http://www.w3.org/2001/XMLSchema\""


def metadata_tostring_fix(desc, nspair, xmlstring=""):
    if not xmlstring:
        xmlstring = desc.to_string(nspair)

    if six.PY2:
        if "\"xs:string\"" in xmlstring and XMLNSXS not in xmlstring:
            xmlstring = xmlstring.replace(MDNS, MDNS + XMLNSXS)
    else:
        if b"\"xs:string\"" in xmlstring and bXMLNSXS not in xmlstring:
            xmlstring = xmlstring.replace(bMDNS, bMDNS + bXMLNSXS)

    return xmlstring


def create_metadata_string(configfile, config=None, valid=None, cert=None,
                           keyfile=None, mid=None, name=None, sign=None):
    valid_for = 0
    nspair = {"xs": "http://www.w3.org/2001/XMLSchema"}
    # paths = [".", "/opt/local/bin"]

    if valid:
        valid_for = int(valid)  # Hours

    eds = []
    if config is None:
        if configfile.endswith(".py"):
            configfile = configfile[:-3]
        config = Config().load_file(configfile, metadata_construction=True)
    eds.append(entity_descriptor(config))

    conf = Config()
    conf.key_file = config.key_file or keyfile
    conf.cert_file = config.cert_file or cert
    conf.debug = 1
    conf.xmlsec_binary = config.xmlsec_binary
    secc = security_context(conf)

    if mid:
        eid, xmldoc = entities_descriptor(eds, valid_for, name, mid,
                                          sign, secc)
    else:
        eid = eds[0]
        if sign:
            eid, xmldoc = sign_entity_descriptor(eid, mid, secc)
        else:
            xmldoc = None

    valid_instance(eid)
    return metadata_tostring_fix(eid, nspair, xmldoc)


def _localized_name(val, klass):
    """If no language is defined 'en' is the default"""
    try:
        (text, lang) = val
        return klass(text=text, lang=lang)
    except ValueError:
        return klass(text=val, lang="en")


def do_organization_info(ava):
    """
    Description of an organization in the configuration is
    a dictionary of keys and values, where the values might be tuples::

        "organization": {
            "name": ("AB Exempel", "se"),
            "display_name": ("AB Exempel", "se"),
            "url": "http://www.example.org"
        }

    """

    if ava is None:
        return None

    org = md.Organization()
    for dkey, (ckey, klass) in ORG_ATTR_TRANSL.items():
        if ckey not in ava:
            continue
        if isinstance(ava[ckey], six.string_types):
            setattr(org, dkey, [_localized_name(ava[ckey], klass)])
        elif isinstance(ava[ckey], list):
            setattr(org, dkey,
                    [_localized_name(n, klass) for n in ava[ckey]])
        else:
            setattr(org, dkey, [_localized_name(ava[ckey], klass)])
    return org


def do_contact_person_info(lava):
    """ Creates a ContactPerson instance from configuration information"""

    cps = []
    if lava is None:
        return cps

    contact_person = md.ContactPerson
    for ava in lava:
        cper = md.ContactPerson()
        for (key, classpec) in contact_person.c_children.values():
            try:
                value = ava[key]
                data = []
                if isinstance(classpec, list):
                    # What if value is not a list ?
                    if isinstance(value, six.string_types):
                        data = [classpec[0](text=value)]
                    else:
                        for val in value:
                            data.append(classpec[0](text=val))
                else:
                    data = classpec(text=value)
                setattr(cper, key, data)
            except KeyError:
                pass
        for (prop, classpec, _) in contact_person.c_attributes.values():
            try:
                # should do a check for valid value
                setattr(cper, prop, ava[prop])
            except KeyError:
                pass

        # ContactType must have a value
        typ = getattr(cper, "contact_type")
        if not typ:
            setattr(cper, "contact_type", "technical")

        cps.append(cper)

    return cps


def do_key_descriptor(cert=None, enc_cert=None, use="both"):
    kd_list = []
    if use in ["signing", "both"] and cert is not None:
        if not isinstance(cert, list):
            cert = [cert]
        for _cert in cert:
            kd_list.append(
                md.KeyDescriptor(
                    key_info=ds.KeyInfo(
                        x509_data=ds.X509Data(
                            x509_certificate=ds.X509Certificate(text=_cert)
                        )
                    ),
                    use="signing"
                )
            )
    if use in ["both", "encryption"] and enc_cert is not None:
        if not isinstance(enc_cert, list):
            enc_cert = [enc_cert]
        for _enc_cert in enc_cert:
            kd_list.append(
                md.KeyDescriptor(
                    key_info=ds.KeyInfo(
                        x509_data=ds.X509Data(
                            x509_certificate=ds.X509Certificate(text=_enc_cert)
                        )
                    ),
                    use="encryption"
                )
            )
    if len(kd_list) == 0 and cert is not None:
        return md.KeyDescriptor(
            key_info=ds.KeyInfo(
                x509_data=ds.X509Data(
                    x509_certificate=ds.X509Certificate(text=cert)
                )
            )
        )
    return kd_list


def do_requested_attribute(attributes, acs, is_required="false",
                           name_format=NAME_FORMAT_URI):
    lista = []
    for attr in attributes:
        attr = from_local_name(acs, attr, name_format)
        args = {}
        if isinstance(attr, six.string_types):
            args["name"] = attr
        else:
            for key in attr.keyswv():
                args[key] = getattr(attr, key)
        args["is_required"] = is_required
        args["name_format"] = name_format
        lista.append(md.RequestedAttribute(**args))
    return lista


def do_uiinfo(_uiinfo):
    uii = mdui.UIInfo()
    for attr in ['display_name', 'description', "information_url",
                 'privacy_statement_url']:
        try:
            val = _uiinfo[attr]
        except KeyError:
            continue

        aclass = uii.child_class(attr)
        inst = getattr(uii, attr)
        if isinstance(val, six.string_types):
            ainst = aclass(text=val)
            inst.append(ainst)
        elif isinstance(val, dict):
            ainst = aclass()
            ainst.text = val["text"]
            ainst.lang = val["lang"]
            inst.append(ainst)
        else:
            for value in val:
                if isinstance(value, six.string_types):
                    ainst = aclass(text=value)
                    inst.append(ainst)
                elif isinstance(value, dict):
                    ainst = aclass()
                    ainst.text = value["text"]
                    ainst.lang = value["lang"]
                    inst.append(ainst)

    try:
        _attr = "logo"
        val = _uiinfo[_attr]
        inst = getattr(uii, _attr)
        # dictionary or list of dictionaries
        if isinstance(val, dict):
            logo = mdui.Logo()
            for attr, value in val.items():
                if attr in logo.keys():
                    setattr(logo, attr, value)
            inst.append(logo)
        elif isinstance(val, list):
            for logga in val:
                if not isinstance(logga, dict):
                    raise SAMLError("Configuration error !!")
                logo = mdui.Logo()
                for attr, value in logga.items():
                    if attr in logo.keys():
                        setattr(logo, attr, value)
                inst.append(logo)
    except KeyError:
        pass

    try:
        _attr = "keywords"
        val = _uiinfo[_attr]
        inst = getattr(uii, _attr)
        # list of six.string_types, dictionary or list of dictionaries
        if isinstance(val, list):
            for value in val:
                keyw = mdui.Keywords()
                if isinstance(value, six.string_types):
                    keyw.text = value
                elif isinstance(value, dict):
                    keyw.text = " ".join(value["text"])
                    try:
                        keyw.lang = value["lang"]
                    except KeyError:
                        pass
                else:
                    raise SAMLError("Configuration error: ui_info keywords")
                inst.append(keyw)
        elif isinstance(val, dict):
            keyw = mdui.Keywords()
            keyw.text = " ".join(val["text"])
            try:
                keyw.lang = val["lang"]
            except KeyError:
                pass
            inst.append(keyw)
        else:
            raise SAMLError("Configuration Error: ui_info keywords")
    except KeyError:
        pass

    return uii


def do_idpdisc(discovery_response):
    return idpdisc.DiscoveryResponse(index="0", location=discovery_response,
                                     binding=idpdisc.NAMESPACE)


ENDPOINTS = {
    "sp": {
        "artifact_resolution_service": (md.ArtifactResolutionService, True),
        "single_logout_service": (md.SingleLogoutService, False),
        "manage_name_id_service": (md.ManageNameIDService, False),
        "assertion_consumer_service": (md.AssertionConsumerService, True),
    },
    "idp": {
        "artifact_resolution_service": (md.ArtifactResolutionService, True),
        "single_logout_service": (md.SingleLogoutService, False),
        "manage_name_id_service": (md.ManageNameIDService, False),
        "single_sign_on_service": (md.SingleSignOnService, False),
        "name_id_mapping_service": (md.NameIDMappingService, False),
        "assertion_id_request_service": (md.AssertionIDRequestService, False),
    },
    "aa": {
        "artifact_resolution_service": (md.ArtifactResolutionService, True),
        "single_logout_service": (md.SingleLogoutService, False),
        "manage_name_id_service": (md.ManageNameIDService, False),
        "assertion_id_request_service": (md.AssertionIDRequestService, False),
        "attribute_service": (md.AttributeService, False)
    },
    "pdp": {
        "authz_service": (md.AuthzService, True)
    },
    "aq": {
        "authn_query_service": (md.AuthnQueryService, True)
    }
}

ENDPOINT_EXT = {
    "sp": {
        "discovery_response": (idpdisc.DiscoveryResponse, True)
    }
}

DEFAULT_BINDING = {
    "assertion_consumer_service": BINDING_HTTP_POST,
    "single_sign_on_service": BINDING_HTTP_REDIRECT,
    "single_logout_service": BINDING_HTTP_POST,
    "attribute_service": BINDING_SOAP,
    "artifact_resolution_service": BINDING_SOAP,
    "authn_query_service": BINDING_SOAP
}


def do_extensions(mname, item):
    try:
        _mod = __import__("saml2.extension.%s" % mname, globals(), locals(),
                          mname)
    except ImportError:
        return None
    else:
        res = []

        for _cname, ava in item.items():
            cls = getattr(_mod, _cname)
            res.append(rec_factory(cls, **ava))
    return res


def _do_nameid_format(cls, conf, typ):
    namef = conf.getattr("name_id_format", typ)
    if namef:
        if isinstance(namef, six.string_types):
            ids = [md.NameIDFormat(namef)]
        else:
            ids = [md.NameIDFormat(text=form) for form in namef]
        setattr(cls, "name_id_format", ids)


def do_endpoints(conf, endpoints):
    service = {}

    for endpoint, (eclass, indexed) in endpoints.items():
        try:
            servs = []
            i = 1
            for args in conf[endpoint]:
                if isinstance(args,
                              six.string_types):  # Assume it's the location
                    args = {"location": args,
                            "binding": DEFAULT_BINDING[endpoint]}
                elif isinstance(args, tuple) or isinstance(args, list):
                    if len(args) == 2:  # (location, binding)
                        args = {"location": args[0], "binding": args[1]}
                    elif len(args) == 3:  # (location, binding, index)
                        args = {"location": args[0], "binding": args[1],
                                "index": args[2]}

                if indexed:
                    if "index" not in args:
                        args["index"] = "%d" % i
                        i += 1
                    else:
                        try:
                            int(args["index"])
                        except ValueError:
                            raise
                        else:
                            args["index"] = str(args["index"])

                servs.append(factory(eclass, **args))
                service[endpoint] = servs
        except KeyError:
            pass
    return service


DEFAULT = {
    "want_assertions_signed": "true",
    "authn_requests_signed": "false",
    "want_authn_requests_signed": "false",
    # "want_authn_requests_only_with_valid_cert": "false",
}


def do_attribute_consuming_service(conf, spsso):
    service_description = service_name = None
    requested_attributes = []
    acs = conf.attribute_converters
    req = conf.getattr("required_attributes", "sp")

    req_attr_name_format = conf.getattr("requested_attribute_name_format", "sp")
    if req_attr_name_format is None:
        req_attr_name_format = conf.requested_attribute_name_format

    if req:
        requested_attributes.extend(
            do_requested_attribute(req, acs, is_required="true",
                                   name_format=req_attr_name_format))

    opt = conf.getattr("optional_attributes", "sp")

    if opt:
        requested_attributes.extend(
            do_requested_attribute(opt, acs, name_format=req_attr_name_format))

    try:
        if conf.description:
            try:
                (text, lang) = conf.description
            except ValueError:
                text = conf.description
                lang = "en"
            service_description = [md.ServiceDescription(text=text, lang=lang)]
    except KeyError:
        pass

    try:
        if conf.name:
            try:
                (text, lang) = conf.name
            except ValueError:
                text = conf.name
                lang = "en"
            service_name = [md.ServiceName(text=text, lang=lang)]
    except KeyError:
        pass

    # Must be both requested attributes and service name
    if requested_attributes:
        if not service_name:
            service_name = [md.ServiceName(text="", lang="en")]

        ac_serv = md.AttributeConsumingService(
            index="1", service_name=service_name,
            requested_attribute=requested_attributes)

        if service_description:
            ac_serv.service_description = service_description

        spsso.attribute_consuming_service = [ac_serv]


def do_spsso_descriptor(conf, cert=None, enc_cert=None):
    spsso = md.SPSSODescriptor()
    spsso.protocol_support_enumeration = samlp.NAMESPACE

    exts = conf.getattr("extensions", "sp")
    if exts:
        if spsso.extensions is None:
            spsso.extensions = md.Extensions()

        for key, val in exts.items():
            _ext = do_extensions(key, val)
            if _ext:
                for _e in _ext:
                    spsso.extensions.add_extension_element(_e)

    endps = conf.getattr("endpoints", "sp")
    if endps:
        for (endpoint, instlist) in do_endpoints(endps,
                                                 ENDPOINTS["sp"]).items():
            setattr(spsso, endpoint, instlist)

    ext = do_endpoints(endps, ENDPOINT_EXT["sp"])
    if ext:
        if spsso.extensions is None:
            spsso.extensions = md.Extensions()
        for vals in ext.values():
            for val in vals:
                spsso.extensions.add_extension_element(val)

    ui_info = conf.getattr("ui_info", "sp")
    if ui_info:
        if spsso.extensions is None:
            spsso.extensions = md.Extensions()
        spsso.extensions.add_extension_element(do_uiinfo(ui_info))

    if cert or enc_cert:
        metadata_key_usage = conf.metadata_key_usage
        spsso.key_descriptor = do_key_descriptor(cert=cert, enc_cert=enc_cert,
                                                 use=metadata_key_usage)

    for key in ["want_assertions_signed", "authn_requests_signed"]:
        try:
            val = conf.getattr(key, "sp")
            if val is None:
                setattr(spsso, key, DEFAULT[key])  # default ?!
            else:
                strval = "{0:>s}".format(str(val))
                setattr(spsso, key, strval.lower())
        except KeyError:
            setattr(spsso, key, DEFAULTS[key])

    do_attribute_consuming_service(conf, spsso)
    _do_nameid_format(spsso, conf, "sp")
    return spsso


def do_idpsso_descriptor(conf, cert=None, enc_cert=None):
    idpsso = md.IDPSSODescriptor()
    idpsso.protocol_support_enumeration = samlp.NAMESPACE

    endps = conf.getattr("endpoints", "idp")
    if endps:
        for (endpoint, instlist) in do_endpoints(endps,
                                                 ENDPOINTS["idp"]).items():
            setattr(idpsso, endpoint, instlist)

    _do_nameid_format(idpsso, conf, "idp")

    scopes = conf.getattr("scope", "idp")
    if scopes:
        if idpsso.extensions is None:
            idpsso.extensions = md.Extensions()
        for scope in scopes:
            mdscope = shibmd.Scope()
            mdscope.text = scope
            # unless scope contains '*'/'+'/'?' assume non regexp ?
            mdscope.regexp = "false"
            idpsso.extensions.add_extension_element(mdscope)

    ui_info = conf.getattr("ui_info", "idp")
    if ui_info:
        if idpsso.extensions is None:
            idpsso.extensions = md.Extensions()
        idpsso.extensions.add_extension_element(do_uiinfo(ui_info))

    if cert or enc_cert:
        idpsso.key_descriptor = do_key_descriptor(cert, enc_cert,
                                                  use=conf.metadata_key_usage)

    for key in ["want_authn_requests_signed"]:
        # "want_authn_requests_only_with_valid_cert"]:
        try:
            val = conf.getattr(key, "idp")
            if val is None:
                setattr(idpsso, key, DEFAULT[key])
            else:
                setattr(idpsso, key, ("%s" % val).lower())
        except KeyError:
            setattr(idpsso, key, DEFAULTS[key])

    return idpsso


def do_aa_descriptor(conf, cert=None, enc_cert=None):
    aad = md.AttributeAuthorityDescriptor()
    aad.protocol_support_enumeration = samlp.NAMESPACE

    endps = conf.getattr("endpoints", "aa")

    if endps:
        for (endpoint, instlist) in do_endpoints(endps,
                                                 ENDPOINTS["aa"]).items():
            setattr(aad, endpoint, instlist)

    _do_nameid_format(aad, conf, "aa")

    if cert or enc_cert:
        aad.key_descriptor = do_key_descriptor(cert, enc_cert,
                                               use=conf.metadata_key_usage)

    attributes = conf.getattr("attribute", "aa")
    if attributes:
        for attribute in attributes:
            aad.attribute.append(Attribute(text=attribute))

    attribute_profiles = conf.getattr("attribute_profile", "aa")
    if attribute_profiles:
        for attribute_profile in attribute_profiles:
            aad.attribute.append(AttributeProfile(text=attribute_profile))

    return aad


def do_aq_descriptor(conf, cert=None, enc_cert=None):
    aqs = md.AuthnAuthorityDescriptor()
    aqs.protocol_support_enumeration = samlp.NAMESPACE

    endps = conf.getattr("endpoints", "aq")

    if endps:
        for (endpoint, instlist) in do_endpoints(endps,
                                                 ENDPOINTS["aq"]).items():
            setattr(aqs, endpoint, instlist)

    _do_nameid_format(aqs, conf, "aq")

    if cert or enc_cert:
        aqs.key_descriptor = do_key_descriptor(cert, enc_cert,
                                               use=conf.metadata_key_usage)

    return aqs


def do_pdp_descriptor(conf, cert=None, enc_cert=None):
    """ Create a Policy Decision Point descriptor """
    pdp = md.PDPDescriptor()

    pdp.protocol_support_enumeration = samlp.NAMESPACE

    endps = conf.getattr("endpoints", "pdp")

    if endps:
        for (endpoint, instlist) in do_endpoints(endps,
                                                 ENDPOINTS["pdp"]).items():
            setattr(pdp, endpoint, instlist)

    _do_nameid_format(pdp, conf, "pdp")

    if cert:
        pdp.key_descriptor = do_key_descriptor(cert, enc_cert,
                                               use=conf.metadata_key_usage)

    return pdp


def entity_descriptor(confd):
    mycert = None
    enc_cert = None
    if confd.cert_file is not None:
        mycert = []
        mycert.append("".join(open(confd.cert_file).readlines()[1:-1]))
        if confd.additional_cert_files is not None:
            for _cert_file in confd.additional_cert_files:
                mycert.append("".join(open(_cert_file).readlines()[1:-1]))
    if confd.encryption_keypairs is not None:
        enc_cert = []
        for _encryption in confd.encryption_keypairs:
            enc_cert.append(
                "".join(open(_encryption["cert_file"]).readlines()[1:-1]))

    entd = md.EntityDescriptor()
    entd.entity_id = confd.entityid

    if confd.valid_for:
        entd.valid_until = in_a_while(hours=int(confd.valid_for))

    if confd.organization is not None:
        entd.organization = do_organization_info(confd.organization)
    if confd.contact_person is not None:
        entd.contact_person = do_contact_person_info(confd.contact_person)

    if confd.entity_category:
        entd.extensions = md.Extensions()
        ava = [AttributeValue(text=c) for c in confd.entity_category]
        attr = Attribute(attribute_value=ava,
                         name="http://macedir.org/entity-category")
        item = mdattr.EntityAttributes(attribute=attr)
        entd.extensions.add_extension_element(item)

    for item in algorithm_support_in_metadata(confd.xmlsec_binary):
        if not entd.extensions:
            entd.extensions = md.Extensions()
        entd.extensions.add_extension_element(item)

    serves = confd.serves
    if not serves:
        raise SAMLError(
            'No service type ("sp","idp","aa") provided in the configuration')

    if "sp" in serves:
        confd.context = "sp"
        entd.spsso_descriptor = do_spsso_descriptor(confd, mycert, enc_cert)
    if "idp" in serves:
        confd.context = "idp"
        entd.idpsso_descriptor = do_idpsso_descriptor(confd, mycert, enc_cert)
    if "aa" in serves:
        confd.context = "aa"
        entd.attribute_authority_descriptor = do_aa_descriptor(confd, mycert,
                                                               enc_cert)
    if "pdp" in serves:
        confd.context = "pdp"
        entd.pdp_descriptor = do_pdp_descriptor(confd, mycert, enc_cert)
    if "aq" in serves:
        confd.context = "aq"
        entd.authn_authority_descriptor = do_aq_descriptor(confd, mycert,
                                                           enc_cert)

    return entd


def entities_descriptor(eds, valid_for, name, ident, sign, secc, sign_alg=None,
                        digest_alg=None):
    entities = md.EntitiesDescriptor(entity_descriptor=eds)
    if valid_for:
        entities.valid_until = in_a_while(hours=valid_for)
    if name:
        entities.name = name
    if ident:
        entities.id = ident

    if sign:
        if not ident:
            ident = sid()

        if not secc.key_file:
            raise SAMLError("If you want to do signing you should define " +
                            "a key to sign with")

        if not secc.my_cert:
            raise SAMLError("If you want to do signing you should define " +
                            "where your public key are")

        entities.signature = pre_signature_part(ident, secc.my_cert, 1,
                                                sign_alg=sign_alg,
                                                digest_alg=digest_alg)
        entities.id = ident
        xmldoc = secc.sign_statement("%s" % entities, class_name(entities))
        entities = md.entities_descriptor_from_string(xmldoc)
    else:
        xmldoc = None

    return entities, xmldoc


def sign_entity_descriptor(edesc, ident, secc, sign_alg=None, digest_alg=None):
    """

    :param edesc: EntityDescriptor instance
    :param ident: EntityDescriptor identifier
    :param secc: Security context
    :return: Tuple with EntityDescriptor instance and Signed XML document
    """

    if not ident:
        ident = sid()

    edesc.signature = pre_signature_part(ident, secc.my_cert, 1, sign_alg=sign_alg, digest_alg=digest_alg)
    edesc.id = ident
    xmldoc = secc.sign_statement("%s" % edesc, class_name(edesc))
    edesc = md.entity_descriptor_from_string(xmldoc)
    return edesc, xmldoc
