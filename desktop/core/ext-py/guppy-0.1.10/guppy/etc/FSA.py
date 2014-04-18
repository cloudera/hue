#._cv_part guppy.etc.FSA

class FiniteAutomaton:
    def __init__(self, start_state, dump_state=''):
	self.start_state = start_state
	self.dump_state = dump_state
	self.table = {self.dump_state:{}}
	self.unresolved_composites = []
	self.resolved_composites = []
	self.composite_memo = {}
	self.is_updated = 1

    def __setitem__(self, (state, symbol), x):
	self.table.setdefault(state, {})[symbol] = x
	self.is_updated = 1

    def add_transition(self, state, symbol, *nexts):
	if len(nexts) == 1:
	    c = nexts[0]
	else:
	    for n in nexts:
		if n not in self.table:
		    self.table[n] = {}
		
	    c = self.new_composite(nexts)
	self[state, symbol] = c
	if c not in self.table:
	    self.table[c] = {}

    def get_row_items(self, state):
	try:
	    x = self.table[state].items()
	except KeyError:
	    return ()
	ris = []
	for k, v in x:
	    if isinstance(v, CompositeState):
		for vi in v:
		    ris.append((k, vi))
	    else:
		ris.append((k, v))
	return ris

    def make_deterministic(self):
	# Resolve all unresolved composite states so we become deterministic

	while self.unresolved_composites:
	    composites = self.unresolved_composites
	    self.unresolved_composites = []
	    for c in composites:
		ds = {}
		l = []
		for a in c:
		    for k, v in self.get_row_items(a):
		       ds.setdefault(k, []).append(v) 
		for k, v in ds.items():
		    for a in c:
			if k not in self.table[a]:
			    v.append(self.dump_state)
			    break
		for k, v in ds.items():
		    self.add_transition(c, k, *v)


    def get_all_input_symbols(self):
	syms = {}
	for state, trans in self.table.items():
	    for k, v in trans:
		syms[k] = 1
	return syms

    def get_all_states(self):
	return self.table

    def get_all_final_states(self):
	return {}

    def get_composites(self):
	if self.is_updated:
	    self.make_deterministic()
	return self.composite_memo.values()

    def get_transition_classes(self):
	# Get classes of states that have the same outgoing transitions 
	tc = {}
	tck = {}
	for k, v in self.table.items():
	    trans = v.keys()
	    trans.sort()
	    trans = tuple(trans)
	    ks = tc.get(trans)
	    if ks is None:
		ks = []
		tc[trans] = ks
	    ks.append(k)
	    tck[k] = ks
	return tc, tck

    def get_minimized_dfa(self, finals):
	def markall(finals, tcv, table):
	    def psrmark(l):
		for pq in l:
		    if pq in PS:
			l1 = PS[pq]
			del PS[pq]
			if l1:
			    psrmark(l1)
	    PS = {}
	    for Q in tcv:
		for ip, p in enumerate(Q):
		    for q in Q[ip+1:]:
			if (p in finals) == (q in finals):
			    PS[(p, q)] = ()

	    for pq in PS.keys():
		p, q = pq
		dp = table[p]
		dq = table[q]
		# Now we know they contain the same symbols
		dps = []
		for a in dp:
		    dpa = dp[a]
		    dqa = dq[a]
		    if dpa is not dqa:
			dpadqa = (dpa, dqa)
			if dpadqa in PS:
			    dps.append(dpadqa)
			else:
			    dqadpa = (dqa, dpa)
			    if dqadpa in PS:
				dps.append(dqadpa)
			    else:
				l = PS[pq]
				del PS[pq]
				if l is not ():
				    psrmark(l)
				break
		else:
		    for dpadqa in dps:
			l = PS[dpadqa]
			if l is ():
			    l = [pq]
			    PS[dpadqa] = l
			else:
			    l.append(pq)
	    return PS

	def combine(QS, PQS):
	    eqs = {}
	    for Q in QS:
		for p in Q:
		    eqs[p] = [p]

	    for p, q in PQS:
		#
		# Combine to equivalence classes
		#
		# Now we know that p, q are combinable
		#
		ep = eqs[p]
		eq = eqs[q]
		if eq is not ep:
		    if len(eq) > len(ep):
			eq, ep = ep, eq
		    ep.extend(eq)
		    for q in eq:
			eqs[q] = ep

	    return eqs

	def finalize(eqs):
	    csbyid = {}		# Composite state by identity of atomic state list
	    csbyas = {}		# Composite state by atomic state

	    i = 0
	    for eq in eqs.values():
		ideq = id(eq)
		if ideq not in csbyid:
		    c = 'MS%d'%i
		    i += 1
		    csbyid[ideq] = eq[0], c
		    for s in eq:
			csbyas[s] = c

	    fsa = self.__class__(csbyas[self.start_state])
	    fsa.final_states = {}

	    for cs0, cst in csbyid.values():
		fsa.table[cst] = trans = {}
		for a, s in self.table[cs0].items():
		    trans[a] = csbyas[s]
		if cs0 in finals:
		    fsa.final_states[cst] = 1
		    
	    return fsa

	if self.is_updated:
	    self.make_deterministic()
	    tctck = self._tctck = self.get_transition_classes()
	    self.is_updated = 0
	else:
	    tctck = self._tctck
	    
	tc, tck = tctck
	tcv = tc.values()
	PS = markall(finals, tcv, self.table)
	eqs = combine(tcv, PS)
	fsa = finalize(eqs)
	return fsa
	
    def new_composite(self, args):
	cs = CompositeState(dict([(arg, 1) for arg in args]).keys())
	if len(cs) == 1:
	    return args[0]
	try:
	    return self.composite_memo[cs]
	except KeyError:
	    self.composite_memo[cs] = cs
	    self.unresolved_composites.append(cs)
	    return cs


    def pp(self):
	ks = self.table.keys()
	ks.sort()
	num = dict([(s, i) for i, s in enumerate(ks)])
	for s in ks:
	    k = self.table[s]
	    print '%d: %s'%(num[s], s)
	    cs = k.keys()
	    cs.sort()
	    for c in cs:
		v = k[c]
		print '   %r  -> #%d: %s'%(c, num[v], v)



class CompositeState(tuple):
    pass

