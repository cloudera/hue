#._cv_part guppy.heapy.Use

import guppy.etc.Glue

class _GLUECLAMP_(guppy.etc.Glue.Interface):
    _preload_ = '_hiding_tag_',
    _chgable_ = ('reprefix', 'default_reprefix', 'gcobjs',
                 'relheap', 'relheapg', 'relheapu', '__doc__')
    _dir_ = (
            'Anything', 'Class', 'Clodo', 'Id', 'Idset', 'Module',
            'Nothing', 'Rcs', 'Root', 'Size', 'Type', 'Unity',
            'Via', 'doc', 'findex', 'heap', 'heapu',
            'idset','iso', 'load', 'monitor', 'pb',
            'setref', 'test')

    _private_ = ('View','_hiding_tag_','_load_stat','ctime','default_reprefix',
                 'dumph','gcobjs','heapg','loadc','relheap','relheapg',
                 'relheapu','reprefix','setrelheap','setrelheapg',
                 'setrelheapu','tc_adapt','tc_repr','union',
                 'uniset_from_setcsatable','warnings','Stat'
                 )

    default_reprefix = 'hpy().'

    def _get_gcobjs(self):
	return self.Nothing

    def _get_relheap(self):
	return self.Nothing

    def _get_relheapg(self):
	return self.Nothing

    def _get_relheapu(self):
	return self.Nothing

    def _get_reprefix(self):
	# The name that this instance (or one with the same ._share)
	# has in the __main__ module, if any, or self.default_reprname otherwise.
	# Used for prefixing the result of repr() of various objects
	# so it becomes possible to evaluate it in a typical environment.
	import __main__
	for k, v in __main__.__dict__.items():
	    if (isinstance(v, self.__class__) and
		getattr(v, '_share', None) is self._share):
		return '%s.'%k
	return self.default_reprefix

    def _get_Root(self):
        """Root: RootStateType

This attribute is a symbolic root containing attributes from which all
reachable objects in the heap can be reached. It is the only value (a
singleton) of its kind; see [1] for a description of its attributes.

References
	[0] heapy_Use.html#heapykinds.Use.Root
	[1] heapy_RootState.html#heapykinds.RootStateType"""

        return self.View.heapyc.RootState

    def __repr__(self):
        return """\
Top level interface to Heapy.
Use eg: %sdoc for more info on %s.""" %(
            self.reprefix,self.reprefix[:-1])
        

    __str__=__repr__

    def Ddir(self, opts=''):
        """\
        #OBSOLETE
$HP.dir(opts: str+])-> GuppyDir
$HP.dir(opts: str+]).<attribute> -> GuppyDoc

A replacement for the builtin function dir(), providing a listing of
public attributes for Heapy objects. It also has an attribute for each
item in the listing, for example:

>>> $HP.dir().heap

returns a GuppyDoc object providing documentation for the heap
method. The method also takes a string argument specifying further
options. Currently the following are provided:

        'l'	Generate a listing of the synopsis lines.
	'L'	Generate a listing of the entire doc strings."""

        obj = self
        return self._root.guppy.etc.Help.dir(obj, opts)

    def _get_doc(self):
        """Overview documentation for top level Heapy object.
Provides a listing of the available attributes.
Accessing the attribute name on the doc objects gives further info, eg:

    >>> hp.doc.heap

gives doc for the heap method when hp is the top level Heapy object.

References may be embedded in the documentations. To access a
reference, opening up a web browser with the doc for it one can do eg:

    >>> hp.doc.heap[1]

The reference number 0 is special. If it is provided, it is the
reference to the html doc for the described object itself. So to see
in the web browser the doc for the heap method one can do:

    >>> hp.doc.heap[0]

References
    [0] heapy_Use.html#heapykinds.Use.doc"""

        return self._root.guppy.etc.Help.dir(self,
                                             header="""\
Top level interface to Heapy. Available attributes:""",
                                             footer="""\
Use eg: %sdoc.<attribute> for info on <attribute>."""%self.reprefix)
        

    def heapg(self, rma=1):
        """ DEPRECATED """
        self.warnings.warn(
"Method Use.heapg is depreciated, it doesn't work well. Use heapu instead.")
	h = self.View.heapg(rma)
	h -= self.relheapg
	return h
	
    def heapu(self, rma=1, abs=0, stat=1):
        """heapu() -> Stat 

Finds the objects in the heap that remain after garbage collection but
are _not_ reachable from the root.  This can be used to find objects
in extension modules that remain in memory even though they are
gc-collectable and not reachable.

Returns an object containing a statistical summary of the objects
found - not the objects themselves. This is to avoid making the
objects reachable.

See also: setref[1]

References
    [0] heapy_Use.html#heapykinds.Use.heapu
    [1] heapy_Use.html#heapykinds.Use.setref"""


	h = self.View.heapu(rma)
        rel = 0
        if not abs and self.relheapu and isinstance(self.relheapu, type(h)):
            h -= self.relheapu
            rel = 1
        if stat:
            h = h.stat
            if not abs and self.relheapu and isinstance(self.relheapu, type(h)):
                h -= self.relheapu
                rel = 1

            h.firstheader = 'Data from unreachable objects'

            if rel:
                h.firstheader += ' relative to: %s'%\
                                 self.ctime(self.relheapu.timemade)
            h.firstheader += '.\n'
            

	return h
	
    def heap(self):
        """heap() -> IdentitySet[1]

Traverse the heap from a root to find all reachable and visible
objects. The objects that belong to a heapy instance are normally not
included. Return an IdentitySet with the objects found, which is
presented as a table partitioned according to a default equivalence
relation (Clodo [3]).

See also: setref[2]

References
    [0] heapy_Use.html#heapykinds.Use.heap
    [1] heapy_UniSet.html#heapykinds.IdentitySet
    [2] heapy_Use.html#heapykinds.Use.setref
    [3] heapy_Use.html#heapykinds.Use.Clodo"""

	h = self.View.heap()
	h |= self.gcobjs
	h -= self.relheap
	return h

    def load(self, fn, use_readline=0):
        """\
load(alt:[fn: loadablefilenamestring+ or
          fn: loadableiterableofstrings+]
     [use_readline = boolean+]) -> Stat

Load heapy-related data from a serialized form. Currently it handles
data generated by Stat.dump.

Arguments
    fn: loadablefilenamestring+
        A string argument is treated as a file name.
    fn: loadableiterableofstrings+
        An open file or an iterator will be iterated over enough
        to read one package of data, and another call to load
        will read the next package.
    use_readline = boolean+
        If true, the method will use .readline() instead of
        iteration, which may be necessary in case the input
        comes from a pipe since otherwise the Python runtime
        would try to read ahead a big block before returning the
        first package of data.
Returns
    one package of statistical data.

References
    [0] heapy_Use.html#heapykinds.Use.load"""

	if isinstance(fn, basestring):
	    # We got a filename.
	    # I want to read only what is being requested
	    # so I can look quickly at some lines of a long table.
	    # (There are seemingly easier ways to do this
	    #  but this takes care of some tricky details.
	    #  Keeping f open avoids it to be overwritten
	    #  (at least by Stat.dump() and if OS=Linux)
	    #  if data are written to a new file with the same name.)
	    f = open(fn)
	    def get_trows():
		pos = 0
		while 1:
		    f.seek(pos)
		    line = f.readline()
		    if not line:
			break
		    pos = f.tell()
		    yield line
	elif hasattr(fn, '__iter__') and not hasattr(fn, 'next'):
	    # We got a sequence, that is not an iterator. Use it directly.
	    def get_trows():
		return fn
	elif hasattr(fn, 'next'):
	    # We got an iterator or file object.
	    # We 'have' to read all lines (at once)-
	    # to update the read position -
	    # to mimic 'pickle' semantics if several
	    # objects are stored in the same file.
	    # We can't use .next always - (eg not on pipes)
	    # it makes a big readahead (regardless of buffering setting).
	    # But since .next() (typically) is much faster, we use it
	    # per default unless use_readline is set.
	    if use_readline:
		get_line = fn.readline
	    else:
		get_line = fn.next

	    trows = []
	    line = get_line()
	    if not line:
		raise StopIteration
	    endline = '.end: %s'%line
	    try:
		while line:
		    trows.append(line)
		    if line == endline:
			break
		    line = get_line()
		else:
		    raise StopIteration
	    except StopIteration:
		trows.append(endline)

	    def get_trows():
		return trows
	else:
	    raise TypeError, 'Argument should be a string, file or an iterable yielding strings.'

	a = iter(get_trows()).next()
	if not a.startswith('.loader:'):
	    raise ValueError, 'Format error in %r: no initial .loader directive.'%fn
	loader = a[a.index(':')+1:].strip()
	try:
	    loader = getattr(self, loader)
	except AttributeError:
	    raise ValueError, 'Format error in %r: no such loader: %r.'%(fn, loader)
	return loader(get_trows)
	
    def loadall(self,f):
        ''' Generates all objects from an open file f or a file named f'''
        if isinstance(f,basestring):
            f=open(f)
        while True:
            yield self.load(f)

    def loadc(self, fn):
	f = open(fn, 'r', 1)
	while 1:
	    print self.load(f, use_readline=1)
	    
    def dumph(self, fn):
	f = open(fn, 'w')
	import gc
	while 1:
	    x = self.heap()
	    x.stat.dump(f)
	    f.flush()
	    print len(gc.get_objects())

    def setref(self, reachable=None, unreachable=None):
        """setref()

Set a reference point for heap usage measurement.  This applies to
both the heap[1] and heapu[2] methods. The heap() method will only
show the objects allocated after the time setref was called. The
heapu() method, since it deals with summary data and not actual
objects, will show the difference of sizes and counts compared to when
setref was called.

References
    [0] heapy_Use.html#heapykinds.Use.setref
    [1] heapy_Use.html#heapykinds.Use.heap
    [2] heapy_Use.html#heapykinds.Use.heapu"""

        if reachable is None and unreachable is None:
            self.setrelheap()
            self.setrelheapu()
        else:
            if reachable is not None:
                self.setrelheap(reachable)
            if unreachable is not None:
                self.setrelheapu(unreachable)

    def setrelheap(self, reference=None):
	if reference is None:
	    reference = self.View.heap()
	self.relheap = reference

    def setrelheapg(self, reference=None):
        self.warnings.warn(
"Method Use.setrelheapg is depreciated, use setref instead.")
	if reference is None:
            self.relheapg = None
	    reference = self.View.heapg()
	self.relheapg = reference

    def setrelheapu(self, reference=None,stat=1):
	if reference is None:
            self.relheapu = None
	    reference = self.heapu(abs=True, stat=stat)
        if stat and not isinstance(reference, self.Stat):
            reference = reference.stat
        self.relheapu = reference

    def test(self, debug=False):
        """test([debug: bool+ = False])

Run the Heapy test suite.

Argument
    debug
        If True, the tests will be run in debug mode so the stack frame
        can be examined with pdb.pm() after the first exception."""

        self._parent.test.test_all.test_main(debug)

    _imports_ = (
	'_parent.Classifiers:Class',
	'_parent.Classifiers:Clodo',
	'_parent.Classifiers:Id',
	'_parent.Classifiers:Idset',
	'_parent.Classifiers:Module',
	'_parent.Classifiers:Rcs',
	'_parent.Classifiers:Size',
	'_parent.Classifiers:Type',
	'_parent.Classifiers:Unity',
	'_parent.Classifiers:Via',
	'_parent.Classifiers:findex',
	'_parent.Classifiers:sonokind',
	'_parent.Classifiers:tc_adapt',
	'_parent.Classifiers:tc_repr',
	'_parent.Monitor:monitor',
	'_parent.Part:_load_stat',
	'_parent.Part:Stat',
	'_parent.Prof:pb',
	'_parent.UniSet:Anything',
	'_parent.UniSet:idset',
	'_parent.UniSet:iso',
	'_parent.UniSet:Nothing',
	'_parent.UniSet:union',
	'_parent.UniSet:uniset_from_setcastable',
	'_parent:View',
	'_parent.View:_hiding_tag_',
        '_root.time:ctime',
        '_root:warnings',
	)

    _doc_Anything = """Anything: Kind

A symbolic set that represents all possible Python objects.

References
    [0] heapy_Use.html#heapykinds.Use.Anything"""

    _doc_Class ="""Class:EquivalenceRelation
Class(tc:typeorclass+) -> Kind

Equivalence relation by class. It defines objects to be equivalent
when their builtin __class__ attributes are identical. When called it
returns the equivalenc class defined by the argument:

    tc: A type or class that the returned kind should represent.

References
    [0] heapy_Use.html#heapykinds.Use.Class"""

    _doc_Clodo ="""Clodo:EquivalenceRelation
Clodo(alt:[tc: typeorclassexceptdict+ or dictof =
        typeorclassoremptytuple+]) -> Kind

Equivalence relation by class or dict owner. It distinguishes between
objects based on their class just like the Class relation, and in
addition distinguishes between dicts depending on what class they are
'owned' by, i.e. occur in __dict__ attribute of.

When called it returns the equivalence class defined by the argument,

EITHER:
    tc: A positional argument, a type or class but not a dict, to
        create the corresponding equivalence class.
OR:
    dictof: A named argument, to create an equivalence class
        consisting of all dicts that are owned by objects of the type
        or class specified in the argument; or dicts with no owner if
        an empty tuple is given. XXX express this simpler&better...


References
    [0] heapy_Use.html#heapykinds.Use.Clodo"""

    _doc_Id="""Id:EquivalenceRelation
Id(address: objectaddress+) -> Kind)

This equivalence relation defines objects to be equivalent only if
they are identical, i.e. have the same address. When called it returns
the equivalence class defined by the argument:

    address: The memory address of an object.

References
    [0] heapy_Use.html#heapykinds.Use.Id"""

    _doc_Idset="""Id:EquivalenceRelation
Idset(node: Anything+) -> IdentitySet

This equivalence relation defines objects to be equivalent only if
they are identical, i.e. have the same address. When called it returns
the equivalence class defined by the argument:

    node: Anything+
        Any object is a valid argument.

Note
    This is mainly for special purpose internal use. The Id
equivalence relation is more efficient when partitioning large
sets."""

    _doc_Module = """Module:EquivalenceRelation
x.Module( draw:[name = modulename+ , at = moduleaddress+]) -> Kind

This equivalence relation defines objects to be equivalent if they are
the same module, or if none of them is a module.  Partitioning a set
of objects using this equivalence relation will therefore result in
one singleton set for each module and one set containing all other
objects.

Calling the Module equivalence relation creates a Kind containing the
module given in the keyword argument(s). Either the name, address or
both may be specified. If no argument is specified the equivalence
class is that of non-module objects.

References
    [0] heapy_Use.html#heapykinds.Use.Module"""

    _doc_Nothing = """Nothing: IdentitySet

The empty set.

References
    [0] heapy_Use.html#heapykinds.Use.Nothing"""

    _doc_Rcs = """Rcs: EquivalenceRelation
Rcs ( 0..*: alt:[kind: Kind+ or sok: SetOfKind+]) -> KindOfRetClaSetFamily

(Referrer classification set.)

In this equivalence relation, objects are classified by classifying
their referrers, using the Clodo equivalence relation. These
classifications are collected in a set, representing the
classification of the object.

Calling Rcs creates an equivalence class from specified set of
referrer classifications. The arguments specify a set of Kind objects,
each of which representing an equivalence class of Clodo.

    kind: Kind+
        This adds a single Kind to the set of Kinds of referrers.
    sok: SetOfKind+
        This adds each Kind in the sok argument to the total set of
        Kinds of referrers.
References
    [0] heapy_Use.html#heapykinds.Use.Rcs"""


    _doc_Size = """\
Size: EquivalenceRelation
Size(size: notnegative+) -> KindOfSizeFamily[1])

In this equivalence relation, objects are classified by memory size,
so each equivalence class represents a particular size of object.

References
    [0] heapy_Use.html#heapykinds.Use.Size
    [1] heapy_UniSet.html#heapykinds.KindOfSizeFamily"""

    _doc_Type = """Type: EquivalenceRelation
Type(type: type+) -> KindOfTypeFamily[1]

In this equivalence relation, objects are classified by type so each
equivalence class represents objects of a particular type.  Calling it
creates a Kind representing the type specified in the argument:

    type: type+
        A Python type object or a representation of it.

References
    [0] heapy_Use.html#heapykinds.Use.Type
    [1] heapy_UniSet.html#heapykinds.KindOfTypeFamily"""

    _doc_Unity = """Unity: EquivalenceRelation
Unity() -> Kind[1]

In this equivalence relation, all objects are considered equivalent.
There is only one equivalence class, that is, Anything[2].

References
    [0] heapy_Use.html#heapykinds.Use.Unity
    [1] heapy_UniSet.html#heapykinds.Kind
    [2] heapy_Use.html#heapykinds.Use.Anything"""

    _doc_Via = """Via: EquivalenceRelation
Via( 0..*:rel: relationname+) -> KindOfInViaFamily[1]

In this equivalence relation, objects are classified by how they are
referred from their referrers, so each equivalence class represents
objects that have a particular set of relations to their referrers.
Calling it creates a Kind representing the set of referrers specified
by the argument:

    rel: relationname+
        Each argument specifies one referrer relation. The arguments
        should be strings and can be of any of the following forms.

[expression]
    Indexing of a dict, list, tuple (etc).  The expression must be a
    Python expression that can be evaluated in a local
    environment. The environment will contain the builtins and a name
    'hp' that is bound to the current Use instance.

.attribute
    Getting an attribute from a builtin type or a slot of a slotted
    type. (I.E. not an attribute that is in a dict of an object.)

.f_locals["name"]
     A local variable of a frame.

.f_locals ["name"]
    A variable in a CELL of a frame. Note the space between f_locals and
    [. This is to distinguish it from ordinary locals, and still use a
    syntax that could be used to access those variables directly from
    Python.

.keys()[integer]
    A key in a dictionary, at the indicated place in its keys().
    
References
    [0] heapy_Use.html#heapykinds.Use.Via
    [1] heapy_UniSet.html#heapykinds.KindOfInViaFamily"""

    _doc_findex = """
findex( 0..*:kind: Kind+) -> (
    Subkind of: EquivalenceRelation[1]
    callable: (index: notnegative+)
        Calling the returned equivalence relation creates an
        equivalence class.
        Argument
            index: notnegative+
                The position of the matching kind in the sequence of
                kinds. The first one has index 0. Specifying the
                length of the sequence means that the equivalence
                class returned is the one where none of the kinds in
                the sequence matched.

    )

Create an equivalence relation based on a sequence of kinds. The
name is a combination of find and index. The classification of
each objects is done as follows:

For each kind in the sequence, check whether the object is an
element of that kind. If it is, the classification is the index
of that kind in the sequence. If the end of the sequence is
reached, the classification is the length of the sequence.
Argument
    kind: Kind+
        Each argument specifies the kind in that position in the
        sequence.
Bugs
    Though the Kind objects representing the equivalence classes
    work with set operations such as intersection and union, the
    tests such as subset and equality do not generally give the
    expected result.
References
    [0] heapy_Use.html#heapykinds.Use.findex
    [1] heapy_UniSet.html#heapykinds.EquivalenceRelation"""

    _doc_idset = """idset(nodes: iterable+) -> IdentitySet[1]

Create a set of objects based on identity.

Argument
    nodes: iterable+
        The argument must be an iterable and may yield any kind
        of objects.
Note
    This method is the same as iso except for the argument.
References
    [0] heapy_Use.html#heapykinds.Use.idset
    [1] heapy_UniSet.html#heapykinds.IdentitySet"""

    _doc_iso = """iso( 0..*:node: Any+) -> IdentitySet[1]

Create a set of objects based on identity.

Argument
    node: Any+
        Any kind of objects are valid arguments.
Note
    This method is the same as idset[2] except for the argument.
References
    [0] heapy_Use.html#heapykinds.Use.iso
    [1] heapy_UniSet.html#heapykinds.IdentitySet
    [2] heapy_Use.html#heapykinds.Use.idset"""


    _doc_sokind = """
"""
