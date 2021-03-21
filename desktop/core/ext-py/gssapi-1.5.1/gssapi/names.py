import six

from gssapi.raw import names as rname
from gssapi.raw import NameType
from gssapi.raw import named_tuples as tuples
from gssapi import _utils

if six.PY2:
    from collections import MutableMapping, Iterable
else:
    from collections.abc import MutableMapping, Iterable


rname_rfc6680 = _utils.import_gssapi_extension('rfc6680')
rname_rfc6680_comp_oid = _utils.import_gssapi_extension('rfc6680_comp_oid')


class Name(rname.Name):
    """A GSSAPI Name

    This class represents a GSSAPI name which may be used with and/or returned
    by other GSSAPI methods.

    It inherits from the low-level GSSAPI :class:`~gssapi.raw.names.Name`
    class, and thus may used with both low-level and high-level API methods.

    This class may be pickled and unpickled, as well as copied.

    The :func:`str` and :func:`bytes` methods may be used to retrieve the
    text of the name.

    Note:
        Name strings will be automatically converted to and from unicode
        strings as appropriate.  If a method is listed as returning a
        :class:`str` object, it will return a unicode string.

        The encoding used will be python-gssapi's current encoding, which
        defaults to UTF-8.
    """

    __slots__ = ('_attr_obj')

    def __new__(cls, base=None, name_type=None, token=None,
                composite=False):
        if token is not None:
            if composite:
                if rname_rfc6680 is None:
                    raise NotImplementedError(
                        "Your GSSAPI implementation does not support RFC 6680 "
                        "(the GSSAPI naming extensions)")

                if rname_rfc6680_comp_oid is not None:
                    base_name = rname.import_name(token,
                                                  NameType.composite_export)
                    displ_name = rname.display_name(base_name, name_type=True)
                    if displ_name.name_type == NameType.composite_export:
                        # NB(directxman12): there's a bug in MIT krb5 <= 1.13
                        # where GSS_C_NT_COMPOSITE_EXPORT doesn't trigger
                        # immediate import logic.  However, we can just use
                        # the normal GSS_C_NT_EXPORT_NAME in this case.
                        base_name = rname.import_name(token, NameType.export)
                else:
                    # NB(directxman12): some older versions of MIT krb5 don't
                    # have support for the GSS_C_NT_COMPOSITE_EXPORT, but do
                    # support composite tokens via GSS_C_NT_EXPORT_NAME.
                    base_name = rname.import_name(token, NameType.export)
            else:
                base_name = rname.import_name(token, NameType.export)
        elif isinstance(base, rname.Name):
            base_name = base
        else:
            if isinstance(base, six.text_type):
                base = base.encode(_utils._get_encoding())

            base_name = rname.import_name(base, name_type)

        return super(Name, cls).__new__(cls, base_name)

    def __init__(self, base=None, name_type=None, token=None, composite=False):
        """
        The constructor can be used to "import" a name from a human readable
        representation, or from a token, and can also be used to convert a
        low-level :class:`gssapi.raw.names.Name` object into a high-level
        object.

        If a :class:`~gssapi.raw.names.Name` object from the low-level API
        is passed as the `base` argument, it will be converted into a
        high-level object.

        If the `token` argument is used, the name will be imported using
        the token.  If the token was exported as a composite token,
        pass `composite=True`.

        Otherwise, a new name will be created, using the `base` argument as
        the human-readable string and the `name_type` argument to denote the
        name type.

        Raises:
            BadNameTypeError
            BadNameError
            BadMechanismError
        """

        if rname_rfc6680 is not None:
            self._attr_obj = _NameAttributeMapping(self)
        else:
            self._attr_obj = None

    def __str__(self):
        if issubclass(str, six.text_type):
            # Python 3 -- we should return unicode
            return bytes(self).decode(_utils._get_encoding())
        else:
            # Python 2 -- we should return a string
            return self.__bytes__()

    def __unicode__(self):
        # Python 2 -- someone asked for unicode
        return self.__bytes__().decode(_utils._get_encoding())

    def __bytes__(self):
        # Python 3 -- someone asked for bytes
        return rname.display_name(self, name_type=False).name

    def display_as(self, name_type):
        """
        Display this name as the given name type.

        This method attempts to display the current :class:`Name`
        using the syntax of the given :class:`NameType`, if possible.

        Warning:

            In MIT krb5 versions below 1.13.3, this method can segfault if
            the name was not *originally* created with a `name_type` that was
            not ``None`` (even in cases when a ``name_type``
            is later "added", such as via :meth:`canonicalize`).
            **Do not use this method unless you are sure the above
            conditions can never happen in your code.**

        Warning:

            In addition to the above warning, current versions of MIT krb5 do
            not actually fully implement this method, and it may return
            incorrect results in the case of canonicalized names.

        :requires-ext:`rfc6680`

        Args:
            name_type (OID): the :class:`NameType` to use to display the given
                name

        Returns:
            str: the displayed name

        Raises:
            OperationUnavailableError
        """

        if rname_rfc6680 is None:
            raise NotImplementedError("Your GSSAPI implementation does not "
                                      "support RFC 6680 (the GSSAPI naming "
                                      "extensions)")
        return rname_rfc6680.display_name_ext(self, name_type).decode(
            _utils._get_encoding())

    @property
    def name_type(self):
        """The :class:`NameType` of this name"""
        return rname.display_name(self, name_type=True).name_type

    def __eq__(self, other):
        if not isinstance(other, rname.Name):
            # maybe something else can compare this
            # to other classes, but we certainly can't
            return NotImplemented
        else:
            return rname.compare_name(self, other)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        disp_res = rname.display_name(self, name_type=True)
        return "Name({name}, {name_type})".format(name=disp_res.name,
                                                  name_type=disp_res.name_type)

    def export(self, composite=False):
        """Export this name as a token.

        This method exports the name into a byte string which can then be
        imported by using the `token` argument of the constructor.

        Args:
            composite (bool): whether or not use to a composite token --
                :requires-ext:`rfc6680`

        Returns:
            bytes: the exported name in token form

        Raises:
            MechanismNameRequiredError
            BadNameTypeError
            BadNameError
        """

        if composite:
            if rname_rfc6680 is None:
                raise NotImplementedError("Your GSSAPI implementation does "
                                          "not support RFC 6680 (the GSSAPI "
                                          "naming extensions)")

            return rname_rfc6680.export_name_composite(self)
        else:
            return rname.export_name(self)

    def canonicalize(self, mech):
        """Canonicalize a name with respect to a mechanism.

        This method returns a new :class:`Name` that is canonicalized according
        to the given mechanism.

        Args:
            mech (OID): the :class:`MechType` to use

        Returns:
            Name: the canonicalized name

        Raises:
            BadMechanismError
            BadNameTypeError
            BadNameError
        """

        return type(self)(rname.canonicalize_name(self, mech))

    def __copy__(self):
        return type(self)(rname.duplicate_name(self))

    def __deepcopy__(self, memo):
        return type(self)(rname.duplicate_name(self))

    def _inquire(self, **kwargs):
        """Inspect this name for information.

        This method inspects the name for information.

        If no keyword arguments are passed, all available information
        is returned.  Otherwise, only the keyword arguments that
        are passed and set to `True` are returned.

        Args:
            mech_name (bool): get whether this is a mechanism name,
                and, if so, the associated mechanism
            attrs (bool): get the attributes names for this name

        Returns:
            InquireNameResult: the results of the inquiry, with unused
                fields set to None

        Raises:
            GSSError
        """

        if rname_rfc6680 is None:
            raise NotImplementedError("Your GSSAPI implementation does not "
                                      "support RFC 6680 (the GSSAPI naming "
                                      "extensions)")

        if not kwargs:
            default_val = True
        else:
            default_val = False

        attrs = kwargs.get('attrs', default_val)
        mech_name = kwargs.get('mech_name', default_val)

        return rname_rfc6680.inquire_name(self, mech_name=mech_name,
                                          attrs=attrs)

    @property
    def is_mech_name(self):
        """Whether or not this name is a mechanism name
        (:requires-ext:`rfc6680`)
        """
        return self._inquire(mech_name=True).is_mech_name

    @property
    def mech(self):
        """The mechanism associated with this name (:requires-ext:`rfc6680`)
        """
        return self._inquire(mech_name=True).mech

    @property
    def attributes(self):
        """The attributes of this name (:requires-ext:`rfc6680`)

        The attributes are presenting in the form of a
        :class:`~collections.MutableMapping` (a dict-like object).

        Retrieved values will always be in the form of :class:`frozensets`.

        When assigning values, if iterables are used, they be considered to be
        the set of values for the given attribute.  If a non-iterable is used,
        it will be considered a single value, and automatically wrapped in an
        iterable.

        Note:
            String types (includes :class:`bytes`) are not considered to
            be iterables in this case.
        """
        if self._attr_obj is None:
            raise NotImplementedError("Your GSSAPI implementation does not "
                                      "support RFC 6680 (the GSSAPI naming "
                                      "extensions)")

        return self._attr_obj


class _NameAttributeMapping(MutableMapping):

    """Provides dict-like access to RFC 6680 Name attributes."""
    def __init__(self, name):
        self._name = name

    def __getitem__(self, key):
        if isinstance(key, six.text_type):
            key = key.encode(_utils._get_encoding())

        res = rname_rfc6680.get_name_attribute(self._name, key)
        return tuples.GetNameAttributeResult(frozenset(res.values),
                                             frozenset(res.display_values),
                                             res.authenticated,
                                             res.complete)

    def __setitem__(self, key, value):
        if isinstance(key, six.text_type):
            key = key.encode(_utils._get_encoding())

        rname_rfc6680.delete_name_attribute(self._name, key)

        if isinstance(value, tuples.GetNameAttributeResult):
            complete = value.complete
            value = value.values
        elif isinstance(value, tuple) and len(value) == 2:
            complete = value[1]
            value = value[0]
        else:
            complete = False

        if (isinstance(value, (six.string_types, bytes)) or
                not isinstance(value, Iterable)):
            # NB(directxman12): this allows us to easily assign a single
            # value, since that's a common case
            value = [value]

            rname_rfc6680.set_name_attribute(self._name, key, value,
                                             complete=complete)

    def __delitem__(self, key):
        if isinstance(key, six.text_type):
            key = key.encode(_utils._get_encoding())

        rname_rfc6680.delete_name_attribute(self._name, key)

    def __iter__(self):
        return iter(self._name._inquire(attrs=True).attrs)

    def __len__(self):
        return len(self._name._inquire(attrs=True).attrs)
