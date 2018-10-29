__author__ = 'roland'


def find_paths(cls, arg, path=None, seen=None, res=None, lev=0):
    if lev == 0 and res is None:
        res = []

    if path is None:
        path = []

    if seen is None:
        seen = [cls]
    else:
        if cls in seen:
            return None

        seen.append(cls)

    for cn, c in cls.c_children.values():
        _path = path + [cn]
        if cn == arg:
            if res is not None:
                res.append(_path)
        else:
            if isinstance(c, list):
                _c = c[0]
            else:
                _c = c

            find_paths(_c, arg, _path, seen, res)

    for an, typ, mult in cls.c_attributes.values():
        if an == arg:
            if res is not None:
                res.append(path + [an])

    if lev == 0:
        return res


def set_arg(cls, arg, value):
    res = []
    for path in find_paths(cls, arg):
        x = y = {}
        for arc in path[:-1]:
            y[arc] = {}
            y = y[arc]
        y[path[-1]] = value
        res.append(x)

    return res


def add_path(tdict, path):
    """

    :param tdict: a dictionary representing a argument tree
    :param path: a path list
    :return: a dictionary
    """
    t = tdict
    for step in path[:-2]:
        try:
            t = t[step]
        except KeyError:
            t[step] = {}
            t = t[step]
    t[path[-2]] = path[-1]

    return tdict


def is_set(tdict, path):
    """

    :param tdict: a dictionary representing a argument tree
    :param path: a path list
    :return: True/False if the value is set
    """
    t = tdict
    for step in path:
        try:
            t = t[step]
        except KeyError:
            return False

    if t is not None:
        return True

    return False


def get_attr(tdict, path):
    t = tdict
    for step in path:
        t = t[step]

    return t
