#._cv_part guppy.etc.KanExtension

class LeftKanExtension:

    # Implementation of algorithms described by Brown and Heyworth (ref.251)
    # and Heyworth (ref.253).

    def __init__(self, mod, A, B, R, X, F):
	# External subsystem dependencies
	#    mod.KnuthBendix
	#    mod.FiniteAutomaton
	#    mod.SolveFSA
	#    mod.Cat
	#	mod.Cat.Function
	#	mod.Cat.Functor
	#	mod.Cat.check_graph
	#	mod.Cat.check_rules

	self.mod = mod
	self.Cat = mod.Cat

	#

	self.Cat.check_graph(A)
	self.Cat.check_graph(B)
	self.Cat.check_rules(R, B)
	
	#

	self.A = A
	self.B = B
	self.R = [(tuple(g), tuple(h)) for (g, h) in R]
	self.X = X
	self.F = F

	self.general_procedure()


    def general_procedure(self):
	self.initialize_tables()
	self.make_confluent_system()
	if 0:
	    self.make_catalogue()
	else:
	    self.make_automaton()
	self.make_natural_transformation()
	
    def initialize_tables(self):
	self.obj_to_str_table = {}
	self.str_to_obj_table = {}
	self.make_initial_rules()

    def make_initial_rules(self):

	# Algorithm 6.1 in (251)

	Re = []

	def add_rule(a, b):
	    aw = self.make_word(a)
	    bw = self.make_word(b)
	    if aw != bw:
		Re.append( ( aw, bw ))

	for a in self.A.arrows:
	    srca = self.A.source(a)
	    tgta = self.A.target(a)
	    XA = self.X.fo(srca)
	    Xa = self.X.fa(a)
	    Fa = tuple(self.F.fa(a))
	    Fsrca = self.F.fo(srca)
	    Ftgta = self.F.fo(tgta)
	    if Fa:
		t = Fsrca
		for b in Fa:
		    srcb = self.B.source(b)
		    if srcb != t:
			raise ValueError, \
'Arrow [%s] with source %s does not compose with target %s'%(b, srcb, t)
		    t = self.B.target(b)
		if t != Ftgta:
		    raise ValueError, \
'Arrow %s with target %s does not compose with %s'%(Fa, t, Ftgta)
	    else:
		if Fsrca != Ftgta:
		    raise ValueError, \
'Source %s does not match target %s'%(Fsrca, Ftgta)
	    for x in XA:
		add_rule(((srca, x),) + Fa , ((tgta, Xa(x)),) )

	Rk = [(self.make_word(x), self.make_word(y)) for (x, y) in self.R]
		    

	self.Re = Re
	self.Rk = Rk
	self.Rinit = Re + Rk

    def make_confluent_system(self):
	self.rs = self.mod.KnuthBendix(self.Rinit, delim='.')
	self.Rconf = self.rs.reductions

    def make_automaton(self):
	# Make nondeterministic finite automaton
	
	def target(e):
	    if len(e) == 1 and isinstance(e[0], tuple):
		return self.F.fo(e[0][0])
	    else:
		return self.B.target(e[-1])

	XA = []
	for A in self.A.objects:
	    for x in self.X.fo(A):
		XA.append(((A, x),))

	follows = dict([(B, []) for B in self.B.objects])
	for b, (srcb, tgtb) in self.B.arrows.items():
	    follows[srcb].append((b, tgtb))

	IR = dict([(self.make_term(u), self.make_term(v)) for u, v in self.Rconf])
		   
	pplR = {}
	for l, r in self.Rconf:
	    t = self.make_term(l)
	    for i in range(1, len(t)):
		pplR[t[:i]] = 1

	s0 = ('s0',)

	fsa = self.mod.FiniteAutomaton(s0)

	for xi in XA:
	    if xi not in IR:
		fsa.add_transition(s0, xi[0], xi)

	for xi in XA:
	    for b, tgtb in follows[target(xi)]:
		bterm = (b,)
		xib = xi + bterm
		if xib in pplR:
		    fsa.add_transition(xi, b, xib, tgtb)
		elif (bterm in pplR and xib not in IR):
		    fsa.add_transition(xi, b, bterm, tgtb)
		elif xib not in IR:
		    fsa.add_transition(xi, b, tgtb)

	for Bi in self.B.objects:
	    for b, tgtb in follows[Bi]:
		bterm = (b,)
		if bterm in pplR:
		    fsa.add_transition(Bi, b, bterm, tgtb)
		elif bterm not in IR:
		    fsa.add_transition(Bi, b, tgtb)

	for u in pplR:
	    if u in XA:
		continue
	    for b, tgtb in follows[target(u)]:
		bterm = (b,)
		ub = u + bterm
		if ub in pplR:
		    fsa.add_transition(u, b, ub, tgtb)
		elif self.irreducible(ub): # ub not in IR:
		    fsa.add_transition(u, b, tgtb)
		
	def get_RS(Bi):
	    finals = {}
	    finals[Bi] = 1
	    for xi in XA:
		if self.F.fo(xi[0][0]) == Bi:
		    finals[xi] = 1
	    for u in pplR:
		if target(u) == Bi:
		    finals[u] = 1
		    
	    for c in fsa.get_composites():
		for s in c:
		    if s not in finals:
			break
		else:
		    finals[c] = 1

	    dfa = fsa.get_minimized_dfa(finals)
	    regexp = self.mod.SolveFSA(dfa)
	    return RegularSet(regexp)

	KB = self.Cat.Function(get_RS, self.B.objects, None)

	Kb = self.Cat.Function(
		      lambda a:KanAction(self.B, KB, a, target, self.irreducible, self.reduce),
		      self.B.arrows,
		      KanAction,
		      )
	    

	self.KB = KB
	self.Kb = Kb
	self.K = self.Cat.Functor(KB, Kb)


    def make_catalogue(self):
	# Catalogue the elements of the sets pointed to by extension functor K,
	# according to algorithm described in 7.1 in (251).

	# Precondition:

	# Tables initialized and a confluent system created.
	# The system is assumed to be finite, otherwise we won't terminate.

	# Postcondition:

	# Functor self.K represented as:
	#
	# self.K.tabo = self.KB = dict mapping,
        #		source: {each B in self.B.objects}
	#		target: sets represented as lists
	# self.K.taba = self.Kb = dict, mapping
	#		source: {each a in self.B.arrows}
	#		target: tabulated function, mapping
	#			source: KB[source of a]
	#			target: KB[target of a]

	def target(e):
	    if len(e) == 1:
		return self.F.fo(e[0][0])
	    else:
		return self.B.target(e[-1])

	def add_element(e):
	    if self.irreducible(e):
		block.append(e)
		KB[target(e)].append(e)
	    else:
		pass
		#print e, self
		#pdb.set_trace()

	KB = dict([(B, []) for B in self.B.objects])
	block = []

	for A in self.A.objects:
	    for x in self.X.fo(A):
		add_element(((A, x),))
		    
	while block:
	    oblock = block
	    block = []
	    for e in oblock:
		tgt = target(e)
		for a in self.B.arrows:
		    if self.B.source(a) == tgt:
			add_element( e + (a,) )

	Kb = {}

	for a in self.B.arrows:
	    src = KB[self.B.source(a)]
	    tgt = KB[self.B.target(a)]
	    tab = dict([(s, self.reduce(s + (a,))) for s in src])
	    Kb[a] = self.Cat.Function(tab, src, tgt)

	KB = self.Cat.Function(KB, self.B.objects, KB.values())
	Kb = self.Cat.Function(Kb, self.B.arrows, Kb.values())

	self.KB = KB
	self.Kb = Kb
	self.K = self.Cat.Functor(KB, Kb)

	
    def make_natural_transformation(self):
	
	# Precondition:
	# initial tables should be initialized
	# self.K.fo should exist

	# Postcondition:
	#
	# self.nat[A] for A in self.A.objects

	get_nat_memo = {}
	def get_nat(A):
	    if A in get_nat_memo:
		return get_nat_memo[A]


	    src = self.X.fo(A)
	    tgt = self.K.fo(self.F.fo(A))
	    tab = dict([(x, self.reduce( ((A, x),) )) for x in src])
	    get_nat_memo[A] = self.Cat.Function(tab, src, tgt)
	    return get_nat_memo[A]

	self.nat = self.Cat.Function(get_nat, self.A.objects, None)
		   


    def make_word(self, x):
	ots = self.obj_to_str
	return '.'.join([ots(e) for e in x if e != ''])

    def obj_to_str(self, x):
	otn = self.obj_to_str_table
	try:
	    return otn[x]
	except KeyError:
	    assert not (isinstance(x, tuple) and len(x) > 2)
	    n = str(len(otn))
	    #n = '%d:%s'%(len(otn), x)
	    #n = str(x)
	    otn[x] = n
	    self.str_to_obj_table[n] = x
	    return n

    def str_to_obj(self, x):
	return self.str_to_obj_table[x]

    def irreducible(self, x):
	tx = self.make_word(x)
	return tx == self.rs.reduce(tx)

    def reduce(self, x):
	w = self.rs.reduce(self.make_word(x))
	return self.make_term(w)

    def make_term(self, word):
	sto = self.str_to_obj_table
	return tuple( [sto[s] for s in word.split('.') if s] )

class KanAction:
    def __init__(self, B, KB, a, targetof, irreducible, reduce):
	srca = B.source(a)
	tgta = B.target(a)
	self.src = KB(srca)
	self.tgt = KB(tgta)
	self.a = a
	self.srca = srca
	self.targetof = targetof
	self.irreducible = irreducible
	self.reduce = reduce

    def __call__(self, s):
	if self.targetof(s) != self.srca:
	    raise TypeError, '''\
Target of %r (= %r) does not match source of %r (= %r)'''%(
    s, self.targetof(s), self.a, self.srca)
	if not self.irreducible(s):
	    raise TypeError, '''\
Argument %r is reducible to %r; and is thus not in the source set K.fo(%r)'''%(
	    s, self.reduce(s),self.srca)
	return self.reduce(s + (self.a,))


class RegularSet:
    # Wraps a regular expression;
    # provides a set protocol for the underlying set of sequences:
    #  o If the RE specifies a finite language, iteration over its strings
    #  [ o set inclusion ]

    is_simplified = 0
    def __init__(self, re):
	self.re = re
    
    def __iter__(self):
	return iter(self.uniform)

    def __getitem__(self, x):
	return self.uniform[x]

    def __len__(self):
	return len(self.uniform)

    def get_xs_covered(self, coverage):
	N = coverage
	X = self.re.limited(coverage)
	xs = X.sequni()
	return [tuple(x) for x in xs]

    def get_uniform(self):
	self.simplify()
	return self.re.sequni()
	
    uniform = property(fget=get_uniform)

    def simplify(self):
	if not self.is_simplified:
	    self.re = self.re.simplified()
	    self.is_simplified = 1

		
class ObjectTester:
    def __init__(self, category_tester, object, code):
	self.category_tester = category_tester
	self.functor = category_tester.functor
	self.object = object
	self.code = code
	
    def get_all_arrows(self):
	return self.category_tester.arrows[self.object]

    def get_intermediate_test_code(self):
	return self.code

    def get_python_test_source_code(self):
	cmap = {
	    'aseq':'assert e[%r] == e[%r]',
	    'evalfa':'e[%r] = fa[%r](e[%r])',
	    'asfo':'assert fo[%r](e[%r])'
	    }

	return '\n'.join([cmap[c[0]]%c[1:] for c in self.code])

    def execode(self, arg):
	code = self.get_python_test_source_code()

	e = {'arg':arg}
	d = {'fa':self.functor.fa,
	     'fo':self.functor.fo,
	     'e':e,
	     }
	exec code in d
	return e
    
    def intercode(self, arg):
	e = {'arg':arg}
	fa = self.functor.fa
	fo = self.functor.fo
	for c in self.code:
	    a = c[0]
	    if a == 'evalfa':
		dst, ar, src = c[1:]
		e[dst] = fa[ar](e[src])
	    elif a == 'asfo':
		ob, src = c[1:]
		if not fo[ob](e[src]):
		    raise ValueError, 'Predicate failed'
	    elif a == 'aseq':
		na, nb = c[1:]
		if e[na] != e[nb]:
		    raise ValueError, 'e[%r] != e[%r]'%(na, nb)
	    else:
		raise ValueError, 'Invalid code: %r'%(a,)


    def test(self, arg):
	return self.intercode(arg)

class CategoryTester:
    def __init__(self, mod, functor, arrows, get_arrow_name=None):
	self.mod = mod
	self.cat = functor.src
	self.functor = functor
	self.arrows = arrows
	if get_arrow_name is not None:
	    self.get_arrow_name = get_arrow_name


    def get_arrow_name(self, a):
	return '.'.join(a)


    def get_eval_arrows_code(self, object, argname):
	fa = self.functor.fa

	name = argname
	memo = {():name}
	memolist = [((),name)]

	codes = []

	def eval_arrow(a):
	    if a in memo:
		return memo[a]
	    a0 = a[:-1]
	    a1 = a[-1]
	    name = self.get_arrow_name(a)
	    na0 = eval_arrow(a0)
	    #codes.append('%s = fa[%r](%s)'%(name, a1, na0))
	    codes.append(('evalfa', name, a1, na0))
	    memo[a] = name
	    memolist.append((a, name))
	    return name

	for ar in self.arrows[object]:
	    eval_arrow(ar)
	
	return codes, memolist

    def get_object_tester(self, object):
	code = self.get_test_object_code(object)
	return ObjectTester(self, object, code)

    def get_test_inclusion_code(self, object, ml):
	codes = []
	src = self.functor.fo.src
	for arrow, value in ml:
	    ob = object
	    if arrow:
		ob = self.cat.graph.target(arrow[-1])
	    #codes.append('assert fo[%r](%s)'%(ob, value))
	    if src is None or ob in src:
		codes.append(('asfo', ob, value))
	return codes

    def get_test_object_code(self, object):
	argname = 'arg'
	evalcodes, memolist = self.get_eval_arrows_code(object, argname)

	relcodes = self.get_test_relations_code(object, memolist)

	incodes = self.get_test_inclusion_code(object, memolist)

	return evalcodes+relcodes+incodes
	

    def get_test_relations_code(self, object, memolist):
	codes = []
	cat = self.cat
	fa = self.functor.fa
	memo = dict(memolist)

	def teval_arrow(ar):
	    if ar in memo:
		return memo[ar]
	    a0 = teval_arrow(ar[:-1])
	    name = self.get_arrow_name(ar)
	    #codes.append('%s = fa[%r](%s)'%(name, ar[-1], a0))
	    codes.append(('evalfa', name, ar[-1], a0))
	    memo[ar] = name
	    return name

	# Check that the equality relations really match up
	# for all arrows in old memolist, i.e. original unique arrows
	# which is arguably overkill sometimes?..
	for a, b in cat.relations:
	    a = tuple(a)
	    b = tuple(b)
	    src = cat.graph.source(a[0])
	    for (arr, val) in memolist:
		if arr:
		    tgt = cat.graph.target(arr[-1])
		else:
		    tgt = object
		if src == tgt:
		    ara = arr + a
		    arb = arr + b
		    if ara != arb:
			va = teval_arrow(ara)
			vb = teval_arrow(arb)
			assert va != vb
			#codes.append('assert %s == %s'%(va, vb))
			codes.append(('aseq', va, vb))
	return codes
	    
    def test_object(self, object, value):
	tester = self.get_object_tester(object)
	tester.test(value)
	return tester

    def test_object_fail(self, object, value):
	try:
	    self.test_object(object, value)
	except:
	    pass
	else:
	    raise Exception, 'Exception excepted'

	    




class _GLUECLAMP_:
    # 'imports'

    def _get_KnuthBendix(self):    	return self._parent.KnuthBendix.KnuthBendix
    def _get_FiniteAutomaton(self):    	return self._parent.FSA.FiniteAutomaton
    def _get_SolveFSA(self):    	return self._parent.RE.SolveFSA
    def _get_Cat(self):		    	return self._parent.Cat

    # Main exported interface is the lke method
    # which provides a context for the LeftKanExtension class.

    def lke(self, A, B, R, X, F):
	return LeftKanExtension(self, A, B, R, X, F)

    # Other functions - examples of applications of Kan extension
    # in alphabetic order

    def arrows_map(self, cat, from_objects=0, coverage=1):
	if from_objects:
	    cat = cat.get_dual()

	A = self.Cat.Graph(cat.graph.objects, [])
	B = cat.graph
	R = cat.relations
	X = self.Cat.Functor(lambda x: [1], lambda x: lambda y:y)
	F = self.Cat.Functor(lambda x: x, lambda x: [])
	ke = self.lke(A, B, R, X, F)

	memo = {}

	def get_arrows(object):
	    if object in memo:
		return memo[object]
	    re = ke.K.fo[object].re.rempretup()
	    if from_objects:
		re = re.reversed()
	    if str(coverage).startswith('length'):
		maxlen = int(coverage[6:])
		ar = []
		xs = re.get_words_memo()
		for i in range(1, maxlen+1):
		    ar.extend([tuple(x) for x in xs.get_words_of_length(i)])
	    else:
		re = re.limited(coverage)
		xs = re.sequni()
		ar = [tuple(x) for x in xs]
	    memo[object] = ar
	    return ar

	return self.Cat.Function(
	    get_arrows,
	    src = ke.K.fo.src,
	    tgt = None
	    )

    def category_tester(self, functor, arrows=None, coverage=1):
	if isinstance(functor, tuple):
	    fo, fa, src = functor
	    if fo is None:
		fo = lambda x:lambda y:1
	    functor = self.Cat.Functor(fo, fa, src)
	if arrows is None:
	    arrows = self.arrows_map(functor.src, from_objects=1, coverage=coverage)
	return CategoryTester(self, functor, arrows)

    def coequalizer(self, S0, S1, f0, f1):
	# Given
	#
	# S0, S1 sets (objects that can be iterated over)
	# f0, f1 functions from S0 to S1
	#
	# Return a coequalizing function,
	# such that in the following diagram:

	#
	#  S0 ===== S0
	#  |	    |
	#  | f0	    | f1
	#  |	    |
	#  V	    V
	#  S1 ===== S1 ==== coequalizing_function.src
	#  |
	#  | coequalizing_function
	#  |
	#  V
	#  coequalizing_function.tgt

	# both paths from S0 to coequalizing_function.tgt will be equivalent,
	# and coequalizing_function.tgt is a colimit of all such sets.
	#
	# The coequalizing_function object is callable with
	# an argument from S1, and has the following attributes:
	#   .src		is identical to S1
	#   .tgt		is a set in iterable form
	#   .asdict()		returns a dict representing the mapping

	objects = [0, 1]
	arrows = {'a0':(0, 1), 'a1': (0, 1)}
	A = self.Cat.Graph(objects, arrows)

	Xo = self.Cat.Function({0:S0, 1:S1}, objects, [S0,S1])
	Xa = self.Cat.Function({'a0':f0, 'a1':f1}, arrows, [f0,f1])
	X = self.Cat.Functor(Xo, Xa)

	colimit_object, colimit_functions = self.colimit(A, X)
	return colimit_functions[1]

    def colimit(self, A, X):
	# According to 9.6 in (ref.251)

	B = self.Cat.Graph([0], {})
	R = []
	F = self.Cat.Functor(lambda x: 0, lambda x: ())

	lka = self.lke(A, B, R, X, F)

	colimit_object = lka.KB[0]
	colimit_functions = lka.nat

	# Reduce elements to a smaller (but isomorphic) form
	# I.E since elements are all of the form
	#	((A, X),)
	# they can be reduced to the form
	#   	(A, X)
	#

	colimit_object = [x[0] for x in colimit_object]

	colimit_functions = dict([
	    (A, self.Cat.Function(
		dict([(a, k[0])
		      for (a, k) in cof.items()]),
		cof.src,
		colimit_object,
		)
	     )
	    for (A, cof) in colimit_functions.items()])


	return colimit_object, colimit_functions

    def test_arrows(self, functor, object, value):
	# Application of arrow listing to test sequencing
	# Discussed in Notes Mar 9 2005

	tester = self.category_tester(functor)
	return tester.test_object(object, value)
