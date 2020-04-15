#!/usr/bin/env python

import re
import time
import getopt
import imp
import sys
import types
import errno
import six

__version__ = 0.5

from xml.etree import cElementTree as ElementTree

INDENT = 4*" "
DEBUG = False

XMLSCHEMA = "http://www.w3.org/2001/XMLSchema"
XML_NAMESPACE = 'http://www.w3.org/XML/1998/namespace'

CLASS_PROP = [("c_children", ".copy()"), 
                ("c_attributes", ".copy()"),
                ("c_child_order", "[:]"),
                ("c_cardinality", ".copy()")]
                
BASE_ELEMENT = ["text", "extension_elements", "extension_attributes"]
    
class MissingPrerequisite(Exception):
    pass

def sd_copy(arg):
    try:
        return arg.copy()
    except AttributeError:
        return {}
        
# ------------------------------------------------------------------------

def class_pyify(ref):
    return ref.replace("-","_")

PROTECTED_KEYWORDS = ["import", "def", "if", "else", "return", "for",
                      "while", "not", "try", "except", "in"]


def def_init(imports, attributes):
    indent = INDENT+INDENT
    indent3 = INDENT+INDENT+INDENT
    line = ["%sdef __init__(self," % INDENT]

    for elem in attributes:
        if elem[0] in PROTECTED_KEYWORDS:
            _name = elem[0] +"_"
        else:
            _name = elem[0]

        if elem[2]:
            line.append("%s%s='%s'," % (indent3, _name, elem[2]))
        else:
            line.append("%s%s=%s," % (indent3, _name, elem[2]))

    for _, elems in imports.items():
        for elem in elems:
            if elem in PROTECTED_KEYWORDS:
                _name = elem +"_"
            else:
                _name = elem
            line.append("%s%s=None," % (indent3, _name))

    line.append("%stext=None," % indent3)
    line.append("%sextension_elements=None," % indent3)
    line.append("%sextension_attributes=None," % indent3)
    line.append("%s):" % indent)
    return line
    

def base_init(imports):
    line = []
    indent4 = INDENT+INDENT+INDENT+INDENT
    if not imports:
        line.append("%sSamlBase.__init__(self, " % (INDENT+INDENT))
        for attr in BASE_ELEMENT:
            if attr in PROTECTED_KEYWORDS:
                _name = attr + "_"
            else:
                _name = attr
            line.append("%s%s=%s," % (indent4, _name, _name))
        line.append("%s)" % indent4)
    else:
        # TODO have to keep apart which properties come from which superior
        for sup, elems in imports.items():
            line.append("%s%s.__init__(self, " % (INDENT+INDENT, sup))
            lattr = elems[:]
            lattr.extend(BASE_ELEMENT)
            for attr in lattr:
                if attr in PROTECTED_KEYWORDS:
                    _name = attr + "_"
                else:
                    _name = attr
                line.append("%s%s=%s," % (indent4, _name, _name))
            line.append("%s)" % indent4)
    return line
    

def initialize(attributes):
    indent = INDENT+INDENT
    line = []
    for prop, val, _default in attributes:
        if prop in PROTECTED_KEYWORDS:
            _name = prop +"_"
        else:
            _name = prop

        if val in PROTECTED_KEYWORDS:
            _vname = val +"_"
        else:
            _vname = val
            
        line.append("%sself.%s=%s" % (indent, _name, _vname))
    return line


def _mod_typ(prop):
    try:
        (mod, typ) = prop.type
    except ValueError:
        typ = prop.type
        mod = None
    except TypeError: # No type property
        try:
            (mod, typ) = prop.ref
        except ValueError:
            if prop.class_name:
                typ = prop.class_name
            else:
                typ = prop.ref
            mod = None
    
    return mod, typ


def _mod_cname(prop, cdict):
    if hasattr(prop, "scoped"):
        cname = prop.class_name
        mod = None
    else:
        (mod, typ) = _mod_typ(prop)
        if not mod:
            try:
                cname = cdict[typ].class_name
            except KeyError:
                cname = cdict[class_pyify(typ)].class_name
        else:
            cname = typ
        
    return mod, cname


def leading_uppercase(string):
    try:
        return string[0].upper()+string[1:]
    except IndexError:
        return string
    except TypeError:
        return ""


def leading_lowercase(string):
    try:
        return string[0].lower()+string[1:]
    except IndexError:
        return string
    except TypeError:
        return ""


def rm_duplicates(properties):
    keys = []
    clist = []
    for prop in properties:
        if prop.name in keys:
            continue
        else:
            clist.append(prop)
            keys.append(prop.name)
    return clist

# def rm_duplicates(lista):
#     res = []
#     for item in lista:
#         if item not in res:
#             res.append(item)
#     return res


def klass_namn(obj):
    if obj.class_name:
        return obj.class_name
    else:
        return obj.name
    

class PyObj(object):
    def __init__(self, name=None, pyname=None, root=None):
        self.name = name
        self.done = False
        self.local = True
        self.root = root
        self.superior = []
        self.value_type = ""
        self.properties = ([], [])
        self.abstract = False
        self.class_name = ""
        
        if pyname:
            self.pyname = pyname
        elif name:
            self.pyname = pyify(name)
        else:
            self.pyname = name

        self.type = None
            
    def child_spec(self, target_namespace, prop, mod, typ, lista):
        if mod:
            namesp = external_namespace(self.root.modul[mod])
            pkey = '{%s}%s' % (namesp, prop.name)
            typ = "%s.%s" % (mod, typ)
        else:
            pkey = '{%s}%s' % (target_namespace, prop.name)

        if lista:
            return "c_children['%s'] = ('%s', [%s])" % (
                        pkey, prop.pyname, typ)
        else:
            return "c_children['%s'] = ('%s', %s)" % (
                        pkey, prop.pyname, typ)
    
    def knamn(self, sup, cdict):
        cname = cdict[sup].class_name
        if not cname:
            (namesp, tag) = cdict[sup].name.split('.')
            if namesp:
                ctag = self.root.modul[namesp].factory(tag).__class__.__name__
                cname = '%s.%s' % (namesp, ctag)
            else:
                cname = tag + "_"
        return cname
    
    def _do_properties(self, line, cdict, ignore, target_namespace):
        args = []
        child = []

        try:
            (own, inh) = self.properties
        except AttributeError:
            (own, inh) = ([], [])
            
        for prop in own:
            if isinstance(prop, PyAttribute):
                line.append("%sc_attributes['%s'] = %s" % (INDENT, 
                                                    prop.name, prop.spec()))
                if prop.fixed:
                    args.append((prop.pyname, prop.fixed, None))
                else:
                    if prop.default:
                        args.append((prop.pyname, prop.pyname, prop.default))
                    else:
                        args.append((prop.pyname, prop.pyname, None))
                        
            elif isinstance(prop, PyElement):

                (mod, cname) = _mod_cname(prop, cdict)
                
                if prop.max == "unbounded":
                    lista = True
                    pmax = 0 # just has to be different from 1
                else:
                    pmax = int(prop.max)
                    lista = False
                    
                if prop.name in ignore:
                    pass
                else:
                    line.append("%s%s" % (INDENT, self.child_spec(
                                                        target_namespace, prop,
                                                        mod, cname,
                                                        lista)))

                pmin = int(getattr(prop, 'min', 1))

                if pmax == 1 and pmin == 1:
                    pass
                elif prop.max == "unbounded":
                    line.append( "%sc_cardinality['%s'] = {\"min\":%s}" % (
                                    INDENT, prop.pyname, pmin))
                else:
                    line.append(
                        "%sc_cardinality['%s'] = {\"min\":%s, \"max\":%d}" % (
                                    INDENT, prop.pyname, pmin, pmax))

                child.append(prop.pyname)
                if lista:
                    args.append((prop.pyname, "%s or []" % (prop.pyname,), 
                                    None))
                else:
                    args.append((prop.pyname, prop.pyname, None))
        
        return args, child, inh
        
    def _superiors(self, cdict):
        imps = {}

        try:
            superior = self.superior
            sups = []
            for sup in superior:
                klass = self.knamn(sup, cdict)
                sups.append(klass)
                
                imps[klass] = []
                for cla in cdict[sup].properties[0]:
                    if cla.pyname and cla.pyname not in imps[klass]: 
                        imps[klass].append(cla.pyname)
        except AttributeError:
            superior = []
            sups = []
        
        return superior, sups, imps
        
    def class_definition(self, target_namespace, cdict=None, ignore=None):
        line = []

        if self.root:
            if self.name not in [c.name for c in self.root.elems]:
                self.root.elems.append(self)

        (superior, sups, imps) = self._superiors(cdict)

        c_name = klass_namn(self)
            
        if not superior:
            line.append("class %s(SamlBase):" % (c_name,))
        else:
            line.append("class %s(%s):" % (c_name, ",".join(sups)))

        if hasattr(self, 'scoped'):
            pass
        else:
            line.append("%s\"\"\"The %s:%s element \"\"\"" % (INDENT, 
                                                        target_namespace,
                                                        self.name))
        line.append("")
        line.append("%sc_tag = '%s'" % (INDENT, self.name))
        line.append("%sc_namespace = NAMESPACE" % (INDENT,))
        try:
            if self.value_type:
                if isinstance(self.value_type, six.string_types):
                    line.append("%sc_value_type = '%s'" % (INDENT, 
                                                            self.value_type))
                else:
                    line.append("%sc_value_type = %s" % (INDENT, 
                                                        self.value_type))
        except AttributeError:
            pass

        if not superior:
            for var, cps in CLASS_PROP:
                line.append("%s%s = SamlBase.%s%s" % (INDENT, var, var, cps))
        else:
            for sup in sups:
                for var, cps in CLASS_PROP:
                    line.append("%s%s = %s.%s%s" % (INDENT, var, sup, var, 
                                                    cps))

        (args, child, inh) = self._do_properties(line, cdict, ignore, 
                                                target_namespace)
        
        if child:
            line.append("%sc_child_order.extend([%s])" % (INDENT,
                            "'"+"', '".join(child)+"'"))
            
        if args:
            if inh:
                cname = self.knamn(self.superior[0], cdict)
                imps = {cname: [c.pyname for c in inh if c.pyname]}
            line.append("")
            line.extend(def_init(imps, args))
            line.extend(base_init(imps))
            line.extend(initialize(args))
        
        line.append("")
        if not self.abstract or not self.class_name.endswith("_"):
            line.append("def %s_from_string(xml_string):" % pyify(
                                                            self.class_name))
            line.append(
                "%sreturn saml2.create_class_from_xml_string(%s, xml_string)" % (
                            INDENT, self.class_name))
            line.append("")
        
        self.done = True
        return "\n".join(line)
    
def prepend(add, orig):
    # return a list which is the lists concatenated with the second list first
    res = [add]
    if orig:
        res.extend(orig)
    return res
    
def pyobj_factory(name, value_type, elms=None):
    pyobj = PyObj(name, pyify(name))
    pyobj.value_type = value_type
    if elms:
        if name not in [c.name for c in elms]:
            elms.append(pyobj)
    return pyobj

def pyelement_factory(name, value_type, elms=None):
    obj = PyElement(name, pyify(name))
    obj.value_type = value_type
    if elms:
        if name not in [c.name for c in elms]:
            elms.append(obj)
    return obj
    
def expand_groups(properties, cdict):
    res = []
    for prop in properties:
        if isinstance(prop, PyGroup):
            # only own, what about inherited ? Not on groups ?
            cname = prop.ref[1]
            res.extend(cdict[cname].properties[0])
        else:
            res.append(prop)
            
    return res
    
class PyElement(PyObj):
    def __init__(self, name=None, pyname=None, root=None, parent=""):
        PyObj.__init__(self, name, pyname, root)
        if parent:
            self.class_name = "%s_%s" % (leading_uppercase(parent), self.name)
        else:
            self.class_name = leading_uppercase(self.name)
        self.ref = None
        self.min = 1
        self.max = 1
        self.definition = None
        self.orig = None
    
    # def prereq(self, prop):
    #     prtext = prop.text(target_namespace, cdict)
    #     if prtext == None:
    #         return []
    #     else:
    #         prop.done = True
    #         return prtext
        
    def undefined(self, cdict):
        try:
            (mod, typ) = self.type
            if not mod:
                cname = leading_uppercase(typ)
                if not cdict[cname].done:
                    return [cdict[cname]], []
        except ValueError:
            pass
        except TypeError: # could be a ref then or a PyObj instance
            if isinstance(self.type, PyType):
                return self.type.undefined(cdict)
            elif isinstance(self.ref, tuple):
                pass
            else:
                cname = leading_uppercase(self.ref)
                if not cdict[cname].done:
                    return [cdict[cname]], []
        return [], []
    
    def _local_class(self, typ, cdict, child, target_namespace, ignore):
        if typ in cdict and not cdict[typ].done:
            raise MissingPrerequisite(typ)
        else:
            self.orig = {"type": self.type}
            try:
                self.orig["superior"] = self.superior
            except AttributeError:
                self.orig["superior"] = []
            self.superior = [typ]
            req = self.class_definition(target_namespace, cdict, 
                                        ignore)
            if not child:
                req = [req]
            
            if not hasattr(self, 'scoped'):
                cdict[self.name] = self
                cdict[self.name].done = True
                if child:
                    cdict[self.name].local = True
            self.type = (None, self.name)
        
        return req
        
    def _external_class(self, mod, typ, cdict, child, target_namespace, 
                        ignore):
        # Will raise exception if class can't be found
        cname = self.root.modul[mod].factory(typ).__class__.__name__
        imp_name = "%s.%s" % (mod, cname)
            
        if imp_name not in cdict:
            # create import object so I can get the properties from it 
            # later
            impo = pyelement_factory(imp_name, None, None)
            impo.properties = [_import_attrs(self.root.modul[mod], typ, 
                                            self.root),[]]
            impo.class_name = imp_name
            cdict[imp_name] = impo
            impo.done = True
            if child:
                impo.local = True
        # and now for this object
        self.superior = [imp_name]
        text = self.class_definition(target_namespace, cdict, 
                                        ignore=ignore)
        
        return text
        
    def text(self, target_namespace, cdict, child=True, ignore=None):
        if ignore is None:
            ignore = []

        if child:
            text = []
        else:
            text = None
        req = []
        try:
            (mod, typ) = self.type
            if not mod:
                req = self._local_class(typ, cdict, child, 
                                        target_namespace, ignore)
            else:
                text = self._external_class(mod, typ, cdict, child, 
                                            target_namespace, ignore)
        except ValueError: # Simple type element
            if self.type:
                text = self.class_definition(target_namespace, cdict, 
                                                ignore=ignore)
                if child:
                    self.local = True
                self.done = True
                    
        except TypeError: # could be a ref then or a PyObj instance
            if isinstance(self.type, PyObj):
                pyobj = self.type
                pyobj.name = self.name
                pyobj.pyname = self.pyname
                pyobj.class_name = self.class_name
                cdict[self.name] = pyobj
                return pyobj.text(target_namespace, cdict, ignore=ignore)
            elif isinstance(self.ref, tuple):
                (mod, typ) = self.ref
                if mod:
                    #self.superior = ["%s.%s" % (mod, typ)]
                    if verify_import(self.root.modul[mod], typ):
                        return req, text
                    else:
                        raise Exception(
            "Import attempted on %s from %s module failed - wasn't there" % (
                                typ,mod))
                elif not child:
                    self.superior = [typ]
                    text = self.class_definition(target_namespace, cdict,
                                                    ignore=ignore)
            else:
                if not cdict[class_pyify(self.ref)].done:
                    raise MissingPrerequisite(self.ref)
                
        self.done = True
        return req, text
        
def _do(obj, target_namespace, cdict, prep):
    try:
        (req, text) = obj.text(target_namespace, cdict)
    except MissingPrerequisite:
        return [], None
        
    if text is None:
        if req:
            #prep = prepend(req, prep)
            prep.append(req)
        return prep, None
    else:
        obj.done = True
        if req:
            if isinstance(req, six.string_types):
                prep.append(req)
            else:
                prep.extend(req)
        if text:
            #prep = prepend(text, prep)
            prep.append(text)
    return prep

def reqursive_superior(supc, cdict):
    properties = supc.properties[0]
    for sup in supc.superior:
        rsup = cdict[sup]
        if rsup.properties[1]:
            properties.extend(rsup.properties[1])
        else:
            properties.extend(reqursive_superior(rsup, cdict))
    return properties
    
class PyType(PyObj):
    def __init__(self, name=None, pyname=None, root=None, superior=None, 
                internal=True, namespace=None):
        PyObj.__init__(self, name, pyname, root)
        self.class_name = leading_uppercase(self.name + '_')
        self.properties = ([], [])
        if superior:
            self.superior = [superior]
        else:
            self.superior = []
        self.value_type = None
        self.internal = internal
        self.namespace = namespace

    def text(self, target_namespace, cdict, _child=True, ignore=None,
             _session=None):
        if not self.properties and not self.type \
                and not self.superior:
            self.done = True
            return [], self.class_definition(target_namespace, cdict)

        if ignore is None:
            ignore = []
        req = []
        inherited_properties = []
        for sup in self.superior:
            try:
                supc = cdict[sup]
            except KeyError:
                (mod, typ) = sup.split('.')
                supc = pyobj_factory(sup, None, None)
                if mod:
                    supc.properties = [_import_attrs(self.root.modul[mod], 
                                                        typ, self.root),[]]
                cdict[sup] = supc
                supc.done = True
                
            if not supc.done:
                res = _do(supc, target_namespace, cdict, req)
                if isinstance(res, tuple):
                    return res
            
            if not self.properties[1]:
                inherited_properties = reqursive_superior(supc, cdict)
        
        if inherited_properties:
            self.properties = (self.properties[0], 
                                rm_duplicates(inherited_properties))
            
        (own, inh) = self.properties
        own = rm_duplicates(expand_groups(own, cdict))
        self.properties = (own, inh)
        for prop in own:
            if not prop.name: # Ignore
                continue 
            if not prop.done:
                if prop.name in ignore:
                    continue
                res = _do(prop, target_namespace, cdict, req)
                if res == ([], None):
                    # # Cleaning up
                    # for prp in own:
                    #     if prp == prop:
                    #         break
                    #     try:
                    #         if cdict[prp.name].local:
                    #             del cdict[prp.name]
                    #             if hasattr(prp, "orig") and prp.orig:
                    #                 for key, val in prp.orig.items():
                    #                     setattr(prp, key, val)
                    #             prp.done = False
                    #             prp.local = False
                    #     except KeyError:
                    #         pass
                    res = (req, None)
                if isinstance(res, tuple):
                    return res
        
        return req, self.class_definition(target_namespace, cdict, ignore)
    
    def undefined(self, cdict):
        undef = ([], [])

        for sup in self.superior:
            supc = cdict[sup]
            if not supc.done:
                undef[0].append(supc)

        (own, _) = self.properties
        for prop in own:
            if not prop.name: # Ignore
                continue 
            if isinstance(prop, PyAttribute):
                continue
            if not prop.done:
                undef[1].append(prop)
        return undef

class PyAttribute(PyObj):
    def __init__(self, name=None, pyname=None, root=None, external=False, 
                    namespace="", required=False, typ=""):
        PyObj.__init__(self, name, pyname, root)

        self.required = required
        self.external = external
        self.namespace = namespace
        self.base = None
        self.type = typ
        self.fixed = False
        self.default = None

    def text(self, _target_namespace, cdict, _child=True):
        if isinstance(self.type, PyObj):
            if not cdict[self.type.name].done:
                raise MissingPrerequisite(self.type.name)
                
        return [], [] # Means this elements definition is empty
        
    def spec(self):
        if isinstance(self.type, PyObj):
            return "('%s', %s, %s)" % (self.pyname, self.type.class_name, 
                                        self.required)
        else:
            if self.type:
                return "('%s', '%s', %s)" % (self.pyname, self.type, 
                                                self.required)
            else:
                return "('%s', '%s', %s)" % (self.pyname, self.base, 
                                                self.required)
       
class PyAny(PyObj):
    def __init__(self, name=None, pyname=None, _external=False, _namespace=""):
        PyObj.__init__(self, name, pyname)
        self.done = True

class PyAttributeGroup(object):
    def __init__(self, name, root):
        self.name = name
        self.root = root
        self.properties = []

class PyGroup(object):
    def __init__(self, name, root):
        self.name = name
        self.root = root
        self.properties = []
        self.done = False
        self.ref = []
    
    def text(self, _target_namespace, _dict, _child, _ignore):
        return [], []
        
    def undefined(self, _cdict):
        undef = ([], [])

        (own, _) = self.properties
        for prop in own:
            if not prop.name: # Ignore
                continue 
            if not prop.done:
                undef[1].append(prop)
        return undef
    
# -----------------------------------------------------------------------------
def verify_import(modul, tag):
    try:
        _ = modul.factory(tag)
        return True
    except Exception:
        return False
    
def external_namespace(modul):
    return modul.NAMESPACE

def _import_attrs(modul, tag, top):
    obj = modul.factory(tag)
    properties = [PyAttribute(key, val[0], top, True, obj.c_namespace, val[2],
                            val[1]) for key,val in obj.c_attributes.items()]
    for child in obj.c_child_order:
        for key, val in obj.c_children.items():
            (pyn, mul) = val
            maximum = 1
            if isinstance(mul, list):
                mul = mul[0]
                maximum = "unbounded"
            if pyn == child:
                cpy = PyElement(name=mul.c_tag, pyname=pyn, root=top) 
    #                            internal=False, ns=obj.c_namespace)
                cpy.max = maximum
                properties.append(cpy)

    return properties

# ------------------------------------------------------------------------

def _spec(elem):
    try:
        name = elem.name
    except AttributeError:
        name = "anonymous"
    txt = "%s" % name
    try:
        txt += " ref: %s" % elem.ref
    except AttributeError:
        try:
            txt += " type: %s" % elem.type
        except AttributeError:
            pass

    return txt
        
# def _klass(elem, _namespace, sup, top):
#     if elem.name in top.py_elements:
#         return None
#     else:
#         kl = PyType(elem.name, root=top)
#         top.py_elements[elem.name] = kl
#         if sup != "SamlBase":
#             kl.superior.append(sup)
#         return kl
        
def _do_from_string(name):
    print
    print("def %s_from_string(xml_string):" % pyify(name))
    print("%sreturn saml2.create_class_from_xml_string(%s, xml_string)" % (
                INDENT, name))

def _namespace_and_tag(obj, param, top):
    try:
        (namespace, tag) = param.split(":")
    except ValueError:
        namespace = ""
        tag = param
    # except AttributeError:
    #     namespace = ""
    #     tag = obj.name

    return namespace, tag
    
# -----------------------------------------------------------------------------

class Simple(object):
    def __init__(self, elem):
        self.default = None
        self.fixed = None
        self.xmlns_map = []
        self.name = ""
        self.type = None
        self.use = None
        self.ref = None
        self.scoped = False
        self.itemType = None
        
        for attribute, value in iter(elem.attrib.items()):
            self.__setattr__(attribute, value)

    def collect(self, top, sup, argv=None, parent=""):
        argv_copy = sd_copy(argv)
        rval = self.repr(top, sup, argv_copy, True, parent)
        if rval:
            return [rval], []
        else:
            return [], []

    def repr(self, _top=None, _sup=None, _argv=None, _child=True, _parent=""):
        return None
        
    def elements(self, _top):
        return []

        
class Any(Simple):
    
    def repr(self, _top=None, _sup=None, _argv=None, _child=True, _parent=""):
        return PyAny()
        
class AnyAttribute(Simple):

    def repr(self, _top=None, _sup=None, _argv=None, _child=True, _parent=""):
        return PyAny()

class Attribute(Simple):
    def repr(self, top=None, sup=None, _argv=None, _child=True, _parent=""):
        # default, fixed, use, type
                    
        if DEBUG:
            print("#ATTR", self.__dict__)

        external = False
        name = ""
        try:
            (namespace, tag) = _namespace_and_tag(self, self.ref, top)
            ref = True
            pyname = tag
            if namespace in self.xmlns_map:
                if self.xmlns_map[namespace] == top.target_namespace:
                    name = tag
                else :
                    external = True
                    name = "{%s}%s" % (self.xmlns_map[namespace], tag)
            else:
                if namespace == "xml":
                    name = "{%s}%s" % (XML_NAMESPACE, tag)
        except AttributeError:
            name = self.name
            pyname = pyify(name)
            ref = False
        except ValueError: # self.ref exists but does not split into two parts
            ref = True
            if "" == top.target_namespace:
                name = self.ref
                pyname = pyify(name)
            else: # referering to what
                raise Exception("Strange reference: %s" % self.ref)
                    
        objekt = PyAttribute(name, pyname, external=external, root=top)
        
        # Initial declaration
        if not ref:
            try:
                (namespace, klass) = _namespace_and_tag(self, self.type, top)
                if self.xmlns_map[namespace] == top.target_namespace:
                    ctyp = get_type_def(klass, top.parts)
                    if not ctyp.py_class:
                        ctyp.repr(top, sup)
                    objekt.type = ctyp.py_class
                elif self.xmlns_map[namespace] == XMLSCHEMA:
                    objekt.type = klass
                else:
                    objekt.type = self.type
            except ValueError:
                if self.xmlns_map[""] == top.target_namespace:
                    ctyp = get_type_def(self.type.replace("-","_"), top.parts)
                    if not ctyp.py_class:
                        ctyp.repr(top, sup)
                    objekt.type = ctyp.py_class                    
                else:
                    objekt.type = self.type
            except AttributeError:
                objekt.type = None
        try:
            if self.use == "required":
                objekt.required = True
        except AttributeError:
            pass
            
        # in init
        try:
            objekt.default = self.default
        except AttributeError:
            pass
                
        # attr def
        try:
            objekt.fixed = self.fixed
        except AttributeError:
            pass
        
        if DEBUG:
            print("#--ATTR py_attr:%s" % (objekt,))
            
        return objekt
        
class Enumeration(Simple):
    pass
    
class Union(Simple):
    pass
    
class Import(Simple):
    pass
    
class Documentation(Simple):
    pass
    
class MaxLength(Simple):
    pass

class Length(Simple):
    pass
    
class MinInclusive(Simple):
    pass
    
class MaxInclusive(Simple):
    pass

class MinExclusive(Simple):
    pass

class MaxExclusive(Simple):
    pass
    
class List(Simple):
    pass

class Include(Simple):
    pass


# -----------------------------------------------------------------------------

def sequence(elem):
    return [evaluate(child.tag, child) for child in elem]

def name_or_ref(elem, top):
    try:
        (namespace, name) = _namespace_and_tag(elem, elem.ref, top)
        if namespace and elem.xmlns_map[namespace] == top.target_namespace:
            return name
        else:
            return elem.ref
    except AttributeError:
        return elem.name

class Complex(object):
    def __init__(self, elem):
        self.value_of = ""
        self.parts = []
        self._own = []
        self._inherited = []
        self._generated = False
        self.py_class = None
        self.properties = []
        # From Elementtree
        self.ref = None
        self.type = None
        self.xmlns_map = []
        self.maxOccurs = 1
        self.minOccurs = 1
        self.base = None
        self.scoped = False
        self.abstract = False
        
        for attribute, value in iter(elem.attrib.items()):
            self.__setattr__(attribute, value)

        try:
            if elem.text.strip():
                self.value_of = elem.text.strip()
        except AttributeError:
            pass

        self.do_child(elem)
        
        try:
            self.name = self.name.replace("-","_")
        except AttributeError:
            pass

    def _extend(self, top, sup, argv=None, parent="", base=""):
        argv_copy = sd_copy(argv)
        for part in self.parts:
            (own, inh) = part.collect(top, sup, argv_copy, parent)
            if own and base:
                if len(own) == 1 and isinstance(own[0], PyAttribute):
                    own[0].base = base
            self._own.extend(own)
            self._inherited.extend(inh)
        
    def collect(self, top, sup, argv=None, parent=""):
        if self._own or self._inherited:
            return self._own, self._inherited
            
        if DEBUG:
            print(self.__dict__)
            print("#-- %d parts" % len(self.parts))
        
        self._extend(top, sup, argv, parent)
        
        return self._own, self._inherited
        
    def do_child(self, elem):
        for child in elem:
            self.parts.append(evaluate(child.tag, child))

    def elements(self, top):
        res = []
        # try:
        #     string = "== %s (%s)" % (self.name,self.__class__)
        # except AttributeError:
        #     string = "== (%s)" % (self.__class__,)
        # print(string)
        for part in self.parts:
            if isinstance(part, Element):
                res.append(name_or_ref(part, top))
            else:
                if isinstance(part, Extension):
                    res.append(part.base)
                res.extend(part.elements(top))

        return res

    def repr(self, _top=None, _sup=None, _argv=None, _child=True, parent=""):
        return None

    def significant_parts(self):
        res = []
        for p in self.parts:
            if isinstance(p, Annotation):
                continue
            else:
                res.append(p)
                
        return res
        
def min_max(cls, objekt, argv):
    try:
        objekt.max = argv["maxOccurs"]
        if cls.maxOccurs != 1:
            objekt.max = cls.maxOccurs
    except (KeyError, TypeError):
        objekt.max = cls.maxOccurs

    try:
        objekt.min = argv["minOccurs"]
        if cls.minOccurs != 1:
            objekt.min = cls.minOccurs
    except (KeyError, TypeError):
        objekt.min = cls.minOccurs
            
    
class Element(Complex):
    def __str__(self):
        return "%s" % (self.__dict__,)

    def klass(self, top):
        xns = None
        ctyp = None
        ref = False
        try:
            (namespace, name) = _namespace_and_tag(self, self.ref, top)
            ref = True
        except AttributeError:
            try:
                (namespace, name) = self.type.split(":")
            except ValueError:
                namespace = None
                name = self.type
            except AttributeError:
                namespace = name = None

        if self.xmlns_map[namespace] == top.target_namespace:
            ctyp = get_type_def(name, top.parts)
        else:
            xns = namespace

        return namespace, name, ctyp, xns, ref

    def collect(self, top, sup, argv=None, parent=""):
        """ means this element is part of a larger object, hence a property of 
        that object """
        
        try:
            argv_copy = sd_copy(argv)
            return [self.repr(top, sup, argv_copy, parent=parent)], []
        except AttributeError as exc:
            print("#!!!!", exc)
            return [], []

    def elements(self, top):            
        (_namespace, name, ctyp, xns, _) = self.klass(top)
        if ctyp:
            return ctyp.elements(top)
        elif xns:
            return ["%s.%s" % (xns, name)]
        else:
            return []

    def repr(self, top=None, sup=None, argv=None, child=True, parent=""):
        #<element ref='xenc:ReferenceList' ...
        #<element name='Transforms' type='xenc:TransformsType' ...
        #<element name='CarriedKeyName' type='string' ...
        #<element name="RecipientKeyInfo" type="ds:KeyInfoType" ...
        #<element name='ReferenceList'>

        if self.py_class:
            return self.py_class
            
        try:
            myname = self.name
        except AttributeError:
            myname = ""

        if DEBUG:
            print("#Element.repr '%s' (child=%s) [%s]" %
                  (myname, child, self._generated))

        self.py_class = objekt = PyElement(myname, root=top)
        min_max(self, objekt, argv)
                
        try:
            (namespace, superkl) = _namespace_and_tag(self, self.ref, top)
            # internal or external reference
            if not myname:
                objekt.name = superkl
                objekt.pyname = pyify(superkl)
            if self.xmlns_map[namespace] == top.target_namespace:
                objekt.ref = superkl 
            else:
                objekt.ref = (namespace, superkl)                
        except AttributeError as exc:
            if DEBUG:
                print("#===>", exc)

            typ = self.type

            try:
                (namespace, klass) = _namespace_and_tag(self, typ, top)
                if self.xmlns_map[namespace] == top.target_namespace:
                    objekt.type = (None, klass)
                elif self.xmlns_map[namespace] == XMLSCHEMA:
                    objekt.type = klass
                    objekt.value_type = {"base": klass}
                else:
                    objekt.type = (namespace, klass)

            except ValueError:
                objekt.type = typ
                objekt.value_type = {"base": typ}

            except AttributeError:
                # neither type nor reference, definitely local
                if hasattr(self, "parts"):
                    if len(self.parts) == 1:
                        if isinstance(self.parts[0], ComplexType) or \
                            isinstance(self.parts[0], SimpleType):
                            self.parts[0].name = self.name
                            objekt.type = self.parts[0].repr(top, sup, 
                                                            parent=self.name)
                            objekt.scoped = True
                    elif len(self.parts) == 2:# One child might be Annotation
                        if isinstance(self.parts[0], Annotation):
                            self.parts[1].name = self.name
                            objekt.type = self.parts[1].repr(top, sup, 
                                                            parent=self.name)
                            objekt.scoped = True
                        elif isinstance(self.parts[1], Annotation):
                            self.parts[0].name = self.name
                            objekt.type = self.parts[0].repr(top, sup, 
                                                            parent=self.name)
                            objekt.scoped = True
                else:
                    if DEBUG:
                        print("$", self)
                    raise 

            if parent:
                objekt.class_name = "%s_%s" % (
                                        leading_uppercase(parent),
                                        objekt.name)
                objekt.scoped = True
                
        return objekt


class SimpleType(Complex):
    def repr(self, top=None, _sup=None, _argv=None, _child=True, parent=""):
        if self.py_class:
            return self.py_class
            
        obj = PyType(self.name, root=top)
        try:
            if len(self.parts) == 1:
                part = self.parts[0]
                if isinstance(part, Restriction):
                    if part.parts:
                        if isinstance(part.parts[0], Enumeration):
                            lista = [p.value for p in part.parts]
                            obj.value_type = {"base":part.base,
                                                "enumeration":lista}
                        elif isinstance(part.parts[0], MaxLength):
                            obj.value_type = {"base":part.base,
                                                "maxlen":part.parts[0].value}
                        elif isinstance(part.parts[0], Length):
                            obj.value_type = {"base":part.base,
                                                "len":part.parts[0].value}
                    else:
                        obj.value_type = {"base":part.base}
                elif isinstance(part, List):
                    if part.itemType:
                        obj.value_type = {"base":"list", "member":part.itemType}
        except ValueError:
            pass
        
        self.py_class = obj
        return obj
        

class Sequence(Complex):
    def collect(self, top, sup, argv=None, parent=""):
        argv_copy = sd_copy(argv)
        for key, val in self.__dict__.items():
            if key not in ['xmlns_map'] and not key.startswith("_"):
                argv_copy[key] = val
    
        if DEBUG:
            print("#Sequence: %s" % argv)
        return Complex.collect(self, top, sup, argv_copy, parent)


class SimpleContent(Complex):
    pass


class ComplexContent(Complex):
    pass


class Key(Complex):
    pass


class Redefine(Complex):
    pass


class Extension(Complex):
    def collect(self, top, sup, argv=None, parent=""):
        if self._own or self._inherited:
            return self._own, self._inherited
        
        if DEBUG:
            print("#!!!", self.__dict__)

        try:
            base = self.base
            (namespace, tag) = _namespace_and_tag(self, base, top)
                    
            if self.xmlns_map[namespace] == top.target_namespace:
                cti = get_type_def(tag, top.parts)
                if not cti.py_class:
                    cti.repr(top, sup)
                #print("#EXT..",ct._collection)
                self._inherited = cti.py_class.properties[0][:]
                self._inherited.extend(cti.py_class.properties[1])
            elif self.xmlns_map[namespace] == XMLSCHEMA: 
                base = tag
            else:
                iattr = _import_attrs(top.modul[namespace], tag, top)
                #print("#EXT..-", ia)
                self._inherited = iattr
        except (AttributeError, ValueError):
            base = None

        self._extend(top, sup, argv, parent, base)

        return self._own, self._inherited

class Choice(Complex):
    def collect(self, top, sup, argv=None, parent=""):
        argv_copy = sd_copy(argv)
        for key, val in self.__dict__.items():
            if key not in ['xmlns_map'] and not key.startswith("_"):
                argv_copy[key] = val

        # A choice means each element may not be part of the choice
        argv_copy["minOccurs"] = 0
            
        if DEBUG:
            print("#Choice: %s" % argv)
        return Complex.collect(self, top, sup, argv_copy, parent=parent)

class Restriction(Complex):
    pass
    # if isinstance(self.parts[0], Enumeration):
    #     values = [enum.value for enum in self.parts]

class ComplexType(Complex):
    def repr(self, top=None, sup=None, _argv=None, _child=True, parent=""):
        if self.py_class:
            return self.py_class
                    
        # looking for a pattern here
        significant_parts = self.significant_parts()
        value_type = ""
        if len(significant_parts) == 1:
            if isinstance(significant_parts[0], ComplexContent) or \
                isinstance(significant_parts[0], SimpleContent):
                cci = significant_parts[0]
                if len(cci.parts) == 1:
                    if isinstance(cci.parts[0], Extension):
                        ext = cci.parts[0]

                        (namespace, name) = _namespace_and_tag(ext, ext.base, 
                                                                top)

                        if ext.xmlns_map[namespace] == top.target_namespace:
                            new_sup = name
                            cti = get_type_def(new_sup, top.parts)
                            if cti and not cti.py_class:
                                cti.repr(top, sup)
                        elif ext.xmlns_map[namespace] == XMLSCHEMA:
                            new_sup = None
                            value_type = name
                        else:
                            new_sup = "%s.%s" % (namespace, name)
                            
                        #print("#Superior: %s" % new_sup)
                        if new_sup:
                            sup = new_sup
            else:
                #print("#>>", self.parts[0].__class__)
                pass
                
        try:
            self.py_class = PyType(self.name, superior=sup, 
                                    namespace=top.target_namespace, root=top)
        except AttributeError: # No name 
            self.py_class = PyType("", superior=sup, 
                                    namespace=top.target_namespace, root=top)

        try:
            self.py_class.abstract = self.abstract
        except AttributeError:
            pass
        
        if value_type:
            self.py_class.value_type = {"base": value_type}
            
        try:
            if not parent:
                try:
                    parent = self.name
                except AttributeError:
                    parent = ""
            
            self.py_class.properties = self.collect(top, sup, parent=parent)
        except ValueError:
            pass
            
        return self.py_class 
        
class Annotation(Complex):
    pass

class All(Complex):
    pass

class Group(Complex):
    def collect(self, top, sup, argv=None, parent=""):
        """ means this element is part of a larger object, hence a property of 
        that object """
        
        try:
            #objekt = PyGroup("", root=top)
            (namespace, tag) = _namespace_and_tag(self, self.ref, top)
    
            try:
                if self.xmlns_map[namespace] == top.target_namespace:
                    cti = get_type_def(tag, top.parts)
                    try:
                        return cti.py_class.properties
                    except ValueError:
                        return cti.collect(top, sup) 
                else:
                    raise Exception(
                        "Reference to group in other XSD file, not supported")
            except KeyError:
                raise Exception("Missing namespace definition")            
        except AttributeError as exc:
            print("#!!!!", exc)
            return [], []

    def repr(self, top=None, sup=None, argv=None, _child=True, parent=""):
        if self.py_class:
            return self.py_class

        self.py_class = objekt = PyGroup(self.name, root=top)

        min_max(self, objekt, argv)
        
        try:
            self._extend(top, sup, argv)
            objekt.properties = (self._own, self._inherited)
        except ValueError:
            pass
            
        return objekt

class Unique(Complex):
    pass

class Selector(Complex):
    pass

class Field(Complex):
    pass

class AttributeGroup(Complex):
    def collect(self, top, sup, argv=None, parent=""):
        try:
            (_namespace, typ) = _namespace_and_tag(self, self.ref, top)
            # TODO: use definitions in other XSD
            cti = get_type_def(typ, top.parts)
            return cti.collect(top, sup)
        except AttributeError:
            if self._own or self._inherited:
                return self._own, self._inherited
            
            argv_copy = sd_copy(argv)
            
            for prop in self.parts:
                if isinstance(prop, Attribute):
                    self._own.append(prop.repr(top, sup, argv_copy, parent))

            return self._own, self._inherited

    def repr(self, top=None, sup=None, _argv=None, _child=True, parent=""):
        if self.py_class:
            return self.py_class
            
        self.py_class = PyAttributeGroup(self.name, root=top)

        try:
            self.py_class.properties = self.collect(top, sup)
        except ValueError:
            pass
            
        return self.py_class 

def pyify_0(name):
    res = ""
    match = re.match(
            r"^(([A-Z])[a-z]+)(([A-Z])[a-z]+)?(([A-Z])[a-z]+)?(([A-Z])[a-z]+)?",
            name)
    res += match.group(1).lower()
    for num in range(3, len(match.groups()), 2):
        try:
            res += "_"+match.group(num+1).lower()+match.group(num)[1:]
        except AttributeError:
            break
    
    res = res.replace("-","_")
    if res in ["class"]:
        res += "_"
    return res


def pyify(name):
    # AssertionIDRef
    res = []
    
    upc = []
    pre = ""
    for char in name:
        if "A" <= char <= "Z":
            upc.append(char)
        elif char == "-":
            upc.append("_")
        else:
            if upc:
                if len(upc) == 1:
                    res.append(pre+upc[0].lower())
                else:
                    if pre:
                        res.append(pre)
                    for uch in upc[:-1]:
                        res.append(uch.lower())
                    res.append("_"+upc[-1].lower())
                        
                upc = []
            res.append(char)
            pre = "_"
    if upc:
        if len(upc) == len(name):
            return name.lower()
        else:
            res.append("_"+("".join(upc).lower()))
        
    return "".join(res)


def get_type_def( typ, defs):
    for cdef in defs:
        try:
            if cdef.name == typ:
                return cdef
        except AttributeError:
            pass
    return None
    

def sort_elements(els):
    res = []
    
    diff = False
    for key, val in els.items():
        if not val:
            res.append(key)
            del els[key]
            diff = True
    
    res.sort()
    while diff:
        diff = False
        for key, val in els.items():
            pres = [v for v in val if v not in res and ':' not in v]
            els[key] = pres
            if pres != val:
                diff = True

        #print(els)
        partres = []
        for key, val in els.items():
            if not val:
                partres.append(key)
                del els[key]
                diff = True
        partres.sort()
        res.extend(partres)
        
    return res, els


def output(elem, target_namespace, eldict, ignore=None):
    done = 0

    if ignore is None:
        ignore = []
        
    try:
        (preps, text) = elem.text(target_namespace, eldict, False, ignore)
    except TypeError:
        return done
    except MissingPrerequisite:
        return done
    
    for prep in preps:
        if prep:
            done = 1
            if isinstance(prep, six.string_types):
                print(prep)
            else:
                for item in prep:
                    print(item)
                    print()
            print()

    if text:
        done = 1
        elem.done = True
        print(text)
        print()
    
    return done
    

def intro():
    print("""#!/usr/bin/env python

#
# Generated %s by parse_xsd.py version %s.
#

import saml2
from saml2 import SamlBase
""" % (time.ctime(), __version__))

#NAMESPACE = 'http://www.w3.org/2000/09/xmldsig#'
    

def block_items(objekt, block, eldict):
    if objekt not in block:
        if isinstance(objekt.type, PyType):
            if objekt.type not in block:
                block.append(objekt.type)
        block.append(objekt)
        if isinstance(objekt, PyType):
            others = [p for p in eldict.values() if isinstance(p, 
                                    PyElement) and p.type[1] == objekt.name]
            for item in others:
                if item not in block:
                    block.append(item)
    return block

    
def find_parent(elm, eldict):
    if isinstance(elm, PyElement):
        if elm.type:
            sup = eldict[elm.type[1]]
            return find_parent(sup, eldict)
        elif elm.ref:
            sup = eldict[elm.ref]
            if sup.name == elm.name:
                return elm
            return find_parent(sup, eldict)
    else:
        if elm.superior:
            sup = eldict[elm.superior[0]]
            if sup.done:
                return elm
            return find_parent(sup, eldict)
    
    return elm
    

class Schema(Complex):

    def __init__(self, elem, impo, add, modul, defs):
        Complex.__init__(self, elem)
        self.impo = impo
        self.add = add
        self.modul = modul
        self.py_elements = {}
        self.py_attributes = {}
        self.elems = []
        self.attrgrp = []
        self.defs = []
        try:
            self.target_namespace = self.targetNamespace
        except AttributeError:
            self.target_namespace = ""
        for def_file in defs:
            self.defs.append(open(def_file).read())

    def _mk_list(self, objekt, alla, eldict):
        tup = []
        for prop in alla:
            (mod, cname) = _mod_cname(prop, eldict)

            if prop.max == "unbounded":
                lista = True
            else:
                lista = False

            spec = objekt.child_spec(self.target_namespace, 
                                        prop, mod, cname, 
                                        lista)
            lines = ["%s.%s" % (objekt.class_name, spec)]
            tup.append((prop, lines, spec))
        
        return tup
        
    def adjust(self, eldict, block):
        udict = {}
        for elem in self.elems:
            if isinstance(elem, PyAttribute) or isinstance(elem, PyGroup):
                elem.done = True
                continue
            if elem in block:
                continue
            if not elem.done:
                udict[elem] = elem.undefined(eldict)

        keys = [k.name for k in udict.keys()]
        print("#", keys)
        res = (None, [])
        if not udict:
            return res
        level = 1
        rblocked = [p.name for p in block]
        while True:
            non_child = 0
            for objekt, (sup, elems) in udict.items():
                if sup:
                    continue
                else:
                    non_child += 1
                    signif = []
                    other = []
                    for elem in elems:
                        if elem.name in keys:
                            signif.append(elem)
                        elif elem.ref in rblocked:
                            other.append(elem)
                    if len(signif) <= level:
                        alla = signif
                        alla.extend(other)
                        tup = self._mk_list(objekt, alla, eldict)
                        res = (objekt, tup)
                        break
            if res[0]:
                ref = res[0].name
                tups = res[1]
                for objekt, (sups, elems) in udict.items():
                    if sups:
                        for sup in sups:
                            if sup.name == ref:
                                for tup in tups:
                                    tup[1].append("%s.%s" % (objekt.class_name,
                                                            tup[2]))
                                break
                    else:
                        pass
            elif not non_child or level > 10:
                elm = udict.keys()[0]
                parent = find_parent(elm, eldict)
                signif = []
                other = []
                tot = parent.properties[0]
                tot.extend(parent.properties[1])
                alla = []
                for elem in tot:
                    if isinstance(elem, PyAttribute):
                        continue
                    else:
                        alla.append(elem)
                tup = self._mk_list(parent, alla, eldict)
                res = (parent, tup)
                
            if res[0]:
                break
            else:
                level += 1
        return res

    def _do(self, eldict):
        not_done = 1
        undone = 0
        while not_done:
            not_done = 0
            undone = 0
            for elem in self.elems:
                if isinstance(elem, PyGroup) or elem.done:
                    continue
                undone += 1
                not_done += output(elem, self.target_namespace, eldict)
        return undone
        
    def _element_from_string(self):
        print("ELEMENT_FROM_STRING = {")
        for elem in self.elems:
            if isinstance(elem, PyAttribute) or isinstance(elem, PyGroup):
                continue
            if elem.abstract:
                continue
            print("%s%s.c_tag: %s_from_string," % (INDENT, elem.class_name, 
                                                   pyify(elem.class_name)))
        print("}")
        print()
        
    def _element_by_tag(self):
        print("ELEMENT_BY_TAG = {")
        listed = []
        for elem in self.elems:
            if isinstance(elem, PyAttribute) or isinstance(elem, PyGroup):
                continue
            if elem.abstract:
                continue
            lcen = elem.name
            print("%s'%s': %s," % (INDENT, lcen, elem.class_name))
            listed.append(lcen)
        for elem in self.elems:
            if isinstance(elem, PyAttribute) or isinstance(elem, PyGroup):
                continue
            lcen = elem.name
            if elem.abstract and lcen not in listed:
                print("%s'%s': %s," % (INDENT, lcen, elem.class_name))
                listed.append(lcen)
        print("}")
        print
        
    def out(self):
        for part in self.parts:
            if isinstance(part, Import):
                continue
            if part is None:
                continue
                
            elem = part.repr(self, "", {}, False)
            if elem:
                if isinstance(elem, PyAttributeGroup):
                    self.attrgrp.append(elem)
                else:
                    self.elems.append(elem)
        
        eldict = {}
        for elem in self.elems:
            eldict[elem.name] = elem

        #print(eldict.keys())
        
        intro()
        for modul in self.add:
            print("from %s import *" % modul)
        for _namespace, (mod, namn) in self.impo.items():
            if namn:
                print("import %s as %s" % (mod, namn))
        print(       )
        print("NAMESPACE = '%s'" % self.target_namespace)
        print

        for defs in self.defs:
            print(defs)
            print
        
        exceptions = []
        block = []
        while self._do(eldict):
            print("#..................")
            (objekt, tups) = self.adjust(eldict, block)
            if not objekt:
                break
            ignore = [p.name for (p, _l, _s) in tups]
            done = output(objekt, self.target_namespace, eldict, ignore)
            if done:
                for (prop, lines, _) in tups:
                    exceptions.extend(lines)
                block = []
            else:
                block = block_items(objekt, block, eldict)

        if exceptions:
            print("#", 70*'+')
            for line in exceptions:
                print(line)
            print("#", 70*'+')
            print
        
        for attrgrp in self.attrgrp:
            print("AG_%s = [" % attrgrp.name)
            for prop in attrgrp.properties[0]:
                if isinstance(prop.type, PyObj):
                    print("%s('%s', %s_, %s)," % (INDENT, prop.name,
                                                  prop.type.name,
                                                  prop.required))
                else:
                    print("%s('%s', '%s', %s)," % (INDENT, prop.name,
                                                   prop.type, prop.required))
            print("]")
            print()
           
        self._element_from_string() 
        self._element_by_tag()
        print
        print("def factory(tag, **kwargs):")
        print("    return ELEMENT_BY_TAG[tag](**kwargs)")
        print
        
        
# -----------------------------------------------------------------------------


NAMESPACE_BASE = ["http://www.w3.org/2001/XMLSchema",
    "http://www.w3.org/2000/10/XMLSchema"]

_MAP = {    
    "element": Element,
    "complexType": ComplexType,
    "sequence": Sequence,
    "any": Any,
    "all": All,
    "anyAttribute": AnyAttribute,
    "simpleContent": SimpleContent,
    "extension": Extension,
    "union": Union,
    "restriction": Restriction,
    "enumeration": Enumeration,
    "import": Import,
    "annotation": Annotation,
    "attributeGroup":AttributeGroup,
    "attribute":Attribute,
    "choice": Choice,
    "complexContent": ComplexContent,
    "documentation": Documentation,
    "simpleType": SimpleType,
    "maxLength": MaxLength,
    "list": List,
    "unique": Unique,
    "group": Group,
    "selector": Selector,
    "field": Field,
    "key": Key,
    "include": Include,
    "redefine": Redefine
    }
    
ELEMENTFUNCTION = {}

for nsp in NAMESPACE_BASE:
    for nskey, func in _MAP.items():
        ELEMENTFUNCTION["{%s}%s" % (nsp, nskey)] = func

    
def evaluate(typ, elem):
    try:
        return ELEMENTFUNCTION[typ](elem)
    except KeyError:
        print("Unknown type", typ)
        
    
NS_MAP = "xmlns_map"

def parse_nsmap(fil):
    events = "start", "start-ns", "end-ns"

    root = None
    ns_map = []

    for event, elem in ElementTree.iterparse(fil, events):
        if event == "start-ns":
            ns_map.append(elem)
        elif event == "end-ns":
            ns_map.pop()
        elif event == "start":
            if root is None:
                root = elem
            elem.set(NS_MAP, dict(ns_map))

    return ElementTree.ElementTree(root)

def usage():
    print("Usage: parse_xsd [-i <module:as>] xsd.file > module.py")
    
def recursive_find_module(name, path=None):
    parts = name.split(".")

    mod_a = None
    for part in parts:
        #print("$$", part, path)
        try:
            (fil, pathname, desc) = imp.find_module(part, path)
        except ImportError:
            raise 

        mod_a = imp.load_module(name, fil, pathname, desc)
        sys.modules[name] = mod_a
        path = mod_a.__path__

    return mod_a

def get_mod(name, path=None):
    try:
        mod_a = sys.modules[name]
        if not isinstance(mod_a, types.ModuleType):
            raise KeyError
    except KeyError:
        try:
            (fil, pathname, desc) = imp.find_module(name, path)
            mod_a = imp.load_module(name, fil, pathname, desc)
        except ImportError:
            if "." in name:
                mod_a = recursive_find_module(name, path)
            else:
                raise
        sys.modules[name] = mod_a
    return mod_a


def recursive_add_xmlns_map(_sch, base):
    for _part in _sch.parts:
        _part.xmlns_map.update(base.xmlns_map)
        if isinstance(_part, Complex):
            recursive_add_xmlns_map(_part, base)

def find_and_replace(base, mods):
    base.xmlns_map = mods.xmlns_map
    recursive_add_xmlns_map(base, mods)
    rm = []
    for part in mods.parts:
        try:
            _name = part.name
        except AttributeError:
            continue
        for _part in base.parts:
            try:
                if _name == _part.name:
                    rm.append(_part)
            except AttributeError:
                continue
    for part in rm:
        base.parts.remove(part)
    base.parts.extend(mods.parts)
    return base

def read_schema(doc, add, defs, impo, modul, ignore, sdir):
    for path in sdir:
        fil = "%s%s" % (path, doc)
        try:
            fp = open(fil)
            fp.close()
            break
        except IOError as e:
            if e.errno == errno.EACCES:
                continue
    else:
        raise Exception("Could not find schema file")

    tree = parse_nsmap(fil)

    known = NAMESPACE_BASE[:]
    known.append(XML_NAMESPACE)
    for key, namespace in tree._root.attrib["xmlns_map"].items():
        if namespace in known:
            continue
        else:
            try:
                modul[key] = modul[namespace]
                impo[namespace][1] = key
            except KeyError:
                if namespace == tree._root.attrib["targetNamespace"]:
                    continue
                elif namespace in ignore:
                    continue
                else:
                    raise Exception("Undefined namespace: %s" % namespace)

    _schema =  Schema(tree._root, impo, add, modul, defs)
    _included_parts = []
    _remove_parts = []
    _replace = []
    for part in _schema.parts:
        if isinstance(part, Include):
            _sch = read_schema(part.schemaLocation, add, defs, impo, modul,
                               ignore, sdir)
            # Add namespace information
            recursive_add_xmlns_map(_sch, _schema)
            _included_parts.extend(_sch.parts)
            _remove_parts.append(part)
        elif isinstance(part, Redefine):
            # This is the schema that is going to be redefined
            _redef = read_schema(part.schemaLocation, add, defs, impo, modul,
                                 ignore, sdir)
            # so find and replace
            # Use the schema to be redefined as starting point
            _replacement = find_and_replace(_redef, part)
            _replace.append((part, _replacement.parts))

    for part in _remove_parts:
        _schema.parts.remove(part)
    _schema.parts.extend(_included_parts)
    if _replace:
        for vad, med in _replace:
            _schema.parts.remove(vad)
            _schema.parts.extend(med)
    return _schema

def main(argv):
    try:
        opts, args = getopt.getopt(argv, "a:d:hi:I:s:",
                                    ["add=", "help", "import=", "defs="])
    except getopt.GetoptError as err:
        # print help information and exit:
        print(str(err)) # will print something like "option -a not recognized"
        usage()
        sys.exit(2)

    add = []
    defs = []
    impo = {}
    modul = {}
    ignore = []
    sdir = ["./"]

    for opt, arg in opts:
        if opt in ("-a", "--add"):
            add.append(arg)
        elif opt in ("-d", "--defs"):
            defs.append(arg)
        elif opt in ("-h", "--help"):
            usage()
            sys.exit()
        elif opt in ("-s", "--schemadir"):
            sdir.append(arg)
        elif opt in ("-i", "--import"):
            mod = get_mod(arg, ['.'])
            modul[mod.NAMESPACE] = mod
            impo[mod.NAMESPACE] = [arg, None]
        elif opt in ("-I", "--ignore"):
            ignore.append(arg)
        else:
            assert False, "unhandled option"

    if not args:
        print("No XSD-file specified")
        usage()
        sys.exit(2)

    schema = read_schema(args[0], add, defs, impo, modul, ignore, sdir)
    #print(schema.__dict__)
    schema.out()

if __name__ == "__main__":    
    main(sys.argv[1:])
