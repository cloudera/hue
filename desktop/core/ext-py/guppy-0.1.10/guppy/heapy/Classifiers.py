#._cv_part guppy.heapy.Classifiers

class Classifier:
    def __init__(self, mod, name, cli=None, supers=(), depends=(), with_referrers=False):
	self.mod = mod
	self.name = name
	if cli is not None:
	    self.cli = cli
	# Set of all super-classifiers (including self).
	# The partial order is defined in Notes Aug 30 2005.
	self.super_classifiers = mod.ImpSet.immnodeset([self])
	if supers:
	    for s in supers:
		self.super_classifiers |= s.super_classifiers
	else:
	    # The Unity classifier is super of all, but we must add it only
	    # if not supers specified; init of ByUnity itself depends on this.
	    self.super_classifiers |= [mod.Use.Unity.classifier]
	
	# The classifiers that self depends on.
	for d in depends:
	    if d.with_referrers:
		with_referrers = True
		break

	# True if we need to setup referrers before calling (the) low-level classifier.
	self.with_referrers = with_referrers

	if with_referrers:
	    self.call_with_referrers = mod.View.call_with_referrers

    def call_with_referrers(self, x, f):
	# Default is to not use referrers.
	return f(x)

    def _get_cli(self):	      # This is not redefined by subclass unless they set cli property.
	return self.get_cli() # This may be defined by subclass w/o setting cli property.

    cli = property(_get_cli)

    def get_alt(self, kind, alt):
	# Get alternative kind for a kind with self as fam.classifier.
	# assert kind.fam.classifier is self
	return self.mod.alt(kind, alt)

    def get_dictof(self, kind):

	name = '%s.dictof'%self.name
	er = self.mod.mker_memoized(
	    name,
	    lambda:
	    self.mod._er_by_(ByDictOwner, self.mod, name, self))

	return er.classifier.dictof(kind)
	

    def get_kind(self, k):
	# Make an equivalence class from low-level classification
	return self.family(k)

    def get_kindarg(self, kind):
	# Inverse of get_kind
	cla, ka, cmp = kind.get_ckc()
	if cla is not self:
	    raise ValueError, 'get_kindarg: argument with classifier %r expected'%self
	return ka

    def get_reprname(self):
	return '%s%s'%(self.mod.Use.reprefix, self.name)

    def get_sokind(self, er, *args, **kwds):
	k = er(*args, **kwds)
	return CallableSoKind(er, (k,))

    def get_sokindrepr(self, sokind):
	# Get the representation of a set of kinds
	# from this classifier / eqv. relation.

	if 0:

	    return '%ssokind(%s)'%(self.mod.Use.reprefix,
				    ', '.join(['%r'%kind for kind in sokind.kinds]))



	return '%s.sokind%s'%(self.get_reprname(),
			      ''.join(['(%s)'%self.get_userkindargrepr(k)
				       for k in sokind.kinds]))
	

    def get_tabheader(self, ctx=''):
	# If ctx = 'and', get the table header when used as a part of the 'and' classifier.
	#     It is sometimes a more compact or parenthesised version of the usual tab header.
	return self.get_byname()

    def get_tabrendering(self, cla, ctx=''):
	# If ctx = 'and', get the table rendering when used as a part of the 'and' classifier
	#     sometimes we want to enclose something in parenthesises.
	return cla.brief

    def get_userkind(self, *args, **kwds):
	# Make a kind from user-level arguments
	return self.family(*args, **kwds)

    def get_userkindarg(self, kind):
	return kind.arg

    def get_userkindargrepr(self, kind):
	return repr(self.get_userkindarg(kind))

    def partition(self, iterable):
	items = []
	for k, v in self.partition_cli(iterable):
	    k = self.get_kind(k)
	    v = self.mod.Use.idset(v, er=self.er)
	    items.append((k, v))
	return items

    def partition_cli(self, a):
	ep = self.call_with_referrers(
	    a,
	    self.cli.epartition)
	return [(k, ep[k]) for k in ep.get_domain()]

    def relimg(self, X):
	p = self.partition_cli(X)
	kinds = [self.get_kind(k) for k, v in p] # could be more efficient
	return self.mod.Use.union(kinds, maximized=1)

    def select_cli(self, a, b, cmp='=='):
	return self.call_with_referrers(
	    a,
	    lambda a: self.cli.select(a, b, cmp))

    def select_ids(self, X, k, alt=None):
	r = self.mod.Use.idset(self.select_cli(X.nodes, k, alt))
	return r

class SoKind(object):
    def __init__(self, er, kinds):
	self.er = er
	self.classifier = er.classifier
	self.kinds = kinds
	self.clikinds = self.classifier.mod.ImpSet.immnodeset(
	    [self.classifier.get_kindarg(kind) for kind in kinds])
    
    def __eq__(self, other):
	if not isinstance(other, SoKind):
	    return False
	if self.classifier != other.classifier:
	    return False
	a = self.classifier.mod.Use.union(self.kinds)
	b = self.classifier.mod.Use.union(other.kinds)
	return a == b

    def __hash__(self):
        return hash(repr(self))

    def __repr__(self):
	return self.classifier.get_sokindrepr(self)
    def _get_refdby(self):
	return self.er.refdby(self)

    refdby = property(_get_refdby)

class CallableSoKind(SoKind):
    def __call__(self, *args, **kwds):
	k = self.er(*args, **kwds)
	return self.__class__(self.er, self.kinds + (k,))

    
class SoNoKind(SoKind):
    def __repr__(self):
	return '%s%s'%(self.classifier.mod.Use.reprefix, 'sonokind')


class QuickSoKind(SoKind):
    # Quicker to make than SoKind,
    # when clikinds is available but not kinds.
    __slots__ = 'classifier', 'clikinds'
    def __init__(self, classifier, clikinds):
	self.classifier = classifier
	self.clikinds = clikinds
    
    def _get_er(self):
	return self.classifier.er

    er = property(_get_er)

    def _get_kinds(self):
	return tuple([self.classifier.get_kind(k) for k in self.clikinds])

    kinds = property(_get_kinds)


class IdentityFamily:
    # Holds a single object node
    def __init__(self, mod, classifier):
	self.defrefining(mod.Use.Anything)
	self.classifier = classifier
    
    def _ge_ATOM(self, a, b):
	# b is known to not be Nothing since its c_le doesn't call back
	if self is b.fam:
	    return a.arg is b.arg
	return b.fam.supercl is not None and b.fam.supercl <= a

    def _le_ATOM(self, a, b):
	# b is known to not be Nothing since its c_ge doesn't call back
	if self is b.fam:
	    return a.arg is b.arg
	return self.supercl is not None and self.supercl <= b

    def c_contains(self, a, b):
	return b is a.arg

    def _and_ID(self, a, b):
	# Just a possible optimization
	return self.mod.Use.idset(b.nodes & [a.arg])

    def c_get_brief(self, a):
	return '<id %s>'%hex(id(a.arg))

    def c_repr(self, a):
	return '%s(%s)'%(self.classifier.get_reprname(), self.classifier.get_userkindargrepr(a))

class ByIdentity(Classifier):
    def __init__(self, mod, name):
	Classifier.__init__(self, mod, name, mod.hv.cli_id())
	self.family = mod.fam_mixin_argatom(IdentityFamily, self)
	# self.super_classifiers = mod.Use.Anything # Replace whatever Classifer had set it to

    def get_byname(self):
	return 'object identity'

    def get_tabheader(self, ctx=''):
	return 'Object Identity'

    def get_userkind(self, address):
	return self.get_kind(self.mod.View.obj_at(address))

    def get_userkindarg(self, kind):
	return id(kind.arg)

    def get_userkindargrepr(self, kind):
	return hex(self.get_userkindarg(kind))

class ByIdentitySet(Classifier):
    # Classification is, conceptually, a singleton immnodeset of each object

    # What this is used to is:
    # to be able to use an iso() set as a kind
    # combined with other classifiers eg in dictof, biper

    # The ckc returned from an iso is then
    # this classifier, nodes of iso, '<='
    
    # The cmp indicates subset
    # select thus selects every object for which it singleton is a subset of the set given
    # which is optimized to select the object that are members of that set
    # and may be optimized at higher levels to invoke the low-level set intersection
    
    def __init__(self, mod, name):
	Classifier.__init__(self, mod, name, mod.hv.cli_idset())
	self.family = mod.Use.idset
	# self.super_classifiers = mod.Use.Anything # Replace whatever Classifer had set it to

    def get_byname(self):
	return 'by identity set'

    def get_userkind(self, node):
	return self.family(self.mod.ImpSet.immnodeset([node]))

    def relimg(self, X):
	p = self.partition_cli(X)
	k = self.mod.ImpSet.immnodeset_union([k for k, v in p])
	return self.family(k)

class PyObjectFamily:
    def __init__(self, mod, classifier):
	self.classifier = classifier

    def c_contains(self, a, b):
	return True

    def c_get_idpart_header(self, a):
	return 'Kind: Name/Value/Address'

    def c_get_idpart_label(self, a):
	return ''

    def c_get_idpart_render(self, a):
	def render(x):
	    x = self.mod.Use.iso(x)
	    r = x.brief.lstrip('<1 ').rstrip('>')
	    return r
	return render

    def c_get_brief(self, a):
	return '<Anything>'

    def c_repr(self, a):
	return '%s%s'%(self.mod.Use.reprefix, 'Anything')

    def _and_ID(self, a, b):
	# Optimization shortcut
	# shcould be made in classifer.select
	return b


class ByUnity(Classifier):
    """byunity
Classify by <unity>.
The classification returned for every object is <Anything>."""

    def __init__(self, mod, name):
	Classifier.__init__(self, mod, name, mod.hv.cli_none(),
			    supers=[self] # Must make it avoid referring to Unity !
			    )
	self.family = mod.fam_mixin_argatom(PyObjectFamily, self)

    def get_byname(self):
	return 'unity'

    def get_tabheader(self, ctx=''):
	return '<unclassified>'

    def get_userkind(self, *args):
	return self.mod.Use.Anything
	
    def get_userkindarg(self, kind):
	return None
	
class IndiSizeFamily:
    def __init__(self, mod, classifier):
	self.defrefining(mod.Use.Anything)
	self.classifier = classifier

    def __call__(self, a):
	a = int(a)
	return self.mod.AtomFamily.__call__(self, a)

    def c_alt(self, a, alt):
	return self.classifier.get_alt(a, alt)

    def c_contains(self, a, b):
	return a.arg == self.classifier.cli.classify(b)

    def c_get_render(self, a):
	return self.mod.summary_str(a.arg)

    def c_get_brief(self, a):
	return '<size = %d>'%a.arg

    def c_get_brief_alt(self, a, alt):
	return '<size %s %d>'%(alt, a.arg)

    def c_repr(self, a):
	return '%s(%s)'%(self.classifier.get_reprname(), a.arg)


class ByIndiSize(Classifier):
    """byindisize
Classify by <individual size>.
The classification will be individual memory size of the object."""
    def __init__(self, mod, name):
	Classifier.__init__(self, mod, name)
	self.family = mod.fam_mixin_argatom(IndiSizeFamily, self)
    
    def get_byname(self):
	return 'individual size'

    def get_cli(self):
	return self.mod.hv.cli_indisize({})

    def get_tabheader(self, ctx=''):
	return 'Individual Size'

    def get_tabrendering(self, cla, ctx=''):
	if ctx:
	    return '%d'%cla.arg
	else:
	    return '%9d'%cla.arg


class TypeFamily:
    def __init__(self, mod, classifier):
	self.defrefining(mod.Use.Anything)
	self.classifier = classifier
	self.range = mod.fam_Family(self)
	self.TypeType = mod.types.TypeType

    def __call__(self, a):
	if not isinstance(a, self.TypeType):
	    raise TypeError, "Argument should be a type."
	return self.Set(self, a)

    def c_alt(self, a, alt):
	return self.classifier.get_alt(a, alt)

    def c_contains(self, a, b):
	return type(b) is a.arg

    def c_get_render(self, a):
	return self.mod.summary_str(a.arg)

    def c_get_brief(self, a):
	return self.mod.summary_str(type(a.arg)) (a.arg)

    def c_get_brief_alt(self, a, alt):
	x = {
	    '<'  : 'strict subtype',
	    '<=' : 'subtype',
	    '>=' : 'supertype',
	    '>'  : 'strict supertype'
	    }[alt]
	return '<%s of %s>'%(x, self.c_get_brief(a))

    def c_repr(self, a):
	return self.classifier.get_repr(a)

class ByType(Classifier):
    """bytype
Classify by <type>.
The classification will be the type of the object."""

    def __init__(self, mod, name):
	Classifier.__init__(self, mod, name, mod.hv.cli_type())
	self.family = mod.fam_mixin_argatom(TypeFamily, self)

    def get_attr_for_er(self, name):
	return self.get_userkind(getattr(self.mod.types, name+'Type'))

    def get_byname(self):
	return 'type'

    def get_repr(self, kind):
	t = kind.arg
	rn = self.get_reprname()
	if t in self.mod.invtypemod:
	    return '%s.%s'%(rn, self.mod.invtypemod[t])
	else:
	    return '%s(%r)'%(rn, self.get_userkindarg(kind))

    def get_tabheader(self, ctx=''):
	return 'Type'

    def get_userkind(self, kind):
	kind = self.mod.tc_adapt(kind)
	return self.family(kind)

    def get_userkindarg(self, kind):
	# A representation that is a valid userkind arg.
	return self.mod.Use.tc_repr(kind.arg)




class ClassFamily:
    def __init__(self, mod, classifier):
	self.classifier = classifier
	self.InstanceType = mod.types.InstanceType
	self.ClassType = mod.types.ClassType
	self.defrefidis(mod.Use.Type(self.InstanceType))
	
    def __call__(self, a):
	if not isinstance(a, self.ClassType):
	    raise TypeError, "Argument should be a class (of type types.ClassType)."
	return self.mod.AtomFamily.__call__(self, a)

    def c_alt(self, a, alt):
	return self.classifier.get_alt(a, alt)

    def c_contains(self, a, b):
	return type(b) is self.InstanceType and b.__class__ is a.arg

    def c_get_brief(self, a):
	return '%s.%s'%(a.arg.__module__, a.arg.__name__)

    def c_get_brief_alt(self, a, alt):
	x = {
	    '<'  : 'strict subclass',
	    '<=' : 'subclass',
	    '>=' : 'superclass',
	    '>'  : 'strict superclass'
	    }[alt]
	return '<%s of %s>'%(x, self.c_get_brief(a))

    def c_repr(self, a):
	return '%s(%r)'%(self.classifier.get_reprname(), self.mod.Use.tc_repr(a.arg))

class ByClass(Classifier):
    """byclass
Classify by 'class', in the following sense.
An object is classified as follows:
1.	If the object is of type InstanceType, the
	classification will be its class.
2.	The classification will be the type of the object.

This is like the __class__ attribute in newer Python, except it 
doesn't change if some type redefines the __class__ attribute.
"""

    def __init__(self, mod, name):
	sup = mod.Use.Type.classifier
	Classifier.__init__(self, mod, name, mod.hv.cli_class(), supers = [sup])
	self.fam_Class = mod.fam_mixin_argatom(ClassFamily, self)
	self.ClassType = self.fam_Class.ClassType
	self.TypeType = mod.types.TypeType
	self.type_get_kind = sup.get_kind

    def get_byname(self):
	return 'class'

    def get_kind(self, kind):
	if isinstance(kind, self.ClassType):
	    return self.fam_Class(kind)
	else:
	    return self.type_get_kind(kind)

    def get_kindarg(self, kind):
	if kind.fam is self.fam_Class:
	    return kind.arg
	else:
	    return self.mod.Use.Type.classifier.get_kindarg(kind)

    def get_tabheader(self, ctx=''):
	return 'Class'

    def get_userkind(self, kind):
	kind = self.mod.tc_adapt(kind)
	try:
	    return self.get_kind(kind)
	except TypeError:
	    raise TypeError, 'Argument should be a class or type.'

    def get_userkindarg(self, kind):
	return self.mod.Use.tc_repr(kind.arg)

class OwnedDictFamily:
    def __init__(self, mod):
	self.defrefidis(mod.Use.Type(self.types.DictType))

    def _get_ownerkind(self, a):
	return a.arg

    def c_alt(self, a, alt):
	return self(a.arg.alt(alt))

    def c_get_render(self, a):
	ka = self._get_ownerkind(a)
	if ka is self.mod.Use.Nothing:
	    return self.mod.Use.Type.Dict.get_render()
	else:
	    ownrender = ka.get_render()
	    def render(x):
		ret = ownrender( self.mod.Use.iso(x).owners.theone )
		if '.' in ret:
		    ret = '..'+ret.split('.')[-1]
		return ret
	    return render

	if ka == self.mod.fam_Type(self.types.ModuleType):
	    modrender = self.mod.Use.Type.Module.get_render()
	    def render(x):
		return modrender( self.mod.Use.iso(x).owners.theone )
	    return render
	else:
	    return self.mod.Use.Type.Dict.get_render()

    def c_get_brief(self, a):
	ka = self._get_ownerkind(a)
	if ka is self.mod.Use.Nothing:
	    return 'dict (no owner)'
	else:
	    return 'dict of ' + ka.brief

    def c_get_ckc(self, a):
	cla, k, cmp = a.arg.get_ckc()
	if cmp != '==':
	    cla, k, cmp = a.arg.biper(0).get_ckc()
	    
	docla = cla.er.dictof.classifier
	if a.arg is self.mod.Use.Nothing:
	    k = docla.notownedtag
	return docla, k, cmp

    def c_get_str_for(self, a, b):
	return self.c_get_brief(a)

    def c_get_idpart_render(self, a):
	ka = self._get_ownerkind(a)
	if ka is not self.mod.Use.Nothing:
	    owner_render = ka.fam.c_get_idpart_render(ka)
	    def render(x):
		return owner_render(self.mod.Use.iso(x).owners.theone)
	    return render
	else:
	    b = self.mod._parent.Spec.Type.Dict
	    return b.fam.c_get_idpart_render(b)

    def c_get_idpart_header(self, a):
	ka = self._get_ownerkind(a)
	if ka is self.mod.Use.Nothing:
	    return 'Address*Length'
	else:
	    return 'Owner ' + ka.fam.c_get_idpart_header(ka)

    def c_repr(self, a):
	ka = self._get_ownerkind(a)
	ra = repr(ka)
	if ra.startswith('~'):
	    ra = '(%s)'%ra
	return '%s.dictof'%ra


class ByDictOwner(Classifier):
    def __init__(self, mod, name, ownerclassifier):
	Classifier.__init__(self, mod, name, depends=[ownerclassifier])
	self.ownerclassifier = ownerclassifier
	self.hv = mod.View.hv
	self.ownership = mod.View.dict_ownership
	self.family = mod.dictof

	self.notdict = mod.notdict
	self.dictofnothing = mod.dictofnothing

	# Hashable unique tags
        # Using sets methods since I dont want our hiding tag here!
        # Confuses heapg. Note feb 3 2006
	self.notdicttag = mod.ImpSet.immnodeset([[]])
	self.notownedtag = mod.ImpSet.immnodeset([[]])
	

    def get_byname(self):
	return '[dict of] %s'%self.ownerclassifier.get_byname()

    def get_cli(self):
	cli = self.hv.cli_dictof(self.ownership, self.ownerclassifier.cli, self.notdicttag,
				 self.notownedtag)
	return cli

    def get_kind(self, k):
	if k is self.notdicttag:
	    return self.notdict
	elif k is self.notownedtag:
	    return self.dictofnothing
	else:
	    return self.family(self.ownerclassifier.get_kind(k))

    def get_kindarg(self, kind):
	if kind is self.notdict:
	    return self.notdicttag
	elif kind is self.dictofnothing:
	    return self.notownedtag
	else:
	    return self.ownerclassifier.get_kindarg(kind.arg)

    def get_tabheader(self, ctx=''):
	return 'Dict of %s'%self.ownerclassifier.get_tabheader(ctx)

    def get_tabrendering(self, kind, ctx=''):
	if kind is self.notdict:
	    r = kind.brief
	elif kind is self.dictofnothing:
	    r = 'dict (no owner)'
	else:
	    r = 'dict of ' + self.ownerclassifier.get_tabrendering(kind.arg, ctx)
	return r

    def get_userkind(self, k):
	if k is None:
	    return self.notdict
	elif k is self.mod.Use.Nothing:
	    return self.dictofnothing
	else:
	    return self.family(k)

    def get_userkindarg(self, kind):
	if kind is self.notdict:
	    return None
	elif kind is self.dictofnothing:
	    return self.mod.Use.Nothing
	else:
	    return kind.arg

    def owners(self, X):
	p = self.partition_cli(X.nodes)
	ns = self.mod.ImpSet.mutnodeset()
	drg = self.ownership
	for k in X.nodes:
	    t = drg[k]
	    if not t:
		self.mod.hv.update_dictowners(drg)
		t = drg[k]
	    if t:
		v = t[0]
		if v is not None:
		    ns.add(v)
	return self.mod.Use.idset(ns)

    

class ByClassOrDictOwner(Classifier):
    """byclodo
Classify by <type, class or dict owner>.
The classification is performed as follows:
1.	If the object is an instance of a class, the
	classification will be the class.
2.	If the object is not a dictionary,
	the classification will be the type of the object.
3.	The object is a dictionary. The referrers of the
	object are searched to find one that 'owns' the
	dictionary. That is, typically, that the dict is
	the __dict__ attribute of the owner. If no such
	owner is found, the type 'dict' will be the
	classification. If an owner is found, a special
	object that indicates the classification of the owner
	will be returned. The classification of the owner
	will be done by class. (As byclass.)"""

    def __init__(self, mod, name):


	a = mod.Class
	d = a.dictof
	ad = (a & d).classifier
	sup = a.classifier
	Classifier.__init__(self, mod, name, cli=None, supers=[sup], depends=[ad])
	self.sup = sup
	self.a = a.classifier
	self.d = d.classifier
	self.ad = ad

    def get_byname(self):
	return '[dict of] class'

    def get_cli(self):
	return self.ad.cli

    def get_kind(self, (ka, kd)):
	if kd is self.d.notdicttag:
	    return self.a.get_kind(ka)
	else:
	    return self.d.get_kind(kd)

    def get_kindarg(self, kind):
        if kind.fam is self.d.family:
	    ka = dict
	    kd = self.d.get_kindarg(kind)
	else:
	    ka = self.a.get_kindarg(kind)
	    kd = self.d.notdicttag
	return (ka, kd)

    def get_tabheader(self, ctx=''):
	return 'Kind (class / dict of class)'

    def get_userkind(self, kind=None, dictof=None):
	try:
	    if kind is None and dictof is not None:
		if dictof == ():
		    do = self.mod.UniSet.Nothing
		else:
		    do = self.sup.get_userkind(dictof)
		return self.d.get_userkind(do)
	    elif kind is not None and dictof is None:
		kind = self.mod.tc_adapt(kind)
		if kind is dict:
		    raise TypeError, 'dict is not an equivalence class of Clodo, use dictof=() etc'
		return self.sup.get_kind(kind)
	    else:
		raise TypeError
	except TypeError:
	    raise TypeError, """\
Argument should be either
    <type or class except dict>
    dictof=<type or class>
    dictof=()"""


    def get_userkindargrepr(self, kind):
        if kind.fam is self.d.family:
	    if kind.arg is self.mod.UniSet.Nothing:
		d = '()'
	    else:
		d = self.d.ownerclassifier.get_userkindargrepr(kind.arg)
	    return 'dictof=%s'%d
	else:
	    return kind.fam.classifier.get_userkindargrepr(kind)

    def owners(self, X):
	return self.d.owners(X)


class RetClaSetFamily:
    def __init__(self, mod, classifier):
	self.defrefining(mod.Use.Anything)
	self.classifier = classifier

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


    def c_alt(self, a, alt):
	return a.arg.classifier.er.refdby.classifier.get_alt(a, alt)

	return self.classifier.get_alt(a, alt)

    def _get_arg_brief(self, a):
	return a.arg.er.refdby.classifier.get_tabrendering(a, False)

    def c_get_brief(self, a):
	return '<referred by: %s>'%self._get_arg_brief(a)

    def c_get_brief_alt(self, a, alt):
	x = {
	    '<'  : 'by less than',
	    '<=' : 'by at most',
	    '>=' : 'by at least',
	    '>'  : 'by more than',
	    }[alt]
	return '<referred %s: %s>'%(x, self._get_arg_brief(a))


    def c_get_ckc(self, a):
	return self.classifier, a.arg.clikinds, '=='

    def c_repr(self, a):
	return '%r.refdby'%a.arg

    # Public

    def sokind(self, sok):
	if not isinstance(sok, SoKind):
	    raise TypeError, 'SoKind expected'
	
	er = sok.classifier.er.refdby
	kinds = (self(sok),)
	return CallableSoKind(er, kinds)


class ByRetClaSet(Classifier):
    def __init__(self, mod, name, rg, referrer_classifier, doc):
	Classifier.__init__(self, mod, name, with_referrers=True)
	self.rg = rg
	self.referrer_classifier = referrer_classifier
	self.family = self.mod.fam_mixin_argatom(RetClaSetFamily, self)
	self.__doc__ = doc

    def get_byname(self):
	return 'referrer kinds'

    def get_cli(self):
	memo = {}
	return self.mod.hv.cli_rcs(self.rg, self.referrer_classifier.cli, memo)

    def get_inverted_refkind(self, k):
	set_trace()
	if k.fam.opname == 'OR':
	    ks = k.arg
	elif k is self.mod.Use.Nothing:
	    ks = ()
	else:
	    ks = (k,)
	rks = []
	for k in ks:
	    rks.append(self.referrer_classifier.get_kindarg(k))
	return self.mod.ImpSet.immnodeset(rks)

    def get_kind(self, k):
	if k:
	    return self.family(QuickSoKind(self.referrer_classifier, k))
	else:
	    return self.mod.refdbynothing

    def get_tabheader(self, ctx=''):
	th = 'Referrers by %s'%self.referrer_classifier.get_tabheader(ctx)
	if ctx:
	    th = '{%s}'%th
	return th

    def get_tabrendering(self, cla, ctx):
	rs = [self.referrer_classifier.get_tabrendering(x, ctx) for x in cla.arg.kinds]
	rs.sort()
	r = ', '.join(rs)
	if ctx:
	    r = '{%s}'%r
	elif not r:
	    r = '<Nothing>'
	return r

    def get_userkind(self, *args):
	firstsok = None
	clikinds = []
	for arg in args:
	    if isinstance(arg, SoKind):
		if not arg.classifier is self.referrer_classifier:
		    raise ValueError, 'Expected a SoKind with the %r classifier, argument had %r.'%(
			self.referrer_classifier.name,
			arg.classifier.name)
		clikinds.extend(arg.clikinds)
		if firstsok is None:
		    firstsok = arg

	    else:
		# Assume we got a single kind
		# get_kindarg takes care of classifier error checking
		clikinds.append(self.referrer_classifier.get_kindarg(arg))

	if len(args) > 1 or firstsok is None:
	    sok = QuickSoKind(self.referrer_classifier,
                              self.mod.ImpSet.immnodeset(clikinds))
	else:
	    sok = firstsok
	    
	return self.family(sok)



class InRelFamily:
    def __init__(self, mod, classifier):
	self.classifier = classifier
	self.defrefining(mod.Use.Anything)

    def _eq_args(self, a, b):
	# They are sequences (immnodesets) of relations.
	# I have not memoized them since I was afraid they would last too long
	# and I thought it not be worthwhile and hope this comparison is not done too often.
	# So I will compare them as equality based sets.
	a = dict([(x, ()) for x in a])
	b = dict([(x, ()) for x in b])
	return a == b

    def _ge_ATOM(self, a, b):
	# b is known to not be Nothing since its c_le doesn't call back
	if self is b.fam:
	    return self._eq_args(a.arg, b.arg)
	return b.fam.supercl is not None and b.fam.supercl <= a

    def _le_ATOM(self, a, b):
	# b is known to not be Nothing since its c_ge doesn't call back
	if self is b.fam:
	    return self._eq_args(a.arg, b.arg)
	return self.supercl is not None and self.supercl <= b


    def c_alt(self, a, alt):
	return self.classifier.get_alt(a, alt)

    def c_get_brief(self, a):
	return '<via %s>'%self.classifier.get_tabrendering(a, None)

    def c_repr(self, a):
	return '%s(%s)'%(self.classifier.get_reprname(),
			 self.classifier.get_userkindargrepr(a))


class ByInRel(Classifier):
    def __init__(self, mod, name, rg):
	Classifier.__init__(self, mod, name, with_referrers=True)
	self.rg = rg
	self.family = mod.fam_mixin_argatom(InRelFamily, self)


    def _rel2str(self, r):
	P = self.mod._parent.Path
	t = P.rel_table
	x = t[r.kind](r.relator)
	return x.stra('')
	

    def _str2rel(self, s):
	# Parse a string as generated by rel2str,
	# to recreate the relation object.
	P = self.mod._parent.Path
	orgs = s
	def mkrel(R, *args):
	    return self.mod.View.heapyc.Relation(R.code, *args)
	if s.startswith('_'):
	    s = s[1:]
	if s.startswith('['):
	    s = s[1:].rstrip(']')
	    loc = {'hp':self.mod.Use}
	    r = eval(s, loc)
	    rel = mkrel(P.R_INDEXVAL, r)
	elif s.startswith('.'):
	    s = s[1:]
	    if s.replace('_','x').isalnum():
		rel = mkrel(P.R_ATTRIBUTE, s)
	    elif s.startswith('f_locals['):
		s = s[9:].rstrip(']')
		r = eval(s, {})
		rel = mkrel(P.R_LOCAL_VAR, r)
	    elif s.startswith('f_locals ['):
		s = s[10:].rstrip(']')
		r = eval(s, {})
		rel = mkrel(P.R_CELL, r)
	    elif s.startswith('keys()['):
		s = s[7:].rstrip(']')
		r = int(s)
		rel = mkrel(P.R_INDEXKEY, r)
	    elif s.startswith('__dict__.keys()['):
		s = s[16:].rstrip(']')
		r = int(s)
		rel = mkrel(P.R_HASATTR, r)
	    else:
		raise SyntaxError, 'Cant make a relation of %r.'%orgs
	elif s.startswith('->'):
	    s = s[2:]
	    if s.startswith('f_valuestack['):
		s = s[13:].rstrip(']')
		r = int(s)
		rel = mkrel(P.R_STACK, r)
	    else:
		rel = mkrel(P.R_INTERATTR, s)
	else:
	    raise SyntaxError, 'Cant make a relation of %r.'%orgs
	return rel
	    

    def get_byname(self):
	return 'referred via'

    def get_cli(self):
	memokind = {}
	memorel = {}
	return self.mod.hv.cli_inrel(self.rg, memokind, memorel)

    def get_kind(self, k):
	return self.family(k)

    def get_tabheader(self, ctx=''):
	if not ctx:
	    return "Referred Via:"
	else:
	    r = 'Referred Via'
	    if ctx == 'and':
		r = '{%s}'%r
	    return r

    def get_tabrendering(self, kind, ctx=''):
	r = self.get_userkindargrepr(kind)
	if ctx == 'and':
	    r = '{%s}'%r
	return r

    def get_userkind(self, *args):
	return self.get_kind([self._str2rel(x) for x in args])

    def get_userkindargrepr(self, kind):
	a = [repr(self._rel2str(x)) for x in kind.arg]
	a.sort()
	return ', '.join(a)
	


class AndClassifier(Classifier):
    def __init__(self, mod, name, args): # At least 2 args	
	if name is None:
	    name = '(%s)'%' & '.join([x.name for x in args])
	Classifier.__init__(self, mod, name, cli=None, supers=args, depends=args)
	self.args = args
		 
    def get_byname(self):
	return '<%s>'%' & '.join([x.get_byname() for x in self.args])

    def get_cli(self):
	memo = {}
	return self.mod.hv.cli_and(tuple([x.cli for x in self.args]), memo)

    def get_kind(self, k):
	ks = []
	for ki, ci in zip(k, self.args):
	    ks.append(ci.get_kind(ki))
	return self.mod.UniSet.fam_And._cons(ks)

    def get_reprname(self):
	return '(%s)'%' & '.join([x.get_reprname() for x in self.args])

    def get_tabheader(self, ctx=''):
	r =  '%s'%' & '.join([x.get_tabheader('and') for x in self.args])
	if ctx == 'and':
	    r = '(%s)'%r
	return r

    def get_tabrendering(self, cla, ctx=''):
	ss = []
	for a, cl in zip(cla.arg, self.args):
	    s = cl.get_tabrendering(a, 'and')
	    ss.append(s)
	r = ' & '.join(ss)
	if ctx == 'and':
	    r = '(%s)'%r
	return r

	    
class ModuleFamily:
    def __init__(self, mod, classifier):
	self.defrefining(mod.Use.Anything)
	self.classifier = classifier
	self.range = mod.fam_Family(self)

    def c_contains(self, a, b):
	return b is a.arg

    def c_get_render(self, a):
	return self.mod.summary_str(a.arg)

    def c_get_brief(self, a):
	return self.mod.summary_str(type(a.arg)) (a.arg)

    def c_repr(self, a):
	return '%s(%s)'%(self.classifier.get_reprname(),
			 self.classifier.get_userkindargrepr(a))

class ByModule(Classifier):
    def __init__(self, mod, name):
	def classify(x):
	    self.nc += 1
	    return x

	cli = mod.hv.cli_user_defined(mod.Use.Type.classifier.cli,
				      mod.Use.Type.Module.arg,
				      classify,
				      None
				      )
	Classifier.__init__(self, mod, name, cli)
	self.not_module = ~mod.Use.Type.Module
	self.nc = 0
	self.family = mod.fam_mixin_argatom(ModuleFamily, self)
	self.ModuleType = mod.types.ModuleType

    def get_byname(self):
	return 'module'

    def get_kind(self, k):
	if k is None:
	    return self.not_module
	else:
	    return self.family(k)

    def get_kindarg(self, kind):
	if kind is self.not_module:
	    return None
	else:
	    assert kind.fam is self.family
	    return kind.arg
	
    def get_tabheader(self, ctx=''):
	return 'Module'

    def get_userkind(self, name=None, at=None):
	if name is None and at is None:
	    return self.not_module
	if at is None:
	    try:
		m = self.mod.View.target.sys.modules[name]
	    except KeyError:
		raise ValueError, 'No module %r in View.target.sys.modules.'%name
	else:
	    m = self.mod.View.obj_at(at)
	if not isinstance(m, self.ModuleType):
	    raise TypeError, 'The specified object is not of module type, but %r.'%type(m)
	if name is not None and m.__name__ != name:
	    raise ValueError, 'The specified module has not name %r but %r.'%(name, m.__name__)
	return self.family(m)
	
    def get_userkindargrepr(self, kind):
	if kind is self.not_module:
	    return ''
	else:
	    m = kind.arg
	    name = m.__name__
	    s = '%r'%name
	    if self.mod._root.sys.modules.get(name) is not m:
		s += ', at=%s'%hex(id(m))
	    return s



class AltFamily:
    def __init__(self, mod, altcode):
	if altcode not in ('<', '<=', '==', '!=', '>', '>='):
	    raise ValueError, 'No such comparison symbol: %r'%altcode
	self.altcode = altcode

    def c_get_brief(self, a):
	return a.arg.fam.c_get_brief_alt(a.arg, self.altcode)

    def c_get_ckc(self, a):
	ckc = list(a.arg.get_ckc())
	if ckc[-1] == '==':
	    ckc[-1] = self.altcode
	else:
	    raise ValueError, 'Can not make alternative kind, non-equality comparison on underlying kind.'
	return tuple(ckc)

    def c_repr(self, a):
	return '%s.alt(%r)'%(repr(a.arg), self.altcode)

class FindexFamily:
    def __init__(self, mod, classifier):
	self.defrefining(mod.Use.Anything)
	self.classifier = classifier
	self.range = mod.fam_Family(self)

    def c_get_brief(self, a):
	if not 0 <= a.arg < len(self.classifier.kinds):
	    return '<None>'
	else:
	    return '%s / %d'%(self.classifier.kinds[a.arg].brief, a.arg)

    def c_repr(self, a):
	return '%s(%d)'%(self.classifier.get_reprname(), a.arg)

    

class ByFindex(Classifier):
    def __init__(self, mod, name, kinds):
	self.alts = [k.fam.c_get_ckc(k) for k in kinds]
	depends = [ckc[0] for ckc in self.alts]
	Classifier.__init__(self, mod, name, depends=depends)
	self.kinds = kinds
	self.family = mod.fam_mixin_argatom(FindexFamily, self)
		 
    def get_cli(self):
	alts = tuple([(cla.cli, k, cmp) for (cla, k, cmp) in self.alts])
	memo = {}
	cli = self.mod.hv.cli_findex(alts, memo)
	return cli

    def get_byname(self):
	return 'index of first matching kind of %s'%(self.kinds,)

    def get_tabheader(self, ctx=''):
	return 'First Matching Kind / Index'


class _GLUECLAMP_:
    _imports_ = (
	'_parent:ImpSet',
	'_parent:View',
	'_parent.View:hv',
	'_parent:UniSet',
	'_parent.UniSet:fam_mixin_argatom',
	'_parent:Use',
        '_root.guppy.etc.etc:str2int',
	'_root:re',
	'_root:types,'
	)

    def _er_by_(self, constructor, *args, **kwds):
	return self.UniSet.fam_EquivalenceRelation(constructor, *args, **kwds)

    # Exported equivalence relations

    def _get_Class(self):
	return self._er_by_(ByClass, self, name='Class')
    
    def _get_Clodo(self):
	return self._er_by_(ByClassOrDictOwner, self, name='Clodo')

    def _get_Id(self):
	return self._er_by_(ByIdentity, self, name='Id')

    def _get_Idset(self):
	return self._er_by_(ByIdentitySet, self, name='Idset')

    def _get_Module(self):
	return self._er_by_(ByModule, self, name='Module')

    def _get_Unity(self):
	return self._er_by_(ByUnity, self, name='Unity')

    def _get_Rcs(self):
	return self.mker_refdby(self.Clodo)

    def mker_and(self, ers):
	if len(ers) == 0:
	    return self.Unity
	classifiers = [er.classifier for er in ers]
	name = None
	return self.UniSet.fam_EquivalenceRelation(AndClassifier, self, name, classifiers)

    def mker_dictof(self, er, name=None):
	if name is None:
	    name='%s.dictof'%er.classifier.name
	return self.mker_memoized(
	    name,
	    lambda:
	    self._er_by_(ByDictOwner, self, name, er.classifier))

    def _get_memo_er(self):
	return {}

    def mker_memoized(self, name, f):
	v = self.memo_er.get(name)
	if v is None:
	    self.memo_er[name] = v = f()
	return v

    def mker_refdby(self, er, name=None):
	if name is None:
	    name='%s.refdby'%er.classifier.name
	return self.mker_memoized(
	    name,
	    lambda:
	    self._er_by_(
		ByRetClaSet,
		self,
		name,
		self.View.rg,
		er.classifier,
		"""%s
Classify by <%s> of referrers.
This classifier uses the %r classifier to classify the
referrers of the object. The classifications of the referrers
are collected in a set. This set becomes the classification of
the object.
"""%(name, er.classifier.get_byname(), er.classifier.name ) ))

    def _get_Size(self):
	return self._er_by_(ByIndiSize, self, 'Size')

    def _get_Type(self):
	return self._er_by_(ByType, self, 'Type')

    def _get_Via(self):
	View = self.View
	return self._er_by_(
	    ByInRel,
	    self,
	    'Via',
	    View.rg)


    def tc_adapt(self, k):
	# Adapt to a type or class.
	# Accepts a type or class object, or a string representation
	# (at least as) by tc_repr.

	if (isinstance(k, self.types.TypeType) or
	    isinstance(k, self.types.ClassType)):
	    return k
	if not isinstance(k, basestring):
	    raise TypeError, 'type, class or basestring expected'

	err = ("String argument to tc_adapt should be of form\n"
	       "'<class MODULE.NAME at 0xADDR>' or\n"
	       "'<type MODULE.NAME at 0xADDR>' or\n"
	       "'<at 0xADDR>'. I got: %r"%k)


	s = k
	if not (s.startswith('<') and s.endswith('>')):
	    raise ValueError, err
	s = s.lstrip('<').rstrip('>')
	s = s.split(' ')
	if len(s) < 2:
	    raise ValueError, err
	t = s[0]
	addr = self.str2int(s[-1])
	kind = self.View.obj_at(addr)
	if t == 'at':
	    if len(s) != 2:
		raise ValueError, err
	    ty = None
	else:
	    if len(s) != 4:
		raise ValueError, err
	    if t not in ('type', 'class'):
		raise ValueError, err
	    ty = getattr(self.types, t.capitalize()+'Type')
	    if not isinstance(kind, ty):
		raise TypeError, '%s object expected'%t
	    if not s[2] == 'at':
		raise ValueError, err
	    names = s[1].split('.')
	    if len(names) < 2:
		raise ValueError, err
	    modulename = '.'.join(names[:-1])
	    tcname = names[-1]
	    if kind.__module__ != modulename:
		raise ValueError, 'The %s %r has wrong __module__, expected %r.'%(t, kind, modulename)
	    if kind.__name__ != tcname:
		raise ValueError, 'The %s %r has wrong __name__, expected %r.'%(t, kind, tcname)

	return kind

    def tc_repr(self, k):
	# Represent a type or class object as a string,
	# so that it can converted back via tc_adapt,
	# as long as it still exists in the heap.
	# There is no absolute guarantee that it will always become the same object,
	# but I hope it will work well enough in practice.
	# See also Notes Sep 7 2005.

	if isinstance(k, self.types.TypeType):
	    t = 'type'
	elif isinstance(k, self.types.ClassType):
	    t = 'class'
	else:
	    raise TypeError, 'type or class expected'
	return '<%s %s.%s at %s>'%(t, k.__module__, k.__name__, hex(id(k)))

    # Convenience interfaces

    def _get_alt(self):
	altmemo = {
	    '==':lambda k:k,
	    '!=':lambda k:~k,
	    }
	def alt(kind, cmp):
	    a = altmemo.get(cmp)
	    if a is None:
		a = self.fam_mixin_argatom(AltFamily, cmp)
		altmemo[cmp] = a
	    return a(kind)
	return alt

    def biper(self, kind):
	return self.findex(kind)

    def _get_dictof(self):
	return self.fam_mixin_argatom(OwnedDictFamily)

    def _get_dictofnothing(self):
	return self.dictof(self.Use.Nothing)

    def _get_invtypemod(self):
	invtypemod = {}
	for k, v in self.types._module.__dict__.items():
	    if k.endswith('Type'):
		invtypemod[v] = k[:-4]
	return invtypemod

    def _get_notdict(self):
	return ~self.Use.Type.Dict

    def findex(self, *kinds):
	return self._er_by_(
	    ByFindex,
	    self,
	    'findex(%s)'%', '.join([repr(k) for k in kinds]),
	    kinds
	    )
	
    def _get_refdbynothing(self):
	return self.sonokind.refdby

    def sokind(self, *kinds):
        """sokind(0..*:Kind+) -> SetOfKind
"""
	cla = None
	clikinds = []
	if not kinds:
	    raise ValueError, 'At least one argument must be given.'
	for kind in kinds:
	    ckc = kind.get_ckc()
	    if cla is None:
		cla = ckc[0]
	    else:
		if ckc[0] is not cla:
		    raise ValueError, 'Kind at index %d has wrong classifier.'%len(clikinds)
	    if ckc[-1] != '==':
		raise ValueError, 'Kind at index %d has wrong comparision.'%len(clikinds)
	    clikinds.append(ckc[1])
	return QuickSoKind(cla, self.ImpSet.immnodeset(clikinds))
			   

    def _get_sonokind(self):
	return SoNoKind(self.Unity, ())

