#!/usr/bin/env python

from importlib import import_module
import sys
import os

__author__ = 'roland'


def load(head, tail):
    if head == "":
        if sys.path[0] != ".":
            sys.path.insert(0, ".")
    else:
        sys.path.insert(0, head)

    if tail.endswith(".py"):
        tail = tail[:-3]

    return import_module(tail)


def intcmp(s1, s2):
    try:
        _i1 = int(s1)
        _i2 = int(s2)
    except ValueError:
        _i1 = s1
        _i2 = s2

    if _i1 < _i2:
        return -1
    if _i1 > _i2:
        return 1
    else:
        return 0


class AMap(object):
    def __init__(self, head, tail, indent=4 * " "):
        self.mod = load(head, tail)
        self.variable = {}
        self.vars = []
        self.text = []
        self.indent = indent
        for key, val in self.mod.__dict__.items():
            if key.startswith("__"):
                continue
            elif key == "MAP":
                continue
            else:
                self.variable[key] = val
                self.vars.append(key)
        self.vars.sort()

    def sync(self):
        for key, val in self.mod.MAP["fro"].items():
            try:
                assert self.mod.MAP["to"][val] == key
            except KeyError:  # missing value
                print("# Added %s=%s" % (self.mod.MAP["to"][val], key))
                self.mod.MAP["to"][val] = key
            except AssertionError:
                raise Exception("Mismatch key:%s '%s' != '%s'" % (
                    key, val, self.mod.MAP["to"][val]))

        for val in self.mod.MAP["to"].values():
            if val not in self.mod.MAP["fro"]:
                print("# Missing URN '%s'" % val)

    def do_fro(self):
        txt = ["%s'fro': {" % self.indent]
        i2 = self.indent + self.indent
        _fro = self.mod.MAP["fro"]
        for var in self.vars:
            _v = self.variable[var]
            li = [k[len(_v):] for k in _fro.keys() if k.startswith(_v)]
            li.sort(intcmp)
            for item in li:
                txt.append("%s%s+'%s': '%s'," % (i2, var, item,
                                                 _fro[_v + item]))
        txt.append('%s},' % self.indent)
        return txt

    def do_to(self):
        txt = ["%s'to': {" % self.indent]
        i2 = self.indent + self.indent
        _to = self.mod.MAP["to"]
        _keys = _to.keys()
        _keys.sort()
        invmap = dict([(v, k) for k, v in self.variable.items()])

        for key in _keys:
            val = _to[key]
            for _urn, _name in invmap.items():
                if val.startswith(_urn):
                    txt.append("%s'%s': %s+'%s'," % (i2, key, _name,
                                                     val[len(_urn):]))

        txt.append('%s}' % self.indent)
        return txt

    def __str__(self):
        self.sync()
        text = []
        for key in self.vars:
            text.append("%s = '%s'" % (key, self.variable[key]))

        text.extend(["", ""])

        text.append("MAP = {")
        text.append("%s'identifier': '%s'," % (self.indent,
                                               self.mod.MAP["identifier"]))
        text.extend(self.do_fro())
        text.extend(self.do_to())

        text.append("}")
        text.append("")
        return "\n".join(text)


if __name__ == "__main__":
    _name = sys.argv[1]
    if os.path.isfile(_name):
        directory, fname = os.path.split(_name)
        amap = AMap(directory, fname, 4 * " ")
        f = open(_name, "w")
        f.write("%s" % amap)
        f.close()
    elif os.path.isdir(_name):
        for fname in os.listdir(_name):
            if fname == "__init__.py":
                continue
            elif fname.endswith(".pyc"):
                continue
            print(10 * "=" + fname + 10 * "=")
            amap = AMap(_name, fname, 4 * " ")
            f = open(fname, "w")
            f.write("%s" % amap)
            f.close()
