#._cv_part guppy.etc.Glue
import new, re, sys, types

class GlueError(Exception):
    pass

class RecursionError(GlueError):
    pass

class NoSuchAttributeError(GlueError):
    pass

def ispackage(m):
    """ Determine if a module is a package - that means, sub-modules can be imported
    Currently uses that it has a file name that matches '.*__init__.py[co]?$'
    xxx is this portable/future-safe?
    
    """
    try:
	name = m.__file__
    except AttributeError:
	return 0
    return re.match('.*__init__.py[co]?$', name)

def dotname(first, last):
    if first and last:
	return '%s.%s'%(first, last)
    else:
	return first + last

class Interface(object):
    def __init__(self, share, owner, name):
	self.__dict__['_share'] = share
	self.__dict__['_owner'] = owner
	self.__dict__['_name'] = name
	for name in share.preload:
	    getattr(self, name)

    def _import(self, *names):
	return ','.join(names) + '=' + ','.join(['self._root.%s'%name for name in names])


    def __getattr__(self, name):
        #print 'getattr', name
	return self._share.getattr(self, name)

    def __setattr__(self, name, value):
	return self._share.setattr(self, name, value)


class Owner:
    def __init__(self, name):
	self.name = name
	self.galog = {}
	self.salog = {}
	self.inters = {}

    def log_getattr(self, cache, name):
	name = dotname(cache['_name'], name)
	self.galog[name] = 1

    def log_setattr(self, name):
	self.salog[name] = 1

    def makeInterface(self, cache, share, name):
	name = dotname(cache['_name'], name)
	if share not in self.inters:
            Clamp=share.Clamp
            if Clamp is not None and issubclass(Clamp, Interface):
                NewInterface = Clamp
            else:
                NewInterface = Interface
	    self.inters[share] = NewInterface(share, self, name)
	return self.inters[share]

    def pp(self, out=None,short=0):
	if out is None:
	    out = sys.stdout
	if not short:
	    print >>out, 'Attributes used by %s:'%self.name
	    print >>out,self.name[:self.name.rindex('.')+1]
	complete = []
	for a in self.galog:
	    for b in self.galog:
		if a != b and b.startswith(a):
		    break
	    else:
		complete.append(a)
	complete.sort()
	for a in complete:
	    print '    ',a

class Share:
    has_getattr_logging_enabled = False
    Clamp=None
    def __init__(self, module, parent, name, Clamp):
	if parent is None:
	    parent = self
	    root = self
	else:
	    root = parent.data['_root']
	self.module = module
	self.parent = parent
	self.name = name
        if Clamp is not None:
            self.Clamp = Clamp

	self.setable = getattr(Clamp, '_setable_', ())
	if not isinstance(self.setable, tuple):
	    raise TypeError, self.message('the _setable_ attribute must be a tuple')

	self.chgable = getattr(Clamp, '_chgable_', ())
	if not isinstance(self.chgable, tuple):
	    raise TypeError, self.message('the _chgable_ attribute must be a tuple')

	imports = getattr(Clamp, '_imports_', ())
	if not isinstance(imports, tuple):
	    raise TypeError, self.message('the _imports_ attribute must be a tuple')
	self.importedfrom = {}
	pres = {}
	parent_inter = root_inter = None
	for fi in imports:
	    presuf = fi.split(':')
	    if len(presuf) != 2:
		if len(presuf) > 2:
		    s = "Too many"
		else:
		    s = "No"
		raise SyntaxError, "%s ':' in import directive %r."%(s, fi)
	    pre, suf = presuf
	    pre = pre.strip()
	    prepa = pres.get(pre)
	    if prepa is None:
		hdta = pre.split('.', 1)
		hd = hdta[0]
		if hd == '_parent':
		    if parent_inter is None:
			parent_inter = Owner('').makeInterface({'_name':''}, parent, '')
		    hdo = parent_inter
		elif hd == '_root':
		    if root_inter is None:
			root_inter = Owner('').makeInterface({'_name':''}, root, '')
		    hdo = root_inter
		else:
		    raise SyntaxError, "Module must begin with _parent or _root"
		if len(hdta) == 2:
		    prepa = [hdo, hdta[1], None]
		else:
		    prepa = [hdo, '', hdo]
		pres[pre] = prepa

	    sufs = suf.split(',')
	    for su in sufs:
		su = su.strip()
		im = getattr(Clamp, '_get_%s'%su, None)
		if im is not None:
		    raise ValueError, 'Cant have both name (=%r) in boht importfrom  and _get'%su

		self.importedfrom[su] = prepa

	self.nowrap = getattr(Clamp, '_nowrap_', ())
	if not isinstance(self.nowrap, tuple):
	    raise TypeError, self.message('the _nowrap_ attribute must be a tuple')
	wrapattr = getattr(Clamp, '_wrapattr_', None)
	if isinstance(wrapattr, types.UnboundMethodType):
	    wrapattr = wrapattr.im_func
	elif wrapattr is not None:
	    raise TypeError, self.message('the _wrapattr_ attribute must be a method')
	self.wrapattr = wrapattr
	self.wrapping = 0
	self.data = {}
	self.owners = {}
	self.ispackage = module is None or ispackage(module)
	self.data['_parent'] = parent
	self.data['_root'] = root
	self.data['_module'] = module
	self.recursion = 0

	preload = getattr(Clamp, '_preload_', ())
	if preload:
	    self.preload = ()
	    inter = Owner('').makeInterface({'_name':''}, self, '')
	    for name in preload:
		getattr(inter, name)
	for name in preload:
	    assert name in self.data
	self.preload = preload

    def message(self, msg):
	return '%s: in %r: %s'%(self.__class__, self.name, msg)

    def getattr(self, inter, name):
	owner = inter._owner
	cache = inter.__dict__
	d = self.getattr2(inter, cache, owner, name)
	if name not in self.chgable:
	    cache[name] = d
	return d
	
    def getattr2(self, inter, cache, owner, name):
	if self.has_getattr_logging_enabled:
	    owner.log_getattr(cache, name)
	try:
	    x = self.data[name]
	except KeyError:
	    try:
		self.recursion += 1
		try:
		    if self.ispackage:
                        try:
                            x = self.getattr3(inter, name)
                        except:
                            x = self.getattr_package(inter, name)
		    else:
			x = self.getattr3(inter, name)
		except NoSuchAttributeError:
		    if name == '__repr__':
			return lambda : str(inter)
		    elif name == '__str__':
			return lambda : '<%s interface at %s>'%(inter._name,
                                                                hex(id(self)))
		    else:
                        x = self.getattr_module(inter, name)
		wrapattr = self.wrapattr
		if wrapattr is not None and name not in self.nowrap:
		    if not self.wrapping :
			try:
			    self.wrapping = 1
			    x = wrapattr(inter, x, name)
			finally:
			    self.wrapping = 0
		    else:
			pdb.set_trace()
		self.data[name] = x
	    finally:
		self.recursion -= 1
	if isinstance(x, Share):
	    x = owner.makeInterface(cache, x, name)
	return x

    def getattr_module(self, inter, name):
        try:
            return getattr(self.module, name)
        except AttributeError:
            raise AttributeError, \
'Module %r or its _GLUECLAMP_ has no attribute %r'%(self.module.__name__, name)

    def getattr_package(self, inter, name):
        try:
            x = __import__(self.makeName(name), globals(), locals())
        except ImportError, exc:
            if (exc.args[0] != 'No module named %s'%name or
                (not self.module and name not in ('__repr__', '__str__'))):
                raise
            x = self.getattr3(inter, name)
            # raise AttributeError, name
        else:
            if self.module:
                x = self.getattr_module(inter, name)
        if isinstance(x, types.ModuleType):
            x = self.makeModule(x, name)
        return x

    def getattr3(self, inter, name):
	if self.recursion >= 10:
	    raise RecursionError, name
	Clamp = self.Clamp
	if Clamp is None:
	    raise NoSuchAttributeError, name
	try:
	    x = getattr(Clamp, name)
	except AttributeError:
	    try:
		im = getattr(Clamp, '_get_%s'%name)
	    except AttributeError:
		if name in self.importedfrom:
		    prepa = self.importedfrom[name]
		    hdo, ta, pa = prepa
		    if pa is None:
			pa = hdo
			tas = ta.split('.')
			for at in tas:
			    pa = getattr(pa, at)
			prepa[2] = pa
		    x = getattr(pa, name)
		    return x

		gp = getattr(Clamp, '_GLUEPATH_', None)
		if gp is None:
		    raise NoSuchAttributeError, name
		if hasattr(gp, 'split'):
		    gp = gp.split(',')
		for a in gp:
		    a = a.strip()
		    bs = a.split('.')
		    ii = inter
		    for b in bs:
			b = b.strip()
			ii = getattr(ii, b)
		    try:
			x = getattr(ii, name)
		    except AttributeError:
			continue
		    else:
			return x
		raise NoSuchAttributeError, name
	    else:
		owner = self.makeOwner(name)
		inter = Interface(self, owner, '')
		f = new.instancemethod(im.im_func, inter, inter.__class__)
		x = f()
		if isinstance(x, Interface):
		    x = x.__dict__['_share']
	else:
	    if isinstance(x, types.UnboundMethodType):
		x = new.instancemethod(x.im_func, inter, inter.__class__)
	return x

    def makeModule(self, module, name):
	Clamp = getattr(module, '_GLUECLAMP_', None)
	return Share(module, self, module.__name__, Clamp)

    def makeName(self, name):
	if self.name:
	    name = '%s.%s'%(self.name, name)
	return name

    def makeOwner(self, name):
	owner_name = self.makeName(name)
	owner = Owner(owner_name)
	self.owners[owner_name] = owner
	return owner
	

    def pp(self,out=sys.stdout):
	if not self.owners:
	    return
	print >>out, 'Dependencies found for %s'%self.name
	print >>out, '-----------------------'+'-'*len(self.name)
	keys = self.owners.keys()
	keys.sort()
	for key in keys:
	    lastname = key[key.rindex('.')+1:]
	    print >>out,lastname
	    self.owners[key].pp(short=1)
	print >>out

    def rpp(self, out=sys.stdout):
	self.pp(out)
	for k, d in self.data.items():
	    if k not in ('_root', '_parent'):
		if isinstance(d, Share):
		    d.rpp()

    def setattr(self, inter, name, value):
	Clamp = self.Clamp
	if Clamp is None:
	    raise ValueError, 'Can not change attribute %r because no _GLUECLAMP_ defined.'%name
	im = getattr(Clamp, '_set_%s'%name, None)
	if im is not None:
	    im.im_func(inter, value)
	    self.data[name] = value
	    inter.__dict__[name] = value
	    return
	setable = self.setable
	chgable = self.chgable
	if (name not in setable and name not in chgable and
	    (not (name in self.data and self.data[name] is value))):
	    raise ValueError, """Can not change attribute %r,
because it is not in _setable_ or _chgable_ and no _set_%s is defined."""%(name, name)
	if name in self.data and self.data[name] is not value and name not in chgable:
	    raise ValueError, """Can not change attribute %r,
because it is already set and not in _chgable_."""%name
	self.data[name] = value
	if name not in chgable:	# This is a pain, I suppose. Should we track interfaces?
	    inter.__dict__[name] = value
	


class Test:
    def __init__(self, root):
	self.root = root

class _GLUECLAMP_:
    pass


def Root():
    """\
Create a new guppy Root object.

All functionality in the system may be accessed from this object.
Modules are imported on demand when accessed. Other objects may be
created or imported on demand using Guppy Glue+ directives.
"""
    share = Share(None, None, '', None)
    r = Owner('').makeInterface({'_name':''}, share, '')
    share.root_interface = r
    return r
