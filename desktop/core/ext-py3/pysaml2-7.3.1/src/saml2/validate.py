import base64
import calendar
from ipaddress import AddressValueError
from ipaddress import IPv4Address
from ipaddress import IPv6Address
import re
import struct
import time
from urllib.parse import urlparse

from saml2 import time_util


XSI_NAMESPACE = "http://www.w3.org/2001/XMLSchema-instance"
XSI_NIL = "{%s}nil" % XSI_NAMESPACE
# ---------------------------------------------------------


class NotValid(Exception):
    pass


class OutsideCardinality(Exception):
    pass


class MustValueError(ValueError):
    pass


class ShouldValueError(ValueError):
    pass


class ResponseLifetimeExceed(Exception):
    pass


class ToEarly(Exception):
    pass


# --------------------- validators -------------------------------------
#

NCNAME = re.compile(r"(?P<NCName>[a-zA-Z_](\w|[_.-])*)")


def valid_ncname(name):
    match = NCNAME.match(name)
    # if not match:                      # hack for invalid authnRequest/ID from meteor saml lib
    #    raise NotValid("NCName")
    return True


def valid_id(oid):
    valid_ncname(oid)


def valid_any_uri(item):
    """very simplistic, ..."""
    try:
        part = urlparse(item)
    except Exception:
        raise NotValid("AnyURI")

    if part[0] == "urn" and part[1] == "":  # A urn
        return True
    # elif part[1] == "localhost" or part[1] == "127.0.0.1":
    #     raise NotValid("AnyURI")

    return True


def valid_date_time(item):
    try:
        time_util.str_to_time(item)
    except Exception:
        raise NotValid("dateTime")
    return True


def valid_url(url):
    try:
        _ = urlparse(url)
    except Exception:
        raise NotValid("URL")

    # if part[1] == "localhost" or part[1] == "127.0.0.1":
    #     raise NotValid("URL")
    return True


def validate_on_or_after(not_on_or_after, slack):
    if not_on_or_after:
        now = time_util.utc_now()
        nooa = calendar.timegm(time_util.str_to_time(not_on_or_after))
        if now > nooa + slack:
            now_str = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(now))
            raise ResponseLifetimeExceed(
                "Can't use response, too old (now=%s + slack=%d > "
                "not_on_or_after=%s" % (now_str, slack, not_on_or_after)
            )
        return nooa
    else:
        return False


def validate_before(not_before, slack):
    if not_before:
        now = time_util.utc_now()
        nbefore = calendar.timegm(time_util.str_to_time(not_before))
        if nbefore > now + slack:
            now_str = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(now))
            raise ToEarly(f"Can't use response yet: (now={now_str} + slack={int(slack)}) <= notbefore={not_before}")
    return True


def valid_address(address):
    """Validate IPv4/IPv6 addresses."""
    if not (valid_ipv4(address) or valid_ipv6(address)):
        raise NotValid("address")
    return True


def valid_ipv4(address):
    """Validate IPv4 addresses."""
    try:
        IPv4Address(address)
    except AddressValueError:
        return False
    return True


def valid_ipv6(address):
    """Validate IPv6 addresses."""
    is_enclosed_in_brackets = address.startswith("[") and address.endswith("]")
    address_raw = address[1:-1] if is_enclosed_in_brackets else address
    try:
        IPv6Address(address_raw)
    except AddressValueError:
        return False
    return True


def valid_boolean(val):
    vall = val.lower()
    if vall in ["true", "false", "0", "1"]:
        return True
    else:
        raise NotValid("boolean")


def valid_duration(val):
    try:
        time_util.parse_duration(val)
    except Exception:
        raise NotValid("duration")
    return True


def valid_string(val):
    """Expects unicode
    Char ::= #x9 | #xA | #xD | [#x20-#xD7FF] | [#xE000-#xFFFD] |
                    [#x10000-#x10FFFF]
    """
    for char in val:
        try:
            char = ord(char)
        except TypeError:
            raise NotValid("string")
        if char == 0x09 or char == 0x0A or char == 0x0D:
            continue
        elif 0x20 <= char <= 0xD7FF:
            continue
        elif 0xE000 <= char <= 0xFFFD:
            continue
        elif 0x10000 <= char <= 0x10FFFF:
            continue
        else:
            raise NotValid("string")
    return True


def valid_unsigned_short(val):
    try:
        struct.pack("H", int(val))
    except struct.error:
        raise NotValid("unsigned short")
    except ValueError:
        raise NotValid("unsigned short")

    return True


def valid_positive_integer(val):
    try:
        integer = int(val)
    except ValueError:
        raise NotValid("positive integer")

    if integer > 0:
        return True
    else:
        raise NotValid("positive integer")


def valid_non_negative_integer(val):
    try:
        integer = int(val)
    except ValueError:
        raise NotValid("non negative integer")

    if integer < 0:
        raise NotValid("non negative integer")
    return True


def valid_integer(val):
    try:
        int(val)
    except ValueError:
        raise NotValid("integer")
    return True


def valid_base64(val):
    try:
        base64.b64decode(val)
    except Exception:
        raise NotValid("base64")
    return True


def valid_qname(val):
    """A qname is either
    NCName or
    NCName ':' NCName
    """

    try:
        (prefix, localpart) = val.split(":")
        return valid_ncname(prefix) and valid_ncname(localpart)
    except ValueError:
        return valid_ncname(val)


def valid_anytype(val):
    """Goes through all known type validators

    :param val: The value to validate
    :return: True is value is valid otherwise an exception is raised
    """
    for validator in VALIDATOR.values():
        if validator == valid_anytype:  # To hinder recursion
            continue
        try:
            if validator(val):
                return True
        except NotValid:
            pass

    if isinstance(val, type):
        return True

    raise NotValid("AnyType")


# -----------------------------------------------------------------------------

VALIDATOR = {
    "ID": valid_id,
    "NCName": valid_ncname,
    "dateTime": valid_date_time,
    "anyURI": valid_any_uri,
    "nonNegativeInteger": valid_non_negative_integer,
    "PositiveInteger": valid_positive_integer,
    "boolean": valid_boolean,
    "unsignedShort": valid_unsigned_short,
    "duration": valid_duration,
    "base64Binary": valid_base64,
    "integer": valid_integer,
    "QName": valid_qname,
    "anyType": valid_anytype,
    "string": valid_string,
}

# -----------------------------------------------------------------------------


def validate_value_type(value, spec):
    """
    c_value_type = {'base': 'string', 'enumeration': ['Permit', 'Deny',
                                                      'Indeterminate']}
        {'member': 'anyURI', 'base': 'list'}
        {'base': 'anyURI'}
        {'base': 'NCName'}
        {'base': 'string'}
    """
    if "maxlen" in spec:
        return len(value) <= int(spec["maxlen"])

    if spec["base"] == "string":
        if "enumeration" in spec:
            if value not in spec["enumeration"]:
                raise NotValid("value not in enumeration")
        else:
            return valid_string(value)
    elif spec["base"] == "list":  # comma separated list of values
        for val in [v.strip() for v in value.split(",")]:
            valid(spec["member"], val)
    else:
        return valid(spec["base"], value)

    return True


def valid(typ, value):
    try:
        return VALIDATOR[typ](value)
    except KeyError:
        try:
            (_namespace, typ) = typ.split(":")
        except ValueError:
            if typ == "":
                typ = "string"
        return VALIDATOR[typ](value)


def _valid_instance(instance, val):
    try:
        val.verify()
    except NotValid as exc:
        raise NotValid(f"Class '{instance.__class__.__name__}' instance: {exc.args[0]}")
    except OutsideCardinality as exc:
        raise NotValid(f"Class '{instance.__class__.__name__}' instance cardinality error: {exc.args[0]}")


ERROR_TEXT = "Wrong type of value '%s' on attribute '%s' expected it to be %s"


def valid_instance(instance):
    instclass = instance.__class__
    class_name = instclass.__name__

    # if instance.text:
    #     _has_val = True
    # else:
    #     _has_val = False

    if instclass.c_value_type and instance.text:
        try:
            validate_value_type(instance.text.strip(), instclass.c_value_type)
        except NotValid as exc:
            raise NotValid(f"Class '{class_name}' instance: {exc.args[0]}")

    for (name, typ, required) in instclass.c_attributes.values():
        value = getattr(instance, name, "")
        if required and not value:
            txt = f"Required value on property '{name}' missing"
            raise MustValueError(f"Class '{class_name}' instance: {txt}")

        if value:
            try:
                if isinstance(typ, type):
                    if typ.c_value_type:
                        spec = typ.c_value_type
                    else:
                        spec = {"base": "string"}  # do I need a default

                    validate_value_type(value, spec)
                else:
                    valid(typ, value)
            except (NotValid, ValueError) as exc:
                txt = ERROR_TEXT % (value, name, exc.args[0])
                raise NotValid(f"Class '{class_name}' instance: {txt}")

    for (name, _spec) in instclass.c_children.values():
        value = getattr(instance, name, "")

        try:
            _card = instclass.c_cardinality[name]
            try:
                _cmin = _card["min"]
            except KeyError:
                _cmin = None
            try:
                _cmax = _card["max"]
            except KeyError:
                _cmax = None
        except KeyError:
            _cmin = _cmax = _card = None

        if value:
            # _has_val = True
            if isinstance(value, list):
                _list = True
                vlen = len(value)
            else:
                _list = False
                vlen = 1

            if _card:
                if _cmin is not None and _cmin > vlen:
                    raise NotValid(f"Class '{class_name}' instance cardinality error: less then min ({vlen}<{_cmin})")
                if _cmax is not None and vlen > _cmax:
                    raise NotValid(f"Class '{class_name}' instance cardinality error: more then max ({vlen}>{_cmax})")

            if _list:
                for val in value:
                    # That it is the right class is handled elsewhere
                    _valid_instance(instance, val)
            else:
                _valid_instance(instance, value)
        else:
            if _cmin:
                raise NotValid(f"Class '{class_name}' instance cardinality error: too few values on {name}")

    return True


def valid_domain_name(dns_name):
    m = re.match(r"^[a-z0-9]+([-.]{ 1 }[a-z0-9]+).[a-z]{2,5}(:[0-9]{1,5})?(\/.)?$", dns_name, re.I)
    if not m:
        raise ValueError("Not a proper domain name")
