#._cv_part guppy.heapy.Doc

class Doc: # base class
    def __mod__(self, other):
	other = self.mod.getdoc(other)
	return self.mapchildren(lambda x: x % other)

    def __rmod__(self, other):
	return self.mod.getdoc(other) % self

    def __str__(self):
	return self.getstr()

    def __eq__(self, other):
	if not isinstance(other, self.__class__):
	    return 0

	return str(self) == str(other)

    def __hash__(self):
	return hash(str(self))

    def shortest(self):
	return self.mapchildren(lambda x: x.shortest())

class Anon(Doc):
    def __init__(self, mod, obj):
	self.mod = mod
	self.obj = obj

    def getstr(self):
	return repr(self.obj)

    def mapchildren(self, f):
	return self

class Source(Doc):
    def __init__(self, mod, text):
	self.mod = mod
	self.text = text

    def getstr(self):
	return self.text

    def mapchildren(self, f):
	return self

class Attribute(Doc):
    def __init__(self, mod, obj, name):
	self.mod = mod
	self.obj = obj
	self.name = name

    def __mod__(self, other):
	if self.obj is other:
	    return self.mod.rootattribute(other, self.name)
	return self.mapchildren(lambda x: x % other)

    def getstr(self):
	return '%s.%s'%(self.obj.getstr(), self.name)

    def mapchildren(self, f):
	return self.__class__(self.mod, f(self.obj), self.name)

class RootAttribute(Doc):
    def __init__(self, mod, obj, name):
	self.mod = mod
	self.obj = obj
	self.name = name

    def getstr(self):
	return '%s'%(self.name,)

    def mapchildren(self, f):
	return self

class BinaryOp(Doc):
    table = {
	'and':'&',
	'or':'|',
	'sub':'-',
	'mul':'*',
	'pow':'**',
	'lshift':'<<',
	'rshift':'>>',
	}
    def __init__(self, mod, op, a, b):
	self.mod = mod
	self.op = op
	self.a = a
	self.b = b

    def getstr(self):
	return '%s %s %s'%(self.a.getstr(),
			   self.table[self.op],
			   self.b.getstr())
			   
    def mapchildren(self, f):
	return self.__class__(self.mod, self.op, f(self.a), f(self.b))


class UnaryOp(Doc):
    table = {
	'invert': '~',
	'neg' : '-',
	'pos' : '+',
	}
    def __init__(self, mod, op, a):
	self.mod = mod
	self.op = op
	self.a = a

    def getstr(self):
	return '%s %s'%(self.table[self.op], self.a.getstr())

    def mapchildren(self, f):
	return self.__class__(self.mod, self.op, f(self.a))

class CallFunc(Doc):
    def __init__(self, mod, obj, *args, **kwds):
	self.mod = mod
	self.obj = obj
	self.args = args
	self.kwds = kwds

    def getstr(self):
	return '%s(%s%s)'%(
	    self.obj.getstr(),
	    ', '.join([x.getstr() for x in self.args]),
	    ', '.join(['%s=%s'%(k,v.getstr()) for k, v in self.kwds.items()]))

    def mapchildren(self, f):
	obj = f(self.obj)
	args = [f(a) for a in self.args]
	kwds = dict([(k, f(v)) for (k, v) in self.kwds.items()])
	return self.__class__(self.mod, obj, *args, **kwds)
		     

class Multi(Doc):
    def __init__(self, mod, set):
	self.mod = mod
	self.str = '{%s}'%', '.join([x.getstr() for x in set])
	self.set = set
    
    def getstr(self):
	return self.str

    def mapchildren(self, f):
	return self.__class__(self.mod, dict([(f(x), 1) for x in self.set]))

    def shortest(self):
	ls = None
	for a in self.set:
	    a = a.shortest()
	    l = len(a.getstr())
	    if ls is None or l < ls:
		ls = l
		st = a
	return st


class Root(Doc):
    def __init__(self, mod, name='<root>'):
	self.mod = mod
	self.name = name

    def __call__(self, name):
	return self.__class__(self.mod, name)

    def mapchildren(self, f):
	return self

    def getstr(self):
	return self.name

class Tuple(Doc):
    def __init__(self, mod, *args):
	self.mod = mod
	self.args = args
	#pdb.set_trace()

    def mapchildren(self, f):
	return self.__class__(self.mod, *[f(x) for x in self.args])

    def getstr(self):
	x = '(%s)'%', '.join([x.getstr() for x in self.args])
	if len(self.args) == 1:
	    x = x[:-1]+',)'
	return x

class DocError(Exception):
    pass

class _GLUECLAMP_:
    
    def add_origin(self, obj, origin):
	o = getattr(obj, '_origin_', None)
	if o is None:
	    obj._origin_ = origin
	else:
	    obj._origin_ = self.multi(o, origin)
	return obj

    def add_wrapdict(self, obj, doc):
	wd = self.wrapdict
	o = wd.get(id(obj))
	if o is None:
	    o = (obj, doc)
	else:
	    o = (obj, self.multi(o[1], doc))
	wd[id(obj)] = o
	return obj

    def anon(self, obj):
	return Anon(self, obj)

    def attribute(self, obj, name):
	return Attribute(self, self.getdoc(obj), name)
	
    def binop(self, op, a, b):
	return BinaryOp(self, op, self.getdoc(a), self.getdoc(b))

    def callfunc(self, obj, *args, **kwds):
	getdoc = self.getdoc
	obj = getdoc(obj)
	args = [getdoc(a) for a in args]
	kwds = dict([(k, getdoc(v)) for (k, v) in kwds.items()])
	return CallFunc(self, obj, *args, **kwds)

    def getdoc(self, obj):
	if isinstance(obj, Doc):
	    return obj
	w = getattr(obj, '_origin_', None)
	if isinstance(w, Doc):
	    return w
	w = self.wrapdict.get(id(obj))
	if w is not None:
	    return w[1]
	if isinstance(obj, tuple):
	    return self.tuple(*obj)
	return self.anon(obj)

    def multi(self, a, b):
	a = self.getdoc(a)
	b = self.getdoc(b)
	if isinstance(a, Multi):
	    #pdb.set_trace()
	    set = a.set.copy()
	    if 1 and len(set) > 4:
		return a
	else:
	    set = {a:1}
	if isinstance(b, Multi):
	    set.update(b.set)
	else:
	    set[b] = 1
	return Multi(self, set)

    def _get_root(self):
	return Root(self)

    def rootattribute(self, root, name):
	return RootAttribute(self, self.getdoc(root), name)

    def source(self, text):
	return Source(self, text)

    def tuple(self, *args):
	return Tuple(self, *[self.getdoc(x) for x in args])

    def unop(self, op, a):
	return UnaryOp(self, op, self.getdoc(a))

    def wrap(self, obj, doc):
	if obj is self._parent.UniSet.UniSet:
	    pdb.set_trace()
	w = getattr(obj, '_derive_origin_', None)
	if w is not None:
	    if getattr(w, 'im_self', None) is obj or isinstance(w, self._root.types.FunctionType):
		obj = w(doc)
	    elif w == 'ADD':
		#pdb.set_trace()
		obj = self.add_origin(obj, doc)
	    else:
		raise DocError, "Doc.wrap:  attribute '_derive_origin_' has invalid value"
	elif isinstance(obj, self._root.types.MethodType):
	    obj = self.wrap_method(obj, doc)
	elif isinstance(obj, self._root.types.FunctionType):
	    obj = self.wrap_function(obj, doc)
	else:
	    obj = self.add_wrapdict(obj, doc)
	return obj
	
    def _get_wrapdict(self):
	return {}

    def wrap_function(mod, obj, doc):
	def f(*args, **kwds):
	    r = obj(*args, **kwds)
	    r = mod.wrap(r, mod.callfunc(doc, *args, **kwds))
	    return r
	f._origin_ = doc
	return f

    def wrap_method(mod, obj, doc):
	im_func = obj.im_func
	def f(self, *args, **kwds):
	    r = im_func(self, *args, **kwds)
	    r = mod.wrap(r, mod.callfunc(doc, *args, **kwds))
	    return r
	return mod._root.new.instancemethod(f, obj.im_self, obj.im_self.__class__)
