#._cv_part guppy.heapy.Spec

"""
Contains some experimental set constructions.
In the current state, not to be used by the faint-hearted.
It is likely due for some major refactoring and has probably
many bugs, it was a long time since I run the tests.
You don't get any other documentation than this right now.

"""


DEBUG=1

def briefstr(x):
    try:
	return getattr(x, 'brief')
    except AttributeError:
	if isinstance(x, tuple):
	    return '(%s)'%(','.join([briefstr(xi) for xi in x]))
	return str(x)


class SpecFamily:
    def __init__(self, unisetmod, specmod):
	self.specmod = specmod
	self.defrefining(unisetmod.Anything)
	self.disjoints -= [self]

    def __call__(self, arg):
	return self.Set(self, arg)

    def c_and(self, a, b):
	if isinstance(b, SpecFamily):
	    return self.mod.fam_And._cons((a, b))
	else:
	    return b.fam._and_ATOM(b, a)
	    

    def _and_ID(self, a, b):
	env = self.specmod._static_test_env
	res = self.mod.mutnodeset()
	for bi in b.nodes:
	    try:
		env.test_contains(a, bi, 'select contains')
	    except : #TestError
		pass
	    else:
		res.add(bi)
	return self.mod.fam_Identity._cons(self.mod.immnodeset(res))


    def c_contains(self, a, b):
	env = self.specmod._static_test_env
	try:
	    return env.test_contains(a, b, 'Spec contains')
	except TestError:
	    return False

    def c_getlimstr(self, a, max_len):
	x = a.brief
	if len(x) > max_len:
	    x = x[:max_len-3]+'...'
	return x

    def c_get_brief(self, a):
	return '<%s(%s)>'%(self.__class__.__name__, briefstr(a.arg))

    if 0:

	def c_select(self, a, b):
	    env = self.specmod._static_test_env
	    res = self.mod.mutnodeset()
	    for bi in b:
		try:
		    env.test_contains(a, bi, 'select contains')
		except TestError:
		    pass
		else:
		    res.add(bi)
	    return self.mod.fam_Identity._cons(self.mod.immnodeset(res))

class ArgNamesFamily(SpecFamily):
    def __call__(self, *args):
	return self.Set(self, args)

    def getargnames(self, code):
	inspect = self.specmod._root.inspect
	(args, varargs, varkw) = inspect.getargs(code)
	if varargs is not None:
	    args.append('*%s'%varargs)
	if varkw is not None:
	    args.append('**%s'%varkw)
	return tuple(args)

    def func_argnames(self, f, args):
	try:
	    code = f.func_code
	    return self.getargnames(code) == args
	except AttributeError:
	    return False

    def meth_argnames(self, m, args):
	try:
	    f = m.im_func
	    code = f.func_code
	    return self.getargnames(code)[1:] == args
	except AttributeError:
	    return False

    def c_contains(self, a, x):
	func_argnames = lambda f:self.func_argnames(f, a.arg)
	meth_argnames = lambda m:self.meth_argnames(m, a.arg)
	types = self.mod._root.types
	return (func_argnames(x) or
		meth_argnames(x) or
		(isinstance(x, types.InstanceType) and
		 hasattr(x, '__call__') and
		 meth_argnames(x.__call__)) or
		(isinstance(x, types.ClassType) and
		 (hasattr(x, '__init__') and
		  meth_argnames(x.__init__))) or
		(isinstance(x, types.TypeType) and
		 (hasattr(x, '__init__') and
		  meth_argnames(x.__init__))) or
		 (hasattr(x, '__call__') and
		  meth_argnames(x.__call__))
		)

class AttributeFamily(SpecFamily):
    def __call__(self, name, type=None):
	if type is None:
	    type = self.specmod.any
	else:
	    if not isinstance(type, self.mod.UniSet):
		type = self.c_from(type)
	return self.specotup((name, type))
	
    def c_test_contains(self, a, b, env):
	name, type = a.arg
	x = env.gengetattr(b, name)
	return type.test_contains(x, env)

    def c_get_brieflimstr(self, a):
	x = '<AttributeFamily(%r%%s>'%(a.arg[0],)
	if a.arg[1] is not None:
	    x = x%(','+a.arg[1].brief)
	else:
	    x = x%''
	return x

class AdaptupleFamily(SpecFamily):
    def __init__(self, *a, **k):
	SpecFamily.__init__(self, *a, **k)
	self.add_export('new', lambda x:x.arg[0])

    def __call__(self, func, type):
	func, doc = self.specmod._exodoc(func)
	type = self.specmod.setcast(type)
	return self.specoargtup((func, type), (doc, type))
	
    def c_test_contains(self, a, b, env):
	func, type = a.arg
	if isinstance(b, tuple):
	    try:
		x = func(*b)
	    except:
		return env.failed_exc_info('calling func failed')
	else:
	    x = b
	return type.test_contains(x, env)


class CartesianProductFamily(SpecFamily):
    def __call__(self, *types):
	return self.Set(self, types)

    def c_domain(self, a):
	types = a.arg
	if len(types) == 2:
	    return types[0]
	raise TypeError, 'Domain is defined on binary relations only'

    def c_get_examples(self, a, env):
	# We have to check length before calling iterpermute - 
	# to give a reasonable error message examples are missing from some set.
	exs = []
	for i, ai in enumerate(a.arg):
	    ex = list(env.get_examples(ai))
	    if not ex: #???
		if not env.failed_coverage('cartesian product', ai, None, 'the argument #%d'%i):
		    return []
	    exs.append(ex)
		      
	return self.mod._root.guppy.etc.iterpermute(*exs)

    def c_len(self, a):
	l = 1
	for ai in a.arg:
	    l = l * len(ai.arg)
	return l

    def c_test_contains(self, a, b, env):
	types = a.arg
	bs = tuple(b)
	if len(types) != len(bs):
	    env.failed('cprod of length %d: argument has length %d'%(len(types), len(bs)))
	else:
	    for t, b in zip(types, bs):
		if not t.test_contains(b, env):
		    return False
	    return True


class SequenceFamily(SpecFamily):
    def __call__(self, type):
	return self.specoarg(type)

    def c_test_contains(self, a, b, env):
	for x in b:
	    if not a.arg.test_contains(x, env):
		return False
	return True

    def c_get_examples(self, a, env):
	for i in range(env.max_sequence_examples_length):
	    for x in env.get_examples(self.specmod.cprod(*[a.arg]*i)):
		yield x
				      


class MappingFamily(SpecFamily):
    def __init__(self, *a, **k):
	SpecFamily.__init__(self, *a, **k)
	self.add_export('arrow', lambda x:lambda f:self.c_arrow(x, f))

    def c_arrow(self, a, f):
	tf, ts, ret = a.arg
	return Arrow(ts, ret, f)

    def __call__(self, *args):
	ts = []
	as_ = []
	ret = None
	i = 0
	setcast = self.specmod.setcast
	while i < len(args):
	    ai = args[i]
	    if isinstance(ai, str):
		if ai == '->':
		    i += 1
		    if not i == len(args)-1:
			raise SyntaxError, \
			      "The '->' specifier must be next to last in the argument list"
		    ret = setcast(args[i])
		elif ai.endswith('='):
		    i += 1
		    t = setcast(args[i])
		    as_.append('%s=%args[%d]'%(ai[:-1], len(ts)))
		    ts.append(t)
		elif ai == '*':
		    i += 1
		    t = setcast(args[i])
		    as_.append('*args[%d]'%len(ts))
		    ts.append(self.specmod.sequence(t))
		else:
		    raise SyntaxError, \
			  "Invalid argument specifier: %r"%ai
				     
	    else:
		as_.append('args[%d]'%len(ts))
		ts.append(setcast(ai))
	    i += 1
		
	fn = 'lambda f: lambda *args: f('+','.join(as_)+')'
	f = eval(fn)
	ts = self.specmod.cprod(*ts)
	if ret is None:
	    ret = self.specmod.Anything
	return self.Set(self, (f, ts, ret))

    def c_test_contains(self, a, func, env):
	f, ts, ret = a.arg
	
	f = f(func)
	def g(env, args):
	    try:
		r = f(*args)
	    except: # TypeError, ValueError, AttributeError ... - what not
		raise
		#env.failed('Call exception')
	    else:
		if ret is not None:
		    return env.test_contains(ret, r, "Mapping Return Type")
		else:
		    return True
		
	return env.forall(ts, g)

    def c_get_examples(self, a, env):
	f, ts, ret = a.arg

	return [lambda *args, **kwds: x for x in env.get_examples(ret)]


class PredicateFamily(SpecFamily):
    def __call__(self, arg, doc):
	return self.Set(self, (arg, doc))
	
    def c_test_contains(self, a, b, env):
	pred, doc = a.arg
	if not pred(env, b):
	    return env.failed('pred: doc = %r; failed for element == %s'%(doc, env.name(b)))
	return True

class PowersetFamily(SpecFamily):
    def __init__(self, *args):
	SpecFamily.__init__(self, *args)
	self.add_export('union', lambda x: x.arg)

    def __call__(self, set):
	return self.specoarg(set)

    def c_get_examples(self, a, env):
	x = [self.specmod.Nothing, a.arg]
	try:
	    y = env.get_examples(a.arg)
	except:
	    # xxx complain? We can always generate 2 examples..
	    return x
	# xxx should we make all permutations?..
	return x

    def c_test_contains(self, a, b, env):
	if not b in self.specmod.set:
	    env.failed('powerset.test_contains: not a set: %s'%self.specmod.iso(b))
	set = a.arg
	return env.forall(b, lambda env, x: env.test_contains(set, x, 'powerset'), 'powerset')


class DocFamily(SpecFamily):
    def __call__(self, doc, type=None):
	if type is None:
	    type = self.specmod.UniSet.NotNothing
	else:
	    if not type in self.specmod.set:
		type = self.specmod.UniSet.convert(type)
	return self.Set(self, (doc, type))

    def c_test_contains(self, a, b, env):
	doc, type = a.arg
	return type.test_contains(b, env)

class RelOpFamily(SpecFamily):
    def __init__(self, *a, **k):
	SpecFamily.__init__(self, *a, **k)
	self.add_export('domain', lambda x:x.arg[0])
	self.add_export('range', lambda x:x.arg[2])
	# The memo dict keeps relops with the same domain, op, and range.
	# Primarily introduced to make equality work with default mechanism,
	# since different compiled func's compared differently even with
	# the same source.
	self.memo = {}

    def __call__(self, domain, op, range=None):
	domain = self.specmod.setcast(domain)
	if range is None:
	    range = domain
	else:
	    range = self.specmod.setcast(range)
	x = self.memo.get((domain, op, range))
	if x is None:
	    if op in ('<', '<=', '==', '!=', '>', '>=', 'in', 'not in', 'is', 'is not'):
		func = eval('lambda x,y: x %s y'%op)
		func.name = op
	    else:
		func = op
		func.name = func.func_name
	    x = self.Set(self, (domain, func, range))
	    self.memo[(domain, op, range)] = x
	return x
    
    def c_get_examples(self, a, env):
	# We have to check length before calling iterpermute - 
	# to give a reasonable error message examples are missing from some set.
	dom = list(env.get_examples(a.domain))
	if not dom:
	    failed_coverage('relation', a.domain, None, 'domain')
	    return []
	
	ran = list(env.get_examples(a.range))
	if not ran:
	    failed_coverage('relation', a.range, None, 'range')
	    return []
	
	exs = []
	for ex in self.specmod._root.guppy.etc.iterpermute(dom, ran):
	    if env.contains(a, ex):
		exs.append(ex)
	return exs

    def c_test_contains(self, a, b, env):
	d, op, r = a.arg
	if not op(*b):
	    return env.failed()
	return True



class EqualsFamily(SpecFamily):
    def __call__(self, *args):
	if not args:
	    return self.specmod.Nothing
	return self.specotup(args)

    def c_test_contains(self, a, b, env):
	if b in a.arg:
	    return True
	return env.failed('equals')

    def c_get_examples(self, a, env):
	return a.arg
	    
class ExampleFamily(SpecFamily):
    def __call__(self, set, *examples):
	return self.Set(self, (set, examples))

    def c_test_contains(self, a, b, env):
	set, examples = a.arg
	return set.test_contains(b, env)

    def c_get_examples(self, a, env):
	set, examples = a.arg
	# for e in examples:	    env.test_contains(set, e, 'ExampleFamily.c_get_examples')
	return examples

class SynonymsFamily(SpecFamily):
    def __call__(self, *names):
	return self.Set(self, names)

    def c_test_contains(self, a, b, env):
	names = a.arg
	ms = self.specmod.UniSet.mutnodeset()
	for name in names:
	    x = env.getattr(b, name)
	    ms.add(x)
	if not len(ms):
	    env.failed('Synonyms: no such names: %r'%names)
	if len(ms) > 1:
	    env.failed('Synonyms: %d different nodes for names: %r'%(len(ms), names))
	return True
		       
class InstanceFamily(SpecFamily):
    def c_test_contains(self, a, b, env):
	if not isinstance(b, a.arg):
	    env.failed('InstanceFamily: %s is not an instance of %s'%(
		self.specmod.iso(b), a.arg))
	return True

    def c_get_examples(self, a, env):
	return env.get_examples(self.specmod.setcast(a.arg))

    def _and_ID(self, a, b):
	return self.mod.fam_Identity(*[bi for bi in b.nodes if isinstance(bi, a.arg)])


class ExpressionPredicateFamily(SpecFamily):
    def __call__(self, names, expression):
	func = None
	return self.Set(self, (names, expression, func))

    def c_test_contains(self, a, b, env):
	names, expression, func = a.arg
	func = eval('lambda %s:%s'%(','.join(names), expression))
	d = {}
	for name in names:
	    x = env.getattr(b, name)
	    d[name] = x
	try:
	    x = func(**d)
	except:
	    raise
	if not x:
	    env.failed('False expression: %s'%expression)
	return True
		       
class ExpressionSetFamily(SpecFamily):
    def __call__(self, expression, *names):
	func = None
	return self.Set(self, (names, expression, func))

    def c_test_contains(self, a, b, env):
	names, expression, func = a.arg
	func = self.specmod.eval('lambda %s:(%s)'%(','.join(('LE',)+tuple(names)), expression))
	d = {'LE':env.LE}
	for name in names:
	    x = env.getattr(b, name)
	    d[name] = x
	try:
	    x = func(**d)
	except:
	    raise
	return env.test_contains(x, b, 'expset(%s, %s)'%(expression, ','.join(names)))

class MatchesFamily(SpecFamily):
    def __init__(self, *a, **k):
	SpecFamily.__init__(self, *a, **k)
	self.sre = self.specmod._root.sre
	    
    def __call__(self, regexp):
	return self.specoargtup(self.sre.compile(regexp), (regexp,))

    def c_test_contains(self, a, b, env):
	regexpobj = a.arg
	m = self.sre.match(regexpobj, b)
	if m is None:
	    return env.failed('Did not match')
	return True

class RecurSelfFamily(SpecFamily):
    def __init__(self, *a, **k):
	SpecFamily.__init__(self, *a, **k)

	class RecurSpec(self.Set):
	    __slots__ = 'func', 'recursion_level', 'recursion_limit'

	self.RecurSpec = RecurSpec

    def __call__(self, expr, recursion_limit = 10):
	s = self.RecurSpec(self, expr)
	s.recursion_limit = recursion_limit
	s.recursion_level = 0
	return s

    def c_test_contains(self, a, b, env):
	try:
	    func = a.func
	except AttributeError:
	    expr = a.arg
	    func = a.func = env.eval('lambda self:%s'%expr)
	s = func(self.specmod.Nothing)
	try:
	    tf = env.test_contains(s, b, 'recur with Nothing, ok to fail')
	    if not tf:
		raise TestError
	except : # TestError: eg for match, we got a TypeError..
	    s = func(a)
	    rl = a.recursion_level
	    try:
		if rl >= a.recursion_limit:
		    return env.failed('recurself: recursion_level = %s'%a.recursion_limit)
		else:
		    a.recursion_level = rl + 1
		tf = env.test_contains(s, b, 'recur')
	    finally:
		a.recursion_level = rl
	return tf

class Dummy:
    pass

class TupleformFamily(SpecFamily):
    def __call__(self, form, set):
	return self.specotup((form, set))

    def c_test_contains(self, a, b, env):
	form, set = a.arg

	bt = tuple(b)

	if len(bt) != len(form):
	    return env.failed('tupleform: wrong length: got %d expected %d'%(len(bt), len(form)))

	ob = Dummy()
	for name, val in zip(form, bt):
	    setattr(ob, name, val)

	return env.test_contains(set, ob, 'tupleform')
	    

class Arrow:
    def __init__(self, category, source, target):
	self.category = category
	self.source = source
	self.target = target

    def of(self, other):
	# compose self <-- other 
	# (Standard composition order)
	other = self.category.validate(other)
	return self.category.compose(self, other)

    def to(self, other):
	# compose self --> other
	# (Nonstandard composition order; sometimes seems more natural)
	other = self.category.validate(other)
	return self.category.compose(other, self)

class IdentityArrow(Arrow):
    def __init__(self, category, object):
	Arrow.__init__(self, category, object, object)

    def __call__(self, x):
	return x

class FunctionArrow(Arrow):
    def __init__(self, category, source, target, function):
	Arrow.__init__(self, category, source, target)
	self.__call__ = function

class RepresentationCategory:
    _derive_origin_ = None
    _origin_ = None
    def __init__(self, mod, spec):
	fam = mod.family(RepresentationObjectFamily)
	fam.init2(self, spec)
	self._fam = fam

    def __eq__(self, other):
	return self is other

    def __hash__(self):
	return hash(id(self))

    def __getattr__(self, name):
	r = self._fam.getobject(name)
	self.__dict__[name] = r
	return r

class RepresentationObjectFamily(SpecFamily):
    def init2(self, cat, spec):
	self.cat = cat
	self.objects = {}
	self.specs = {}
	self.arrows = {}


	self.add_export('fromuniversal', self.fromuniversal)

	Set = self.Set
	class RepresentationObject(Set):
	    __slots__ = 'to', 'from'

	self.Set = RepresentationObject

	class RepresentationCategorySpec(spec):
	    def __init__(self, fam):
		self._fam = fam
		self._cat = fam.cat

	    def __getattr__(self, name):
		if hasattr(self.__class__, '_get_%s'%name):
		    r = getattr(self, '_get_%s'%name)(self._fam.specmod)
		    self.__dict__[name] = r
		    return r
		raise AttributeError, name

	self.spec = RepresentationCategorySpec(self)




    def getarrow(self, dom, cod):
	dc = (dom, cod)
	if dc in self.arrows:
	    return self.arrows[dc]

	raise SpecError

    def getobject(self, name):
	if name in self.objects:
	    return self.objects[name]
	normname = self.normoname(name)
	if normname in self.objects:
	    self.objects[name] = self.objects[normname]
	    return self.objects[normname]

	o = self(normname)
	self.objects[normname] = self.objects[name] = o
	return o

	raise SpecError, 'No such object: %r'%name

    def getspec(self, obj):
	name = obj.arg
	if name in self.specs:
	    return self.specs[name]
	
	gs = getattr(self.spec, '_get_spec_%s'%name, None)
	if gs is not None:
	    sp = gs(self.specmod)
	    self.specs[name] = sp
	    return sp

	raise SpecError, 'getspec: No spec of %r'%name

    def fromuniversal(self, target):
	# Find a most general arrow into 'target'
	# 1. Find all predefined arrows to target 
	# 2. Make a category sum of the set of sources S of all such arrows
	# 3. Make a specification-set P for this sum, which is that:
	#    a. The element should be isomorphic to a tuple (O, A) where
	#    b. O, the tag, should be an object in S
	#    c. A, the value,  should be an element in O

	# Return an arrow taking this object to target.
	#
	# Arrows thus created are memoized.

	name = target.arg
	arrowname = '%s.fromuniversal'%name
	if arrowname in self.arrows:
	    return self.arrows[arrowname]

	S = {}

	S[name] = IdentityArrow(self.cat, target)

	for an in dir(self.spec):
	    if not (an.startswith('map_') and '_to_' in an):
		continue
	    s, t = an.split('_to_')
	    s = s[4:]
	    if t == name:
		f = getattr(self.spec, an)
		S[s] = FunctionArrow(self.cat, getattr(self.cat, s), target,
				     lambda x: f(self.specmod, x))
		    
	def p(env, e):
	    try:
		O, A = e
	    except:
		return env.failed('Not a sequence with length 2')
	    fam = getattr(O, 'fam', None)
	    if fam is not self:
		return env.failed('Tag is not an object of this family')
	    name_ = getattr(O, 'arg', None)
	    if name_ not in S:
		return env.failed('Object is not a source of this target')
	    return env.test_contains(O, A, 'Value is not an element of this object')

	uniname = '%s.universal'%name
	P = self.specmod.predicate(p, 'Specification-set for %r'%uniname)
	self.specs[uniname] = P
	source = self(uniname)

	class AlphaSum(Arrow):
	    def __init__(self, category, source, target, S):
		Arrow.__init__(self, category, source, target)

		self._S = S

	    def __getitem__(self, x):	# Don't know what to call this unique arrow
		return self._S[self.source.fam.normoname(x)]

	    def __call__(self, (O, E)):
		return self[O.arg](E)
	    

	arrow = AlphaSum(self.cat, source, target, S)
	self.arrows[arrowname] = arrow
	return arrow

    def normoname(self, on):
	isos = getattr(self.spec, '_isos_', None)
	if isos is not None:
	    for l in self.spec._isos_:
		nn = None
		for n in l:
		    if n.isdigit():
			nn = n
		    if n == on:
			if nn is not None:
			    return nn
			raise SpecError, 'No numeric object name corresponding to %r'%on
	return on

    def __call__(self, name):
	r = self.specoarg(name)
	class To:
	    __slots__ = 'source',
	    def __init__(self, source):
		self.source = source
		
	    def __call__(self, target):
		return self.source.fam.getarrow(self.source, target)

	    def __getattr__(self, name):
		source = self.source
		fam = source.fam
		target = fam.getobject(name)
		return fam.getarrow(source, target)

	r.to = To(r)
	return r

    def c_test_contains(self, a, b, env):
	set = self.getspec(a)
	return env.test_contains(set, b, 'RepresentationObjectFamily: not in object specification')

    def c_get_examples(self, a, env):
	set = self.getspec(a)
	return env.get_examples(set)

class AbstractSetFamily(SpecFamily):
    def __init__(self, *a, **k):
	SpecFamily.__init__(self, *a, **k)
	class AbstractSet(self.Set):
	    __slots__ = '_memo',
	    def __init__(self, fam, arg):
		self.fam = fam
		self.arg = arg
		self._origin_ = None
		self._memo = {}
	self.Set = AbstractSet

    def __call__(self, arrow, set):
	r = self.specotup((arrow, set))
	r._memo = {}
	return r

    def c_and(self, a, b):
	if b.fam is self:
	    aa, sa = a.arg
	    ab, sb = b.arg
	    if aa is ab:
		return self(aa, sa & sb)
	return b.fam._rand_ATOM(b, a)

    def c_getattr2(self, a, b):
	if b in a._memo:
	    return a._memo[b]
	arrow, set = a.arg

	pararrow = arrow[b]
	srcset = pararrow.source

	def p(env, x):
	    t = env.test_contains(srcset, x, 'AbstractSet: not in arrow.source')
	    if t:
		e = pararrow(x)
		t = env.test_contains(set, e, 'AbstractSet: not in argument set')
	    return t

	    return env.contains(set, y)

	s = self.specmod.predicate(p, 'Abstract set attribute: %r'%b) #...
	a._memo[b] = s
	return s

    def c_test_contains(self, a, b, env):
	arrow, set = a.arg
	t = env.test_contains(arrow.source, b, 'AbstractSet: not in arrow.source')
	if t:
	    e = arrow(b)
	    t = env.test_contains(set, e, 'AbstractSet: not in argument set')
	return t
							  
class ElemFamily(SpecFamily):
    def __call__(self, func):
	return self.specoarg(func)

    def c_test_contains(self, a, b, env):
	func = a.arg
	s = func(b)
	return env.test_contains(s, b, 'ElemFamily')

class IntersectionFamily(SpecFamily):
    def __call__(self, domain, function):
	return self.specotup((domain, function))

    def c_test_contains(self, a, b, env):
	domain, function = a.arg
	return env.forall(domain, lambda env, x:
			  env.test_contains(function(x), b, 'Intersection'))
		   

class SpecError(Exception):
    pass

class TestError(Exception):
    pass

class CoverageError(Exception):
    pass



class LocalEnv:
    _derive_origin_ = 'ADD'
    def __init__(self, mod, spec, nodoc=1):
	self._mod = mod
	self._spec = spec
	self._origin_ = None
	self.nodoc = nodoc


    def __getattr__(self, attribute_name):
	mod = self._mod
	f = getattr(self._spec, attribute_name)
	d = self._mod._load_names(mod._root.guppy.etc.Code.co_findloadednames(f.func_code))
	nf = mod._root.new.function(
	    f.func_code,
	    d,
	    f.func_name,
	    f.func_defaults,
	    f.func_closure)
	r = nf(())
	self.__dict__[attribute_name] = r
	return r
			    

class TestEnv:
    _derive_origin_ = 'ADD'
    iscomplete = False
    issilent = False
    max_sequence_examples_length = 2	# ie. (), cprod(x) cprod(x, y) are yielded by default
    TestError = TestError
    def __init__(self, mod, Spec):
	self.mod = mod
	self.messages = []
	self.examples = {}
	if Spec is not None:
	    self.spec = spec = Spec()
	    try:
		lex = spec.LocalEnvExpr
	    except AttributeError:
		lex = ''
	    LE = LocalEnv(mod, lex)
	    LE._OBJ_ = mod
	    self.LE = LE

	    self.topspec = self.eval(spec.GlueTypeExpr)

    def eval(self, expr):
	mod = self.mod
	types = mod._root.types
	if isinstance(expr, types.StringTypes):
	    func = self.mod.eval('lambda LE:(\n%s\n)'%expr)
	    return func(self.LE)
	
	ls = []
	selfset = None
	#print 1

	names = expr.__dict__.keys()
	names.sort()

	for name in names:
	    f = getattr(expr, name)
	    try:
		co = f.func_code
	    except AttributeError:
		continue
	    if co.co_varnames[:co.co_argcount] == ('IN',):
		d = mod._load_names(mod._root.guppy.etc.Code.co_findloadednames(co))
		#d = mod._load_names()

		nf = mod._root.new.function(
		    f.func_code,
		    d,
		    f.func_name,
		    f.func_defaults,
		    f.func_closure)
		s = nf(())
		if name == '_SELF_':
		    selfset = s
		else:
		    ls.append(mod.attr(name, s))
	    else:
		raise SpecError, 'TestEnv.eval: invalid argument mode'
	# Constructing an AND in one sweep = faster
	# We assume they are not disjoint - which
	# would be determined by testing that we are going to do
	# (We know they are all attr's of different names here)

	# Except that selfset may perhaps be disjoint; but why care here
	#
	if selfset is not None:
	    ls.append(selfset)

	    # Alternatively: r = r & selfset afterwards,
	    # but could be unnecessarily slow

	#print 2
	r = mod.UniSet.fam_And._cons(ls)
	#print 3
	return r
		

    def get_examples(self, collection):
	try:
	    it = iter(collection)
	except TypeError:
	    try:
		ex = self.examples[collection]
	    except KeyError:
		if isinstance(collection, self.mod.UniSet.UniSet):
		    ex = collection.get_examples(self)
		else:
		    ex = list(collection)
	    it = iter(ex)
	return it

    def getattr(self, obj, name):
	if '.' in name:
	    x = obj
	    for subname in name.split('.'):
		try:
		    x = getattr(x, subname)
		except:
		    return self.failed('getattr: %s has no attribute %r'%(self.name(obj), name)+
				      ',\nbecause %s has no attribute %r'%(self.name(x), subname))
	else:
	    try:
		x = getattr(obj, name)
	    except:
		if DEBUG:
		    raise
		return self.failed('attr: %s has no attribute %r'%(self.name(obj), name))
	return x
	    
    def gengetattr(self, obj, name_or_tuple):
	if isinstance(name_or_tuple, str):
	    return self.getattr(obj, name_or_tuple)
	elif isinstance(name_or_tuple, tuple):
	    if len(name_or_tuple) == 2 and name_or_tuple[0] is self.mod.quote:
		return name_or_tuple[1]
	    else:
		return tuple([self.gengetattr(obj, nt) for nt in name_or_tuple])
	else:
	    raise TypeError, 'gengetattr: I am picky, required string or tuple'
	
    def log(self, message):
	self.messages.append(message)

    def name(self, obj):
	if isinstance(obj, self.mod.UniSet.UniSet):
	    return str(obj)
	else:
	    return '%s'%self.mod.iso(obj)

    def name_coll(self, collection):
	return '%s'%collection

    def test(self, obj):
	self.get_obj_examples(obj)
	try:
	    self.test_contains(self.topspec, obj, 'Top spec')
	except:
	    tvt = self.mod._root.sys.exc_info()
	    self.dump_failure(tvt)

    def get_obj_examples(self, obj):
	ex = self.spec.GetExamples(self, obj)
	for e in ex:
	    vs = e[1:]
	    e = e[0]
	    s = self.examples.setdefault(e, [])
	    for v in vs:
		s.append(v)
		self.test_contains(e, v, 'testing example of set')

	

    def dump_failure(self, (type, value, traceback), noraise=0):
	list = []
	tb = traceback
	while tb is not None:
	    f = tb.tb_frame
	    if f.f_code is self.test_contains.im_func.func_code:
		list.append(f)
	    tb = tb.tb_next
	for f in list:
	    lo = f.f_locals
	    print 'a = %r' % (lo['a'],)
	    print 'b = %r' % (lo['b'],)
	    print 'message = ', lo['message']
	    print '-----'
	if noraise:
	    self.mod._root.traceback.print_exception(type, value, traceback)
	else:
	    raise

    def contains(self, a, b):
	try:
	    x = self.test_contains(a, b, 'contains')
	except CoverageError:
	    raise
	except:
	    return False
	return x

    def test_contains(self, a, b, message):
	if 0:
	    try:
		a.test_contains(b, self)
	    except TestError:
		raise
		# return self.failed('test_contains, from: %s'% message)
	    return True
	else:
	    return a.test_contains(b, self)

    def test_contains_not(self, a, b, message):
	try:
	    a.test_contains(b, self)
	except CoverageError:
	    raise
	except:	# TestError: # well we axcept anything.. ok?
	    return True
	else:
	    return self.failed('test_contains_not, from: %s'%message)

    def failed(self, message=''):
	if not self.issilent:
	    self.log( 'Failed:' + message)
	    raise TestError, message
	return False

    def failed_coverage(self, forwhat, collection, func, message):
	if collection is self.mod.Nothing:
	    return True
	raise CoverageError, '%s: no examples for collection = %s, message: %s'%(forwhat, collection, message)

    def failed_exc_info(self, message):
	exc_info = self.mod._root.sys.exc_info()
	type, value, traceback = exc_info
	if not self.issilent:
	    self.log( 'Failed:' + message)
	    raise type, value
	return False

    def forall(self, collection, func, message=''):
	ex = self.get_examples(collection)
	n = 0
	for e in ex:
	    if not func(self, e):
		return self.failed('forall: e = %s, from: %s'%(self.name(e), message))
	    n += 1
	if not n:
	    try:
		a = len(collection)
		if a > 0:
		    raise CoverageError
		# Otherwise ok, it was really an Nothing collection.
	    except:
		self.failed_coverage('forall', collection, func, message)

	return True
	    
    def forall_pairs(self, collection, func, message=''):
	as_ = self.get_examples(collection)
	n = 0
	for a in as_:
	    for b in self.get_examples(collection):
		if not func(self, a, b):
		    self.failed('forall_pairs: a = %s, b = %s, from: %s'%(
			self.name(a), self.name(b), message))
		n += 1
	if not n:
	    self.failed_coverage('forall_pairs', collection, func, message)
	return True

    def forall_triples(self, collection, func, message=''):
	as_ = self.get_examples(collection)
	n = 0
	for a in as_:
	    for b in self.get_examples(collection):
		for c in self.get_examples(collection):
		    if not func(self, a, b, c):
			self.failed('forall_triples: a = %s, b = %s, c=%s, from: %s'%(
			    self.name(a), self.name(b), self.name(c), message))
		    n += 1
	if not n:
	    self.failed_coverage('forall_triples', collection, func, message)
	return True


    def forsome(self, collection, func, message=''):
	failures = []
	for i, x in enumerate(collection):
	    try:
		b = func(x)
	    except : # TestError:
		failures.append((i, self.mod._root.sys.exc_info()))
		continue
	    if b:
		return True
	for (i, tvt) in failures:
	    print 'forsome: exception at collection[%d]:'%i
	    self.dump_failure(tvt, noraise=1)
	self.failed(message)
	

class _GLUECLAMP_:

    _chgable_ = '_loaded',
    _nowrap_ = ('_origin_', 'Doc', 'family', 'eval', 'setcast', 'compile', 'wrap_source_string',
		'_load_names', 'iso')

    _preload_ = '_hiding_tag_',

    # 'imports'

    _imports_ = (
	'_parent:Use',
	'_parent.Use:iso',
	'_parent.Use:Nothing',
	)

    def _get_AbstractAlgebra(self):	return self._parent.AbstractAlgebra
    def _get_UniSet(self):		return self._parent.UniSet
    def _get_Doc(self):			return self._parent.Doc
    def _get_View(self):		return self._parent.View

    #

    def _get__origin_(self):
	return self.Doc.attribute(self.Doc.root, 'guppy.heapy.Spec')	

    def _wrapattr_(self, obj, name):
	Doc = self.Doc
	if name == 'setof':
	    pass
	    #pdb.set_trace()
	try:
	    obj = Doc.wrap(obj, Doc.attribute(self._origin_, name))
	except Doc.DocError:
	    print 'no wrap:', name
	return obj

    def _get_AA(self):
	return self.AbstractAlgebra

    def _get_abstractset(self):
	return self.family(AbstractSetFamily)

    def _get_adaptuple(self):
	return self.family(AdaptupleFamily)

    def _get_any(self):
	return ~self.Nothing

    def _get_argnames(self):
	return self.family(ArgNamesFamily)

    def _get_attr(self):
	return self.family(AttributeFamily)

    def attrs(self, names, type=None):
	x = self.any
	for n in names:
	    x &= self.attr(n, type)
	return x

    def _get_boolean(self):
	def p(env, x):
	    try:
		if x:
		    pass
	    except:
		env.failed("boolean: 'if x' raised an exception")
	    return True
	return self.predicate(p, 'boolean')


    def _get_callable(self):
	return self.predicate(lambda env, x:callable(x), 'callable')

    def _get_compile(self):
	token = self._root.token
	parser = self._root.parser
	symbol = self._root.symbol

	def mapchildren_id(node, f):
	    return node

	def mapchildren_default(node, f):
	    return [node[0]] + [f(n) for n in node[1:]]

	mapchildren_dispatch = dict([(value, mapchildren_id) for value in range(token.N_TOKENS)])

	mapchildren_dispatch.update(dict([(value, mapchildren_default)
				     for value, name in symbol.sym_name.items()]))

	def mapchildren(node, f):
	    return mapchildren_dispatch[node[0]](node, f)

	def visitor(C):
	    d = mapchildren_dispatch.copy()
	    for value, name in symbol.sym_name.items():
		if hasattr(C, name):
		    d[value] = getattr(C, name).im_func
	    _visit = lambda node: d[node[0]](node, _visit)
	    return _visit

	def recover_source_node(node, l):
	    for n in node[1:]:
		recover_source_dispatch[n[0]] (n, l)

	def recover_source_token(node, l):
	    if l and l[-1] != '(':
		l.append(' ')
	    l.append(node[1])

	def recover_source_name(node, l):
	    if l and l[-1] not in ('.', '('):
		l.append(' ')
	    l.append(node[1])

	    
	def recover_source_tight_left(node, l):
	    l.append(node[1])

	def recover_source_lpar(node, l):
	    if l and not (l[-1][-1:].isalnum() or l[-1] == '('):
		l.append(' ')
	    l.append(node[1])


	recover_source_dispatch = dict([(value, recover_source_node)
				     for value, name in symbol.sym_name.items()])
	recover_source_dispatch.update(
	    dict([(value, recover_source_token) for value in range(token.N_TOKENS)]))

	recover_source_dispatch[token.NAME] = recover_source_name

	for tok in ('RPAR', 'LSQB', 'RSQB', 'COLON', 'COMMA', 'SEMI',
		    'DOT', 'LBRACE', 'RBRACE'):
	    recover_source_dispatch[getattr(token, tok)] = recover_source_tight_left

	recover_source_dispatch[token.LPAR] = recover_source_lpar


	def recover_source(node):
	    l = []
	    recover_source_dispatch[node[0]] (node, l)
	    return ''.join(l)

	class wrap_lambdef:
	    def test(node, f):
		# and_test ('or' and_test)* | lambdef
		if len(node) == 2 and node[1][0] == symbol.lambdef:
		    lsource = recover_source(node[1])
		    lnode = mapchildren(node[1], f)

		    return (
			292, (293, (294, (295, (297, (298, (299, (300, (301,
			(302, (303, (304, (305, (1, 'wrap_source_string')),
			(308, (7, '('),	(317, (318, (292, lnode)), (12, ','),
			(318, (292, (293, (294, (295, (297, (298, (299, (300,
			(301, (302, (303, (304, (305, (3, '%r'%lsource
			)))))))))))))))), (8, ')'))))))))))))))


		return mapchildren(node, f)

	wrap_lambdef = visitor(wrap_lambdef)

	def compile_(source, filename, mode, *args):
	    if mode != 'spec':
		return compile(source, filename, mode, *args)
	    ast = parser.expr(source)
	    node = parser.ast2tuple(ast, line_info=1)
	    node = mapchildren(node, wrap_lambdef)

	    ast = parser.tuple2ast(node)
	
	    co = parser.compileast(ast)
	    return co

	return compile_

    def _get_cprod(self):
	return self.family(CartesianProductFamily)

    def dictof(self, set=None):
	return self.UniSet.byclodo.dictof(set)

    def _get_doc(self):
	return self.family(DocFamily)

    def docof(self, set):
	doc = (set.doc % self._origin_).shortest()
	do = str(doc)
	print do
	return do

    def eval(self, expr, init=None, nodoc=0):
	if nodoc:
	    mode = 'eval'
	else:
	    mode = 'spec'
	co = self.compile(expr, '', mode)


	d = self._load_names(self._root.guppy.etc.Code.co_findloadednames(co))
	if init is not None:
	    d = d.copy()
	    exec init in d
	    

	return eval(co, d)
	
    def _get_all_names(self):
	names = {'_root':1}
	for x in _GLUECLAMP_.__dict__:
	    # print 'x', x
	    if x.startswith('_get_'):
		x = x[5:]
	    names[x] = 1
	return names
	

    def _load_names(self, names = None):
	if names is None:
	    if '_loaded' not in self.__dict__:
		for x in self.all_names:
		    getattr(self, x)
		self._loaded = 1
	else:
	    all = self.all_names
	    for name in names:
		if name in all:
		    getattr(self, name)
	d = self.__dict__
	d['__builtins__'] = self._load_names.func_globals['__builtins__']
	return d

	

    def _get_eg(self):
	return self.family(ExampleFamily)

    def _get_elem(self):
	return self.family(ElemFamily)

    def _exodoc(self, expr):
	if expr in self.LE.string:
	    r = self.eval(expr)
	    return r, self.Doc.anon(expr)
	elif (expr in self.Type.Function and
	      expr.func_code.co_name == '<lambda>' and
	      expr.func_code.co_filename.startswith('<!SPECEVAL!>')):
	      fn = expr.func_code.co_filename
	      lines = fn.split('\n')
	      lnum = expr.func_code.co_firstlineno
	      inspect = self._root.inspect
	      print lines[lnum:]
	      block = inspect.getblock(lines[lnum:])
	      source = '\n'.join(block)
	      return expr, self.Doc.getdoc(source)
	      
	    
	else:
	    return expr, self.Doc.getdoc(expr)
	    

    def _get_expred(self):
	return self.family(ExpressionPredicateFamily)

    def _get_expression(self):
	def p(env, x):
	    try:
		eval( 'lambda : %s'%x )
	    except SyntaxError:
		env.failed('Not a valid expression: %r'%x)
	    return True
	return self.predicate(p, 'expression')

    def _get_expset(self):
	return self.family(ExpressionSetFamily)

    def _get_equals(self):
	return self.family(EqualsFamily)

    def family(self, fam, *args, **kwds):
	return self.UniSet.fam_mixin_argatom(fam, self, *args, **kwds)

    def _get__hiding_tag_(self):
	return self.UniSet._hiding_tag_

    def _get_instance(self):
	return self.family(InstanceFamily)

    def _get_intersection(self):
	return self.family(IntersectionFamily)

    def _get_LE(self):
	return LocalEnv(self, self._Specification_.LocalEnvExpr)

    def _get_SPLE(self):
	return self.LE


    def _get_mapping(self):
	return self.family(MappingFamily)

    def _get_matches(self):
	return self.family(MatchesFamily)

    def mkTestEnv(self, Spec):
	return TestEnv(self, Spec)

    def newtype(self, name):
	return self.predicate(lambda e, x: 1, name) # xxx new family? 

    def _get_nothing(self):
	return self.Use.Nothing
	
    def partition(self, set):
	return self.doc('partition',
			self.union_equals(set) &
			self.LE.nonempty &
			self.set_of_disjoint_sets
			)

    def _get_predicate(self):
	return self.family(PredicateFamily)

    def _get_powerset(self):
	return self.family(PowersetFamily)

    def _get_Anything(self):
	return self.UniSet.Anything

    def _get_quote(self):
	return []

    def _get_recurself(self):
	return self.family(RecurSelfFamily)

    def _get_relation(self):
	# relation is a representation category
	# We have the following representation objects:
	# 1. set of pairs with attribute dom, cod
	# 2. set of pairs with dom is cod
	# 3. fuop = func | op, string in ('==',..)
	# 4. (A, fuop), where A is a set
	# 5. (A, fuop, B), where A and B are sets
	#
	# A final object is 1.
	class RelationSpec:
	    _isos_ = [
		('1', 'paxb'),
		('2', 'paxa'), 
		('3', 'defiop', 'fuop', ),
		('4', 'defipair'),
		('5', 'defitriple'),
		]
		 
	    def _get_spec_1(self, e):
		return e.setof(e.cprod(e.Anything, e.Anything))
		
	    def _get_spec_2(self, e):
		return (e.setof(e.cprod(e.Anything, e.Anything)))

	    def _get_spec_3(self, e):
		return (e.boolean << (e.Anything, e.Anything) |
			e.equals('<', '<=', '==', '!=', '>', '>=', 'in', 'not in', 'is', 'is not'))
			
	    def _get_spec_4(self, e):
		return e.cprod(e.set, self._cat.fuop)
		
	    def _get_spec_5(self, e):
		return e.cprod(e.set, self._cat.fuop, e.set)
		
	    def _get__relop(self, e):
		return e.family(RelOpFamily)

	    map_2_to_1 = id
	    def map_3_to_4(self, e, fuop):	return (e.Anything, fuop)
	    def map_3_to_2(self, e, fuop):	return self._relop(e.Anything, fuop) # redundant
	    def map_4_to_2(self, e, (A, fuop)):	return self._relop(A, fuop)
	    def map_5_to_1(self, e, (A,fuop,B)):return self._relop(A, fuop, B)

	return self.repcat(RelationSpec)

    def _get_relop(self):
	return self.relation.defiop.to.paxa

    def repcat(self, spec):
	return RepresentationCategory(self, spec)

    def _get_sequence(self):
	return self.family(SequenceFamily)

    def _get_set(self):
	return self.instance(self.UniSet.UniSet)

    def _get_set_of_disjoint_sets(self):
	def p(env, x):
	    return env.forall_pairs(x, lambda env, a, b: a == b or a.disjoint(b),
				    'a == b or a.disjoint(b)')
	return self.predicate(p, 'set of disjoint sets')

    def setcast(self, arg):
	if not isinstance(arg, self.UniSet.UniSet):
	    arg = self.UniSet.convert(arg)
	    arg = self.Doc.wrap(arg, self.Doc.callfunc(
		self.Doc.attribute(self._origin_, 'setcast'),
		arg))
	return arg

    def _get_setof(self):
	return self.powerset

    def _get__static_test_env(self):
	return self.mkTestEnv(None)

    def _get_synonyms(self):
	return self.family(SynonymsFamily)

    def _get_tupleform(self):
	return self.family(TupleformFamily)

    def _get_Type(self):
	return self.Use.Type

    def union_equals(self, set):
	return self.eg(self.attr('union', self.equals(set)),
		  self.powerset(set))

    def wrap_source_string(self, func, str):
	func._origin_ = self.Doc.source(str)
	return func

