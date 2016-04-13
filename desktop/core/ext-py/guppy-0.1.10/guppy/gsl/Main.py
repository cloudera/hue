#._cv_part guppy.gsl.Main

from guppy.gsl.Exceptions import *

class SpecEnv:
    def __init__(self, mod):
	self.mod = mod
	self.imported_packages = {}
	self.importing_packages = {}
	self.error_reports = []
	self.num_errors = 0
	self.num_warnings = 0

    def errmsg_context(self, context):
	linetext = ''
	filename = '<unknown file>'
	if context is not None:
	    node = context	# Assume it's a node - that's all we use for now
	    lineno = node.index + 1
	    src = node.src
	    if src is not None:
		filename = src.filename
		linetext = src.get_line(index=context.index)
	    print '%s:%s:'% (filename, lineno)
	    if linetext:
		print '    %r'%linetext
	

    def error(self, message, context=None, exception=ReportedError, more=(), harmless = 0):
	self.error_reports.append((message, context, exception, more, harmless))
	if harmless:
	    self.num_warnings += 1
	else:
	    self.num_errors += 1
	    

	self.errmsg_context(context)
	if harmless:
	    print '*   %s'%message
	else:
	    print '*** %s'%message
	print

	for msg, ctx in more:
	    self.errmsg_context(ctx)
	    print '    %s'%msg
	    print

	if self.debug:
	    set_trace()
	else:
	    if self.num_errors >= self.max_errors:
		raise TooManyErrors, 'Too many errors, giving up'
	    if exception is not None:
		raise exception

    def get_filers(self, documents):
	filers = []
	for d in documents:
	    filers.extend(d.get_filers(self.output_dir))
	return filers

    def import_package(self, name, context):
	pac = self.imported_packages.get(name)
	if pac is None:
	    if name in self.importing_packages:
		self.error('Invalid mutual import involving packages %r'%(
		    self.importing_packages.keys(),), context)
	    self.importing_packages[name] = 1
	    filename = name.replace('.', self.mod.IO.path.sep)+'.gsl'
	    ip = self.package_of_filename(filename, name)
	    pac = self.mkPackage(ip)
	    self.imported_packages[name] = pac
	    del self.importing_packages[name]
	return pac

    def link_documents(self, documents):
	defines = {}

	links = {}
	def walk(node):
	    t = node.tag
	    if t == 'link_to':
		name = node.arg.strip()
		links.setdefault(name, []).append((d, node))
	    elif t == 'define':
		name = node.arg.strip()
		defines.setdefault(name, []).append((d, node))
	    elif t == 'to_tester_only':
		return
	    for ch in node.children:
		walk(ch)

	for d in documents:
	    node = d.get_result()
	    walk(node)

	for name, ds in defines.items():
	    if len(ds) > 1:
		print 'Duplicate definition of name %r, defined in:'%name
		for (d, node) in ds:
		    print '    %s line %s'%(d.get_doc_name(), node.index+1)
		print 'Will use the first one.'

	nodefs = []

	for name, ds in links.items():
	    if name not in defines:
		used = {}
		for (d, node) in ds:
		    used[d.get_doc_name()] = 1
		    node.tag = 'link_to_unresolved'
		used = used.keys()
		used.sort()
		used = ', '.join(used)
		nodefs.append('%s used in %s'%(name, used))
	    else:
		defd, defnode = defines[name][0]
		for (d, node) in ds:
		    if d is defd:
			node.tag = 'link_to_local'
		    else:
			node.tag = 'link_to_extern'
			node.children = (defd.doc_name_node,)+node.children
	if nodefs:
	    nodefs.sort()
	    print 'Unresolved links:'
	    for nd in nodefs:
		print '  ', nd

    def mkPackage(self, sub):
	pac = PackageDescription(self, sub, sub)
	pac.output_dir = self.output_dir
	pac.resolve_all()
	return pac
	
    def package_of_filename(self, filename, packname = None, nostrip=1, input_string=None):
	mod = self.mod
	if packname is None:
	    if filename.endswith('.gsl'):
		packname = filename[:-4]
	    else:
		packname = filename
	    packname = packname.replace(mod.IO.path.sep, '.')
	if self.input_dir:
	    filename = mod.IO.path.join(self.input_dir, filename)
	else:
	    filename = mod.IO.path.abspath(filename)
	if input_string is not None:
	    data = input_string
	else:
	    data = mod.IO.read_file(filename)
	md5 = mod.md5()
	md5.update('.filename: %s\n'%filename)
	md5.update('.packname: : %s\n'%packname)
	md5.update(data)
	digest = md5.digest()
	if digest in mod.package_cache:
	    return mod.package_cache[digest]
	
	node = mod.SpecNodes.node_of_string(data, filename, nostrip=nostrip)
	numerr = self.num_errors
	print 'Making package subject %r'%packname
	package = PackageSubject(mod, self, node, packname, filename)
	if numerr == self.num_errors:
	    mod.package_cache[digest] = package
	return package


    def process_main(self, filename, input_dir=None, output_dir=None, debug = False, max_errors=None,
		     process_despite_errors=False, raise_at_errors=False,
		     input_string=None
		     ):
	if input_dir is None:
	    input_dir = self.mod.input_dir
	self.input_dir = input_dir
	if output_dir is None:
	    output_dir='/tmp'
	self.output_dir = output_dir
	self.debug = debug
	if max_errors is None:
	    max_errors = self.mod.max_errors
	self.max_errors = max_errors

	try:
	    pac = self.mkPackage(self.package_of_filename(filename, input_string=input_string))
	    documents = pac.get_documents()
	    if not documents:
		self.error('No documents specified.', exception=None, harmless=1)
	    if not self.num_errors or process_despite_errors:
		print 'Linking'
		self.link_documents(documents)
	    if not self.num_errors or process_despite_errors:
		filers = self.get_filers(documents)
	except TooManyErrors:
	    giving_up = ' giving up --'
	else:
	    giving_up = ''
	if not self.num_errors:
	    for filer in filers:
		f = self.mod.Filer.filer(filer)
		print 'Writing: ', ', '.join(list(f.writefile_names))
		f.write()
	if self.num_warnings:
	    print '*   %d warning%s reported.'%(
		self.num_warnings, 's'[:self.num_warnings>1])
	if self.num_errors:
	    print '*** %d error%s reported --%s no files written.'%(
		self.num_errors, 's'[:self.num_errors>1], giving_up)
	    if raise_at_errors:
		raise HadReportedError, 'Some error has been reported.'



class UntypedDescription:
    def __init__(self, env, tgt, src):
	self.env = env
	self.pac = env.pac
	self.mod = env.mod
	self.tgt = tgt
	self.src = src

    def combine_with_subject(self, subject):
	self.combined_subjects.append(subject)

    def resolve_all(self):
	self.resolve_primary()
	self.resolve_lookuped()

    def resolve_primary(self):
	self.resolve_type()
	self.resolve_tgt()

    def resolve_type(self):
	dc = self.tgt.description_class
	if not hasattr(dc, 'd_tag'):
	    self.d_tag = self.tgt.tag
	self.tgtfullname = self.mod.tgt_prefix+self.tgt.fullname
	self.tgtnode = self.tgt.node
	self.tgtlastname = self.tgt.lastname
	self.srcnode = self.tgt.node
	self.srcfullname = self.src.fullname
	self.srclastname = self.tgt.lastname

	self.__class__ = dc

class Description:
    d_max_occur = None # Max occurence as an aspect if a number
    d_sub = ()	# Tags of allowed sub-aspects
    d_type = 'other'
    d_is_def = 0
    is_lookuped = False
    is_synthetic = False # Set if it was made not to correspond with a user node
    the_less_specific_descr = None
    args = ()


    def aspects_extend(self, as_):
	for asp in as_:
	    try:
		k = asp.src.definame
		# k = asp.tgt.definame # Humm
		if k:
		    w = self.localview.get(k)
		    if w:
			if w is asp:
			    # May happen eg as in test16, for a product
			    # But it is somewhat mystical.
			    continue
			self.error('Duplicate aspect %r (may be correct in future).'%(k,),
				   w.src.node,
				   DuplicateError)
		    self.localview[k] = asp
		bn = self.aspects_by_tag.setdefault(asp.d_tag, [])
		oc = asp.d_max_occur
		if oc is not None:
		    if len(bn) + 1 > oc:
			self.error('More than %d %r aspects.'%(
			    oc, asp.d_tag), asp.src.node)
		bn.append(asp)
		self.aspects.append(asp)
	    except ReportedError:
		pass

    def aspects_extend_by_subjects(self, subjects):
	for v in subjects:
	    try:
		asp = UntypedDescription(self, v, v)
		asp.resolve_primary()
		self.aspects_extend((asp,))
	    except ReportedError:
		pass


    def deftgt(self, forme=None):
	if forme is None:
	    forme = self

	try:
	    tgtview = self.tgtview
	except AttributeError:
	    self.env.deftgt(forme)
	else:
	    if forme.tgtfullname in tgtview:
		self.error('Duplicate definition of %r'%forme.tgtfullname, forme.src.node)
	    tgtview[forme.tgtfullname] = forme

    def error(self, msg, node=None, exception=ReportedError, **kwds):
	return self.pac.env.error(msg, node, exception, **kwds)

    def resolve_lookuped(self):
	if not self.is_lookuped:
	    self.is_lookuped = 1
	    self.resolve_aspects()
	
    def resolve_tgt(self):
	self.deftgt()

    def find_aspects(self, tag = '*', *tags):
	al = []
	tag = tag.replace(' ', '_')
	if tag in ('*', 'arg'):
	    for a in self.args:
		a.resolve_lookuped()
		al.append(a)
	    if tag == '*':
		for a in self.aspects:
		    a.resolve_lookuped()
		    al.append(a)
		return al
	tags = (tag,) + tags
	for a in self.aspects:
	    if a.d_tag in tags:
		a.resolve_lookuped()
		al.append(a)
	return al


    def find_arg_aspects(self):
	al = []
	for a in self.args:
	    a.resolve_lookuped()
	    al.append(a)
	for a in self.aspects:
	    if a.d_tag in ('arg', 'seq', 'repeat', 'alt', 'args', 'optionals', 'key_arg',
			  'draw', 'no_arg'):
		a.resolve_lookuped()
		al.append(a)
	return al

    def find_kind_aspects(self):
	kas = []
	for asp in self.find_aspects('*'):
	    if asp.d_tag in ('attribute', 'mapping', 'kind', 'either', 'kind_of', 'superkind',
			     'superkind_of'):
		kas.append(asp)
	    else:
		pass
	return kas

    def merge_policy(self, descrs):
	return descrs

    def get_descr_for_aspect(self, aspect):
	if not self.aspects and self.the_less_specific_descr is not None:
	    return self.the_less_specific_descr.get_descr_for_aspect(aspect)
	return self


    def get_atom_beams(self):
	aspects = self.find_aspects('*')
	aks = []
	for asp in aspects:
	    if asp.d_tag in ('attribute', 'mapping', 'either',  'operator',
			     'inplace_operator', 'reverse_operator', 'function_operator',
			     'delitem', 'getitem', 'setitem',
			     ):
		aks.append(beam(self, asp))
	    elif asp.d_tag in ('kind', 'kind_of', 'subkind_of') and asp is not self:
		a = beam(self, asp)
		for b in asp.get_atom_beams():
		    aks.append(a + b)
	return aks
	    


    def get_aspects_kind(self, aspects=None):
	if aspects is None:
	    aspects = self.find_aspects('*')
	aks = []
	for asp in aspects:
	    if asp.d_tag in ('attribute', 'mapping', 'either',
			     'operator', 'inplace_operator', 'reverse_operator', 'function_operator',
			     'delitem', 'getitem', 'setitem',
			     ):
		aks.append(asp)
	    elif asp.d_tag in ('kind', 'kind_of', 'subkind_of') and asp is not self:
		aks.extend(asp.get_atom_kinds())
	return aks

    def get_atom_kinds(self):
	return self.get_aspects_kind([self] + self.find_aspects('*'))

    def get_examples(self, get_all=False):
	examples = []
	exs = self.find_aspects('example')
	for ex in exs:
	    examples.extend(ex.get_examples())
	return examples

    def get_re(self, opt):
	if opt.get('get_examples'):
	    exres = [self.mod.RE.Single(x) for x in self.get_examples() ]
	    if not exres:
		self.error('Test coverage error: no examples specified.',
			   self.tgt.node,
			   CoverageError)
	    return self.mod.RE.Union(*exres)
	else:
	    return self.mod.RE.Single(self)

    def get_most_specific_descrs(self, descrs):
	nds = []
	for d in descrs:
	    nds = [x for x in nds if not d.is_more_specific_than(x)]
	    for x in nds:
		if x is d:
		    break
		if x.is_more_specific_than(d):
		    break
	    else:
		nds.append(d)
	return nds

    
    def get_package(self):
	return self.pac

    def is_more_specific_than(self, d):
	r = self.the_less_specific_descr
	return r is d or (r is not None and r.is_more_specific_than(d))


    def get_self_name(self):
	def find(e):
	    sa = e.find_aspects('self')
	    if sa:
		# length = 1, has been checked
		assert len(sa) == 1
		return sa[0].src.node.arg.strip()
	    if e.d_tag != 'package':
		return find(e.env)
	    return None
	return find(self)

    def gen_description_doc(self, out):
	ds = self.find_aspects('description')
	if not ds:
	    out.gen_text('<NO DESCRIPTION OF %r>'%self.tgtfullname)
	else:
	    for d in ds:
		d.gen_doc(out)

    def get_id_name(self):
	return self.tgtfullname

    def get_link_name(self):
	return self.tgtfullname

    def get_local_name(self):
	return self.srclastname

    def get_test_name(self):
	return self.tgtfullname

    def get_name(self):
	return self.tgtfullname

    def get_Name(self):
	# To be used in Name of doc.
	n = self.find_aspects('name')
	if not n:
	    name = self.tgtlastname
	else:
	    name = n.tgt.node.arg.strip()
	return name

    def get_descr_by_subject(self, subject):
	return self.pac.get_descr_by_subject(subject)


    def init_localview(self, only_vars=0):
	self.localview = {}
	self.aspects = []
	self.aspects_by_tag = {}

	if not only_vars:
	    self.aspects_extend_by_subjects(self.tgt.aspects)
				    

    def resolve_aspects(self):
	self.init_localview()
	if self.src.args:
	    self.args = [self.env.get_descr_by_subject(arg) for arg in self.src.args]
	self.resolve_special()

    def resolve_special(self):
	# To be overridden with special checks etc.
	pass

    def get_the_one_argument(self):
	arg = self.src.node.arg.strip()
	if self.aspects:
	    'No children expected for %r'%self.node.tag
	return arg

    def make_and_test_kind(self, kinds):
	ks = []
	def flatten(k):
	    if k.d_tag == 'kind':
		for k1 in k.find_kind_aspects():
		    flatten(k1)
	    else:
		ks.append(k)

	if (len(kinds) == 1 and kinds[0].d_tag == 'kind'):
	    return kinds[0]
	for k in kinds:
	    flatten(k)
	kinds = ks

	k = Kind()
	k.d_tag = 'kind'
	k.aspects = kinds
	k.tgtfullname = '(%s)'%('&'.join([x.tgtfullname for x in kinds]))
	k.is_lookuped = 1
	return k

    def make_and_kind(self, kinds):
	if (len(kinds) == 1 and kinds[0].d_tag in( 'kind', 'kind_of')):
	    return kinds[0]

	k = Kind()
	k.d_tag = 'kind'
	k.aspects = kinds
	k.tgtfullname = '(%s)'%('&'.join([x.tgtfullname for x in kinds]))
	k.is_lookuped = True
	k.is_synthetic = True
	return k

    def make_or_kind(self, kinds):
	if len(kinds) == 1:
	    return kinds[0]
	else:
	    k = Superkind()
	    k.d_tag = 'kind'
	    k.aspects = kinds
	    k.tgtfullname = '(%s)'%('|'.join([x.tgtfullname for x in kinds]))
	    k.is_lookuped = True
	    k.is_synthetic = True
	    return k
	    
	    

class Definition(Description):
    d_is_def = 1
    d_type = 'definition'
    def export_aspects(self, src):
	src.__class__ = self.__class__
	if src.d_tag == 'import':
	    src.d_tag = self.d_tag
	else:
	    if src.d_tag != self.d_tag:
		# Can't think of how this would happen - 
		# so not yet converted to .error()
		raise ImportError, 'Different description tag'
	src.aspects_extend(self.aspects)


class DescriptionDescription(Description):
    d_sub = ('text', )
    d_tag  = 'description'

    def gen_doc(self, out):
	self.srcnode.arg_accept(out)

class Default(DescriptionDescription):
    def gen_doc(self, out):
	arglines = self.srcnode.arg.strip().split('\n')
	default = arglines[0]
	rest = '\n'.join(arglines[1:])
	out.open('dl')
	out.open('dt')
	out.open('strong')
	out.gen_text('Default: ')
	out.close()
	out.gen_text(default)
	out.close()
	out.open('dd')
	out.gen_text(rest)
	self.srcnode.children_accept(out)
	out.close()
	out.close('dl')


class DescriptionWithHeader(DescriptionDescription):
    def gen_doc(self, out):
	arglines = self.srcnode.arg.strip().split('\n')
	header = arglines[0]
	rest = '\n'.join(arglines[1:])

	out.open('dl')
	out.gen_outer_dt(header)
	out.open('dd')
	out.gen_text(rest)
	self.srcnode.children_accept(out)
	out.close()
	out.close()

class Comment(DescriptionDescription):
    d_tag = 'comment'
    pass

class Either(Description):
    d_type = 'with_args'
    def get_atom_beams(self):
	return [beam(self)]

    def get_atom_kinds(self):
	return [self]

    def get_alt_kinds(self):
	return self.find_kind_aspects()

class Import(Definition):
    d_sub = ('from', 'resolve_by', 'using',
	     'attribute', 'condition', 'description', 'comment', 'constructor',
	     'mapping', 'method',
	     'operator', 'inplace_operator', 'reverse_operator', 'function_operator',
	     'delitem', 'getitem', 'setitem',
	     'self', 
	     'subkind_of',
	     )
    def resolve_tgt(self):
	self.is_lookuped = 1
	using_name, using_node = self.src.imp_using_map.get(
	    self.src.definame, (self.src.definame, self.src.node))
	import_node = self.src.node
	ds = [self.pac.import_package(from_name, from_node).
	          get_descr_by_name(using_name, using_node)
	      for (from_name, from_node) in self.src.imp_froms]

	if len(ds) == 1:
	    d = ds[0]
	else:
	    d = Product(self, ds, ProductSubject([x.src for x in ds]),
			self.src.imp_resolve_mode)
	    
	self.tgt = d.tgt
	self.tgtfullname = self.mod.tgt_prefix+self.tgt.fullname
	self.the_less_specific_descr = d

	self.init_localview(only_vars=1)
	d.export_aspects(self)
	self.aspects_extend_by_subjects(self.src.aspects)
	self.deftgt()
    
    def resolve_aspects(self):
	pass

class Product(Description):
    def __init__(self, env, ds, src, mode):
	self.env = env
	self.mod = env.mod
	self.src = src
	self.mode = mode
	self.pac = env.pac

	tgt = ds[0].tgt
	for d in ds[1:]:
	    if d.tgt is not tgt:
		self.error('Import error when importing from multiple packages:\n'+
			   '  Can not make a product of %r (tgt = %r) with %r (tgt = %r)\n'%(
		    d.src.fullname, d.tgt.fullname, ds[0].src.fullname, ds[0].tgt.fullname) +
		    '  because of different targets.',
		    d.src.node)
	
	self.tgt = tgt
	self.ds = ds

    def export_aspects(self, src):
	for d in self.ds:
	    d.export_aspects(src)

    def is_more_specific_than(self, d):
	for x in self.ds:
	    if x is d or x.is_more_specific_than(d):
		return True
	return False

class PackageDescription(UntypedDescription):
    def __init__(self, env, tgt, src):
	self.env = env
	self.pac = self
	self.mod = env.mod
	self.tgt = tgt
	self.src = src
    

class ErrorDescription:
    d_tag = 'error'
    def __init__(self, env):
	self.env = env

    def get_id_name(self):
	return '<error>.<error>'


class Package(Description):
    d_sub = ('and', 'comment', 'condition', 'document', 'import', 'kind', 'macro',
	     'superkind',
	     )

    def get_tgtdicts(self):
	seen = {id(self.tgtview):1}
	tgtdicts = [self.tgtview]
	for p in self.imported_packages.values():
	    sds = p.get_tgtdicts()
	    for sd in sds:
		if id(sd) not in seen:
		    seen[id(sd)] = 1
		    tgtdicts.append(sd)
	return tgtdicts

    def get_descr_by_name(self, name, context=None):
	if name.startswith(self.mod.tgt_prefix):
	    return self.get_descr_by_tgt_name(name, context)

	e = self
	parts = name.split('.')
	for part in parts:
	    try:
		e = e.localview[part]
	    except KeyError:
		assert context
		self.env.error(
		    'Undefined: %r in %r.'%(part, e.get_id_name()), context,
		    exception=UndefinedError)
	    e.resolve_lookuped()
	return e


    def get_descr_by_subject(self, subject):
	name = subject.fullname
	if name.startswith(self.srcfullname+'.'):
	    name = name[len(self.srcfullname)+1:].strip()
	else:
	    self.error('Undefined: %r'%name, subject.node)
	return self.get_descr_by_name(name, subject.node)

    def get_descr_by_tgt_name(self, name, context=None):
	tgtdicts = self.get_tgtdicts()
	descrs = []
	for tgtdict in tgtdicts:
	    if name in tgtdict:
		d = tgtdict[name]
		d.resolve_lookuped()
		d = d.get_descr_for_aspect('*')
		descrs.append(d)
	if not descrs:
	    self.error('No definition of tgt %r'%name, context, UndefinedError)
	descrs = self.get_most_specific_descrs(descrs)
	if len(descrs) > 1:
	    descrs = self.merge_policy(descrs)
	    if len(descrs) > 1:
		self.error('Conflicting descriptions of %r:%r'%(
		    name, [d.src.fullname for d in descrs]),
			   context,
			   DuplicateError)
			   
	return descrs[0]

    def get_filename(self):
	return self.src.filename

    def get_package(self):
	return self

    def resolve_tgt(self):
	self.tgtview = {}

    def resolve_aspects(self):
	self.imported_packages = {}
	self.init_localview()

    def import_package(self, name, context):
	pac = self.imported_packages.get(name)
	if pac is None:
	    pac = self.env.import_package(name, context)
	    self.imported_packages[name] = pac
	return pac

    def get_documents(self):
	documents = []
	for doc in self.src.documents:
	    node = doc.node
	    doc = self.mod.Document.document(node, self)
	    documents.append(doc)

	return documents

class Attribute(Definition):
    d_sub = ('attribute', 'comment', 'description', 'description_with_header',
	     'either', 'kind_of', 'mapping', 'method', 'self')
    def export_aspects(self, src):
	src.__class__ = self.__class__
	src.aspects_extend(self.aspects)

    def get_attr_name(self):
	return self.tgtlastname

    def get_name(self):
	return self.tgtlastname

    def get_kind(self):
	kas = self.find_kind_aspects()
	return self.make_and_kind(kas)

    def get_kind_name(self):
	k = self.get_kind()
	if k.d_tag == 'kind_of':
	    kas = k.find_kind_aspects()
	    if len(kas) == 1:
		k = kas[0]
	    else:
		raise ValueError, "Don't know how to name this kind, %r"%self
	return k.tgtfullname

    def get_link_name(self):
	# xxx needs smoother logic
	s = '%s.%s'%(self.get_descr_by_subject(self.tgt.parent).get_link_name(), self.tgt.lastname)
	#set_trace()
	return s

    def get_test_kind(self):
	kas = self.find_kind_aspects()
	return self.make_and_test_kind(kas)

    def is_method(self):
	return (self.find_aspects('mapping') and
		not self.find_aspects('kind_of'))

    def get_op_name(self):
	return self.get_attr_name()

class KindOf(Description):
    d_type = 'with_args'
    d_sub = ()


class SubkindOf(Description):
    d_type = 'with_args'
    d_sub = ('description',)

class Kind(Definition):
    d_sub = ('attribute', 'condition', 'description', 'comment', 'constructor',
	     'example',
	     'mapping', 'method',
	     'operator', 'inplace_operator', 'reverse_operator', 'function_operator',
	     'self',
	     'subkind_of',
	     'delitem', 'getitem', 'setitem',
	     )

    def get_attributes(self):
	return self.find_aspects('attribute')

    def get_mappings(self):
	return self.find_aspects('mapping')



class Superkind(Definition):
    d_sub = ('comment', 'description', 'example', 'superkind_of')

    def get_local_name(self):
	if 0: # hmm xxx why was this?
	    if not self.aspects:
		return '<nothing+>'
	return self.srclastname

class SuperkindOf(Description):
    d_type = 'with_args'
    def get_examples(self, enough=1):
	examples = Description.get_examples(self, enough)
	if len(examples) < enough:
	    for ka in self.find_kind_aspects():
		if ka is self:
		    continue
		examples.extend(ka.get_examples(enough-len(examples)))
		if len(examples) >= enough:
		    break
	return examples

    

class Example(Description):
    d_sub = ('comment', 'description', 'in_context')
    partab = {"'''":"'''",
	      '"""':'"""',
	      '(':')',
	      '[':']',
	      '{':'}'
	      }
    def get_ex_text(self):
	return self.src.ex_text

    def get_examples(self, get_all=False):
	return [self]

    def get_ctx_text(self):
	asp = self.find_aspects('in_context')
	if not asp:
	    return ''
	# It is of length 1, has been checked.
	return asp[0].tgt.node.arg.strip()

    def get_use_text(self, x):
	return x

class InContext(Description):
    d_max_occur = 1

class Defines(Description):
    d_type = 'with_args'
    def get_defined_tgt_names(self):
	return [x.tgtfullname for x in self.find_aspects('arg')]

    
class Macro(Definition):
    def export_aspects(self, src):
	src.__class__ = self.__class__
	src.tgtnode = self.tgtnode

    def use(self, options):
	return self.mod.SpecNodes.node_of_taci(
	    'block', '', self.tgtnode.children, self.tgtnode.index)


class Self(Description):
    d_max_occur = 1

class Mapping(Description):
    d_type = 'other'
    d_sub = ('alt', 'arg', 'args', 'comment', 'description', 'description_with_header',
	     'equation',
	     'draw',
	     'key_arg',
	     'optionals',
	     'precondition', 'postcondition',
	     'repeat', 'returns', 
	     'self',
	     'seq',
	     )

    def chk_num_args(self, min, max):
	re = self.get_args_re({})
	xs = re.sequni()
	for x in xs:
	    try:
		if min is not None and min == max and len(x) != min:
		    self.error(
			'%s requires %d argument%s specified, got %d.'%(
			    self.d_tag, min, 's'[min == 1:], len(x)),
			self.src.node)

		elif min is not None and len(x) < min:
		    self.error(
			'%s requires at least %d argument%s specified, got %d.'%(
			    self.d_tag, min, 's'[min == 1:], len(x)),
			self.src.node)

		elif max is not None and len(x) > min:
		    self.error(
			'%s can take at most %d argument%s specified, got %d.'%(
			    self.d_tag, max, 's'[max == 1:], len(x)),
			self.src.node)
	    except ReportedError:
		pass

    def get_arg_kinds(self):
	ak = []
	for a in self.find_aspects('args'):
	    ak.extend(list(a.args))
	return ak

    def get_args_examples(self, mapname, top_kind):
	# Get arguments example, esp. for test purposes

	try:
	    opt = {'get_examples':True}

	    re = self.get_args_re(opt)

	    coverage = 1
	    try:
		xs = re.sequni()
	    except self.mod.RE.InfiniteError:
		print 'Infinitely long args example for %s'%self.srcfullname
		print 'Limiting by expanding each Cleene closure 0 up to %d times.'%coverage
		re = re.limited(coverage)
		xs = re.sequni()
	    examples = [ArgsExample(self, tuple(x), mapname, top_kind) for x in xs]
	except CoverageError:
	    return []
	else:
	    return examples
	
    def get_args_for_args(self, args, match):
	arglist = []
	for a in self.find_arg_aspects():
	    t = a.d_tag
	    if t == 'arg':
		name = a.get_name()
		if name in match:
		    v = args.get_arg_value(match[name])
		else:
		    ex = a.get_examples()
		    if not ex:
			# I have been able to cause this to happen in test67.
			self.error(
    'Test coverage error: Can not create precondition for %r\n -- no examples specified for the argument above.'%args.mapping.tgtfullname,
    a.src.node
    )
		    v = ex[0]
		arglist.append(v)
	    else:
		assert 0
		# raise ConditionError, 'Can not match this precondition'

	return ArgsExample(self, tuple(arglist), args.mapname, args.top_kind)

    def get_args_re(self, opt):
	re = self.mod.RE.Epsilon
	for a in self.find_arg_aspects():
	    re += a.get_re(opt)
	return re


    def get_arguments(self):
	# Get the arguments subjects, for doc description purposes
	return self.find_arg_aspects()
	


    def get_return_kind(self):
	return self.make_and_kind([x.get_kind() for x in self.find_aspects('returns')])

    def get_return_test_kind(self):
	return self.make_and_test_kind([x.get_test_kind() for x in self.find_aspects('returns')])



class ArgsExample:
    def __init__(self, mapping, egs, mapname, top_kind):
	self.mapping = mapping
	self.egs = egs
	self.mapname = mapname
	self.top_kind = top_kind
	self.negs = [mapname(x) for x in egs]

    def __str__(self):
	return ', '.join(self.negs)

    def get_arg_value(self, name):
	i = 0
	for a in self.mapping.find_arg_aspects():
	    t = a.d_tag
	    if t == 'arg':
		if a.get_name() == name:
		    return self.egs[i]
	    else:
		raise ConditionError, 'No argument matches: %r'%name
	    i += 1

    def get_preconditions(self):
	return self.mapping.find_aspects('precondition')

    def get_postconditions(self):
	return self.mapping.find_aspects('postcondition')

    def get_setups_for_preconditions(self):
	pres = self.get_preconditions()
	if not pres:
	    return []
	kind = self.top_kind
	
	map = self.mapping

	pres = map.find_aspects('precondition')
	# print 'map', map, map.d_tag
	if pres:
	    #set_trace()
	    for a in kind.find_aspects('attribute'):
		for m in a.find_aspects('mapping'):
		    mpre = m.find_aspects('precondition')
		    if mpre:
			continue
		    match = self.match_to(m.find_aspects('postcondition'))
		    if match is not None:
			# found one
			# print 'found precondition, match = ', match
			args = m.get_args_for_args(self, match)
			return [SetUp(a.get_attr_name(), args)]
			break
		else:
		    continue
		break
	    else:
		# Caller will do error reporting
		return None
	return []

    def match_to_kind(self, kind):
	pass

    def match_to(self, posts):
	match = {}
	for pre in self.get_preconditions():
	    for pos in posts:
		if pos.cond_id == pre.cond_id:
		    if len(pos.arg_names) != len( pre.arg_names):
			continue
		    upd = {}
		    for a, b in zip(pos.arg_names, pre.arg_names):
			if a in match:
			    break
			upd[a] = b
		    else:
			match.update(upd)
			break
	    else:
		return None
	assert ',' not in match
	return match
			    
class SetUp:
    def __init__(self, name, args):
	self.name = name
	self.args = args

    def get_name(self):
	return self.name

    def get_args(self):
	return self.args



class Operator(Mapping):
    d_is_def = 1
    d_type = 'operator'
    d_sub = ('arg', 'comment', 'description', 'description_with_header',
	     'equation',
	     'postcondition', 'precondition',
	     'self', 'returns', )

    def get_op_name(self):
	return self.src.node.arg.strip()

    def resolve_special(self):
	self.chk_num_args(1, 1)


class ReverseOperator(Operator):
    pass

class FunctionOperator(Operator):
    def resolve_special(self):
	self.chk_num_args(0, 0)

class InplaceOperator(Operator):
    pass

class SetItem(Mapping):
    d_type = 'other'
    d_sub = ('arg', 'comment', 'description', 'description_with_header',
	     'equation',
	     'postcondition', 'precondition',
	     'self')
    
    def get_op_name(self):
	return '[]'

    def resolve_special(self):
	self.chk_num_args(2, None)

class DelItem(SetItem):
    def resolve_special(self):
	self.chk_num_args(1, None)

class GetItem(SetItem):
    d_sub = SetItem.d_sub + ('returns', )

    def resolve_special(self):
	self.chk_num_args(1, None)

class Condition(Description):
    d_is_def = 1
    d_sub = ('self', 'arg', 'comment', 'description', 'python_code')

    def get_arg_names(self):
	an = []
	for a in self.find_aspects('*'):
	    if a.d_tag in ('self', 'arg'):
		an.append(a.src.node.arg.strip())
	return an
			  
    def get_def_name(self):
	dn = self.src.lastname
	self.def_name = dn
	return dn

    def_name = property(get_def_name)

class PythonCode(Description):
    d_sub = ('comment', 'description', 'in_context')

class ConditionRef(Description):
    d_sub = ('comment', 'description',)
    def __repr__(self):
	try:
	    return self.cond_expr
	except AttributeError:
	    return Description.__repr__(self)

    def get_cond_id(self):
	cond_id = self.cond_definition.tgtfullname
	if self.is_not:
	    cond_id = 'not ' + cond_id
	self.cond_id = cond_id
	return cond_id

    cond_id = property(get_cond_id)

    def get_definition(self):
	return self.cond_definition

    def resolve_special(self):
	cond_def = self.src.cond_definition
	self.cond_definition = self.env.get_descr_by_subject(cond_def)
	self.cond_doc_name = cond_def.parent.lastname + '.' + cond_def.lastname
	self.cond_expr = self.src.node.arg.strip()    # Mostly for information
	self.arg_names = self.src.arg_names
	self.is_not = self.src.is_not



class Precondition(ConditionRef):
    #doc_name = 'Before'
    doc_name = 'Precondition'

class Postcondition(ConditionRef):
    #doc_name = 'After'
    doc_name = 'Postcondition'

class PostcondCase:
    # Postcondition with specific variables
    def __init__(postcond, variables):
	self.postcond = postcond
	self.variables = variables
    
class Constructor(Description):
    d_type = 'with_args'
    d_sub = ('comment', 'description',)
    


class Equation(Description):
    d_sub = ('comment', 'description', 'precondition', 'postcondition')

class Args(Description):
    d_type = 'with_args'
    d_sub = ('comment', 'description', 'optionals', )

    def get_re(self, opt):
	re = self.mod.RE.Epsilon
	for a in self.find_arg_aspects():
	    re += a.get_re(opt)
	return re

class NoArg(Description):
    def get_re(self, opt):
	return self.mod.RE.Epsilon

class Arg(Description):
    d_sub = ('comment', 'default', 'description', 'superkind_of', 'name', )

    def get_kind(self):
	return self.make_or_kind(self.find_kind_aspects())

    def get_name(self):
	try:
	    return self.get_arg_name()
	except AttributeError:
	    return '?'

    def get_arg_name(self):
	return self.src.specified_name

    def get_examples(self, get_all=False):
	examples = []
	exs = self.find_aspects('example')
	for ex in exs:
	    examples.extend(ex.get_examples())
	if not exs or get_all:
	    k = self.get_kind()
	    examples.extend(k.get_examples())
	return examples
	
class KeyArgEG:
    def __init__(self, name, eg):
	self.name = name
	self.eg = eg
    
    def get_ex_text(self):
	return self.eg.get_ex_text()

    def get_ctx_text(self):
	return self.eg.get_ctx_text()

    def get_use_text(self, x):
	return '%s=%s'%(self.name, x)
			  

class KeyArg(Arg):
    # Spec with keyarg means it is:
    # NOT to be used as positional argument
    # ONLY as keyword argument

    def get_examples(self, get_all=False):
	name = self.get_arg_name()
	return [KeyArgEG(name, eg) for eg in Arg.get_examples(self, get_all)]
	
class Draw(Description):
    d_sub = ('comment', 'description', 'key_arg', 'seq', )
    def get_re(self, opt):
	re = self.mod.RE.Epsilon
	for a in self.find_arg_aspects():
	    re += a.get_re(opt)('?')
	return re
				
class Optionals(Description):
    d_sub = ('arg', 'args', 'key_arg', 'comment', 'seq', )
    d_type = 'with_args'
    def get_re(self, opt):
	def opt_ra(aspects):
	    if not aspects:
		return self.mod.RE.Epsilon
	    return (aspects[0].get_re(opt) + opt_ra(aspects[1:]))('?')
	return opt_ra(self.find_arg_aspects())


class Repeat(Description):
    d_sub = ('alt', 'arg', 'args', 'comment', 'description')
    def get_arg(self):
	return self.src.node.arg.strip()

    def get_re(self, opt):
	asp = self.find_arg_aspects()
	if not asp:
	    self.error('No argument aspects.',self.src.node)
		

	re = asp[0].get_re(opt)
	for a in asp[1:]:
	    re += a.get_re(opt)

	arg = self.get_arg()
	sep = '..'

	if sep in arg:
	    args = arg.split(sep)
	    if len(args) != 2:
		self.error('More than one %r in argument.'%sep, self.src.node)
	    lo, hi = [x.strip() for x in args]
	    try:
		lo = int(lo)
	    except:
		self.error('Expected int in lower bound.', self.src.node)
	    if hi != '*':
		try:
		    hi = int(hi)
		except:
		    self.error('Expected int or * in upper bound.', self.src.node)
	else:
	    try:
		lo = int(arg)
	    except:
		self.error('Expected int, int..int or int..* in argument.', self.src.node)
	    hi = lo
	if lo < 0 or (hi != '*' and hi < 0):
	    self.error('Expected non-negative repetition count.',  self.src.node)

	if hi == '*':
	    res = re('*')
	    for i in range(lo):
		res = re + res
	else:
	    if hi < lo:
		self.error('Expected upper bound >= lower bound.', self.src.node)

	    a = self.mod.RE.Epsilon
	    for i in range(lo):
		a += re
	    b = self.mod.RE.Epsilon
	    for i in range(lo, hi):
		b = (re + b)('?')
	    res = a + b
		
	return res


class Seq(Description):
    d_sub = ('arg', 'comment', 'description', 'optionals',)
    d_sub += ('key_arg', ) # May perhaps be optionally disabled
    d_type = 'with_args'
    def get_re(self, opt):
	re = self.mod.RE.Epsilon
	for a in self.find_arg_aspects():
	    re += a.get_re(opt)
	return re

class Alt(Description):
    d_sub = ('arg', 'comment', 'descripton', 'key_arg', 'no_arg', 'seq', )
    d_type = 'with_args'
    def get_re(self, opt):
	asp = self.find_arg_aspects()
	if not asp:
	    self.error('No alternatives.', self.src.node)
	re = asp[0].get_re(opt)
	for a in asp[1:]:
	    re |= a.get_re(opt)
	return re

class Returns(Description):
    d_sub = ('attribute', 'comment', 'description', 'description_with_header',
	     'either', 'mapping', 'method')
    d_type = 'with_opt_args'
    
    def get_kind(self):
	return self.make_and_kind(self.find_kind_aspects())

    def get_test_kind(self):
	return self.make_and_test_kind(self.find_kind_aspects())

# help functions

def find_aspects_inseq(seq, tag):
    as_ = []
    for o in seq:
	as_.extend(o.find_aspects(tag))
    return as_

# Beam base class

class Beam:
    def __init__(self, k_tag, *objects):
	self.src = objects[0]
	self.tgt = objects[-1]
	self.k_tag = k_tag
	self.objects = objects

    def __add__(self, other):
	return compose(self, other)

class KindBeam(Beam):
    pass

class AtomKindBeam(Beam):
    pass

class KindMappingBeam(Beam):
    pass

class KindOpBeam(Beam):
    op_index = 1
    op_name_index = 1

    def find_equations(self):
	return find_aspects_inseq(self.get_op_seq(), 'equation')

    def find_postconditions(self):
	return find_aspects_inseq(self.get_op_seq(), 'postcondition')

    def find_preconditions(self):
	return find_aspects_inseq(self.get_op_seq(), 'precondition')

    def get_args_examples(self, mapname):
	top_kind = self.objects[0]
	return self.get_the_op().get_args_examples(mapname, top_kind)
    
    def get_op_id_name(self):
	return self.objects[self.op_name_index].get_id_name()

    def get_op_name(self):
	return self.objects[self.op_name_index].get_op_name()

    def get_op_seq(self):
	return self.objects[self.op_index:]

    def get_self_name(self):
	return self.get_the_op().get_self_name()

    def get_the_op(self):
	return self.objects[self.op_index]

    def get_return_test_kind(self):
	return self.get_the_op().get_return_test_kind()

class KindAttributeBeam(KindOpBeam):
    def get_the_op(self):
	assert 0

class KindAttributeMappingBeam(KindOpBeam):
    op_index = 2

class KindMappingBeam(KindOpBeam):
    def get_op_name(self):
	return '()'

class KOKOpBeam(KindOpBeam):
    op_index = 2
    op_name_index = 2

def subkind_of_kind(*objects):
    return beam(*objects[2:])

def compose(a, b):
    if a.tgt is not b.src:
	raise "Composition error, tgt %r is not src %r"%(a.tgt, b.src)

    objects = a.objects + b.objects[1:]
    return beam(*objects)


def remove_1_2(k_tag, *objects):
    return beam(objects[0], *objects[3:])

def remove_0(k_tag, *objects):
    return beam(*objects[1:])

beam_table = {
    ('attribute', 'attribute') : Beam,
    ('attribute', 'either') : Beam,
    ('attribute', 'kind_of') : Beam,
    ('attribute', 'kind_of', 'kind', 'attribute') : Beam,
    ('attribute', 'kind_of', 'kind', 'function_operator') : Beam,
    ('attribute', 'kind_of', 'kind', 'inplace_operator') : Beam,
    ('attribute', 'kind_of', 'kind', 'mapping') : Beam,
    ('attribute', 'kind_of', 'kind', 'operator') : Beam,
    ('attribute', 'kind_of', 'kind', 'reverse_operator') : Beam,
    ('attribute', 'kind_of', 'kind', 'delitem') : Beam,
    ('attribute', 'kind_of', 'kind', 'getitem') : Beam,
    ('attribute', 'kind_of', 'kind', 'setitem') : Beam,
    ('attribute', 'mapping') : Beam,
    ('either', ) : Beam,
    ('either', 'kind') : Beam,
    ('either', 'kind', 'attribute') : Beam,
    ('kind', 'attribute') : Beam,
    ('kind', 'attribute', 'kind_of', 'kind', 'mapping') : KindAttributeBeam,
    ('kind', 'attribute', 'mapping') : KindAttributeMappingBeam,
    ('kind', 'either') : Beam,
    ('kind', 'function_operator') : KindOpBeam,
    ('kind', 'delitem') : KindOpBeam,
    ('kind', 'getitem') : KindOpBeam,
    ('kind', 'inplace_operator') : KindOpBeam,
    ('kind', 'kind_of') : Beam,
    ('kind', 'kind_of', 'kind', 'attribute') : Beam,
    ('kind', 'mapping') : KindMappingBeam,
    ('kind', 'operator') : KindOpBeam,
    ('kind', 'reverse_operator') : KindOpBeam,
    ('kind', 'setitem') : KindOpBeam,
    ('kind', 'subkind_of') : Beam,
    ('kind', 'subkind_of', 'kind', 'attribute') : remove_1_2,
    ('kind', 'subkind_of', 'kind', 'function_operator') : remove_1_2,
    ('kind', 'subkind_of', 'kind', 'delitem') : remove_1_2,
    ('kind', 'subkind_of', 'kind', 'getitem') : remove_1_2,
    ('kind', 'subkind_of', 'kind', 'inplace_operator') : remove_1_2,
    ('kind', 'subkind_of', 'kind', 'mapping') : remove_1_2,
    ('kind', 'subkind_of', 'kind', 'operator') : remove_1_2,
    ('kind', 'subkind_of', 'kind', 'reverse_operator') : remove_1_2,
    ('kind', 'subkind_of', 'kind', 'setitem') : remove_1_2,
    ('kind_of', 'kind') : Beam,
    ('kind_of', 'kind', 'attribute') : Beam,
    ('kind_of', 'kind', 'function_operator') : KOKOpBeam,
    ('kind_of', 'kind', 'delitem') : KOKOpBeam,
    ('kind_of', 'kind', 'getitem') : KOKOpBeam,
    ('kind_of', 'kind', 'inplace_operator') : KOKOpBeam,
    ('kind_of', 'kind', 'operator') : KOKOpBeam,
    ('kind_of', 'kind', 'reverse_operator') : KOKOpBeam,
    ('kind_of', 'kind', 'setitem') : KOKOpBeam,
    ('kind_of', 'kind', 'mapping') : Beam,
    ('subkind_of', 'kind') : Beam,
    ('subkind_of', 'kind', 'attribute') : Beam,
    ('subkind_of', 'kind', 'function_operator') : Beam,
    ('subkind_of', 'kind', 'delitem') : Beam,
    ('subkind_of', 'kind', 'getitem') : Beam,
    ('subkind_of', 'kind', 'inplace_operator') : Beam,
    ('subkind_of', 'kind', 'mapping') : Beam,
    ('subkind_of', 'kind', 'operator') : Beam,
    ('subkind_of', 'kind', 'reverse_operator') : Beam,
    ('subkind_of', 'kind', 'setitem') : Beam,

    }

def beam(*objects):
    k_tag = tuple([x.d_tag for x in objects])
    C = beam_table[k_tag]
    return C(k_tag, *objects)
		     


class ProductSubject:
    def __init__(self, subjects):
	self.subjects = subjects
	self.fullname = '(%s)'%'*'.join([x.fullname for x in subjects])

class Subject:
    args = ()
    specified_name = None
    def __init__(self, parent, node, lastname):
	self.parent = parent
	self.pac = parent.pac
	self.mod = self.pac.mod
	self.node = node
	self.filename = self.pac.filename
	self.lastname = lastname
	self.aspects = []
	self.subjects = {}
	self.node_index = 0
	self.tag = node.tag
	self.description_class = self.mod.get_description_class(node.tag)
	self.aspect_mode = None

	if self.parent is not self:
	    self.fullname = self.parent.make_child_name(self.lastname)
	else:
	    self.fullname = self.lastname

    def _visit_type_definition(self, node):
	names = self.get_arglist(node, min=1)
	for name in names:
	    self.add_new_subject(node, name)

    def _visit_type_operator(self, node):
	shtag = self.mod.SpecNodes.reverse_node_aliases[node.tag]
	names = self.get_arglist(node, min=1)
	for name in names:
	    name = '%s:%s'%(shtag, name)
	    self.add_new_subject(node, name)

    def _visit_type_other(self, node):
	self.add_new_subject(node)

    def _visit_type_with_args(self, node):
	names = self.get_arglist(node)
	args = [self.find_subject(name, node) for name in names]
	subject = self.add_new_subject(node)
	if args:
	    subject.args = args

    def _visit_type_with_opt_args(self, node):
	names = self.get_arglist(node, min=0)
	args = [self.find_subject(name, node) for name in names]
	subject = self.add_new_subject(node)
	if args:
	    subject.args = args

    def add_new_subject(self, node, lastname=None):
	subject = self.new_subject(node, lastname)
	self.add_subject(subject)
	return subject

    def add_subject(self, subject):
	self.def_subject(subject)
	subject.add_top_node()
	return subject
	
    def add_top_node(self):
	node = self.node
	self._visit_children(node)

    def def_new_subject(self, node, lastname=None):
	subject = self.new_subject(node, lastname)
	self.def_subject(subject)
	return subject

    def def_subject(self, subject):
	if subject.description_class.d_is_def:
	    name = subject.lastname
	    if name in self.subjects:
		self.error('Redefinition of %r.'%name, subject.node,
			   more = [(
			       'Previous definition of %r.'%name, 
			       self.subjects[name].node)]
			   )
		return # For clarity; there's most certainly an exception

	    subject.definame = name
	    self.subjects[name] = subject
	else:
	    subject.definame = None
	self.aspects.append(subject)


    def error(self, msg, node=None, exception=ReportedError, **kwds):
	return self.pac.error(msg, node, exception, **kwds)

    def find_subject(self, name, node):
	return self.pac.find_subject(name, node, self)

    def get_arglist(self, node, min=0):
	arglist = node.get_arglist()
	for arg in node.get_arglist():
	    if not arg:
		if node.arg.strip().startswith(',') or node.arg.strip().endswith(','):
		    m = 'Arg list to definition can not start or end with a comma.'
		else:
		    m = 'Missing argument to definition.'
		self.error(m, node, exception=None)
		arglist = [x for x in arglist if x]
		break
	if len(arglist) < min:
	    self.error(
		'Not enough arguments, minimum %d expected to node %s'%(min, node),
		node)
	return arglist
	
    def get_arglist_only(self, node, min=0):
	al = self.get_arglist(node, min)
	self.no_children(node)
	return al

    def get_line(self, index):
	try:
	    text = list(open(self.filename).readlines())[index].rstrip()
	except:
	    text = None
	return text

    def _visit_aspect(self, node, mode):
	if self.aspect_mode is None:
	    self.aspect_mode = mode
	else:
	    if self.aspect_mode != mode:
		self.error('Inconsistent aspect mode: %r, was: %r'%(mode, self.aspect_mode),
			   node)
	self._visit_children(node)

    def _visit_children(self, node):
	for ch in node.children:
	    try:
		if ch.tag not in self.description_class.d_sub:
		    self.error('Invalid  tag: %r  in: %r. Allowed = %s'%(
			ch.tag, self.tag, self.description_class.d_sub), node)
		if self.mod.cover_check is not None:
		    self.mod.cover_check.setdefault(self.tag, {})[ch.tag] = 1
		ch.accept(self)
	    except ReportedError:
		pass
	    self.node_index += 1

    def make_child_name(self, child_lastname):
	return '%s.%s'%(self.fullname, child_lastname)

    def new_subject(self, node, name=None):
	is_def = self.mod.get_description_class(node.tag).d_is_def
	assert is_def == (name is not None)
	if name is None:
	    name = '<%d>'%self.node_index
	tag = node.tag
	if tag == 'macro':
	    return MacroSubject(self, node, name)
	elif tag == 'document':
	    return DocumentSubject(self, node, name)
	else:
	    return Subject(self, node, name)

    def new_tag_node(self, tag, node):
	return self.mod.SpecNodes.node_of_taci(tag, '', node.children, node.index)

    def no_children(self, node):
	if node.children:
	    self.error('No children expected for node with tag %r'%node.tag,
		       node,
		       exception=None)

    def visit_and(self, node):
	for name in self.get_arglist(node, min=1):
	    ofsubject = self.find_subject(name, node)
	    ofsubject._visit_aspect(node, 'and')
	    
    def visit_aspects_of(self, node):
	for name in self.get_arglist(node, min=1):
	    ofsubject = self.find_subject(name, node)
	    ofsubject._visit_aspect(node, 'aspect')

    def visit_arg(self, node, must_have_name=False):
	arg = node.arg.strip()
	arg_name = None
	kind = None
	if arg:
	    if ':' in arg:
		nk = arg.split(':')
		if len(nk) > 2:
		    self.error('More than 1 colon in argument.', node)
		name, kind_name = [x.strip() for x in nk]
		if kind_name:
		    kind = self.find_subject(kind_name, node)
		if name:
		    arg_name = name
	    else:
		# Is there an obvious default ?
		# For KeyArg, yes, the name is always.
		# let's say it's the name
		arg_name = arg

	subject = self.new_subject(node)
	if arg_name:
	    subject.specified_name = arg_name
	self.add_subject(subject)

	if must_have_name and subject.specified_name is None:
	    self.error('No argument name specified.', node)

	if kind is not None:
	    subject.args = [kind]

    def visit_comment(self, node):
	pass

    def visit_condition(self, node):
	names = self.get_arglist(node, min=1)
	for name in names:
	    self.add_new_subject(node, 'cond:%s'%name)

    def visit_default(self, node):
	description_class = self.mod.get_description_class(node.tag)
	arg = node.arg.strip()
	colon = arg.startswith(':')
	if (description_class.d_type == 'definition') != colon:
	    if colon:
		msg = 'Tag %r is not a definition, should not have ::'%node.tag
	    else:
		msg = 'Tag %r is a definition, requires ::'%node.tag
	    self.error(msg, node, exception=None)

	getattr(self, '_visit_type_%s'%description_class.d_type)(node)

    def visit_description(self, node):
	self.def_new_subject(node)

    def visit_description_with_header(self, node):
	self.visit_description(node)

    def visit_example(self, node):
	subject = self.add_new_subject(node)
	partab = subject.description_class.partab
	ex = node.arg.strip()

	if '\n' in ex:
	    if not (partab.get(ex[:1]) == ex[-1:] or
		    partab.get(ex[:3]) == ex[-3:]):
		self.error('Multi-line expression should be in parentheses (for clarity).', node,
		       exception=None, harmless=1)
	    ex = '(%s)'%ex

	subject.ex_text = ex

    def visit_import(self, node):

	my_names = self.get_arglist(node, min=1)
	resolve_mode = None
	usings = None
	froms = []
	for ch in node.children:
	    t = ch.tag
	    if t == 'from':
		for name in self.get_arglist_only(ch):
		    froms.append((name, ch))
	    elif t == 'resolve_by':
		if resolve_mode:
		    self.error("More than 1 'resolve' clause.", ch.node, exception=None)
		else:
		    resolve_mode = ch.arg.strip()
		    if not resolve_mode in ('and', 'or'):
			self.error("Resolve by: and / or expected.",
				   ch,
				   exception=None)
			resolve_mode = 'and'
	    elif t == 'using':
		if usings is None:
		    usings = []
		for name in self.get_arglist_only(ch):
		    usings.append((name, ch))
	    else:
		self.error('Unexpected clause in import', ch, exception=None)
				   
	using_map = {}
	if usings is not None:
	    if len(usings) != len(my_names):
		if len(using_names) < len(my_names):
		    manyfew = 'few'
		else:
		    manyfew = 'many'
		self.error(
		    "Too %s 'using' names, should match number of names in .import"%manyfew,
		    using_node,
		    exception=None)
	    for m, u in zip(my_names, usings):
		# zip stops at the shortest list, ok
		using_map[m] = u

	if len(froms) == 0:
	    self.error("No 'from' clause", node)

	if len(froms) > 1:
	    if not resolve_mode:
		self.error("Importing from multiple packages but no 'resolve by' clause",
			   node, exception=None)
		resolve_mode = 'and'
	    
	for name in my_names:
	    subject = self.def_new_subject(node, name)
	    subject.imp_resolve_mode = resolve_mode
	    subject.imp_using_map = using_map
	    subject.imp_froms = froms

    def visit_key_arg(self, node):
	self.visit_arg(node, must_have_name=True)

    def visit_method(self, node):
	arg = node.arg.strip()
	if not arg.startswith(':'):
	    self.error("Tag 'method' is a definition, requires ::", node)
	self.mod.node_of_taci('attribute', arg,
			  (self.mod.node_of_taci('mapping', '', node.children),)).accept(self)

    def visit_name(self, node):
	if self.specified_name is not None:
	    self.error('Duplicate name specification.', node)
	name = node.arg.strip()
	if not name:
	    self.error('No name specification.', node)
	self.specified_name = name

    def visit_or(self, node):
	for name in self.get_arglist(node, min=1):
	    ofsubject = self.find_subject(name, node)
	    ofsubject._visit_aspect(node, 'or')
	    

    def visit_postcondition(self, node):
	arg = node.arg.strip()
	if not '(' in arg:
	    self.error('No left parenthesis', node)
	lpar = arg.index('(')
	rpar = arg.find(')')
	if rpar < lpar:
	    self.error('None or misplaced right parenthesis', node)

	n = arg[lpar+1:rpar].strip()
	if ',' in n:
	    n = [x.strip() for x in n.split(',')]
	else:
	    n = [n]
	arg_names = n

	cond_name = arg[:lpar].strip()
	if not cond_name:
	    self.error('No condition name', node)
	is_not = 0
	if cond_name.startswith('not '):
	    cond_name = cond_name[4:].strip()
	    is_not = 1


	parts = cond_name.split('.')
	if not parts[-1].startswith('cond:'):
	    parts[-1] = 'cond:'+parts[-1]
	    cond_name = '.'.join(parts)

	cond_def = self.find_subject(cond_name, node)
	subject = self.add_new_subject(node)
	subject.cond_definition = cond_def
	subject.cond_name = cond_name
	subject.arg_names = arg_names
	subject.is_not = is_not

    def visit_precondition(self, node):
	self.visit_postcondition(node)



class ErrorSubject(Subject):
    pass

class PackageSubject(Subject):
    def __init__(self, mod, specenv, node, name, filename):
	self.mod = mod
	self.specenv = specenv
	self.pac = self
	self.filename = filename
	#name = 'package_%s'%(name,)
	name = '%s'%(name,)
	Subject.__init__(self, self, node, name)
	self.lastname = name.split('.')[-1]
	self.tag = 'package'
	self.description_class = Package
	
	self.documents = []
	for s in mod.predefined_subjects:
	    s = s(self)
	    self.subjects[s.fullname] = s

	self._visit_children(node)
	del self.specenv # It was used only for error report

    def error(self, msg, node=None, exception=ReportedError, **kwds):
	return self.specenv.error(msg, node, exception, **kwds)

    def find_subject(self, name, node, context=None):
	if not name:
	    self.error('Invalid subject name: %r'%name, node)

	parts = [x.strip() for x in name.split('.')]
	if not parts[0]:
	    tag = parts[1]
	    parts = parts[2:]
	else:
	    tag = 'myfile'
	    
	if tag == 'myfile':
	    s = self
	elif tag == 'mykind':
	    s = context
	    if s is not None:
		kind_tags = ('kind', 'and', 'import')
		while s.parent != self and s.tag not in kind_tags:
		    s = s.parent
		if s.tag not in kind_tags:
		    s = None
	    if s is None:
		self.error('mykind tag without such a context: %r'%name, node)
	else:
	    self.error('Invalid tag %r in %r'%(tag, name), node)

	sname = s.lastname
	for i, n in enumerate(parts):
	    ns = s.subjects.get(n)
	    if ns is None:
		if s.tag != 'import':
		    self.error('No such subject: %r  in %r.'%(n, sname), node)
		return SubImportSubject(s, node, parts[i:])
	    sname = sname + '.' + n
	    s = ns
	return s

class SubImportSubject:
    def __init__(self, parent, node, rnparts):
	self.parent = parent
	self.node = node
	self.rnparts= rnparts
	self.fullname = '.'.join([parent.fullname]+rnparts)
	self.lastname = rnparts[-1]

class MacroSubject(Subject):
    def add_top_node(self):
	pass

class DocumentSubject(Subject):
    def add_top_node(self):
	self.parent.documents.append(self)

class GuppyWorld(Subject):
    def __init__(self, env):
	self.pac = env
	self.fullname = self.lastname = "Guppy_World"
	self.node = None
	self.tag = '<GuppyWorld>'
	self.aspects = []
	self.description_class = Description


	
class _GLUECLAMP_:
    _imports_ = (
	'_parent:Document',
	'_parent:FileIO',
	'_parent.FileIO:IO',
	'_parent:Filer',
	'_parent:Html',
	'_parent:Latex',
	'_parent:SpecNodes',
	'_parent.SpecNodes:node_of_taci',
	'_parent:Tester',
	'_root.md5:md5',
	'_root.guppy.etc:iterpermute',
	'_root.guppy.etc:RE',
	)

    _chgable_ = ('cover_check', 'io_dir', 'max_errors')

    description_classes = {
	'alt'		: Alt,
	'arg'		: Arg,
	'args'		: Args,
	'attribute'	: Attribute,
	'comment'	: Comment,
	'condition'	: Condition,
	'constructor'	: Constructor,
	'default'	: Default,
	'defines'  	: Defines,
	'delitem'	: DelItem,
	'description'	: DescriptionDescription,
	'description_with_header': DescriptionWithHeader,
	'equation'	: Equation,
	'example'	: Example,
	'either'	: Either,
	'draw'		: Draw,
	'function_operator' : FunctionOperator,
	'getitem'	: GetItem,
	'import'	: Import,
	'in_context'	: InContext,
	'inplace_operator': InplaceOperator,
	'key_arg'	: KeyArg,
	'kind'  	: Kind,
	'kind_of'	: KindOf,
	'macro'		: Macro,
	'mapping'	: Mapping,
	'no_arg'	: NoArg,
	'operator'	: Operator,
	'postcondition'	: Postcondition,
	'precondition'	: Precondition,
	'python_code'	: PythonCode,
	'reverse_operator'	: ReverseOperator,
	'optionals'	: Optionals,
	'package'	: Package,
	'repeat'	: Repeat,
	'returns'	: Returns,
	'self'		: Self,
	'seq'		: Seq,		
	'setitem'	: SetItem,
	'subkind_of'	: SubkindOf,
	'superkind'	: Superkind,
	'superkind_of'	: SuperkindOf,
	}
	

    tgt_prefix = '.tgt.'

    cover_check = None
    io_dir = None
    max_errors = 10

    def get_description_class(self, tag):
	return self.description_classes.get(tag, Description)

    def _get_predefined_subjects(self):
	return (GuppyWorld,)

    def _get_package_cache(self):
	return {}

    def main(self, filename, **kwds):
	se = SpecEnv(self)
	se.process_main(filename, **kwds)

    def _test_main_(self):
	pass

    def set_input_dir(self, dir):
	dir = self.IO.path.abspath(dir)
	self.input_dir = dir


if 0 or __name__=='__main__':
    from guppy import Root
    Root().guppy.gsl.Main._test_main_()
