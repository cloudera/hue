#._cv_part guppy.etc.RE

from guppy.etc.RE_Rect import chooserects
from guppy.etc.IterPermute import iterpermute

class InfiniteError(Exception):
    pass

class WordsMemo:
    def __init__(self, re, ch):
	self.re = re
	self.ch = ch
	self.xs = {}
	self.N = 0

    def get_words_of_length(self, N):
	# Return a list of words of length up to N
	if N not in self.xs:
	    self.xs[N] = self.re.get_words_of_length_memoized(N, self)
	return self.xs[N]
    

    def get_words_of_length_upto(self, N):
	# Return all words of length up to N, in the form
	# [(0, <list of words of length 0>),
	#  (1, <list of words of length 0>),
	#  ...]
	xsu = []
	for i in range(N+1):
	    xs = self.get_words_of_length(i)
	    if xs:
		xsu.append((i, xs))
	return xsu

REBASE = tuple

class RE(REBASE):
    # Regular expression nodes
    # The operators are choosen to be compatible with Pythonic standards:
    #	o sets     	     : using | for union
    #   o strings, sequences : using + for concatenation.
    #
    # This differs from mathematical presentations of regular
    # expressions where + is the union, but it seemed more important
    # to not confuse the Python usage.

    # There are also operators for closure x*, x+ that can not be
    # represented directly in Python expressions and these were choosen
    # to use a function call syntax.
    # The following table summarizes the operators.

    #   RE node expr	re lib		mathematical	name

    #   x + y		x y		x y		Concatenation
    #	x | y		x | y		x + y		Union
    #	x('*')		x*		x*		Kleene closure
    #	x('+')		x+		x+		Positive closure
    #	x('?')		x?				

    _re_special = r'.^$*+?{}\[]|()'
    def __add__(a, b):
	if isinstance(b, RE):
	    return concat(a, b)
	else:
	    return Concatenation(a, Single(b))

    def __call__(a, *args, **kwds):
	if not kwds:
	    if args == ('*',):
		return KleeneClosure(a)
	    elif args == ('+',):
		return PositiveClosure(a)
	    elif args == ('?',):
		return EpsilonOrOne(a)
	raise ValueError, "Argument to regular expression must be '*' or '+' or '?'"

    def __eq__(a, b):
	return (a._name == b._name and
		tuple(a) == tuple(b))
	    
    def __lt__(a, b):
	if a._name == b._name:
	    return tuple(a) < tuple(b)
	else:
	    return a._name < b._name
	    
    def __or__(a, b):
	return Union(a, b)

    def get_num_closures(self):
	ns = 0
	for ch in self:
	    ns += ch.get_num_closures()
	return ns

    def get_num_syms(self):
	ns = 0
	for ch in self:
	    ns += ch.get_num_syms()
	return ns

    def get_sum_sym_lengths(self):
	ns = 0
	for ch in self:
	    ns += ch.get_sum_sym_lengths()
	return ns

    def get_words_memo(self):
	ch = [x.get_words_memo() for x in self]
	return WordsMemo(self, ch)

    def get_words_of_length(self, N):
	xs = self.get_words_memo()
	return xs.get_words_of_length(N)

    def mapchildren(self, f):
	return self.__class__(*[f(x) for x in self])

    def regexpform(self):
	return self.mappedrepr(regexpname)

    def reversed(self):
	return self.mapchildren(lambda x:x.reversed())

    def rempretup(self):
	def f(x):
	    if isinstance(x, Seq):
		if x is not Epsilon and isinstance(x[0], tuple):
		    ws = x[1:]
		    return Seq(*ws)
		else:
		    return x
	    return x.mapchildren(f)

	return f(self)

    def seqatoms(self):
	sa = []
	self.apseqatoms(sa.append)
	return sa

    def sequni(self):
	d = {}
	us = []
	def ap(x):
	    if x not in d:
		d[x] = 1
		us.append(x)
	self.apseq(ap)
	return Union(*us)

    def shform(self, conc = ' '):
	r = self.mappedrepr(regexpname)
	if conc != ' ':
	    r = conc.join(r.split(' '))
	return r

    def simplified(self, *a, **k):
	return self

    def simulform(self):
	def f(x):
	    if x == '':
		return '()'
	    return str(x)
	return self.mappedrepr(f)


def regexpname(s):
    if s == '':
	return '()'
    special = RE._re_special
    ren = []
    for c in str(s):
	if c in special+"', ":
	    #c = r'\%s'%c
	    c = ''
	ren.append(c)
    return ''.join(ren)


def re_compare(a, b):
    return a.__cmp__(b)

class Seq(RE):
    _priority = 0
    _name = 'Seq'

    def __new__(clas, *symbols):
	if not symbols:
	    return Epsilon
	return REBASE.__new__(clas, symbols)

    def __repr__(self):
	return '%s(%s)'%(self.__class__.__name__, ', '.join(['%r'%(x,) for x in self]))

    def __hash__(self):
        return hash(repr(self))

    def apseq(self, ap):
	ap(self)

    def apseqatoms(self, ap):
	for x in self:
	    ap(Single(x))

    def get_num_closures(self):
	return 0

    def get_num_syms(self):
	return len(self)

    def get_sum_sym_lengths(self):
	s = 0
	for x in self:
	    s += len(str(x))
	return s

    def get_words_memo(self):
	return WordsMemo(self, ())

    def get_words_of_length_memoized(self, N, memo):
	if N == len(self):
	    return [self]
	else:
	    return []

    def limited(self, N):
	return self

    def mappedrepr(self, f):
	if not self:
	    return f('')
	return ' '.join(['%s'%(f(x),) for x in self])

    def reversed(self):
	r = list(self)
	r.reverse()
	return self.__class__(*r)

    def unionsplitted(self):
	return [self]

def Single(symbol):
    return REBASE.__new__(Seq, (symbol,))

Epsilon = REBASE.__new__(Seq, ())

def concat(*args):
    args = [x for x in args if x is not Epsilon]
    if len(args) < 2:
	if not args:
	    return Epsilon
	return args[0]
    return REBASE.__new__(Concatenation, args)
    

class Concatenation(RE):
    _priority = 2
    _name = 'Concat'

    def __new__(clas, *args):
	#assert Epsilon not in args
	if len(args) < 2:
	    if not args:
		return Epsilon
	    return args[0]
	return REBASE.__new__(clas, args)

    def __repr__(self):
	rs = []
	for ch in self:
	    r = '%r'%(ch,)
	    if ch._priority > self._priority:
		r = '(%s)'%(r,)
	    rs.append(r)
	return ' + '.join(rs)

    def apseq(self, ap):
	uns = [x.sequni() for x in self]
	ixs = [0]*len(uns)
	while 1:
	    xs = []
	    for (i, us) in enumerate(uns):
		for x in us[ixs[i]]:
		    if x is not Epsilon:
			xs.append(x)
	    ap(Seq(*xs))
	    j = 0
	    for j, ix in enumerate(ixs):
		ix += 1
		if ix >= len(uns[j]):
		    ix = 0
		ixs[j] = ix
		if ix != 0:
		    break
	    else:
		break

    def apseqatoms(self, ap):
	for x in self:
	    x.apseqatoms(ap)

    def get_words_of_length_memoized(self, N, memo):
	chxs = []
	for ch in memo.ch:
	    chxs.append(ch.get_words_of_length_upto(N))
	xs = []
	seen = {}

	def ads(xx, i, n):
	    if i == len(chxs):
		if n == N:
		    for toconc in iterpermute(*xx):
			conc = simple_Concatenation(toconc)
			if conc not in seen:
			    xs.append(conc)
			    seen[conc] = 1
	    else:
		for m, x in chxs[i]:
		    if n + m <= N:
			ads(xx + [x], i + 1, n + m)
		
        ads([], 0, 0)
	return xs
			  

    def limited(self, N):
	return Concatenation(*[x.limited(N) for x in self])

    def mappedrepr(self, f):
	rs = []
	for ch in self:
	    r = ch.mappedrepr(f)
	    if ch._priority > self._priority:
		r = '(%s)'%(r,)
	    rs.append(r)
	return ' '.join(rs)

    def reversed(self):
	r = [x.reversed() for x in self]
	r.reverse()
	return self.__class__(*r)

    def simplified(self, *a, **k):
	conc = [x.simplified(*a, **k) for x in self]
	sa = []
	for c in conc:
	    for a in c.seqatoms():
		sa.append(a)
	return simple_Concatenation(sa)

    def unionsplitted(self):
	runs = []
	uns = []
	for (i, x) in enumerate(self):
	    us = x.unionsplitted()
	    if len(us) > 1:
		uns.append((i, us))
	if not uns:
	    return [self]
	ixs = [0]*len(uns)
	ch = list(self)
	while 1:
	    xs = []
	    i0 = 0
	    for j, (i, us) in enumerate(uns):
		xs.extend(ch[i0:i])
		ix = ixs[j]
		xs.append(us[ix])
		i0 = i + 1
	    xs.extend(ch[i0:])
	    runs.append( concat(*xs) )

	    j = 0
	    for j, ix in enumerate(ixs):
		ix += 1
		if ix >= len(uns[j][1]):
		    ix = 0
		ixs[j] = ix
		if ix != 0:
		    break
	    else:
		return runs


class SimplifiedConcatenation(Concatenation):    
    def simplified(self, *a, **k):
	# pdb.set_trace()
	return self


def conclosure(conc):
    # Simplification noted Mar 5 2005
    # Simplify ... b b* ... or ... b* b ... to ... b+ ...
    # conc is a sequence of regular expressions

    seen = {}
    nconc = []
    w0 = None
    for w in conc:
	if w0 is not None:
	    if (w._name == '*' and	# Not isinstance(KleeneClosure), would catch PositiveClosure
		w[0] == w0):
		w = PositiveClosure(w0)
	    elif (w0._name == '*' and
		  w0[0] == w):
		w = PositiveClosure(w)
	    else:
		if w0 is not None:
		    nconc.append(w0)
	w0 = w
    if w0 is not None:
	nconc.append(w0)
    return nconc


def simple_Concatenation(conc):
    if len(conc) > 1:
	conc0 = conc
	conc = conclosure(conc)
    nconc = []
    i = 0
    j = 0
    while i < len(conc):
	e = conc[i]
	if not isinstance(e, Seq):
	    i += 1
	    nconc.append(e)
	    continue
	j = i
	while j < len(conc):
	    if not isinstance(conc[j], Seq):
		break
	    j += 1
	if j == i + 1:
	    nconc.append(e)
	else:
	    syms = []
	    for k in range(i, j):
		e = conc[k]
		syms.extend(list(e))
	    nconc.append(Seq(*syms))
	i = j
    if len(nconc) > 1:
	return Concatenation(*nconc)
    elif nconc:
	return nconc[0]
    else:
	return Epsilon

gauges = [
    lambda x:x.get_num_syms(),
    lambda x:x.get_num_closures(),
    lambda x:x.get_sum_sym_lengths()
    ]


def simpleunion(lines, trace=''):
    choosen = chooserects(lines, gauges, trace)
    have_epsilon = 0
    while 1:
	if len(choosen) == 1 and (choosen[0].width == 0 or len(choosen[0].lines) == 1):
	    us = []
	    for line in choosen[0].lines:
		if line:
		    us.append(line)
		else:
		    have_epsilon = 1
	    break
	us = []
	for r in choosen:
	    conc = r.get_common_part()
	    olines = r.get_uncommons()
	    u = simpleunion(olines)
	    if u is not Epsilon:
		if r.dir == -1:
		    conc = [u]+conc
		else:
		    conc = conc + [u]
	    if conc:
		us.append(conc)
	    else:
		have_epsilon = 1
	    assert not isinstance(us[-1], str)

	choosen = chooserects(us, gauges, trace)

    if len(us) > 1:
	nus = [simple_Concatenation(line) for line in us]
	u = SimplifiedUnion(*nus)
    elif us:
	u = simple_Concatenation(us[0])
    else:
	u = None
    if have_epsilon:
	if u is not None:
	    u = simple_EpsilonOrOne(u)
	else:
	    u = Epsilon

    return u



class Union(RE):
    _priority = 3
    _name = 'Union'

    def __new__(clas, *args):
	return REBASE.__new__(clas, args)

    def __repr__(self):
	rs = []
	for ch in self:
	    r = '%r'%(ch,)
	    if ch._priority > self._priority:
		r = '(%s)'%r
	    rs.append(r)
	return ' | '.join(rs)

    def apseq(self, ap):
	for c in self:
	    c.apseq(ap)

    def apseqatoms(self, ap):
	for x in self:
	    x.apseqatoms(ap)

    def get_words_of_length_memoized(self, N, memo):
	xs = []
	seen = {}
	for ch in memo.ch:
	    for x in ch.get_words_of_length(N):
		if x not in seen:
		    seen[x] = 1
		    xs.append(x)
	return xs

    def limited(self, N):
	uni = [x.limited(N) for x in self]
	for i, x in enumerate(uni):
	    if x is not self[i]:
		return self.__class__(*uni)
	return self

    def mappedrepr(self, f):
	rs = []
	for ch in self:
	    r = '%s'%(ch.mappedrepr(f),)
	    if ch._priority > self._priority:
		r = '(%s)'%r
	    rs.append(r)
	return ' | '.join(rs)

    def simplified(self, args=None, trace='', *a, **k):
	if args is None:
	    args = [x.simplified() for x in self.unionsplitted()]
	    #args = [x for x in self.unionsplitted()]

	# Create a simplfied union
	# Assuming args are simplified, non-unions

	ch = [a.seqatoms() for a in args]
	return simpleunion(ch, trace)

    def unionsplitted(self):
	us = []
	for x in self:
	    us.extend(list(x.unionsplitted()))
	return us

class SimplifiedUnion(Union):
    def simplified(self, *a, **k):
	return self

class Called(RE):
    _priority = 1

    def __new__(clas, arg):
	return REBASE.__new__(clas, (arg,))

    def __repr__(self):
	ch = self[0]
	r = '%r'%(ch,)
	if ch._priority > self._priority:
	    r = '(%s)'%r
	return "%s(%r)"%(r, self._name)

    def apseqatoms(self, ap):
	ap(self)

    def get_num_closures(self):
	return 1 + self[0].get_num_closures()

    def mappedrepr(self, f):
	ch = self[0]
	r = ch.mappedrepr(f)
	if (ch._priority > self._priority
	    or isinstance(ch, Seq) and len(ch) > 1):
	    r = '(%s)'%r
	return "%s%s"%(r, self._name)

    def simplified(self, *a, **k):
	return self.__class__(self[0].simplified(*a, **k))

class Closure(Called):
    def get_words_of_length_memoized(self, N, memo):
	if N == 0:
	    return [Epsilon]
	if N == 1:
	    return memo.ch[0].get_words_of_length(1)
	xs = []
	seen = {}
	for i in range(1, N):
	    a = memo.get_words_of_length(i)
	    b = memo.get_words_of_length(N-i)
	    for ai in a:
		for bi in b:
		    aibi = simple_Concatenation((ai, bi))
		    if aibi not in seen:
			xs.append(aibi)
			seen[aibi] = 1
	for x in memo.ch[0].get_words_of_length(N):
	    if x not in seen:
		xs.append(x)
		seen[x] = 1
	return xs

    def unionsplitted(self):
	return [self]

class KleeneClosure(Closure):
    _name = '*'

    def apseq(self, ap):
	raise InfiniteError, 'apseq: Regular expression is infinite: contains a Kleene Closure'

    def limited(self, N):
	if N == 0:
	    return Epsilon
	cl = self[0].limited(N)
	uni = []
	for i in range(N+1):
	    toconc = [cl]*i
	    uni.append(Concatenation(*toconc))
	return Union(*uni)

    def simplified(self, *a, **k):
	return simple_KleeneClosure(self[0].simplified(*a, **k))


def simple_KleeneClosure(x):
    # (b+)* -> b*
    if x._name == '+':
	return simple_KleeneClosure(x[0])
    return KleeneClosure(x)

class PositiveClosure(Closure):
    _name = '+'

    def apseq(self, ap):
	raise InfiniteError, 'apseq: Regular expression is infinite: contains a Positive Closure'

    def apseqatoms(self, ap):
	self[0].apseqatoms(ap)
	simple_KleeneClosure(self[0]).apseqatoms(ap)

    def get_words_of_length_memoized(self, N, memo):
	if N <= 1:
	    return memo.ch[0].get_words_of_length(N)
	return Closure.get_words_of_length_memoized(self, N, memo)

    def limited(self, N):
	a = self[0].limited(N)
	b = KleeneClosure(self[0]).limited(N)
	return Concatenation(a, b)
	

class EpsilonOrOne(Called):
    _name = '?'

    def apseq(self, ap):
	ap(Epsilon)
	self[0].apseq(ap)

    def get_words_of_length_memoized(self, N, memo):
	if N == 0:
	    return [Epsilon]
	return memo.ch[0].get_words_of_length(N)

    def limited(self, N):
	x = self[0].limited(N)
	if x is not self[0]:
	    self = self.__class__(x)
	return self

    def simplified(self, *a, **k):
	return simple_EpsilonOrOne(self[0].simplified(*a, **k))

    def unionsplitted(self):
	return [Epsilon] + list(self[0].unionsplitted())

def simple_EpsilonOrOne(x):
    # (a+)? -> a*
    
    if x._name == '+':
	return simple_KleeneClosure(x)

    # (a*)? -> a*
    if x._name == '*':
	return x

    return EpsilonOrOne(x)

class RegularSystem:

    def __init__(self, table, Start, final_states):
	self.table = table
	self.Start = Start
	self.Final = '358f0eca5c34bacdfbf6a8ac0ccf84bc'
	self.final_states = final_states

    def pp(self):

	def statename(state):
	    try:
		name = self.names[state]
	    except KeyError:
		name = str(state)
	    return name

	def transname(trans):
	    name = trans.simulform()
	    if trans._priority > 1:
		name = '(%s)'%(name,)
	    return name
	    
	self.setup_names()

	X = self.X
	
	xs = [self.Start]+self.order
	xs.append(self.Final)
	for Xk in xs:
	    if Xk not in X:
		continue
	    print '%3s = '%(statename(Xk),),
	    Tk = X[Xk]
	    es = []
	    for Xj in xs:
		if Xj in Tk:
		    es.append('%s %s'%(transname(Tk[Xj]), statename(Xj)))
	    if es:
		print ' | '.join(es)
	    else:
		print

    def setup_equations(self):
	table = self.table
	final_states = self.final_states
	Final = self.Final
	self.X = X = {Final:{}}
	for Xi, transitions in table.items():
	    X[Xi] = Ti = {}
	    for (symbol, Xj) in transitions.items():
		Ti.setdefault(Xj, []).append(Single(symbol))
	    for Xj, Aij in Ti.items():
		if len(Aij) > 1:
		    Aij.sort()
		    Aij = Union(*Aij)
		else:
		    Aij = Aij[0]
		Ti[Xj] = Aij
	    if Xi in final_states:
		Ti[Final] = Epsilon

    def setup_order(self):
	def dists(X, start):
	    i = 0
	    S = {start:i}
	    news = [start]
	    while news:
		oldnews = news
		news = []
		i += 1
		for s in oldnews:
		    if s not in X:
			continue
		    for t in X[s]:
			if t not in S:
			    news.append(t)
			    S[t] = i
	    return S

	def start_distance(x):
	    return start_dists[x]

	def sumt(f):
	    memo = {}
	    def g(x):
		if x in memo:
		    return memo[x]
		s = 0.0
		for y in X[x]:
		    s += f(y)
		memo[x] = s
		return s
	    return g
	    
	def cmp3(x, y):
	    # Comparison for the sorting of equation solving order
	    # First in list = solved last

	    if x is y:
		return 0

	    c = cmp(len(X[y]), len(X[x])) # Equations with more terms are resolved later
	    if c:
		return c

	    # The equations with terms more distant from start node will be resolved earlier
	    i = 0
	    while i < 10: # 4 was enough with tests so far at Feb 24 2005
		try:
		    f = sumdists[i]
		except:
		    f = sumt(sumdists[i-1])
		    sumdists.append(f)
		c = cmp(f(x), f(y))
		if c:
		    return c
		i += 1

	    #pdb.set_trace()
	    return cmp(x, y)

	sumdists = [start_distance]
	X = self.X
	Start = self.Start
	Final = self.Final
	start_dists = dists(X, Start)
	order = [x for x in start_dists if x is not Start and x is not Final]
	order.sort(cmp3)
	self.order = order

    def setup_names(self):
	try:
	    self.order
	except AttributeError:
	    self.setup_order()
	self.names = {}
	self.names[self.Start] = 'X0'

	for i, s in enumerate(self.order):
	    self.names[s] = 'X%d'%(i+1)
	self.names[self.Final] = 'Final'


    def solve(self):
	# Set up equation system

	self.setup_equations()
	self.setup_order()

	X = self.X
	Start = self.Start
	Final = self.Final
	todo = list(self.order)

	# Solve equation system

	while todo:
	    Xk = todo.pop()
	    Tk = X[Xk]

	    if Xk in Tk:
		# Recursive equation
		# Eliminate Akk Xk, using Adler's theorem
		# Given:
		# Xk = Ak0 X0 | ... Akk Xk |.. Akn Xkn
		# we get:
		# Xk = Akk* (Ak0 X0 | ... <no Xk> ... | Akn Xn)
		# which we evaluate to:
		# Xk = Bk0 X0 | ... Bkn Xn
		# where coefficients get the new values
		# Bki := Akk* Aki
		
		Akk = Tk[Xk]
		del Tk[Xk]

		AkkStar = Akk('*')
		for Xi, Aki in Tk.items():
		    Bki = AkkStar + Aki
		    Tk[Xi] = Bki


	    # Substitute Xk in each other equation in X
	    # containing Xk, except eqv. Xk itself, which will not be used any more..

	    del X[Xk]

	    for Xj, Tj in X.items():
		Bjk = Tj.get(Xk)
		if Bjk is None:
		    continue
		del Tj[Xk]
		for Xji, Tk_Xji in Tk.items():
		    Cji = (Bjk + Tk_Xji)
		    Bji = Tj.get(Xji)
		    if Bji is not None:
			Cji = Bji | Cji
		    Tj[Xji] = Cji

	# The equation system is now solved
	# The result is in Final term of Start equation

	return X[Start][Final]

Nothing = Union()

def SolveFSA(fsa):
    RS = RegularSystem(fsa.table, fsa.start_state, fsa.final_states)
    return RS.solve()

