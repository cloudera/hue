#._cv_part guppy.heapy.View

class Horizon:
    def __init__(self, mod):
	self.mod = mod
	self._hiding_tag_ = mod._hiding_tag_
	# Make preallocations of things that will be needed for news()
	self.retset = self.mod.retset
	self.hv = mod.hv
	self.exc_info = self.mod._root.sys.exc_info
	self.iso = self.mod.iso
	str(self.retset(self.iso(1,[],(),{}, self.__dict__)) -
	    self.iso(()))
	mod.hv.heap
	mod.enter
	mod.gc.collect()
	self.hv_horizon = mod.heapyc.Horizon(self.hv)

    def news(self):
	r = self.retset(self.hv_horizon.news(self.mod.enter(self.hv.heap)))
	return r
	    
class ClearCallback(object):
    __slots__ = 'callback',
    def __init__(self, callback):
	self.callback = callback
    def __call__(self, wr):
	if self.callback is not None:
	    self.callback(wr)
	else:
	    print 'No callback'

class Gchook_type(object):
    __slots__ = 'x', '__weakref__', 'cb'
    def __init__(g):
	g.x = g

class ObservationList(list):
    __slots__ = '_hiding_tag_',
    def __init__(self, iterable, hiding_tag):
	list.__init__(self, iterable)
	self._hiding_tag_ = hiding_tag

class _GLUECLAMP_:
    _imports_ = (
	'_parent.ImpSet:immnodeset',
	'_parent.ImpSet:immnodeset_union',
	'_parent.ImpSet:mutnodeset',
	'_parent.ImpSet:NodeSet',
	'_parent.UniSet:nodeset_adapt',
	'_parent.UniSet:retset',
	'_parent.Use:idset',
	'_parent.Use:iso',
	'_parent.Use:Type',
	'_root:gc',
	'_root:types',
	)


    _chgable_ =  ('is_rg_update_all', 'referrers_lock', '_is_clear_drg_enabled')
    _setable_ =  ('_hiding_tag_','target', 'is_hiding_calling_interpreter',

		  )

    is_hiding_calling_interpreter = False
    is_rg_update_all = False
    _is_clear_drg_enabled = 1 # Flag mainly for test, Note Apr 19 2005
    _hiding_tag_ = []

    #opt_rg_update_all = True

    _uniset_exports = (
#	'dominos',
#	'domisize',
	'imdom',
#	'indisize',
#	'referents',
#	'referrers',
	'referrers_gc',
	)


    def _get__clear_hook(self):
	return self.mutnodeset()

    def clear_check(self):
	ch = self._clear_hook
	try:
	    wr = list(ch)[0]
	except IndexError:
	    self.clear_setup()
	else:
	    c = wr()
	    if c is None:
		self.clear_setup()
	    elif self._root.sys.getrefcount(c) > 3:
		print 'GC hook object was referred to from somebody!'
		self.clear_callback(wr)
		c.cb.callback = None

    def clear_callback(self, wr):
	# print 'clear callback'
	self._clear_hook.clear()
	for m in self.clear_methods:
	    m()
	self.clear_setup()

    def clear_setup(self):
	ch = self._clear_hook
	ch.clear()
	c=self.gchook_type()
	cb = self.ClearCallback(self.clear_callback)
	c.cb = cb
	ch.add(self._root.weakref.ref(c, cb))

    def _get_clear_methods(self):
	return []

    def clear_register_method(self, m):
	self.clear_methods.append(m)
	self.clear_check()


    def _get_dict_ownership(self):
	drg = self.nodegraph()
	def clear_drg():
	    # print 'clear_drg?'
	    if drg.is_sorted and self._is_clear_drg_enabled:
		# print 'yes'
		drg.clear()
	    else:
		# print 'no, enabled = ', self.is_clear_drg_enabled
		pass
	self.clear_register_method(clear_drg)
	return drg
	
    def _get_gchook_type(self):
	return Gchook_type
	
    def _get_heapdef_modules(self):
	# We touch self.heapyc to import it & its dependent guppy.sets;
	# this is kinda specialcase-hacky but see Notes Apr 8 2005.
	self.heapyc
	return self.target.sys.modules.items()

    def _get_heapdefs(self):
	heapdefs = []
	for n, m in self.heapdef_modules:
	    try:
		hd = getattr(m, '_NyHeapDefs_')
	    except:
		continue
	    heapdefs.append(hd)
	return tuple(heapdefs)

    def _get_heapyc(self):	return self._parent.heapyc
    
    def _get_hv(self):
	hv = self.new_hv(_hiding_tag_=self._hiding_tag_,
			 is_hiding_calling_interpreter = self.is_hiding_calling_interpreter)
	return hv

    def _get_norefer(self): return self.mutnodeset()

    def _get_referrers_targets(self): return []

    def _get_rg(self):
	rg = self.nodegraph()
	self.clear_register_method(self._clear_rg)
	return rg

    def _clear_rg(self):
	if self.referrers_lock:
	    return
	rg = self.rg
	if rg.is_sorted:
	    #print 'clearing', rg
	    rg.clear()
	    self.norefer.clear()
	else:
	    #print 'no clear', rg, len(rg), len(self.norefer)
	    pass

    def _get_referrers_lock(self)	: return 0

    def _get_root(self):	return self.heapyc.RootState
    def _get_target(self):	return self._parent.Target.Target()

    def _set_root(self, root):
	self.clear_retainers()
	self.hv.root = root

    def call_with_referrers(self, X, f):
	self.referrers_lock += 1
	try:
	    self.update_referrers(X)
	    return f(X)
	finally:
	    self.referrers_lock -= 1

    def clear_retainers(self):
	"""G.clear_retainers()
Clear the retainer graph V.rg.
"""
	self.rg.clear()
	self.norefer.clear()

    def dominos(self, X):
	"""dominos(X) -> idset
Return the dominos of a set of objects X. The dominos of X is the set
of objects that are dominated by X, which is the objects that will become
deallocated, directly or indirectly, when the objects in X are deallocated."""
	return self.dominos_tuple((X,))[0]
	
    def dominos_tuple(self, X):
	"""V.dominos_tuple(X) -> tuple of idsets
Return a tuple of dominos for the tuple of sets of objects X."""
	D_ = [self.nodeset_adapt(x) for x in X] # Convert to naming like in the appendix
	T = self.hv.reachable
	S = self.immnodeset([self.root])
	D = self.immnodeset_union(D_)
	W = T(S, D)
	return tuple([self.retset(T(Di, W) - T(D, W | Di)) for Di in D_])
	
    def domisize(self, X):
	"""domisize(X) -> int
Return the dominated size of a set of objects X. The dominated size of X
is the total size of memory that will become deallocated, directly or
indirectly, when the objects in X are deallocated. See also: indisize."""

	return self.domisize_tuple((X,))[0]

    def domisize_tuple(self, X):
	""""V.domisize_tuple(X) -> tuple of ints
Return a tuple of dominated sizes for the tuple of sets of objects X."""
	return tuple([self.indisize(dominos_i)
		      for dominos_i in self.dominos_tuple(X)])

    def enter(self, func):
	if self.hv.is_hiding_calling_interpreter:
	    self.hv.limitframe = None
	elif self.hv.limitframe is not None:
	    return func()
	else:
	    import sys
	    try:
		1/0
	    except:
		type, value, traceback = sys.exc_info()
		limitframe = traceback.tb_frame.f_back.f_back
	    sys.last_traceback=None
	    sys.exc_clear()
	    del type,value,traceback
	    self.hv.limitframe = limitframe

	try:
	    retval = func()
	finally:
	    self.hv.limitframe = None
	return retval

    def gchook(self, func):
	c=self.gchook_type()
	ho = self.mutnodeset()
	def cb(wr):
	    func()
	    ho.clear()
	    c=self.gchook_type()
	    ho.add(self._root.weakref.ref(c, cb))

	ho.add(self._root.weakref.ref(c, cb))
	return self.mutnodeset([ho])

    def heapg(self, rma=1):
	# Almost the same as gc.get_objects(), 
	# except:
	# 1. calls gc.collect() first (twice)
	# 2. removes objects of type gchook
	# 3. removes objects of type ClearCallback
	# 4. removes all objects of type types.FrameType
	# 5. removes all objects of weakref type
	# 6. If rma = 1,
	#    removes all that is in the reachable heap
	#    except what is in the set itself.

	# . wraps the result in an IdSet

	self.gc.collect()
	self.gc.collect()
	objs = self.gc.get_objects()
	cli = self.hv.cli_type()
	objs = cli.select(objs, self.gchook_type, '!=')
	objs = cli.select(objs, ClearCallback, '!=')
	objs = cli.select(objs, self._root.types.FrameType, '!=')
	objs = cli.select(objs, self._root.weakref.ReferenceType, '!=')
	r = self.retset(objs)
	del cli, objs

	if rma:
	    r = (r - self.idset(self.heapyc.HeapView(
		self.heapyc.RootState,
		self.heapdefs
		).reachable_x(
		    self.immnodeset([self.heapyc.RootState]),
                    self.observation_containers()
                    ))
                 )


	return r

    def heapu(self, rma=1):

	self.gc.collect()
	self.gc.collect()
	r = self.gc.get_objects()
        
        exclude = (self.Type(self.gchook_type) |
                   self.Type(ClearCallback)
                   )
                   

	if rma:
	    exclude |= self.idset(self.heapyc.HeapView(
		self.heapyc.RootState,
		self.heapdefs
		).reachable_x(
		    self.immnodeset([self.heapyc.RootState]),
                    self.immnodeset([r])
                    ))
            
	r = self.retset(r) - exclude
        ref = r.referents - exclude
        while not ref <= r:
            r |= ref
            ref = ref.referents - exclude

	del ref, exclude


        r = r.byclass # Avoid memoizing for complicated classification
	return r

    def heap(self):
	"""V.heap() -> idset
Return the set of objects in the visible heap.
"""
        global heap_one_time_initialized
        # This is to make sure that the first time called
        # the heap will contain things that may likely be loaded later
        # because of common operations.
        if not heap_one_time_initialized:
            heap_one_time_initialized = 1
	    repr(self.idset(self.hv.heap()))
            x=[]
            repr(self.iso(x).shpaths)
            repr(self.iso(x).rp)

	self.gc.collect() # Sealing a leak at particular usage ; Notes Apr 13 2005
	# Exclude current frame by encapsulting in enter(). Note Apr 20 2005
	return self.enter(lambda:
	    self.idset(self.hv.heap()))

    def horizon(self):
	return self.Horizon(self)

    def imdom(self, X):
	"""imdom(X) -> idset
Return the immediate dominators of a set of objects X. The immediate
dominators is a subset of the referrers. It includes only those
referrers that are reachable directly, avoiding any other referrer."""
	pred = self.nodeset_adapt(self.referrers(X))
	visit = self.hv.reachable_x(self.immnodeset([self.root]), pred)
	return self.retset(pred & visit)

    def indisize(self, X):
	"""indisize(X) -> int
Return the sum of the individual sizes of the set of objects X. 
The individual size of an object is the size of memory that is
allocated directly in the object, not including any externally
visible subobjects. See also: domisize."""
	return self.hv.indisize_sum(self.nodeset_adapt(X))

    def new_hv(self, _hiding_tag_=None, is_hiding_calling_interpreter=False,
	       heapdefs=None, root=None, gchook_type=None):
	if heapdefs is None:
	    heapdefs = self.heapdefs
	if root is None:
	    root = self.root
	if gchook_type is None:
	    gchook_type = self.gchook_type
	hv = self.heapyc.HeapView(root, heapdefs)
	hv._hiding_tag_ = _hiding_tag_
	hv.is_hiding_calling_interpreter = is_hiding_calling_interpreter
	hv.register_hidden_exact_type(gchook_type)
	#hv.register__hiding_tag__type(self._parent.UniSet.UniSet)
	hv.register__hiding_tag__type(self._parent.UniSet.Kind)
	hv.register__hiding_tag__type(self._parent.UniSet.IdentitySetMulti)
	hv.register__hiding_tag__type(self._parent.UniSet.IdentitySetSingleton)

	return hv

    def nodegraph(self, iterable = None, is_mapping = False):
	ng = self.heapyc.NodeGraph(iterable, is_mapping)
	ng._hiding_tag_ = self._hiding_tag_
	return ng

    def obj_at(self, addr):
        try:
            return self.immnodeset(self.hv.static_types).obj_at(addr)
        except ValueError:
            pass
        try:
            return self.immnodeset(self.gc.get_objects()).obj_at(addr)
        except ValueError:
            pass
        try:
            return self.immnodeset(self.hv.heap()).obj_at(addr)
        except ValueError:
            raise ValueError, 'No object found at address %s'%hex(addr)
	
    def observation_containers(self):
	# Return the current set of 'observation containers'
	# as discussed in Notes Oct 27 2005.
	# returns a nodeset, not an idset, to avoid recursive referenes

	objs = self.gc.get_objects()
	cli = self.hv.cli_type()
	objs = (cli.select(objs, self.NodeSet, '<=') +
		cli.select(objs, ObservationList, '<=') +
		cli.select(objs, self._parent.UniSet.IdentitySetSingleton, '<=')
		)
	r = self.immnodeset([x for x in objs if getattr(x, '_hiding_tag_', None) is self._hiding_tag_])
	del x, cli, objs
	return r
			    


    def observation_list(self, iterable=()):
	# Return an ObservationList object with our _hiding_tag_
	return ObservationList(iterable, self._hiding_tag_)

    def referents(self, X):
	"""V.referents(X) -> idset
Return the set of objects that are directly referred to by
any of the objects in the set X."""
	return self.retset(self.hv.relimg(self.nodeset_adapt(X)))

    def referrers(self, X):
	"""V.referrers(X) -> idset
Return the set of objects that directly refer to
any of the objects in the set X."""

	X = self.nodeset_adapt(X)
	if self.is_rg_update_all and self.root is self.heapyc.RootState:
	    if not (self.rg.domain_covers(X) or
		    self.rg.domain_covers(X - self.norefer)):
		# print 'new update old len = %d'%len(self.rg)
		# print self.idset(X-self.rg.get_domain())
		self.rg.clear()
		import gc
		gc.collect()
		self.hv.update_referrers_completely(self.rg)
		addnoref = X - self.rg.get_domain()
		#print 'done 1', len(X), len(addnoref)
		self.norefer |= addnoref
		#print 'done 1a', len(self.rg)
	else:
            # print 'X', X, len(X)
            # print self.idset(X)
	    Y = self.mutnodeset(X)
	    Y -= self.norefer
	    if not self.rg.domain_covers(Y):
		for wt in self.referrers_targets:
		    t = wt()
		    if t is not None:
			Y |= t.set.nodes
		if 0:
		    print 'old update'
		    print self.idset(Y - self.rg.get_domain())
		Y |= self.rg.get_domain()
		self.rg.clear()
		self.hv.update_referrers(self.rg, Y)
		self.norefer.clear()
		self.norefer |= (X | Y | self.rg.get_range())
		self.norefer -= self.rg.get_domain()
                Y = self.mutnodeset(X) - self.norefer
                if not self.rg.domain_covers(Y):
                    print 'update_referrers failed' 
                    print 'Y - domain of rg:'
                    print self.idset(Y - self.rg.get_domain())
                    from pdb import pm, set_trace
                    set_trace()
                        
		Y = None

	X = self.rg.relimg(X)
	X = self.immnodeset(X) - [None]
	X = self.retset(X)
	return X

    def referrers_gc(self, X):
	"""V.referrers_gc(X) -> idset
Return the set of objects that directly refer to
any of the objects in the set X.
This differs from referrers in that it uses the
gc module's view of the referrers. This is more or less
valid depending on viewpoint.

"""
	X = tuple(self.nodeset_adapt(X))
	return self.idset(self.gc.get_referrers(*X)) - self.iso(X)

    def referrers_add_target(self, t):
	def remove(wr):
	    self.referrers_targets.remove(wr)
	wr = self._root.weakref.ref(t, remove)
	self.referrers_targets.append(wr)

    def update_referrers(self, X):
	"""V.update_referrers(X)
Update the view V from the set X. X must be adaptable to NodeSet. V.rg is
updated so that in addition to its previos mapping, it will also contain
mappings for the elements of X to their referrers, from them to their
referrers and so on.
"""
	self.referrers(X)

def prime_builtin_types():
    # Make sure builtin types have been completely allocated
    # with all method descriptors etc.
    # so subsequent events will not give spurios confusing allocations.
    # This should need to be done only once.
    # (Or whenever a new (extension) module is imported??)
    # The problem & solution is further discussed in Notes Nov 9 2005.

    import types
    import guppy.heapy.heapyc
    import guppy.sets.setsc
    import sys
    import weakref

    for mod in sys.modules.values():
	if mod is None:
	    continue
	for t in mod.__dict__.values():
	    if isinstance(t, type):
		dir(t)
    # Other type(s)
    for t in [type(iter([])), type(iter(())),
              ]:
        dir(t)


prime_builtin_types()

# The following global variable is used by heap()
# to do extra initializations the first time it is called.
# having to do that we want to do import and init things
# but only if heap is actually called

heap_one_time_initialized = 0
