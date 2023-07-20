#!/usr/bin/env python
#

from importlib import import_module
import logging
import os
import sys

from saml2 import NAMESPACE
from saml2 import ExtensionElement
from saml2 import SAMLError
from saml2 import extension_elements_to_elements
from saml2 import saml
from saml2.s_utils import do_ava
from saml2.s_utils import factory
from saml2.saml import NAME_FORMAT_UNSPECIFIED
from saml2.saml import NAMEID_FORMAT_PERSISTENT


logger = logging.getLogger(__name__)


class UnknownNameFormat(SAMLError):
    pass


class ConverterError(SAMLError):
    pass


def load_maps(dirspec):
    """load the attribute maps

    :param dirspec: a directory specification
    :return: a dictionary with the name of the map as key and the
        map as value. The map itself is a dictionary with two keys:
        "to" and "fro". The values for those keys are the actual mapping.
    """
    mapd = {}
    if dirspec not in sys.path:
        sys.path.insert(0, dirspec)

    for fil in os.listdir(dirspec):
        if fil.endswith(".py"):
            mod = import_module(fil[:-3])
            for item in _find_maps_in_module(mod):
                mapd[item["identifier"]] = item

    return mapd


def ac_factory(path=""):
    """Attribute Converter factory

    :param path: The path to a directory where the attribute maps are expected
        to reside.
    :return: A list of AttributeConverter instances
    """
    acs = []

    if path:
        if path not in sys.path:
            sys.path.insert(0, path)

        for fil in sorted(os.listdir(path)):
            if fil.endswith(".py"):
                mod = import_module(fil[:-3])
                acs.extend(_attribute_map_module_to_acs(mod))
    else:
        from saml2 import attributemaps

        for typ in attributemaps.__all__:
            mod = import_module(f".{typ}", "saml2.attributemaps")
            acs.extend(_attribute_map_module_to_acs(mod))

    return acs


def _attribute_map_module_to_acs(module):
    """Scan an attribute map module and return any attribute maps defined

    :param: module: the python map module
    :type: types.ModuleType
    :return: a generator yielding AttributeConverter defintions
    :rtype: typing.Iterable[AttributeConverter]
    """
    for item in _find_maps_in_module(module):
        atco = AttributeConverter(item["identifier"])
        atco.from_dict(item)
        yield atco


def _find_maps_in_module(module):
    """Find attribute map dictionaries in a map file

    :param: module: the python map module
    :type: types.ModuleType
    :return: a generator yielding dict objects which have the right shape
    :rtype: typing.Iterable[dict]
    """
    for key, item in module.__dict__.items():
        if key.startswith("__"):
            continue
        if isinstance(item, dict) and "identifier" in item and ("to" in item or "fro" in item):
            yield item


def to_local(acs, statement, allow_unknown_attributes=False):
    """Replaces the attribute names in a attribute value assertion with the
    equivalent name from a local name format.

    :param acs: List of Attribute Converters
    :param statement: The Attribute Statement
    :param allow_unknown_attributes: If unknown attributes are allowed
    :return: A key,values dictionary
    """
    return list_to_local(acs, statement.attribute, allow_unknown_attributes)


def list_to_local(acs, attrlist, allow_unknown_attributes=False):
    """Replaces the attribute names in a attribute value assertion with the
    equivalent name from a local name format.

    :param acs: List of Attribute Converters
    :param attrlist: List of Attributes
    :param allow_unknown_attributes: If unknown attributes are allowed
    :return: A key,values dictionary
    """
    if not acs:
        acs = [AttributeConverter()]
        acsd = {"": acs}
    else:
        acsd = {a.name_format: a for a in acs}

    ava = {}
    for attr in attrlist:
        try:
            _func = acsd[attr.name_format].ava_from
        except KeyError:
            if attr.name_format == NAME_FORMAT_UNSPECIFIED or allow_unknown_attributes:
                _func = acs[0].lcd_ava_from
            else:
                logger.info("Unsupported attribute name format: %s", attr.name_format)
                continue

        try:
            key, val = _func(attr)
        except KeyError:
            if allow_unknown_attributes:
                key, val = acs[0].lcd_ava_from(attr)
            else:
                logger.info("Unknown attribute name: %s", attr)
                continue
        except AttributeError:
            continue

        try:
            ava[key].extend(val)
        except KeyError:
            ava[key] = val

    return ava


def from_local(acs, ava, name_format):
    for aconv in acs:
        # print(ac.format, name_format)
        if aconv.name_format == name_format:
            # print("Found a name_form converter")
            return aconv.to_(ava)

    return None


def from_local_name(acs, attr, name_format):
    """
    :param acs: List of AttributeConverter instances
    :param attr: attribute name as string
    :param name_format: Which name-format it should be translated to
    :return: An Attribute instance
    """
    for aconv in acs:
        # print(ac.format, name_format)
        if aconv.name_format == name_format:
            # print("Found a name_form converter")
            return aconv.to_format(attr)
    return attr


def to_local_name(acs, attr):
    """
    :param acs: List of AttributeConverter instances
    :param attr: an Attribute instance
    :return: The local attribute name
    """
    for aconv in acs:
        lattr = aconv.from_format(attr)
        if lattr:
            return lattr

    return attr.friendly_name


def get_local_name(acs, attr, name_format):
    for aconv in acs:
        # print(ac.format, name_format)
        if aconv.name_format == name_format:
            return aconv._fro.get(attr)


def d_to_local_name(acs, attr):
    """
    :param acs: List of AttributeConverter instances
    :param attr: an Attribute dictionary
    :return: The local attribute name
    """
    for aconv in acs:
        lattr = aconv.d_from_format(attr)
        if lattr:
            return lattr

    # if everything else fails this might be good enough
    try:
        return attr["friendly_name"]
    except KeyError:
        raise ConverterError(f"Could not find local name for {attr}")


class AttributeConverter:
    """Converts from an attribute statement to a key,value dictionary and
    vice-versa"""

    def __init__(self, name_format=""):
        self.name_format = name_format
        self._to = None
        self._fro = None

    def adjust(self):
        """If one of the transformations is not defined it is expected to
        be the mirror image of the other.
        """

        if self._fro is None and self._to is not None:
            self._fro = {value.lower(): key for key, value in self._to.items()}
        if self._to is None and self._fro is not None:
            self._to = {value.lower(): key for key, value in self._fro.items()}

    def from_dict(self, mapdict):
        """Import the attribute map from  a dictionary

        :param mapdict: The dictionary
        """

        self.name_format = mapdict["identifier"]
        try:
            self._fro = {k.lower(): v for k, v in mapdict["fro"].items()}
        except KeyError:
            pass
        try:
            self._to = {k.lower(): v for k, v in mapdict["to"].items()}
        except KeyError:
            pass

        if self._fro is None and self._to is None:
            raise ConverterError("Missing specifications")

        if self._fro is None or self._to is None:
            self.adjust()

    def lcd_ava_from(self, attribute):
        """
        If nothing else works, this should

        :param attribute: an Attribute instance
        :return:
        """
        name = attribute.name.strip()
        values = [(value.text or "").strip() for value in attribute.attribute_value]
        return name, values

    def fail_safe_fro(self, statement):
        """In case there is not formats defined or if the name format is
        undefined

        :param statement: AttributeStatement instance
        :return: A dictionary with names and values
        """
        result = {}
        for attribute in statement.attribute:
            if attribute.name_format and attribute.name_format != NAME_FORMAT_UNSPECIFIED:
                continue
            try:
                name = attribute.friendly_name.strip()
            except AttributeError:
                name = attribute.name.strip()

            result[name] = []
            for value in attribute.attribute_value:
                if not value.text:
                    result[name].append("")
                else:
                    result[name].append(value.text.strip())
        return result

    def ava_from(self, attribute, allow_unknown=False):
        try:
            attr = self._fro[attribute.name.strip().lower()]
        except AttributeError:
            attr = attribute.friendly_name.strip().lower()
        except KeyError:
            if allow_unknown:
                try:
                    attr = attribute.name.strip().lower()
                except AttributeError:
                    attr = attribute.friendly_name.strip().lower()
            else:
                raise

        val = []
        for value in attribute.attribute_value:
            if value.extension_elements:
                ext = extension_elements_to_elements(value.extension_elements, [saml])
                for ex in ext:
                    if attr == "eduPersonTargetedID" and ex.text:
                        val.append(ex.text.strip())
                    else:
                        cval = {}
                        for key, (name, typ, mul) in ex.c_attributes.items():
                            exv = getattr(ex, name)
                            if exv:
                                cval[name] = exv
                        if ex.text:
                            cval["value"] = ex.text.strip()
                        val.append({ex.c_tag: cval})
            elif not value.text:
                val.append("")
            else:
                val.append(value.text.strip())

        return attr, val

    def fro(self, statement):
        """Get the attributes and the attribute values.

        :param statement: The AttributeStatement.
        :return: A dictionary containing attributes and values
        """

        if not self.name_format:
            return self.fail_safe_fro(statement)

        result = {}
        for attribute in statement.attribute:
            if attribute.name_format and self.name_format and attribute.name_format != self.name_format:
                continue

            try:
                (key, val) = self.ava_from(attribute)
            except (KeyError, AttributeError):
                pass
            else:
                result[key] = val

        return result

    def to_format(self, attr):
        """Creates an Attribute instance with name, name_format and
        friendly_name

        :param attr: The local name of the attribute
        :return: An Attribute instance
        """
        try:
            _attr = self._to[attr]
        except KeyError:
            try:
                _attr = self._to[attr.lower()]
            except KeyError:
                _attr = ""

        if _attr:
            return factory(saml.Attribute, name=_attr, name_format=self.name_format, friendly_name=attr)
        else:
            return factory(saml.Attribute, name=attr)

    def from_format(self, attr):
        """Find out the local name of an attribute

        :param attr: An saml.Attribute instance
        :return: The local attribute name or "" if no mapping could be made
        """
        if attr.name_format:
            if self.name_format == attr.name_format:
                try:
                    return self._fro[attr.name.lower()]
                except KeyError:
                    pass
        else:  # don't know the name format so try all I have
            try:
                return self._fro[attr.name.lower()]
            except KeyError:
                pass

        return ""

    def d_from_format(self, attr):
        """Find out the local name of an attribute

        :param attr: An Attribute dictionary
        :return: The local attribute name or "" if no mapping could be made
        """
        if attr["name_format"]:
            if self.name_format == attr["name_format"]:
                try:
                    return self._fro[attr["name"].lower()]
                except KeyError:
                    pass
        else:  # don't know the name format so try all I have
            try:
                return self._fro[attr["name"].lower()]
            except KeyError:
                pass

        return ""

    def to_(self, attrvals):
        """Create a list of Attribute instances.

        :param attrvals: A dictionary of attributes and values
        :return: A list of Attribute instances
        """
        attributes = []
        for key, value in attrvals.items():
            name = self._to.get(key.lower())
            if name:
                if name == "urn:oid:1.3.6.1.4.1.5923.1.1.1.10":
                    # special case for eduPersonTargetedID
                    attr_value = self.to_eptid_value(value)
                else:
                    attr_value = do_ava(value)
                attributes.append(
                    factory(
                        saml.Attribute,
                        name=name,
                        name_format=self.name_format,
                        friendly_name=key,
                        attribute_value=attr_value,
                    )
                )
            else:
                attributes.append(factory(saml.Attribute, name=key, attribute_value=do_ava(value)))

        return attributes

    def to_eptid_value(self, values):
        """
        Create AttributeValue instances of NameID from the given values.

        Special handling for the "eptid" attribute
        Name=urn:oid:1.3.6.1.4.1.5923.1.1.1.10
        FriendlyName=eduPersonTargetedID

        values is a list of items of type str or dict. When an item is a
        dictionary it has the keys: "NameQualifier", "SPNameQualifier", and
        "text".

        Returns a list of AttributeValue instances of NameID elements.
        """

        if type(values) is not list:
            values = [values]

        def _create_nameid_ext_el(value):
            text = value["text"] if isinstance(value, dict) else value
            attributes = (
                {
                    "Format": NAMEID_FORMAT_PERSISTENT,
                    "NameQualifier": value["NameQualifier"],
                    "SPNameQualifier": value["SPNameQualifier"],
                }
                if isinstance(value, dict)
                else {"Format": NAMEID_FORMAT_PERSISTENT}
            )
            element = ExtensionElement("NameID", NAMESPACE, attributes=attributes, text=text)
            return element

        attribute_values = [saml.AttributeValue(extension_elements=[_create_nameid_ext_el(v)]) for v in values]
        return attribute_values


class AttributeConverterNOOP(AttributeConverter):
    """Does a NOOP conversion, that is no conversion is made"""

    def __init__(self, name_format=""):
        AttributeConverter.__init__(self, name_format)

    def to_(self, attrvals):
        """Create a list of Attribute instances.

        :param attrvals: A dictionary of attributes and values
        :return: A list of Attribute instances
        """
        attributes = []
        for key, value in attrvals.items():
            key = key.lower()
            attributes.append(
                factory(saml.Attribute, name=key, name_format=self.name_format, attribute_value=do_ava(value))
            )

        return attributes
