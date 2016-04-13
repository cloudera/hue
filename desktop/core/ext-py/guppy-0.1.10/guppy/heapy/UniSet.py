#._cv_part guppy.heapy.UniSet

import guppy

class UniSet(object):
    __slots__ = '_hiding_tag_', 'fam',  '_origin_'
    _help_url_ = 'heapy_UniSet.html#heapykinds.UniSet'
    _instahelp_ = ''

    _doc_nodes = """nodes: ImmNodeSet

The actual objects contained in x. These are called nodes because
they are treated with equality based on address, and not on the
generalized equality that is used by ordinary builtin sets or dicts."""


    def __and__(self, other):
	"""
Return the intersection of self and other.
"""
	return self.fam.c_binop('and', self, other)

    __rand__ = __and__

    def __call__(self, *args, **kwds):	return self.fam.c_call(self, args, kwds)

    def __contains__(self, other): 
	"""
Return True if other is a member of self, False otherwise.
"""
	return self.fam.c_contains(self, other)

    def __eq__(self, other):
	"""
Return True if self contains the same elements as other,
False otherwise."""
	return self <= other and self >= other

    def __hash__(self):
	"""
Return an hash based on the kind of the set of self and
the addresses of its elements, if any.
	"""
	return self.fam.c_hash(self)

    def __invert__(self):
	"""
Return the complement of self.
"""
	return self.fam.c_unop('invert', self)

    def __ge__(self, other):
	"""
Return True if self is a superset of (and may be equal to) other,
False otherwise.
"""
	if self is other:
	    return True
	if not isinstance(other, UniSet):
	    other = self.fam.c_uniset(other)
	return self.fam.c_ge(self, other)

    def __gt__(self, other):
	"""
Return True if self is a strict (may not be equal to) superset of other.
False otherwise.
"""
	return self >= other and not self <= other

    def __getattr__(self, other):
	"""
Get family-specific attribute.
"""
	return self.fam.mod.View.enter(lambda:self.fam.c_getattr(self, other))

    def __le__(self, other):
	"""
Return True if self is a subset of (and may be equal to) other,
False otherwise.
"""
	if self is other:
	    return True
	if not isinstance(other, UniSet):
	    other = self.fam.c_uniset(other)
	return self.fam.c_le(self, other)

    def __lshift__(return_spec, argument_spec):
	"""
<<This is about to change, does not work as one may expected.
Nov 19 2005. >>>

Return a 'mapping' set, which may be used for specification and test
purposes. It implements the syntax:

	return_spec << argument_spec

The elements of the set returned are the callable objects that return
values in return_spec, when called with arguments according to
argument_spec. The return_spec may be any kind of sets that can test
for element containment. The argument_spec may be a set or a tuple. If
it is a set, it should be able to generate some examples, to allow the
mapping to be tested.  When argument_spec is a set, the mapping will
have a single argument. Any number of arguments may be specified using
an argument_spec which is a tuple.  The arguments are then specified
with sets, that should be able to generate examples. Special features
of the mapping such as optional arguments may be specified in the same
way as when using the 'mapping' function in the Spec.py module.


"""
	return return_spec.fam.c_lshift(return_spec, argument_spec)

    def __lt__(self, other):
	"""
Return True if self is a strict (may not be equal to) subset of other,
False otherwise.
"""
    	return self <= other and not self >= other
    def __mul__(self, other):
	"""
Return the cartesian product of self and other, which is the set of
pairs where the first element is a member of self and the second
element is a member of other.

NOTE: Unlike what one might expect from the way the cartesian product
may be defined mathematically, the operation as implemented here is
nonassociative, i.e.

     a*b*c == (a*b)*c != a*(b*c)


In the mathematical case, a*b*c would be a set of triples, but here it
becomes a set of pairs with the first element in (a*b) and the second
element in c.

To create sets of triples etc. the cprod() factory function in Spec.py
could be used directly.
"""
	if not isinstance(other, UniSet):
	    other = self.fam.c_uniset(other)
	return self.fam.c_mul(self, other)

    def __ne__(self, other):
	"""
Return True if self does not equal other,
False otherwise. See also: __eq__.
"""
	return not self == other

    def __nonzero__(self):
	"""
Return True if self contains some element, 
False otherwise.
"""
	return self.fam.c_nonzero(self)

    def __or__(self, other):
	"""
Return the union of self and other.
"""
	return self.fam.c_binop('or', self, other)

    __ror__ = __or__

    def __repr__(self):
	"""
Return a string representing self.  This is usually the same string
as from __str__.

"""
	return self.fam.c_repr(self)

    def __str__(self):
	"""
Return a string representing self. The string is usually the same as the .brief
attribute, but a major exception is the IdentitySet class.

"""
	return self.fam.c_str(self)

    def __sub__(self, other):
	"""
Return the assymetrical set difference.  That is, the set of elements
in self, except those that are in others.
"""
	if not isinstance(other, UniSet):
	    other = self.fam.c_uniset(other)
	return self.fam.c_sub(self, other)

    def __rsub__(self, other):
	"""
Return the assymetrical set difference.  That is, the
set of elements in other, except those that are in self.

This is like __sub__ except it handles the case when the left
argument is not a UniSet (but convertible to a UniSet).
"""
	if not isinstance(other, UniSet):
	    other = self.fam.c_uniset(other)
	return other.fam.c_sub(other, self)

    def __xor__(self, other):
	"""
Return the symmetrical set difference.  That is, the set of elements
that are in one of self or other, but not in both.
"""
	if not isinstance(other, UniSet):
	    other = self.fam.c_uniset(other)
	return self.fam.c_xor(self, other)
    __rxor__ = __xor__

    brief = property(lambda self:self.fam.c_get_brief(self),
                     doc="""\
A string representation of self, which is brief relative to the
representation returned by __str__ and __repr__. (In many cases it is
the same - both are then brief - but for IdentitySet objects the brief
representation is typically much shorter than the non-brief one.)"""
                     )

    def _get_help(self):
        return self.fam.mod._root.guppy.doc.help_instance(self)

    #dir = property(lambda self:self.fam.mod._root.guppy.doc.get_dir(self))
    #dir = property(lambda self:self.fam.mod._root.guppy.doc.get_dir(self))
    #man = guppy.man_property
    #dir = guppy.gpdir_property

    #man = property(lambda self:self.fam.mod._root.guppy.doc.get_man(self))
    #man = property(guppy.getman)

    doc = property(lambda self:self.fam.mod._root.guppy.etc.Help.dir(self))

    def get_ckc(self):
	# Get low-level classification information, where available.
	# Returns a tuple (classifier, kind, comparator)
	return self.fam.c_get_ckc(self)

    def _derive_origin_(self, doc):
	"""
Return information about the 'origin' of the set. This was intended to be
used for specification purposes - is experimental, noncomplete, temporary.
"""
	return self.fam.c_derive_origin(self, doc)

    def disjoint(self, other):
	"""
Return True if self and other are disjoint sets, False otherwise. This
is equivalent to calculating

	(self & other) == Nothing

but may be implemented more efficiently in some cases.
"""
	return self.fam.c_disjoint(self, other)

    def get_examples(self, env):
	"""
Return an iterable object or an iterator, which provides someexamples
of the elements of self.  (A minimum of 2 examples should normally be
provided, but it may depend on some test configuration options.)

This is used for automatic test generation from specifications.  The
env argument is according to specification of TestEnv in Spec.py,
"""
	return self.fam.c_get_examples(self, env)

    def get_render(self):
	"""
Return a function that may be used to render the representation of the
elements of self. This is mainly intended for internal representation
support.

The function returned depends on the kind of elements self
contains. The rendering function is choosen so that it will be
appropriate, and can be used safely, for all objects of that kind.
For the most general kind of objects, the rendering function will only
return an address representation. For more specialized kinds, the
function may provide more information, and can be equivalent to the
builtin repr() when the kind is narrow enough that it would work for
all elements of that kind without exception.

"""
	return self.fam.c_get_render(self)

    def test_contains(self, element, env):
	"""
Test if self contains the element object.  This is used mainly for
internal use for automatic (experimental) testing of specifications.

The env argument is according to specification of TestEnv in Spec.py.
It provides support for things that depends on the specific test
situation, such as a test reporting protocol. If test_contains did
find the element to be contained in self, the method will return
(usually True). But if the element was not contained in self, the
method should call env.failed(message), and return whatever may
be returned; though typically env.failed() would raise an exception.
	 """
	return self.fam.c_test_contains(self, element, env)

    biper = property(lambda self:self.fam.c_get_biper(self),
                     doc = """\
A bipartitioning equivalence relation based on x. This may be used to
partition or classify sets into two equivalence classes:

x.biper(0) == x
    The set of elements that are in x.
x.biper(1) == ~x
    The set of elements that are not in x.
	""")

    dictof = property(lambda self:self.fam.c_get_dictof(self),
                      doc = """dictof: UniSet

If x represents a kind of objects with a builtin __dict__ attribute,
x.dictof is the kind representing the set of all those dict
objects. In effect, x.dictof maps lambda e:getattr(e, '__dict__') for
all objects e in x. But it is symbolically evaluated to generate a new
symbolic set (a Kind).""")

class Kind(UniSet):
    __slots__ = 'arg',
    def __init__(self, fam, arg):
	self.fam = fam
	self._hiding_tag_ = fam._hiding_tag_
	self.arg = arg
	self._origin_ = None

    def alt(self, cmp):
	return self.fam.c_alt(self, cmp)

class IdentitySet(UniSet):
    __slots__ = '_er', '_partition'
    _help_url_ = 'heapy_UniSet.html#heapykinds.IdentitySet'

    def __getitem__(self, idx):	return self.fam.c_getitem(self, idx)
    def __len__(self):		return self.fam.c_len(self)
    def __iter__(self):		return self.fam.c_iter(self)

    def __str__(self):
	"""
Return a string representating self. This differs from the .brief
attribute in that it is a tabular representation. 

...

"""

	return self.fam.c_str(self)


    def get_rp(self, depth=None, er=None, imdom=0, bf=0, src=None,
               stopkind=None, nocyc=False, ref=None):
	"""
x.get_rp(depth=None, er=None, imdom=0, bf=0, src=None, stopkind=None,
	nocyc=False, ref=None)

Return an object representing the pattern of references to the objects in X.
The returned object is of kind ReferencePattern.

Arguments
	depth	The depth to which the pattern will be generated. The
		default is taken from depth of this module.
	er	The equivalence relation to partition the referrers.
        	The default is Clodo.

	imdom   If true, the immediate dominators will be used instead
		of the referrers. This will take longer time to
		calculate, but may be useful to reduce the complexity
		of the reference pattern.

	bf	If true, the pattern will be printed in breadth-first
		order instead of depth-first. (Experimental.)
	src	If specified, an alternative reference source instead
		of the default root.
        stopkind
                The referrers of objects of kind stopkind will not be
		followed.
	nocyc	When True, certain cycles will not be followed.
        ref

See also
        rp (a shorthand for common cases)

"""
	return self.fam.RefPat.rp(self, depth, er, imdom, bf, src, stopkind,
                                  nocyc, ref)


    def get_shpaths(self, src=None, avoid_nodes=None, avoid_edges=()):
	"""x.get_shpaths(draw:[src, avoid_nodes, avoid_edges]) -> Paths

Return an object containing the shortest paths to objects in x.
The optional arguments are:

    src:IdentitySet		An alternative source set of objects
    avoid_nodes:IdentitySet	Nodes to avoid           
    avoid_edges:NodeGraph       Edges to avoid                  

"""
	return self.fam.Path.shpaths(self, src, avoid_nodes, avoid_edges)

    # 'Normal' methods

    def by(self, er):

        """ x.by(er) -> A copy of x, but using er for equiv. relation. """
        return self.fam.get_by(self, er)

    def diff(self, other):
	return self.stat - other.by(self.er).stat

    def dump(self, *args, **kwds):
        """ Dump statistical data to a file
          Shorthand for .stat.dump """
        self.stat.dump(*args, **kwds)

    byclass = property(lambda self:self.by('Class'), doc="""\
A copy of self, but with 'Class' as the equivalence relation.""")

    byclodo = property(lambda self:self.by('Clodo'), doc="""\
A copy of self, but with 'Clodo' as the equivalence relation.""")

    byidset = property(lambda self:self.by('Idset'), doc="""\
A copy of self, but with 'Idset' as the equivalence relation.

Note
    This is mainly for special purpose internal use. The Id
equivalence relation is more efficient when partitioning large
sets.""")

    byid = property(lambda self:self.by('Id'), doc="""\
A copy of self, but with 'Id' as the equivalence relation.""")

    bymodule = property(lambda self:self.by('Module'), doc="""\
A copy of self, but with 'Module' as the equivalence relation.""")

    byrcs = property(lambda self: self.by('Rcs'), doc="""\
A copy of self, but with 'Rcs' as the equivalence relation.""")

    bysize = property(lambda self: self.by('Size'), doc="""\
A copy of self, but with 'Size' as the equivalence relation.""")

    bytype = property(lambda self: self.by('Type'), doc="""\
A copy of self, but with 'Type' as the equivalence relation.""")

    byunity = property(lambda self: self.by('Unity'), doc="""\
A copy of self, but with 'Unity' as the equivalence relation.""")

    byvia = property(lambda self: self.by('Via'), doc="""
A copy of self, but with 'Via' as the equivalence relation.""")

    er = property(lambda self: self.fam.get_er(self), doc="""\
The equivalence relation used for partitioning when representing /
printing this set.""")

    count = property(lambda self: len(self.nodes), doc="""\
The number of individual objects in the set.""")

    dominos = property(lambda self: self.fam.View.dominos(self), doc="""\
The set 'dominated' by a set of objects. This is the objects that will
become deallocated, directly or indirectly, when the objects in the
set are deallocated.

See also: domisize.""")

    domisize = property(lambda self: self.fam.View.domisize(self), doc="""\
The dominated size of a set of objects. This is the total size of
memory that will become deallocated, directly or indirectly, when the
objects in the set are deallocated.

See also: dominos, size.
""")

    imdom = property(lambda self: self.fam.View.imdom(self), doc="""\
The immediate dominators of a set of objects. The immediate dominators
is a subset of the referrers. It includes only those referrers that
are reachable directly, avoiding any other referrer.""")

    indisize = size = property(lambda self:self.fam.View.indisize(self),doc="""\
The total 'individual' size of the set of objects.  The individual
size of an object is the size of memory that is allocated directly in
the object, not including any externally visible subobjects. See also:
domisize.""")

    kind = property(lambda self: self.er[self], doc="""\
The kind of objects in the set. The kind is the union of the
element-wise classifications as determined by the equivalence relation
in use by the set.""")

    maprox = property(lambda self: MappingProxy(self), doc="""\
An object that can be used to map operations to the objects in self,
forming a new set of the result. The returned object is an instance of
MappingProxy.

This works currently as follows:

o Getting an attribute of the MappingProxy object will get the
  attribute from each of the objects in the set and form a set of the
  results. If there was an exception when getting some attribute, it
  would be ignored.

o Indexing the MappingProxy object will index into each of the objects
  in the set and return a set of the results. Exceptions will be
  ignored.

Example:

>>> hp.iso({'a':'b'}, {'a':1}).maprox['a'].byid
Set of 2  objects. Total size = 40 bytes.
 Index     Size   %   Cumulative  %   Kind: Name/Value/Address
     0       28  70.0        28  70.0 str: 'b'
     1       12  30.0        40 100.0 int: 1
>>> 

<This is an experimental feature, so the name is intentionally made
mystically-sounding, and is a shorthand for 'mapping proxy'.>""")

    more = property(lambda self:self.fam.get_more(self), doc="""\
An object that can be used to show more lines of the string
representation of self. The object returned, a MorePrinter instance,
has a string representation that continues after the end of the
representation of self.""")

    owners = property(lambda self: self.fam.get_owners(self), doc="""\
The set of objects that 'own' objects in self. The owner is defined
for an object of type dict, as the object (if any) that refers to the
object via its special __dict__ attribute.""")

    partition = property(lambda self: self.fam.get_partition(self), doc="""\
A partition of the set of objects in self. The set is partitioned into
subsets by equal kind, as given by a equivalence relation.  Unless
otherwise specified, the equivalence relation used is 'byclodo', which
means it classifies 'by type or class or dict owner'. Different
equivalence relations are specified for sets created by the 'by_...'
attributes of any IdentitySet object.

The value is an instance of guppy.heapy.Part.Partition.""")

    parts = property(lambda self: self.fam.get_parts(self), doc="""\
An iterable object, that can be used to iterate over the 'parts' of
self. The iteration order is determined by the sorting order the set
has, in the table printed when partitioned.""")

    pathsin = property(lambda self: self.get_shpaths(self.referrers), doc="""\
The paths from the direct referrers of the objects in self.""")

    pathsout = property(lambda self:self.referents.get_shpaths(self), doc="""\
The paths to the referents of the objects in self.""")

    referents = property(lambda self: self.fam.View.referents(self), doc="""\
The set of objects that are directly referred to by any of the objects
in self.""")

    referrers = property(lambda self: self.fam.View.referrers(self), doc="""\
The set of objects that directly refer to any of the objects in self.""")

    rp = property(get_rp, doc="""\
rp: ReferencePattern

An object representing the pattern of references to the objects in X.

See also
    get_rp""")

    shpaths = property(get_shpaths, doc="""x.shpaths: Paths

An object containing the shortest paths to objects in x.

Synonym
    sp
See also
    get_shpaths""")

    shpaths = property(get_shpaths, doc="""x.sp: Paths

An object containing the shortest paths to objects in x.

Synonym
    sp
See also
    get_shpaths""")

    sp = property(get_shpaths, doc="""x.sp: Paths

An object containing the shortest paths to objects in x.

Synonym
    shpaths
See also
    get_shpaths""")



    stat = property(lambda self: self.partition.get_stat(), doc="""\
x.stat: Stat

An object summarizing the statistics of the partitioning of x. This is
useful when only the statistics is required, not the objects
themselves. The statistics can be dumped to a file, unlike the set of
objects itself.""")

    theone = property(lambda self: self.fam.get_theone(self), doc="""\
theone: Anything

The one object in a singleton set. In case the set does not contain
exactly one object, the exception ValueError will be raised.
""")
			 
class IdentitySetMulti(IdentitySet):
    __slots__ = 'nodes',

    def __init__(self, fam, nodes):
	self.fam = fam
	self._hiding_tag_ = fam._hiding_tag_
	self.nodes = nodes
	self._origin_ = None

class IdentitySetSingleton(IdentitySet):
    __slots__ = '_node',
    _help_url_ = 'heapy_UniSet.html#heapykinds.IdentitySetSingleton'

    def __init__(self, fam, node):
	self.fam = fam
	self._hiding_tag_ = fam._hiding_tag_
	self._node = node
	self._origin_ = None

    # RefPat (eg) depends on this being usable as a hashable key.
    nodes = property(lambda self: self.fam.immnodeset((self._node,)), doc="""\
x.nodes: ImmNodeSet

The actual objects contained in x. These are called nodes because they
are treated with equality based on address, and not on the generalized
equality that is used by ordinary builtin sets or dicts.""")

    def _get_theone(self):
	return self._node

    theone = property(_get_theone)


class EquivalenceRelation(UniSet):
    """\
An equivalence relation is a binary relation between two elements of a
set which groups them together as being "equivalent" in some way.

An equivalence relation is reflexive, symmetric, and transitive. In
other words, the following must hold for "~" to be an equivalence
relation on X:

    * Reflexivity: a ~ a
    * Symmetry: if a ~ b then b ~ a
    * Transitivity: if a ~ b and b ~ c then a ~ c.

An equivalence relation partitions a set into several disjoint
subsets, called equivalence classes. All the elements in a given
equivalence class are equivalent among themselves, and no element is
equivalent with any element from a different class.
"""

    __slots__ = 'classifier', 'erargs'
    _help_url_ = 'heapy_UniSet.html#heapykinds.EquivalenceRelation'

    def __init__(self, fam, classifier, erargs=()):
	self.fam = fam
	self._hiding_tag_ = fam._hiding_tag_
	self.classifier = classifier
	self.erargs = erargs
	self._origin_ = None
    
    def __getitem__(self, idx):
	return self.fam.c_getitem(self, idx)

    def _get_dictof(self):
	return self.fam.Classifiers.mker_dictof(self)
    dictof = property(_get_dictof)

    def _get_refdby(self):
	return self.fam.Classifiers.mker_refdby(self)
    refdby = property(_get_refdby)

    def sokind(self, *args, **kwds):
	return self.classifier.get_sokind(self, *args, **kwds)

class MappingProxy(object):
    __slots__ = '_set_',
    def __init__(self, set):
	self._set_ = set
	
    def __getattribute__(self, name):
	if name == '_set_':
	    return object.__getattribute__(self, name)
	return self._set_.fam.maprox_getattr(self._set_, name)

    def __getitem__(self, name):
	return self._set_.fam.maprox_getitem(self._set_, name)


class Family:
    supercl = None

    def __init__(self, mod):
	self.mod = mod
	self.Doc = mod._parent.Doc
	self._hiding_tag_ = mod._hiding_tag_
	self.types = mod.types
	self.disjoints = mod.immnodeset()
	self.export_dict = self.mod.export_dict
	self.supers = mod.immnodeset([self])
	self.Set = Kind

    def __call__(self, arg):
	return self.Set(self, arg)
	
    def _derive_origin_(self, origin):
	return self.Doc.add_origin(self, origin)

    def specotup(self, tup):
	r = self.Set(self, tup)
	r = self.Doc.add_origin(r, self.Doc.callfunc(self, *tup))
	return r

    def specoarg(self, arg):
	r = self.Set(self, arg)
	r = self.Doc.add_origin(r, self.Doc.callfunc(self, arg))
	return r

    def specoargtup(self, arg, tup):
	r = self.Set(self, arg)
	r = self.Doc.add_origin(r, self.Doc.callfunc(self, *tup))
	return r


    def add_export(self, name, value):
	if self.export_dict is self.mod.export_dict:
	    self.export_dict = self.mod.export_dict.copy()
	if name in self.export_dict and self.export_dict[name] is not value:
	    raise ValueError, 'Duplicate: %s'%name
	self.export_dict[name] = value

    def c_alt(self, a, cmp):
	raise ValueError, 'No alternative set for family %s.'%self
	

    def c_binop(self, op, a, b):
	if not isinstance(b, UniSet):
	    b = self.c_uniset(b)
	r = getattr(self, 'c_'+op)(a, b)
	# r = self.Doc.add_origin(r, self.Doc.binop(op, a.doc, b.doc))
	return r

    def c_unop(self, op, a):
	r = getattr(self, 'c_'+op)(a)
	# r = self.Doc.add_origin(r, self.Doc.unop(op, a.doc))
	return r

    def c_derive_origin(self, a, b):
	return self.Doc.add_origin(a, b)

    def c_call(self, a, args, kwds):
	raise ValueError, 'Not callable set'

    def c_contains(self, a, b):
	mod = self.mod
	return (a & mod.iso(b)) is not mod.Nothing

    def c_get_biper(self, a):
	return self.mod.Classifiers.biper(a)

    def c_get_dictof(self, a):
	return self.mod.Classifiers.dictof(a)

    def c_disjoint(self, a, b):
	# Determine if a, b are disjoint
	return (a & b) is self.mod.Nothing

    def c_factordisjoint(self, a, b):
	# Given a and b factors, and not a <= b and not b <= a,
	# determine if they are disjoint

	return getattr(self, '_factordisjoint_%s'%(b.fam.opname,)) (a, b)

    def c_get_brief_alt(self, a, alt):
	return '[%s %s]'%(alt, self.c_get_brief(a))

    def c_uniset(self, X):
	return self.mod.uniset_from_setcastable(X)

    def c_get_examples(self, a, env):
	return []

    def c_getattr(self, a, b, args=(), kwds={}):
	d = self.export_dict
	if b in d:
	    return d[b](a, *args, **kwds)
	return self.c_getattr2(a, b)

    def c_getattr2(self, a, b):
	raise AttributeError, b

    def c_get_render(self, a):
	return self.mod.summary_str.str_address

    def c_get_str_for(self, a, b):
	# A modification of str, for some cases,
	# when the set a is used as a determination of an idset b
	# Normally the same as brief, but.. 'dict of' will be different for eg module
	return a.brief

    def c_get_idpart_header(self, a):
	render = a.get_render()
	h = getattr(render, 'im_func', render)
	h = getattr(h, '_idpart_header', None)
	if not h:
	    h = 'Value'
	return h

    def c_get_idpart_label(self, a):
	return '<%s>'%a

    def c_get_idpart_render(self, a):
	return self.c_get_render(a)

    def c_get_idpart_sortrender(self, a):
	render = self.c_get_idpart_render(a)
	if render is repr:
	    return 'IDENTITY'
	h = getattr(render, 'im_func', render)
	render = getattr(h, '_idpart_sortrender', render)
	return render

    def c_hash(self, a):
	return hash(a.arg)

    def c_iter(self, a):
	raise TypeError, 'iteration over non-sequence'

    def c_len(self, a):
	raise TypeError, 'len() of unsized object'

    def c_nonzero(self, a):
	return True

    def c_mul(self, a, b):
	return self.mod._parent.Spec.cprod(a, b)

    def c_lshift(self, a, b):
	return self.Doc.add_origin(self.c_map(a, b), self.Doc.binop('lshift', a, b))

    def c_map(self, a, b):
	if isinstance(b, list):
	    b = tuple(b)
	if not isinstance(b, tuple):
	    b = b,
	t = b + ('->', a)
	return self.mod._parent.Spec.mapping(*t)

    def c_repr(self, a):
	return self.c_str(a)

    def c_str(self, a):
	return self.c_get_brief(a)

    def c_sub(self, a, b):
	return a & ~b

    def c_test_contains(self, a, b, env):
	if not self.c_contains(a, b):
	    return env.failed('%s: %s does not contain %s'%(self.__class__, env.name(a), env.name(b)))
	return True

    def c_xor(self, a, b):
	return (a - b) | (b - a)

    def _or_OR(self, a, b):
	return b.fam._or_TERM(b, a)

    def _rand_ATOM(self, a, b):
	return self._and_ATOM(a, b)

class AtomFamily(Family):
    isatom = True
    isfactor = True
    opname = 'ATOM'

    def __init__(self, mod):
	Family.__init__(self, mod)
	self.disjoints |= [self]

    def c_and(self, a, b):
	return b.fam._and_ATOM(b, a)

    def _and_ATOM(self, a, b):
	return self.mod.fam_And(a, b)

    def _and_AND(self, a, b):
	return b.fam._and_ATOM(b, a)
    
    def _and_FACTOR(self, a, b):
	return self.mod.fam_And(a, b)

    def _and_INVERT(self, a, b):
	return b.fam._and_ATOM(b, a)

    def _factordisjoint_ATOM(self, a, b):
	return (a.fam.disjoints & b.fam.supers or
		b.fam.disjoints & a.fam.supers)

    def _factordisjoint_INVERT(self, a, b):
	return b.fam._factordisjoint_ATOM(b, a)

    def c_le(self, a, b):
	return b.fam._ge_ATOM(b, a)

    _le_AND = _le_INVERT = _le_AND = c_le

    def _le_ATOM(self, a, b):
	# b is known to not be Nothing since its c_ge doesn't call back
	return self.supercl is not None and self.supercl <= b

    def c_ge(self, a, b):
	return b.fam._le_ATOM(b, a)

    _ge_INVERT = _ge_AND = c_ge

    def _ge_ATOM(self, a, b):
	# b is known to not be Nothing since its c_le doesn't call back
	return b.fam.supercl is not None and b.fam.supercl <= a

    def c_or(self, a, b):
	return b.fam._or_ATOM(b, a)

    def _or_ATOM(self, a, b):
	return self.mod.fam_Or(a, b)

    _or_AND = _or_INVERT = c_or

    def c_invert(self, a):
	return self.mod.fam_Invert(a)

    def defrefining(self, arg):
	self.supercl = arg
	self.supers |= arg.fam.supers
	
    def defdisjoint(self, *args):
	# Define disjointness of sets under the condition that
	# neither of them is a subset of the other (determined in some other way.)
	# I.E., define that there is no partial overlap.
	# Declare that all sets of my (self) family are disjoint under this condition
	# from all sets of each family in args.

	self.disjoints |= args
	sc = self.supercl
	if sc is not None:
	    self.disjoints |= sc.fam.disjoints

    def defrefidis(self, arg):
	self.defrefining(arg)
	self.defdisjoint(arg.fam)

    def fam_union(self):
	return self.supercl


class ArgAtomFamily(AtomFamily):
    def _and_ID(self, a, b):
	cla, k, cmp = self.c_get_ckc(a)
	return cla.select_ids(b, k, cmp)
	
    def _ge_ATOM(self, a, b):
	# b is known to not be Nothing since its c_le doesn't call back
	if self is b.fam:
	    return a.arg == b.arg
	return b.fam.supercl is not None and b.fam.supercl <= a

    def _le_ATOM(self, a, b):
	# b is known to not be Nothing since its c_ge doesn't call back
	if self is b.fam:
	    return a.arg == b.arg
	return self.supercl is not None and self.supercl <= b

    def c_get_ckc(self, a):
	return self.classifier, a.arg, '=='


class AndFamily(Family):
    opname = 'AND'
    isatom = False
    isfactor = False

    def __call__(self, a, b):
	if a <= b:
	    return a
	if b <= a:
	    return b
	if a.fam.c_factordisjoint(a, b):
	    return self.mod.Nothing
	return self._cons((a, b))

    def _cons(self, arg):
	# We allow explicit non-normalized constructions, as an optimization
	# for a in arg:
	#    assert a.fam.isatom or isinstance(a.fam, InvertFamily)
	if len(arg) > 1:
	    return self.Set(self, tuple(arg))
	elif len(arg) == 1:
	    return arg[0]
	else:
	    return self.mod.Nothing

    def c_get_examples(self, a, env):
	ex = []
	for ai in a.arg:
	    try:
		e = env.get_examples(ai)
	    except CoverageError:
		pass
	    else:
		for ei in list(e):
		    for aj in a.arg:
			if aj is not ai:
			    if not env.contains(aj, ei):
				break
		    else:
			ex.append(ei)
	return ex


    def c_and(self, a, b):
	return b.fam._and_AND(b, a)

    def _and_AND(self, a, b):
	for b in b.arg:
	    a &= b
	return a

    def _and_FACTOR(self, a, b):
	# a0 & a1 & ... & b
	xs = []
	for ai in a.arg:
	    if ai <= b:
		return a
	    elif b <= ai:
		pass
	    elif ai.fam.c_factordisjoint(ai, b):
		return self.mod.Nothing
	    else:
		xs.append(ai)
	xs.append(b)
	return self._cons(xs)

    _and_ATOM = _and_INVERT = _and_FACTOR

    def _and_ID(self, a, b):
	b = a.arg[0] & b
	for a in a.arg[1:]:
	    if b is self.mod.Nothing:
		break
	    b = a & b
	return b


    def c_le(self, a, b):
	return b.fam._ge_AND(b, a)

    def _le_TERM(self, a, b):
	b = a & b
	if b.fam is not self or len(b.arg) != len(a.arg):
	    return False
	for x in a.arg:
	    for y in b.arg:
		if x <= y:
		    break
	    else:
		return False
	return True
	
    _le_ATOM = _le_INVERT = _le_AND = _le_TERM

    def c_ge(self, a, b):
	return b.fam._le_AND(b, a)

    def _ge_TERM(self, a, b):
	for a in a.arg:
	    if not a >= b:
		return False
	return True

    _ge_ATOM = _ge_INVERT = _ge_AND = _ge_TERM

    def c_or(self, a, b):
	return b.fam._or_AND(b, a)

    def _or_AND(self, a, b):
	# a0 & a1 ... | b0 & b1 ...
	# = 
	Omega = ~self.mod.Nothing
	for i, ai in enumerate(a.arg):
	    for j, bj in enumerate(b.arg):
		if ai | bj == Omega:
		    aa = self._cons(a.arg[:i] + a.arg[i+1:])
		    bb = self._cons(b.arg[:j] + b.arg[j+1:])
		    if aa == bb:
			return aa
	return self.mod.fam_Or(a, b)

    def _or_TERM(self, a, b):
	# a0 & a1 ... | b
	if a <= b:
	    return b
	if b <= a:
	    return a
	
	xs = []
	for ai in a.arg:
	    aib = ai | b
	    if aib.fam.isfactor:
		xs.append(aib)
	    else:
		break
	else:
	    r = ~self.mod.Nothing
	    for x in xs:
		r &= x
	    return r
	return self.mod.fam_Or(a, b)
	
    _or_ATOM = _or_INVERT = _or_TERM
	
    def c_invert(self, a):
	# ~(a0 & a1 ...) = ~a0 | ~a1 ...
	r = self.mod.Nothing
	for ai in a.arg:
	    r |= ~ai
	return r

    def c_contains(self, a, b):
	for x in a.arg:
	    if b not in x:
		return False
	return True

    def c_test_contains(self, a, b, env):
	for x in a.arg:
	    if not env.test_contains(x, b, 'and'):
		return env.failed('Failed')
	return True

    def c_disjoint3(self, a, b):
	return (a & b) is self.mod.Nothing

    def c_get_render(self, c):
	for kind in c.arg:
	    r = kind.get_render()
	    if r:
		return r
	def r(o):
	    return hex(id(o))
	return r

    def c_get_brief(self, c):
	names = [kind.brief for kind in c.arg]
	# names.sort() ?? I think now I want them in given order.
	return '(%s)'%' & '.join(names) + ')'

    def c_get_ckc(self, a):
	return (
	    self.mod.Classifiers.mker_and([x.biper for x in a.arg]).classifier,
	    (0,)*len(a.arg),
	    '=='
	    )

    def c_repr(self, a):
	reprs = [repr(k) for k in a.arg]
	return '(%s)'%' & '.join(reprs)

class OrFamily(Family):
    opname = 'OR'
    isatom = False
    isfactor = False
    def __call__(self, a, b):
	if b <= a:
	    return a
	if a <= b:
	    return b
	return self._cons((a, b))

    def _cons(self, arg):
	# Must only be called with maximalized args
	for a in arg:
	    assert a.fam.isfactor or isinstance(a.fam, AndFamily)
	if len(arg) > 1:
	    return Family.__call__(self, tuple(arg))
	elif len(arg) == 1:
	    return arg[0]
	else:
	    return self.mod.Nothing

    def c_contains(self, a, b):
	for x in a.arg:
	    if b in x:
		return True
	return False

    def c_get_ckc(self, a):
	return self.mod.Use.findex(*a.arg).classifier, len(a.arg), '<'

    def c_get_examples(self, a, env):
	exa = [iter(env.get_examples(x)) for x in a.arg]
	while 1:
	    n = 0
	    for i, e in enumerate(exa):
		if e is not None:
		    try:
			yield e.next()
		    except StopIteration:
			exa[i] = None
		    else:
			n += 1
	    if not n:
		break

    def c_test_contains(self, a, b, env):
	return env.forsome(a.arg, lambda x:env.test_contains(x, b, 'Some x'), 'or')

    def c_and(self, a, b):
	if self is b.fam:
	    return self._and_OR(a, b)
	else:
	    return self._and_TERM(a, b)
	
    def _and_TERM(self, a, b):
	# (a0 | a1 ..) & b = a0 & b | a1 & b | ...
	r = self.mod.Nothing
	for a in a.arg:
	    r |= a & b
	return r

    _and_ATOM = _and_INVERT = _and_AND = _and_TERM


    def _and_OR(self, a, b):
	# (a0 | a1 ..) & (b0 | b1 ..) = a0 & b0 | a0 & b1 ... a1 & b0 | a1 & b1 ...
	r = self.mod.Nothing
	for a in a.arg:
	    for bi in b.arg:
		r |= a & bi
	return r

    def _and_ID(self, a, b):
	ai = a.arg[0]
	r = ai.fam._and_ID(ai, b)
	for ai in a.arg[1:]:
	    r |= ai.fam._and_ID(ai, b)
	return r

    def _ge_TERM(self, a, b):
	#pdb.set_trace()
	a = a & b
	if a.fam is self:
	    if b.fam is not a.fam or len(b.arg) != len(a.arg):
		return False
	    assert 0
	else:
	    return b <= a

    _ge_ATOM = _ge_INVERT = _ge_AND = _ge_TERM

    def c_ge(self, a, b):
	if b.fam is self:
	    return self.c_le(b, a)
	else:
	    return self._ge_TERM(a, b)

    def c_le(self, a, b):
	for x in a.arg:
	    if not x <= b:
		return False
	return True

    _le_ATOM = _le_INVERT = _le_AND = c_le

    def c_or(self, a, b):
	return b.fam._or_OR(b, a)
	
    def _or_TERM(self, a, b):
	# a0 | a1 ... | b
	xs = []
	lt = False
	for a in a.arg:
	    if not b >= a:
		xs.append(a)
		if b <= a:
		    lt = True
	if not lt:
	    xs.append(b)
	return self._cons(xs)

    _or_ATOM = _or_INVERT = _or_AND = _or_TERM

    def _or_OR(self, a, b):
	# (a0 | a1 ...) | (b0 | b1 ...)
	xs = maximals(a.arg + b.arg)
	return self._cons(xs)

    def c_invert(self, a):
	# ~(a0 | a1 ...) = ~a0 & ~a1 ...
	r = ~a.arg[0]
	for ai in a.arg[1:]:
	    r &= ~ai
	return r

    def c_get_render(self, c):
	renders = self.mod.mutnodeset([kind.get_render() for kind in c.arg])
	if len(renders) == 1:
	    return list(renders)[0]
	else:
	    def r(o):
		return hex(id(o))
	    r._idpart_header = 'Address'
	    r._idpart_sortrender = lambda x:id(x)
	    return r

    def c_get_brief(self, c):
	names = [kind.brief for kind in c.arg]
	names.sort()
	return '(' + ' | '.join(names) + ')'

    def c_get_idpart_header(self, a):
	return 'Brief'

    def c_get_idpart_label(self, a):
	return '<mixed>'

    def c_get_idpart_render(self, a):
	er = self.mod.Use.Clodo
	cla = er.classifier
	cli = cla.cli

	brmemo = {}

	def render(x):
	    k = cli.classify(x)

	    br = brmemo.get(k)
	    if br is None:
		kind = cla.get_kind(k)
		b = cla.get_kind(k).brief
		r = kind.get_render()
		br = (b, r)
		brmemo[k] = br
	    b, r = br

	    return '%s: %s'%(b, r(x))
	
	return render

    def c_get_idpart_sortrender(self, a):
	er = self.mod.Use.Clodo
	cla = er.classifier
	cli = cla.cli

	brmemo = {}

	def render(x):
	    k = cli.classify(x)
	    br = brmemo.get(k)
	    if br is None:
		kind = cla.get_kind(k)
		b = cla.get_kind(k).brief
		r = kind.fam.c_get_idpart_sortrender(kind)
		br = (b, r)
		brmemo[k] = br
	    else:
		b, r = br
	    if r != 'IDENTITY':
		x = r(x)
	    return (b, x)
	return render

    def c_repr(self, a):
	reprs = [repr(k) for k in a.arg]
	reprs.sort()
	return '(%s)'%' | '.join(reprs)


class InvertFamily(Family):
    opname = 'INVERT'
    isatom = False
    isfactor = True
    def __call__(self, a):
	assert a.fam.isatom
	if a is self.mod.Nothing:
	    return self.mod.NotNothing
	else:
	    return Family.__call__(self, a)

    def c_test_contains(self, a, b, env):
	return env.test_contains_not(a.arg, b, 'InvertFamily')

    def c_contains(self, a, b):
	return not b in a.arg

    def c_and(self, a, b):
	return b.fam._and_INVERT(b, a)

    _and_AND = c_and

    def _and_FACTOR(self, a, b):
	# ~a.arg & ~b.arg
	# ~a.arg & b
	# Is normal form?
	x = a.arg & b
	if x.fam.isatom:
	    a = self(x)
	return self.mod.fam_And(a, b)

    _and_ATOM = _and_INVERT = _and_FACTOR

    def _and_ID(self, a, b):
	return b - (b & a.arg)

    def _factordisjoint_ATOM(self, a, b):
	# ~ a.arg <disjoint> b
	return b <= a.arg

    def _factordisjoint_INVERT(self, a, b):
	# ~ a.arg <disjoint> ~b.arg
	return False

    def c_le(self, a, b):
	return b.fam._ge_INVERT(b, a)

    _le_AND = c_le

    def _le_ATOM(self, a, b):
	# ~a.arg <= b
	return False 

    def _le_INVERT(self, a, b):
	# ~a.arg <= ~b.arg
	return b.arg <= a.arg

    def c_ge(self, a, b):
	# ~a.arg >= b
	return a.arg.disjoint(b)
	
    _ge_ATOM = _ge_INVERT = _ge_AND = c_ge

    def c_or(self, a, b):
	return b.fam._or_INVERT(b, a)

    _or_AND = c_or

    def _or_FACTOR(self, a, b):
	# ~a.arg | b
	if a.arg <= b:
	    return ~self.mod.Nothing
	x = a.arg & b
	if x is self.mod.Nothing:
	    return a
	return self.mod.fam_Or(a, b)

    _or_ATOM = _or_INVERT = _or_FACTOR

    def c_invert(self, a):
	# ~(~a.arg) = a.arg
	return a.arg

    def c_get_render(self, a):
	return a.arg.get_render()

    def c_get_brief(self, a):
	n = a.arg.brief
	if (not (n.startswith('(') or n.startswith('<')) and
	    ' ' in n):
	    n = '(%s)'%n
	return '~%s'%n

    def c_get_ckc(self, a):
	# This uses only existing machinery for C-level classification.
	# The alternatives are discussed in Notes 21 Sep 2005.
	
	return (
	    a.arg.biper.classifier,
	    0,
	    '!='
	    )

    def c_repr(self, a):
	return '~%s'%repr(a.arg)

class FamilyFamily(AtomFamily):
    def __init__(self, mod):
	AtomFamily.__init__(self, mod)
	self.add_export('union', lambda x: x.arg.fam_union())

    def c_contains(self, a, b):
	return isinstance(b, UniSet) and b.fam is a.arg

    def c_get_brief(self, c):
	return '<Family: %s>'%c.arg.__class__

class IdentitySetFamily(AtomFamily):
    def __init__(self, mod):
	AtomFamily.__init__(self, mod)
	self.defrefining(mod.Anything)
	# I think this is wrong
	# It's not used?
	#
	if 0:
	    self.defdisjoint(mod.Anything.fam) # No overlap with sets of other families??

	self.immnodeset = mod.immnodeset
	self.Part = mod.Part
	self.Path = mod.Path
	self.RefPat = mod.RefPat
	self.View = mod.View
	self.Use = mod.Use

    def __call__(self, *args, **kwds):
	return self._cons(args, **kwds)

    def _cons(self, arg, er=None):
	# arg is a sequence of nodes
	arg = self.immnodeset(arg)
	if not arg:
	    return self.mod.Nothing

	# elif len(arg) == 1: # Not using special case. Screws up some things Note 27 Oct 2005
	#     r = IdentitySetSingleton(self, tuple(arg)[0])
	else:
	    r = IdentitySetMulti(self, arg)
	if er is not None:
	    r._er = er
	return r

    def c_and(self, a, b):
	if b.fam is self:
	    return self._cons(a.nodes & b.nodes)
	elif b.fam is self.mod.fam_Invert:
	    return self._and_INVERT(a, b)
	else:
	    return b.fam._and_ID(b, a)

    def _and_ATOM(self, a, b):
	if b.fam is self:
	    return self._cons(a.nodes & b.nodes)
	else:
	    return b.fam._and_ID(b, a)

    def _and_AND(self, a, b):
	return b.fam._and_ID(b, a)

    def _and_ID(self, a, b):
	return self._cons(a.nodes & b.nodes)

    def _and_INVERT(self, a, b):
	if b.arg.fam  is self:
	    return self._cons(a.nodes - b.arg.nodes)
	elif b is self.mod.NotNothing:
	    return a
	else:
	    return b.fam._and_ID(b, a)

    def c_get_ckc(self, a):
	return self.mod.Classifiers.Idset.classifier, a.nodes, '<='

    def c_hash(self, a):
	return hash(a.nodes)

    def c_iter(self, a):
	# It's not well-defined to iterate and is considered error-prone
	# and may be SO much slower than expected
	# they need to be explicit to iterate over elements or partition subset
	raise TypeError, 'iteration over non-sequence'


    def c_len(self, a):
	# The length corresponds to 
	# o the number of rows in how it is printed
	# o the max getitem-wise index + 1
	# (Notes May 13 2005)
	return a.partition.numrows

    def c_contains(self, a, b):
	return b in a.nodes

    def c_le(self, a, b):
	if not b.fam is self:
	    b = b.fam._and_ID(b, a)
	return a.nodes <= b.nodes

    _le_ATOM = _le_INVERT = _le_AND = c_le

    def c_or(self, a, b):
	if b.fam is self:
	    return self._cons(a.nodes | b.nodes)
	else:
	    a = a - b.fam._and_ID(b, a)
	    return b.fam._or_ATOM(b, a)

    _or_ATOM = _or_INVERT = _or_AND = _or_OR = c_or

    def c_get_brief(self, c):
	return self.get_str_summary(c)

    def c_get_render(self, a):
	return a.kind.get_render()

    def c_getitem(self, a, idx):
	return a.partition.get_set(idx)

    def c_str(self, a):
	ob = self.mod._parent.OutputHandling.output_buffer()
	a.fam.get_partition(a).ppob(ob)
	return ob.getvalue().rstrip()

    def maprox_getattr(self, set, name):
	ns = self.mod.mutnodeset()
	for x in set.nodes:
	    try:
		v = getattr(x, name)
	    except:
		pass
	    else:
		ns.add(v)
	return self._cons(self.mod.immnodeset(ns))


    def maprox_getitem(self, set, idx):
	ns = self.mod.mutnodeset()
	for x in set.nodes:
	    try:
		v = x[idx]
	    except:
		pass
	    else:
		ns.add(v)
	return self._cons(self.mod.immnodeset(ns))

    def c_get_idpart_header(self, a):
	return 'Kind: Name/Value/Address'

    def c_get_idpart_label(self, a):
	return ''

    def c_get_idpart_render(self, a):
	def render(x):
	    x = self.mod.iso(x)
	    r = x.brief.lstrip('<1 ').rstrip('>')
	    return r
	return render

    def get_by(self, a, er):
	ers = []
	if isinstance(er, EquivalenceRelation):
	    ers.append(er)
	else:
	    try:
		ss = er.split('&')
	    except:
		raise TypeError, 'by(): Equivalence relation or string expected.'
	    if ss == ['']:
		ss = []
	    for s in ss:
		try:
		    if not s.istitle() or s.startswith('er_'):
			s = 'er_'+s
		    er = getattr(self.Use, s)
		except AttributeError:
		    raise ValueError, 'by(): No such equivalence relation defined in heapy.Use: %r'%s
		ers.append(er)
		    
	if not ers:
	    er = self.Use.Unity
	else:
	    er = ers[0]
	    for i in range(1, len(ers)):
		er &= ers[i]
	if a.er is not er:
	    a = self._cons(a.nodes, er=er)
	return a

    def get_er(self, a):
	try:
	    er = a._er
	except AttributeError:
	    er = self.mod.Use.Clodo
	    a._er = er
	return er

    def get_more(self, a):
	return self.mod.OutputHandling.basic_more_printer(a, a.partition)

    def get_owners(self, a):
	return self.mod.Use.Clodo.classifier.owners(a)

    def get_partition(self, a):
	try:
	    p = a._partition
	except AttributeError:
	    a.fam.View.clear_check()
	    p = a.fam.Part.partition(a, a.er)
	    self._partition = p
	return p




    def get_str_idpart(self, set, cla):
	# Get the string that is used for the 'identity partition'
	# when the objects share a common classification (cla)
	s = cla.fam.c_get_str_for(cla, set)
	return s


    def get_str_refpat(self, set, cla, max_length):
	# Get the string that is used at the end of a reference pattern line
	strs = []
	strs.append('%d '%set.count)
	strs.append(cla.fam.c_get_str_for(cla, set))
	strs.append(': ')
	strs.append(self.get_str_rendered(set, cla, max_length-len(''.join(strs))))
	s = ''.join(strs)
	if len(s) > max_length:
	    s = s[:max_length - 3]+'...'
	return s

    def get_str_rendered(self, set, cla, max_length=None):
	if max_length is None:
	    max_length = 50
	strs = []
	lens = 0
	render = cla.get_render()
	for p in set.nodes:
	    rs = render(p)
	    if lens and lens + len(rs) + 2 >= max_length:
		strs[-1] +='...' # but what can be done in limited time
		break
	    lens += len(rs) + 2
	    strs.append(rs)
	strs.sort()
	return ', '.join(strs)


    def get_str_summary(self, c, max_length=None, er=None):
	if max_length is None:
	    max_length = self.mod.max_summary_length
	if er is None:
	    er = c.er
	set = c.nodes
	items = er.classifier.partition(set)
	keys = [k for k, v in items]
	cla = reduce(lambda x, y: x | y, keys)
	s = '<%d %s'%(len(set), cla.fam.c_get_str_for(cla, c))
	s += ': '
	bslen = len(s)

	bstrs = []
	for cla, set in items:
	    css = self.get_str_rendered(set, cla, max_length-bslen)
	    if len(items) > 1:
		css = '<%d %s: %s>'%(set.count, cla, css)
	    bstrs.append(css)
	    bslen += len(css) + 3
	    if bslen > max_length:
		break
	def comp(a, b):
	    # Don't use the initial count when comparing
	    return cmp(a[a.index(' '):],b[b.index(' '):])
	bstrs.sort(comp)
	s += ' | '.join(bstrs) + '>'
	if len(s) > max_length:
	    s = s[:max_length-4]+'...>'
	return s

    def get_parts(self, X):
	return [x for x in X.partition.get_sets()]

    def get_theone(self, set):
	if len(set.nodes) == 1:
	    return list(set.nodes)[0]
	raise ValueError, 'theone requires a singleton set'

class EmptyFamily(IdentitySetFamily):
    # Inherits from IdentitySetFamily because the special exported methods
    # tend to be required by applications.
    # There is only one object of EmptyFamily: UniSet.Nothing
    # The new method implementations added here are mostly for optimization.
    # (Other families may assume the EmptyFamily have these methods.)
    # The .nodes is an empty immnodeset so IdentitySetFamily methods should work.
    # The main change from IdentitySetFamily is the representations.
    def __init__(self, mod):
	IdentitySetFamily.__init__(self, mod)

    def c_and(self, a, b):
	return a

    _and_ATOM = _and_INVERT = _and_AND = _and_OR = _and_ID = c_and

    def c_contains(self, a, b):
	return False

    def c_ge(self, a, b):
	if b is a:
	    return True
	return False

    _ge_ATOM = _ge_INVERT = _ge_AND = c_ge

    def c_get_brief(self, a):
	return '<Nothing>'

    def c_repr(self, a):
	return '%s%s'%(self.mod.Use.reprefix, 'Nothing')

    def c_iter(self, a):
	return iter(())

    def c_le(self, a, b):
	return True

    _le_ATOM = _le_INVERT = _le_AND = c_le

    def c_len(self, a):
	return 0

    def c_nonzero(self, a):
	return False

    def c_or(self, a, b):
	return b

    _or_ATOM = _or_INVERT = _or_AND = _or_OR = c_or

    def c_str(self, a):
	return self.c_get_brief(a)

    def c_sub(self, a, b):
	return a

    def c_xor(self, a, b):
	return b

class EquivalenceRelationFamily(AtomFamily):
    def __init__(self, mod):
	AtomFamily.__init__(self, mod)
	self.Set = EquivalenceRelation
	self.Use = mod.Use
	self.Classifiers = mod.Classifiers

    def __call__(self, constructor, *args, **kwds):
	# Passing classifier constructor rather than constructed classifier,
	# to make sure there is a 1-1 relation between equivalence relations and classifers.
	cl = constructor(*args, **kwds)
	er = self.Set(self, cl)
	cl.er = er
	return er

    def c_contains(self, a, b):
	# XXX should have a smoother protocol
	try:
	    return len(b.by(a)) == 1
	except AttributeError:
	    try:
		ckc = b.get_ckc()
	    except:
		return False
	    else:
		return ckc[0].er <= a and ckc[2] == '=='

    def c_getattr(self, a, name):
	classifier = a.classifier
	try:
	    g = getattr(classifier, 'get_attr_for_er')
	except AttributeError:
	    raise AttributeError, name
	return g(name)
	

    def c_and(self, a, b):
	if b.fam is not self:
	    return AtomFamily.c_and(self, a, b)
	ers = []
	for x in (a, b):
	    if x.erargs:
		ers.extend(x.erargs)
	    else:
		ers.append(x)
	ers = minimals(ers)
	if len(ers) == 1:
	    return ers[0]
	er = self.Classifiers.mker_and(ers)
	er.erargs = tuple(ers)
	return er

    def _ge_ATOM(self, a, b):
	if b.fam is self:
	    return a.classifier in b.classifier.super_classifiers
	return False
	

    def _le_ATOM(self, a, b):
	if b.fam is self:
	    return b.classifier in a.classifier.super_classifiers
	return False

    def c_call(self, a, args, kwds):
	return a.classifier.get_userkind(*args, **kwds)

    def c_get_brief(self, a):
	return 'Equiv. relation %s'%a.classifier

    def c_getitem(self, a, idx):
	return a.classifier.relimg(self.mod.nodeset_adapt(idx))
    
    def c_repr(self, a):
	return a.classifier.get_reprname()

class Summary_str:
    def __init__(self, mod):
	self.mod = mod
	types = mod.types._module
	self.invtypes = {}
	for k, v in types.__dict__.items():
	    if isinstance(v, types.TypeType):
		self.invtypes[v] = 'types.%s'%k
	for k, v in types.__builtins__.items():
	    if isinstance(v, types.TypeType) and v in self.invtypes:
		self.invtypes[v] = k

	# This is to make common printouts prettier / shorter (: and clearer ? :)
	# but may be disabled for clearer repr()
	
	self.shorter_invtypes = {}
	for name in ('module', 'class', 'function'):
	    t = getattr(types, name.capitalize()+'Type')
	    self.shorter_invtypes[t] = name

	#

	self.table = {
	        mod.NodeSet: self.str_address_len,
		types.BooleanType: self.str_repr,
		types.BuiltinFunctionType: self.str_builtin_function,
		types.ClassType: self.str_class,
		types.CodeType: self.str_code,
		types.ComplexType: self.str_repr,
		types.DictType: self.str_address_len,
		types.FloatType: self.str_repr,
		types.FrameType: self.str_frame,
		types.FunctionType: self.str_function,
		types.InstanceType: self.str_instance,
		types.IntType: self.str_repr,
		types.ListType: self.str_address_len,
		types.LongType: self.str_repr,
		types.NoneType: self.str_repr,
		types.MethodType: self.str_method,
		types.ModuleType: self.str_module,
		types.TracebackType: self.str_traceback,
		types.StringType: self.str_limrepr,
		types.UnicodeType: self.str_limrepr,
		types.TupleType: self.str_address_len,
		types.TypeType: self.str_type,
		}
    def __call__(self, key, longer=False):
	x = self.table.get(key)
	if x is None:
	    x = self.str_address
	if longer and 'longer' in x.im_func.func_code.co_varnames:
	    return lambda k:x(k, longer=longer)
	else:
	    return x

    def set_function(self, type, func):
	self.table[type] = func

    def str_address(self, x):
	return hex(id(x))
    str_address._idpart_header = 'Address'
    str_address._idpart_sortrender = id
    def str_address_len(self, x):
	return self.str_address(x)+self.str_len(x)
    str_address_len._idpart_header = 'Address*Length'
    str_address_len._idpart_sortrender = id
    def str_builtin_function(self, x):
	n = x.__name__
	m = x.__module__
	if m != '__builtin__':
	    n = '%s.%s'%(m, n)
	return n
    str_builtin_function._idpart_header = 'Name'
    def str_class(self, x):
	return str(x)
    str_class._idpart_header = 'Name'
    def str_code(self, x):
	return '%s:%d:%s'%(self.mod._root.os.path.basename(x.co_filename),
			   x.co_firstlineno,
			   x.co_name)
    str_code._idpart_header = 'File:Line:Name'
    def str_frame(self, x):
	return '<%s at %s>'%(x.f_code.co_name, self.str_address(x))
    str_frame._idpart_header = 'Name at Address'
    def str_function(self, x):
	return '%s.%s'%(x.__module__, x.func_name)
    str_function._idpart_header = 'Name'
    def str_instance(self, x):
	return '<%s at %s>' %(self.str_class(x.__class__), self.str_address(x))
    str_instance._idpart_header = 'Name at Address'
    def str_len(self, x):
	return '*%d'%len(x)
    str_len._idpart_header = 'Length'
    def str_method(self, x):
	cn = self.str_type(x.im_class)
	if x.im_self is not None:
	    cn = '<%s at %s>'%(cn, self.str_address(x.im_self))
	func = x.im_func
	try:
	    func_name = func.im_func
	except AttributeError:
	    func_name = func.__name__
	return '%s.%s'%(cn, func_name)
    str_method._idpart_header = 'Class/<Class at address> . method'
    def str_module(self, x):
	return x.__name__
    str_module._idpart_header = 'Name'
    def str_limrepr(self, x):
	return self.mod._root.repr.repr(x)
    str_limrepr._idpart_header = 'Representation (limited)'
    str_limrepr._idpart_sortrender = 'IDENTITY'
    str_repr = repr
    def str_traceback(self, x):
	return '<in frame %s at %s>'%(self.str_frame(x.tb_frame), self.str_address(x))
    str_traceback._idpart_header = 'Frame at Address'
    def str_type(self, x, longer=False):
	if x in self.shorter_invtypes and not longer:
	    return self.shorter_invtypes[x]
	if x in self.invtypes:
	    return self.invtypes[x]
	return '%s.%s'%(x.__module__, x.__name__)
    str_type._idpart_header = 'Name'
    def str_type_longer(self, x):
	if x in self.invtypes:
	    return self.invtypes[x]
	return '%s.%s'%(x.__module__, x.__name__)
    str_type._longer_method = lambda x:str_type


def maximals(A, le=lambda x,y:x<=y):
    " Find the maximal element(s) of a partially ordered sequence"
    r = []
    for x in A:
	for a in A:
	    if le(x, a) and not le(a, x):
		break
	else:
	    for a in r:
		if le(x, a):
		    break
	    else:
		r.append(x)
    return r

def minimals(A, le=lambda x,y:x<=y):
    " Find the minimal element(s) of a sequence of partially ordered elements"
    r = []
    for x in A:
	for a in A:
	    if le(a, x) and not le(x, a):
		break
	else:
	    for a in r:
		if le(a, x):
		    break
	    else:
		r.append(x)
    return r


class _GLUECLAMP_:
    max_summary_length = 80
    auto_convert_type = True
    auto_convert_class = True
    auto_convert_iter = False	# Can give problems if enabled; notes 22/11-04
    out_reach_module_names = ('UniSet', 'View', 'Path', 'RefPat')

    _chgable_ = ('max_summary_length','out_reach_module_names',
		 'auto_convert_type', 'auto_convert_class', 'auto_convert_iter', 'output')

    # _preload_ = ('_hiding_tag_',)

    # Module 'imports'

    _imports_ = (
	'_parent:Classifiers',
	'_parent:ImpSet',
	'_parent.ImpSet:emptynodeset',
	'_parent.ImpSet:immnodeset',
	'_parent.ImpSet:mutnodeset',
	'_parent.ImpSet:NodeSet',
	'_parent:Part',
	'_parent:Path',
	'_parent:RefPat',
	'_parent:OutputHandling',
	'_parent:View',
	'_parent.View:_hiding_tag_',
	'_parent.View:hv',
	'_parent:Use',
	'_root:types',
	)

    #

    def _get_Anything(self):	return self.Use.Unity.classifier.get_kind(None)
    def _get_Nothing(self):	return IdentitySetMulti(EmptyFamily(self), self.emptynodeset)
    def _get_NotNothing(self):	return Family.__call__(self.fam_Invert, self.Nothing)

    def _get_export_dict(self):
	d = {}
	for k, v in self.out_reach_dict.items():
	    sc = getattr(v, '_uniset_exports', ())
	    for sc in sc:
		x = getattr(v, sc)
		if sc in d and d[sc] is not x:
		    raise RuntimeError, 'Duplicate export: %r defined in: %r'%(sc, k)
		d[sc] = x
	return d

    def _get_out_reach_dict(self):
	d = {}
	for name in self.out_reach_module_names:
	    d[name] = getattr(self._parent, name)
	return d

    def _get_summary_str(self):	return self.Summary_str(self)

    def _get_fam_And(self):	return self.AndFamily(self)
    def _get_fam_EquivalenceRelation(self): return EquivalenceRelationFamily(self)
    def _get_fam_Or(self):	return self.OrFamily(self)
    def _get_fam_IdentitySet(self):return self.IdentitySetFamily(self)
    def _get_fam_Invert(self): 	return self.InvertFamily(self)
    def _get_fam_Family(self): 	return self.FamilyFamily(self)
    

    def _get_fam_mixin_argatom(self):
	memo = {}
	def f(Mixin, *args, **kwds):
	    C = memo.get(Mixin)
	    if C is None:
		class C(Mixin, self.ArgAtomFamily):
		    def __init__(self, mod, *args, **kwds):
			mod.ArgAtomFamily.__init__(self, mod)
			Mixin.__init__(self, mod, *args, **kwds)

		C.__name__ = Mixin.__name__
		memo[Mixin] = C
	    return C(self, *args, **kwds)
	return f

    def idset_adapt(self, X):
        if isinstance(X, self.IdentitySet):
	    ids = X
	elif isinstance(X, self.NodeSet):
	    ids = self.idset(X)
	else:
	    raise TypeError, 'IdentitySet or NodeSet expected, got %r.'%type(X)
	if X._hiding_tag_ is not self._hiding_tag_:
	    raise ValueError,	\
		  "The argument has wrong _hiding_tag_, you may convert it by Use.idset or Use.iso."
	return ids

    def idset(self, iterable, er=None):
	return self.fam_IdentitySet._cons(self.immnodeset(iterable), er=er)

    def _get_iso(self):
	return self.fam_IdentitySet

    def isuniset(self, obj):
	return isinstance(obj, self.UniSet)
	# Or has some particular attributes?

    def nodeset_adapt(self, X):
	if isinstance(X, self.NodeSet):
	    ns = X
	elif isinstance(X, self.IdentitySet):
	    ns = X.nodes
	else:
	    raise TypeError, 'IdentitySet or NodeSet expected, got %r.'%type(X)
	if X._hiding_tag_ is not self._hiding_tag_:
	    raise ValueError,	\
		  "The argument has wrong _hiding_tag_, you may convert it by Use.idset or Use.iso."
	return ns

    def retset(self, X):
	if not isinstance(X, self.IdentitySet):
	    X = self.idset(X)
	return X

    def union(self, args, maximized=False):
	if not args:
	    return self.Nothing
	a = args[0]
	for b in args[1:]:
	    a |= b
	return a

        # This optimization didn't work for idsets!!
	# XXX to fix back

	if not maximized:
	    args = maximals(args)
	return self.fam_Or._cons(args)

    def uniset_from_setcastable(self, X):
	if isinstance(X, UniSet) and X._hiding_tag_ is self._hiding_tag_:
	    return X
	
	types = self.types
	if isinstance(X, types.TypeType) and self.auto_convert_type:
	    return self.Use.Type(X)
	elif isinstance(X, types.ClassType) and self.auto_convert_class:
	    return self.Use.Class(X)
	elif isinstance(X, self.NodeSet) and X._hiding_tag_ is self._hiding_tag_:
	    return self.idset(X)
	elif self.auto_convert_iter:
	    try:
		it = iter(X)
	    except TypeError:
		pass # Will raise a 'more informative' exception below
	    else:
		return self.idset(it)
	raise TypeError, \
          "Argument is not automatically convertible to a UniSet with correct _hiding_tag_."


