#._cv_part guppy.heapy.AbstractAlgebra

class AA:
    def __mul__(self, other):
	return BOAPP('op', self, other)

    def __add__(self, other):
	return BOAPP('op2', self, other)

    def __eq__(self, other):
	return BOAPP('eq', self, other)

class ANAME(AA):
    def __init__(self, name):
	self.name = name

    def __str__(self):
	return self.name

class BOAPP(AA):
    def __init__(self, funcname, *args):
	self.funcname = funcname
	self.args = args

    def __str__(self):
	return '%s(%s)'%(self.funcname, ','.join([str(x) for x in self.args]))

class AlgebraicStructure:
    def __init__(self, mod, range, *ops, **kwds):
	self.mod = mod
	self.range = range
	self.ops = []
	for i, op in enumerate(ops):
	    if hasattr(op, 'range') and op.range == range:
		pass
	    elif callable(op) or op in mod.LE.binary_operation_name:
		opkwds = {}
		if 'identity' in kwds:
		    opkwds['identity'] = kwds['identity']
		op = mod.binary_operation.new(range, op, **opkwds)
	    else:
		raise TypeError, '%s is not a valid operation'%op
	    self.ops.append(op)
	    setattr(self, 'op%d'%i, op)
	self.numops = len(self.ops)

	for k, v in kwds.items():
	    setattr(self, k, v)

				
    def eq(self, x, y, *more):
	if not x == y:
	    return False
	for m in more:
	    if not y == m:
		return False
	return True


class BinaryOperation:
    def __init__(self, range, op, identity=None, invert=None, zeros=None, zero=None, complement=None):
	self.range = range
	self.arity = 2
	if isinstance(op, str):
	    opname = op
	    func = eval('lambda x,y: x %s y'%opname)
	elif callable(op):
	    func = op
	    opname = str(func)
	self.opname = opname
	self.__call__ = func
	if identity is not None:
	    self.identity = identity
	if invert is not None:
	    self.invert = invert
	if zeros is not None:
	    self.zeros = zeros

	if zero is not None:
	    self.zero = zero

	if complement is not None:
	    self.complement = complement

	# mimic alg. st.

	self.op0 = self

    def eq(self, x, y, *more):
	if not x == y:
	    return False
	for m in more:
	    if not y == m:
		return False
	return True

class BinaryAlgebraicStructureFamily:
    def __call__(self, names, cond):
	di = {}
	for name in names:
	    di[name] = ANAME(name)
	c = eval(cond, di)
	assert isinstance(c, AA)
	
	def gentestfunc(binop):
	    d = {'op':binop}
	    expr = 'lambda %s:%s'%(','.join(names), c)
	

	    d = {'op':binop,
		 'eq': lambda x,y: x==y}

	    f = eval (expr, d)
				  
	    def testfunc(env, x, y):
		if not f(x, y):
		    return env.failed('not %s in %s'%((x, y), expr))
		return True

	    return testfunc
	return self.Set(self, (gentestfunc, cond))


    def c_test_contains(self, a, b, env):
	f, name = a.arg
	return env.forall_pairs(b.range,
				f(b),
				'not in %s'%name)

class TernaryAlgebraicStructureFamily:
    def __call__(self, names, cond):
	di = {}
	for name in names:
	    di[name] = ANAME(name)
	c = eval(cond, di)
	assert isinstance(c, AA)
	
	def gentestfunc(binop):
	    d = {'op':binop}
	    expr = 'lambda %s:%s'%(','.join(names), c)
	

	    d = {'op':binop,
		 'eq': lambda x,y: x==y}

	    f = eval (expr, d)
				  
	    def testfunc(env, x, y, z):
		if not f(x, y, z):
		    return env.failed('not %s in %s'%((x, y, z), expr))
		return True

	    return testfunc
	return self.Set(self, (gentestfunc, cond))


    def c_test_contains(self, a, b, env):
	f, name = a.arg
	return env.forall_triples(b.range,
				  f(b),
				  'not in %s'%name)

class DistributiveAlgebraicStructureFamily:
    def __call__(self, names, cond):
	di = {}
	for name in names:
	    di[name] = ANAME(name)
	c = eval(cond, di)
	assert isinstance(c, AA)
	
	def gentestfunc(binop1, binop2):
	    d = {'op':binop1, 'op2': binop2}
	    expr = 'lambda %s:%s'%(','.join(names), c)
	

	    d = {'op':binop1,
		 'op2':binop2,
		 'eq': lambda x,y: x==y}

	    f = eval (expr, d)
				  
	    def testfunc(env, x, y, z):
		if not f(x, y, z):
		    return env.failed('not %s in %s'%((x, y, z), expr))
		return True

	    return testfunc
	return self.Set(self, (gentestfunc, cond))


    def c_test_contains(self, a, b, env):
	f, name = a.arg
	op1, op2 = b
	if isinstance(op1, tuple):
	    op1 = self.specmod.AA.binary_operation.new(*op1)
	if isinstance(op2, tuple):
	    op2 = self.specmod.AA.binary_operation.new(*op2)
	if not op1.range == op2.range:
	    return env.failed('Not the same range')
	return env.forall_triples(op1.range,
				  f(op1, op2),
				  'not in %s'%name)


class _GLUECLAMP_:
    def _get_abelian_group(self):
	return self.Spec.adaptuple(
	    self.group.new,
	    self.group & self.Spec.attr('op0', self.commutative))

    def _get_associative(self):
	return self.asuf('xyz', 'x * (y * z) == (x * y) * z')
	
    def algestruct(self, S, *args, **kwds):
	S = self.Spec.setcast(S)
	return AlgebraicStructure(self, S, *args, **kwds)

    def asuf(self, names, cond):
	if len(names) == 2:
	    x = self.BinaryAlgebraicStructure(names, cond)
	elif len(names) == 3:
	    x = self.TernaryAlgebraicStructure(names, cond)
	else:
	    raise ValueError
	return self.Spec.adaptuple(self.binary_operation.new, x)

    def _get_binary_operation(self):
	def binop(S, func, **kwds):
	    S = self.Spec.setcast(S)
	    if isinstance(func, BinaryOperation) and func.range == S and not kwds:
		return func
	    return BinaryOperation(S, func, **kwds)

	e = self.Spec
	return e.adaptuple(
	    binop, 
	    e.expset("""(
	        attr('range', set) &
		attr('arity', equals(2)) &
		expset('''mapping(range, range, '->', range)''', 'range')
	)"""))

    def _get_binary_relation(self):
	return self.relation

    def _get_BinaryAlgebraicStructure(self):
	return self.family(BinaryAlgebraicStructureFamily)

    def _get_boolean_algebra(self):
	def boolalg(set, op0, op1, complement, id0, id1):
	    if complement in ('~', '-', 'not'):
		complement = eval('lambda x: %s x'%complement)
	    return self.algestruct(
		set,
		self.binary_operation.new(set, op0, identity = id0, zero = id1, complement=complement),
		self.binary_operation.new(set, op1, identity = id1, zero = id0, complement=complement)
		)

	e = self.Spec
	return (e.adaptuple(
	    boolalg,
	    e.attr('op0', e.AA.commutative & e.AA.complemented & e.AA.monoid) &
	    e.attr('op1', e.AA.commutative & e.AA.complemented & e.AA.monoid) &
	    e.attr(('op0', 'op1'), e.AA.distributive) &
	    e.attr(('op1', 'op0'), e.AA.distributive) &
	    e.attr(('op0.zero', 'op1.identity'), e.LE.eq) &
	    e.attr(('op1.zero', 'op0.identity'), e.LE.eq)
	    ))


    def _get_complemented(self):
	# Not a standard term: expresses for an op op, that
	# x op x' = op.zero where x' = op.complement
	def p(env, x):
	    op = x.op0
	    zero = op.zero
	    f = op
	    complement = f.complement
	    return env.forall(x.range, lambda env, y:
			      x.eq(f(y, complement(y)), zero), 'complemented')
	return self.Spec.predicate(p, 'complemented')
	      

    def _get_commutative(self):
	return self.asuf('xy', 'x * y == y * x')
	
    def _get_DistributiveAlgebraicStructure(self):
	return self.family(DistributiveAlgebraicStructureFamily)

    def _get_distributive(self):
	return self.distributive_1 & self.distributive_2

    def _get_distributive_1(self):
	return self.DistributiveAlgebraicStructure(
	    'xyz', 'x * (y + z) == (x * y) + (x * z)')

    def _get_distributive_2(self):
	return self.DistributiveAlgebraicStructure(
	    'xyz', '(x + y) * z == (x * z) + (y * z)')

    def _get_field(self):
	e = self.Spec
	AA = self

	class Field:
	    def __init__(self, S, add, mul, neg, invert, zero, one):
		if neg in ('-','~','not'):
		    neg = eval('lambda x: %s x'%neg)

		self.range = S
		self.ring = AA.ring.new(S, add, mul, neg, zero)
		self.mulgroup = AA.group.new(S - e.equals(zero), mul, invert, one)

	return e.adaptuple(
	    Field,
	    e.attr('ring', e.AA.ring) &
	    e.attr('mulgroup', e.AA.abelian_group))

    def _get_group(self):
	def mkgroup(S, op, invert, identity):
	    if invert in ('-', '~', 'not'):
		invert = eval('lambda x: %s x'%invert)
	    return self.algestruct(S, op, identity=identity, invert=invert)
	    
	def p(env, g):
	    try:
		inv = g.invert
	    except AttributeError:
		env.failed("no invert function")
	    f = g.op0
	    return env.forall(g.range, lambda env, x:
			      g.eq(f(inv(x), x), f(x, inv(x)), g.identity))

	e = self.Spec
	return e.adaptuple(
	    mkgroup,
	    self.monoid & self.Spec.predicate(p, 'group'))
	

    def _get_latticeform(self):
	# latticeform is a representation category
	
	class RelationSpec:

	    def _get_spec_quadruple(self, e):
		binop = (e.boolean << (e.PyObject, e.PyObject) |
			 e.AA.LE.binary_operation_name)
		return e.cprod(
		    e.LE.setcastable,
		    e.relation.fuop,
		    binop,
		    binop)
		    
	    def _get_spec_struct(self, e):
		return (attr('range', e.set),
			attr('LE'),
			attr('GLB'),
			attr('LUB')
			)

	    def map_quadruple_to_struct(self, e, (S, LE, GLB, LUB)):
		S = e.setcast(S)
		LE = e.relation.paxa.fromuniversal((e.relation.defipair, (S, LE)))
		GLB = e.AA.binary_operation.new(S, GLB)
		LUB = e.AA.binary_operation.new(S, LUB)

		class C:
		    pass
		c = C()
		c.range = S
		c.LE = LE
		c.GLB = GLB
		c.LUB = LUB
		return c
		
	return self.Spec.repcat(RelationSpec)

    def _get_lattice(self):
	e = self.Spec

	def p(env, lat):
	    def test(R, op, name):
		def testlb(env, x, y):
		    lb = op(x, y)
		    if not (R(lb, x) and R(lb, y)):
			return env.failed('not an %s'%name)
		    if R(x, lb) or R(y, lb):    return True # redundant fast way out

		    return env.forall(lat.range,
			       lambda env, lb2:
			       (not (R(lb2, x) and R(lb2, y)) or
				R(lb2, lb)))
		return env.forall_pairs(lat.range, testlb)

	    return (test( lambda x, y: env.contains(lat.LE, (x, y)), lat.GLB, 'lower bound') and
		    test( lambda x, y: env.contains(lat.LE, (y, x)), lat.LUB, 'upper bound'))


	return (
	    e.abstractset(
		self.latticeform.struct.fromuniversal,
		e.attr('range') &
		e.attr('LE', e.AA.partial_order.paxa) &
		e.attr('GLB', e.AA.binary_operation) &
		e.attr('LUB', e.AA.binary_operation) &
		e.predicate(p, 'lattice')
		)
	    )

    def _get_LE(self):
	return self.Spec.LocalEnv(self.Spec, self._Specification_.LocalEnvExpr)

    def _get_monoid(self):
	def p(env, x):
	    op = x.op0
	    e = op.identity
	    f = op
	    return env.forall(x.range, lambda env, y:
			      x.eq(f(e, y), f(y, e), y))
	def mkmonoid(S, op, identity):
	    return self.algestruct(S, op, identity=identity)

	e = self.Spec
	return e.adaptuple(
	    mkmonoid,
	    e.attr('op0', self.associative) &
	    e.predicate(p, 'monoid'))

	
    def _get_ring(self):
	def mkring(S, add, mul, neg, zero):
	    if neg in ('-','~','not'):
		neg = eval('lambda x: %s x'%neg)
	    return self.algestruct(
		S,
		self.binary_operation.new(S, add, identity=zero, invert=neg),
		self.binary_operation.new(S, mul))

	e = self.Spec
	return (e.adaptuple(
	    mkring,
	    (e.attr('op0', e.AA.abelian_group) &
	     e.attr('op1', e.AA.semigroup) &
	     e.attr(('op1', 'op0'), e.AA.distributive)
	     )))

    def _get_semigroup(self):
	return self.Spec.adaptuple(self.binary_operation.new, self.Spec.attr('op0', self.associative))

    def _get_Spec(self):
	return self._parent.Spec

    def _get_TernaryAlgebraicStructure(self):
	return self.family(TernaryAlgebraicStructureFamily)

    def family(self, F):
	class C(F, self.Spec.SpecFamily):
	    def __init__(innerself, *args, **kwds):
		self.Spec.SpecFamily.__init__(innerself, *args, **kwds)
		try:
		    ini = F.__init__
		except AttributeError:
		    pass
		else:
		    ini(innerself, *args, **kwds)
	C.__name__ = F.__name__
	return self.Spec.family(C)

    # 
    # 2. Relations and their properties
    #

    def relpropred(self, s, name):
	return self.relprop(self.Spec.predicate(s, name))

    def _get_antisymmetric(self):
	# Assumes implicitly equality relation via '==' operation.
	# Could be generalized, see notes Jan 19 2005
	return self.relpropred(
	    lambda env, R: env.forall_pairs(
		R.range,
		lambda env, x, y:
		(not (env.contains(R, (x, y)) and env.contains(R, (y, x))) or
		 x == y)),
	    "antisymmetric wrt '==' op")

    def _get_equivalence_relation(self):
	return (
	    self.reflexive &
	    self.symmetric &
	    self.transitive)

    def _get_irreflexive(self):
	return self.relpropred(
	    lambda env, R: env.forall(R.range,
				      lambda env, x: env.test_contains_not(R, (x, x), 'irrreflexive')),
	    'reflexive')
	

    def _get_partial_order(self):
	return (
	    self.reflexive &
	    self.antisymmetric &
	    self.transitive)

    def _get_total_order(self):
	return (
	    self.partial_order &
	    self.total_relation)

    def _get_total_relation(self):
	# Nonstandard name (?)
	return self.relpropred(
	    lambda env, R: env.forall_pairs(
		R.range,
		lambda env, x, y:
		(env.contains(R, (x, y)) or env.contains(R, (y, x)))),
	    "total_relation: xRy or yRx for all x,y in A")



    def _get_reflexive(self):
	return self.relpropred(
	    lambda env, R: env.forall(
		R.range,
		lambda env, x: env.test_contains(R, (x, x), 'reflexive')),
	    'reflexive')

    def _get_symmetric(self):
	return self.relpropred(
	    lambda env, R: env.forall(
		R,
		lambda env, (x, y):
		env.test_contains(R, (y, x), 'symmetric')),
	    'symmetric')

    def _get_transitive(self):
	return self.relpropred(
	    lambda env, R: env.forall(
		R,
		lambda env, (x, y):
		env.forall(R.range,
			   lambda env, z:
			   (not env.contains(R, (y, z)) or
			    env.test_contains(R, (x, z), 'transitive')))),
	    'transitive')


    def relprop(self, s):
	e = self.Spec	
	return e.abstractset(
	    e.relation.paxa.fromuniversal,
	    s)

	return e.adaptuple(
	    self.relation.new,
	    e.attr(('domain', 'range'), e.LE.eq) &
	    s)


class _Specification_:
    """
        Specification of some general algebraic structures
    """

    def GetExamples(self, te, obj):
	AA = obj
	LE = AA.LE
	env = te.mod
	S3 = [
	    [0,1,2,3,4,5],
	    [1,0,4,5,2,3],
	    [2,5,0,4,3,1],
	    [3,4,5,0,1,2],
	    [4,3,1,2,5,0],
	    [5,2,3,1,0,4]]

	Type = env.Type
	asexs = [
    # Too slow now with many examples, cubic complexity for associative etc.
    # sets are tested more extensively elsewhere
    #(env.set, env.set, env.empty, ~env.empty, env.equals(0), env.equals(0, 1), env.equals(1)),
	    (env.set,		env.set, env.empty),
	    (env.Type.Int,	-1, 0, 1),
	    #(env.Type.Float,	-2.5,-1.0, 0.0, 1.3, 2.0),
	    #(env.Type.Float,	-2.0,-1.0, 0.0, 1.0, 2.0),
	    (env.Type.Float,	-1.0, 0.0),
	    (env.Type.String,	'', '1234%^', 'asdf*&('),
	    (LE.algebraic_class,AA.binary_operation),
	    (AA.binary_operation,
	     			(int, '*')),
	    (~AA.binary_operation,
	     			(env.equals(1), '+')),
	    (AA.commutative,	(int, '*')),
	    (~AA.commutative,	(int, '-')),
	    (AA.associative,	(int, '*')),
	    (~AA.associative,	(int, '-')),
	    (AA.distributive,	((int, '*'), (int, '-'))),
	    (AA.distributive_1, ((int, '*'), (int, '-'))),
	    (AA.distributive_2, ((int, '*'), (int, '-'))),
	    (~AA.distributive,	((int, '*'), (int, '|'))),
	    (~AA.distributive_1,((int, '*'), (int, '|'))),
	    (~AA.distributive_2,((int, '*'), (int, '|'))),
	    
	    (AA.semigroup, 	(int, '*')),
	    (AA.semigroup, 	(str, '+')),
	    (~AA.semigroup, 	(int, '-')),
	    (AA.monoid,		(int, '*', 1)),
	    (AA.monoid, 	(str, '+', '')),
	    (~AA.monoid, 	(int, '*', 0)),
	    (AA.group, 		(int, '+', '-', 0)),
	    (~AA.group, 	(int, '*', '-', 1)),
	    (AA.abelian_group,	(int, '+', '-', 0)),
	    (AA.group & ~AA.abelian_group, (
						env.equals(0,1,2,3,4,5),
						lambda x,y : S3[x][y],
						lambda x:[0,1,2,3,5,4][x],
						0)),
	    (AA.ring,		(int, '+', '*', '-', 0)),
	    (~AA.ring,		(str, '+', '*', '-', 0),
	     			(int, '*', '*', '-', 0),
				(int, '+', '+', '-', 0),
				(int, '+', '*', '~', 0),
				(int, '+', '*', '-', 1)),
	    (AA.field,		(float, '+', '*', '-', lambda x:1.0/x, 0.0, 1.0)),
	    (~AA.field,		(float, '+', '*', '-', lambda x:2.0/x, 0.0, 1.0)),
	    (AA.boolean_algebra,(env.equals(False, True), 'or', 'and', 'not', False, True),
	     			(int, '|', '&', '~', 0, ~0),
	     			(env.set, '|', '&', '~', env.empty, ~env.empty)
	     ),
	    (~AA.boolean_algebra,
	     # Mutate each argument..
				(env.equals(True, True), 'or', 'or', 'not', False, True),
	     			(env.equals(False, True), 'and', 'and', 'not', False, True),
			     	(env.equals(False, True), 'or', 'or', 'not', False, True),
	     			(env.equals(False, True), 'or', 'and', '~', False, True),
	     			(env.equals(False, True), 'or', 'and', 'not', True, True),
	     			(env.equals(False, True), 'or', 'and', 'not', False, False),
	     )
	    ]

	ex = []
	for a in asexs:
	    name = a[0]
	    exs = list(a[1:])
	    if isinstance(name, str):
		x = env
		names = name.split('.')
		for name in names:
		    x = getattr(x, name)
	    else:
		x = name
	    ex.append((x, exs))

	return ex

    class LocalEnvExpr:
	exec("""\
if 1:
    binary_operation_name	<is> equals(
    	'+', '-', '*', '/', '%', '|', '&', '**', '<<', '>>')
    algebraic_class	<is>	(setof(Type.Tuple) &
    				 attr('new', callable))
    			

    relation_class	<is>	(setof(	setof(any*any) | 
				    	Type.Tuple))

    relational_operator_name <is>	equals(
    '<', '<=', '>', '>=', '==', '!=', 'in', 'not in', 'is', 'is not')
""".replace('<is>', ' = lambda IS: '))

    class    GlueTypeExpr:
	exec("""
if 1:
    abelian_group	<in>	 setof(AA.group)
    associative		<in>	setof(AA.binary_operation)
    binary_operation	<in>	 doc('''
A \emp{binary operation} $*$ on a set $S$ is a function $*: S \cross S \mapsto S$.
The element in $S$ assigned to $(x, y)$ is denoted $x*y$.
\citemh(p.21)
''') & LE.algebraic_class
    boolean_algebra	<in> 	LE.algebraic_class
    commutative		<in> 	LE.algebraic_class
    distributive	<in> 	setof(cprod(AA.binary_operation, AA.binary_operation))
    distributive_1	<in> 	setof(cprod(AA.binary_operation, AA.binary_operation))
    distributive_2	<in> 	setof(cprod(AA.binary_operation, AA.binary_operation))
    field		<in>	LE.algebraic_class
    group		<in>	(LE.algebraic_class & doc('''
'''	))
    monoid		<in>	LE.algebraic_class
    ring		<in>	(LE.algebraic_class,
    				attr('new', argnames('S', 'add', 'mul', 'neg', 'zero')))
    semigroup		<in>	LE.algebraic_class
    		      
""".replace('<in>', '= lambda IN:'))

# Relations and functions

    def GetExamples(self, te, obj):
	AA = obj
	LE = AA.LE
	e = te.mod
	S = e.iso(0, 1, 2)
	def subsetof(x, y):
	    # Subset relation treating ints as bitsets
	    return x & y == x

	def D(S, op):
	    return (e.relation.defipair, (S, op))

	def L(*args):
	    return (AA.latticeform.quadruple, args)

	asexs = [
	    (e.PyObject,		0), # why not ()?
	    #(AA.relation,		D(S, '==')),
	    (AA.reflexive,	 	D(S, '==')),
	    #(AA.reflexive, 		AA.relation.new(S, '<=')),
	    (~AA.reflexive, 		D(S, '<')),
	    (AA.symmetric,		D(S, '==')),
	    (~AA.symmetric, 		D(S, '<=')),
	    (AA.transitive, 		D(S, '<')),
	    (~AA.transitive, 		D(S, '!=')),
	    (AA.irreflexive,		D(S, '<')),
	    (~AA.irreflexive,		D(S, '<=')),
	    (AA.antisymmetric,		D(S, '<=')),
	    (~AA.antisymmetric,		D(S, '!=')),
	    (AA.total_relation,		D(S, '<=')),
	    (~AA.total_relation,	D(S, '!=')),
	    (AA.equivalence_relation, 	D(S, '==')),
	    (~AA.equivalence_relation, 	D(S, '<=')),
	    (AA.partial_order,		D(S, subsetof)),
	    (~AA.partial_order,		D(S, '<')),
	    (AA.total_order,		D(S, '<=')),
	    (~AA.total_order,		D(S, subsetof)),
	    
	    (e.Type.Int,		0, 1, 2, 3),
	    (AA.lattice,		L(int, '<=', min, max)),
	    (~AA.lattice,		L(int, '<=', '&', max)),
	    (~AA.lattice,		L(int, '<=', min, '|')),
	    (AA.lattice,		L(int, lambda x, y: x & y == x, '&', '|')),
	    (~AA.lattice,		L(int, lambda x, y: x & y == x, min, '|')),
	    (~AA.lattice,		L(int, lambda x, y: x & y == x, '&', max)),

	    (AA.lattice.quadruple,	(int, '<=', min, max)),

	    ]
	return asexs



    class GlueTypeExpr:
	exec("""\
if 1:	
    reflexive		<in>	doc('x R x for every x in A',
    				AA.LE.relation_class)
    symmetric		<in>	doc('x R y implies y R x, for all x, y in A',
				AA.LE.relation_class)
    transitive		<in>	doc('x R y, y R z implies x R z, for all x, y, z in A',	
    				AA.LE.relation_class)
    irreflexive		<in>	doc('not (x R y), for all x in A',
    				AA.LE.relation_class)
    antisymmetric	<in>	doc('x R y, y R x implies x == y, for all x, y in A',
    				AA.LE.relation_class)
    total_relation	<in>	doc('x R y or y R x, for all x, y in A',
    				AA.LE.relation_class)
    equivalence_relation<in>	doc('Reflexive, symmetric and transitive',
				AA.LE.relation_class)
    partial_order	<in>	doc('Reflexive, antisymmetric and transitive',
				AA.LE.relation_class)
    total_order		<in>	doc('Partial order and x R y or y R x, for all x, y in A',
				AA.LE.relation_class)

    lattice		<in>	attr('quadruple', doc('''\
Tuples (S, R, V, A), where:
	S: 	set or convertible to set, i.e. 'setcastable'
	R:	relation operator on S
	V:	binary operator on S
	A:	binary operator on S

R, V and A are either operator symbols or functions.

(S, R) forms a partial order such that 
every pair x, y of elements in S have a greatest
lower bound GLB and a least upper bound LUB.

The GLB is given by V(x, y) or x V y depending on if V is
a function or operator symbol. Likewise, ULB is given
by A(x, y) or x A y.

For example, these are lattice specifications:

(int, '<=', min, max)
(int, lambda x, y: x & y == x, '&', '|')

''',				setof(tupleform(
			('S', 'R', 'V', 'A'),
			attr('S', SPLE.setcastable) &
			expset('''\
attr('R', AA.LE.relational_operator_name | boolean<<(S, S)) &
attr('V', AA.LE.binary_operation_name | setcast(S)<<(S, S)) &
attr('A', AA.LE.binary_operation_name | setcast(S)<<(S, S))
''',			 'S')
			))))
""".replace('<in>', '=lambda IN:'))

from guppy.heapy.test import support
import sys, unittest

class TestCase(support.TestCase):
    pass

class FirstCase(TestCase):
    def test_1(self):
	Spec = self.heapy.Spec
	TestEnv = Spec.mkTestEnv(_Specification_)
	#print SpecSpec.getstr(1000)

	TestEnv.test(self.guppy.heapy.AbstractAlgebra)


support.run_unittest(FirstCase, 1)
    
