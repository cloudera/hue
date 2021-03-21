from enum import EnumMeta


_extra_values = {}


def register_value(cl_str, name, value):
    _extra_values[cl_str] = _extra_values.get(cl_str, {})
    _extra_values[cl_str][name] = value


class ExtendableEnum(EnumMeta):
    def __new__(metacl, name, bases, classdict):
        extra_vals = _extra_values.get(name)

        if extra_vals is not None:
            for extra_name, extra_val in list(extra_vals.items()):
                if extra_name in classdict:
                    raise AttributeError(
                        "Enumeration extensions cannot override existing "
                        "enumeration members")
                else:
                    classdict[extra_name] = extra_val

        return super(ExtendableEnum, metacl).__new__(metacl, name,
                                                     bases, classdict)
