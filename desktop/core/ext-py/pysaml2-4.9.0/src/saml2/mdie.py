#!/usr/bin/env python
import six

from saml2 import element_to_extension_element
from saml2 import extension_elements_to_elements
from saml2 import SamlBase
from saml2 import md

__author__ = 'rolandh'

"""
Functions used to import metadata from and export it to a pysaml2 format
"""

IMP_SKIP = ["_certs", "e_e_", "_extatt"]
EXP_SKIP = ["__class__"]


# From pysaml2 SAML2 metadata format to Python dictionary
def _eval(val, onts, mdb_safe):
    """
    Convert a value to a basic dict format
    :param val: The value
    :param onts: Schemas to be used in the conversion
    :return: The basic dictionary
    """
    if isinstance(val, six.string_types):
        val = val.strip()
        if not val:
            return None
        else:
            return val
    elif isinstance(val, dict) or isinstance(val, SamlBase):
        return to_dict(val, onts, mdb_safe)
    elif isinstance(val, list):
        lv = []
        for v in val:
            if isinstance(v, dict) or isinstance(v, SamlBase):
                lv.append(to_dict(v, onts, mdb_safe))
            else:
                lv.append(v)
        return lv
    return val


def to_dict(_dict, onts, mdb_safe=False):
    """
    Convert a pysaml2 SAML2 message class instance into a basic dictionary
    format.
    The export interface.

    :param _dict: The pysaml2 metadata instance
    :param onts: List of schemas to use for the conversion
    :return: The converted information
    """
    res = {}
    if isinstance(_dict, SamlBase):
        res["__class__"] = "%s&%s" % (_dict.c_namespace, _dict.c_tag)
        for key in _dict.keyswv():
            if key in IMP_SKIP:
                continue
            val = getattr(_dict, key)
            if key == "extension_elements":
                _eel = extension_elements_to_elements(val, onts)
                _val = [_eval(_v, onts, mdb_safe) for _v in _eel]
            elif key == "extension_attributes":
                if mdb_safe:
                    _val = dict([(k.replace(".", "__"), v) for k, v in
                                 val.items()])
                    #_val = {k.replace(".", "__"): v for k, v in val.items()}
                else:
                    _val = val
            else:
                _val = _eval(val, onts, mdb_safe)

            if _val:
                if mdb_safe:
                    key = key.replace(".", "__")
                res[key] = _val
    else:
        for key, val in _dict.items():
            _val = _eval(val, onts, mdb_safe)
            if _val:
                if mdb_safe and "." in key:
                    key = key.replace(".", "__")
                res[key] = _val
    return res


# From Python dictionary to pysaml2 SAML2 metadata format

def _kwa(val, onts, mdb_safe=False):
    """
    Key word argument conversion

    :param val: A dictionary
    :param onts: dictionary with schemas to use in the conversion
        schema namespase is the key in the dictionary
    :return: A converted dictionary
    """
    if not mdb_safe:
        return dict([(k, from_dict(v, onts)) for k, v in val.items()
                     if k not in EXP_SKIP])
    else:
        _skip = ["_id"]
        _skip.extend(EXP_SKIP)
        return dict([(k.replace("__", "."), from_dict(v, onts)) for k, v in
                     val.items() if k not in _skip])


def from_dict(val, onts, mdb_safe=False):
    """
    Converts a dictionary into a pysaml2 object
    :param val: A dictionary
    :param onts: Dictionary of schemas to use in the conversion
    :return: The pysaml2 object instance
    """
    if isinstance(val, dict):
        if "__class__" in val:
            ns, typ = val["__class__"].split("&")
            cls = getattr(onts[ns], typ)
            if cls is md.Extensions:
                lv = []
                for key, ditems in val.items():
                    if key in EXP_SKIP:
                        continue
                    for item in ditems:
                        ns, typ = item["__class__"].split("&")
                        cls = getattr(onts[ns], typ)
                        kwargs = _kwa(item, onts, mdb_safe)
                        inst = cls(**kwargs)
                        lv.append(element_to_extension_element(inst))
                return lv
            else:
                kwargs = _kwa(val, onts, mdb_safe)
                inst = cls(**kwargs)
            return inst
        else:
            res = {}
            for key, v in val.items():
                if mdb_safe:
                    key = key.replace("__", ".")
                res[key] = from_dict(v, onts)
            return res
    elif isinstance(val, six.string_types):
        return val
    elif isinstance(val, list):
        return [from_dict(v, onts) for v in val]
    else:
        return val
