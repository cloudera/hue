#._cv_part guppy.gsl.Document

class Document:
    def __init__(self, mod, node, env):
	self.mod = mod
	self.env = env

	self.kindbrackets = mod.kindbrackets
	self.eitherbrackets = mod.eitherbrackets
	self.anykind = mod.anykind

	self.out = []
	self.localstack = []
	self.outstack = []
	self.output_directives = []
	self.document_title = None
	self.specified_definitions = None
	self.macro_args = None
	self.subdoc = None
	self.in_in = 0
	self.macro_stack = []

	node.accept(self)

	self.result = self.node_of_taci('string', '', self.out, 0)
	self.doc_name_node = self.node_of_taci('text', self.get_doc_name())

    def _visit_children(self, node):
	E = self.mod.ReportedError
	for ch in node.children:
	    try:
		ch.accept(self)
	    except E:
		pass

    def _visit_subjects(self, subjects):
	for s in subjects:
	    self.out.append(self.node_of_taci('symbol', s.tgtfullname))

    def _visit_gets(self, node, what):
	self._visit_subjects(getattr(self.get_arg_subject(node), 'get_%s'%what)())
	
    def ap_text(self, text):
	self.out.append(self.node_of_taci('text', text, (), 0))

    def close(self, chktag = None, n=1, chk = None, get=False):
	for i in range(n):
	    out, tag, arg = self.outstack.pop()
	    node = self.node_of_taci(tag, arg, self.out)
	    if not get:
		out.append(node)
	    self.out = out
	    if chk is not None:
		assert chk is out
	if chktag is not None:
	    assert chktag == tag
	return node

    def error(self, msg, context=None, **kwds):
	msg = 'Document: ' + msg
	more = [('Macro call site.', ms[0]) for ms in self.macro_stack]
	more.reverse()

	self.env.error(msg, context, more=more, **kwds)

    def error_no_sub_element(self, node, subelement):
	self.error('No such subelement allowed in the enclosing element %r.'%
		   node.tag, subelement, exception=None)

    def expand_arg(self, arg):
	i = len(self.localstack) - 1
	while i >= 0:
	    argnode = self.localstack[i].get(arg)
	    if argnode is not None:
		assert argnode.tag == 'symbol'
		return argnode.arg.strip()
	    i -= 1
	return arg

    def expand_list(self, li):
	oldout = self.out
	self.out = newout = []
	for node in li:
	    node.accept(self)
	self.out = oldout
	return newout

	
    def expand_node(self, node, optarg=0, optmore=0):
	arg, rest = self.get_arg_rest(node, optarg=optarg, optmore=optmore,nostrip=1)
	return self.node_of_taci(node.tag, arg, rest, node.index, node.src)
	

    def gen_char(self, char):
	self.gen_tag('char', char)

    def gen_document_header(self):
	self.open('document_header')
	self.close()

    def gen_document_trailer(self):
	self.open('document_trailer')
	self.close()

    def gen_link_to(self, s, text=None, children=()):
	if text is not None:
	    children = list(children)
	    children.append(self.node_of_taci('text', text))
	ln = self.get_link_name(s)
	self.gen_tag('link_to', ln, children)

    def gen_localname(self, s):
	self.gen_link_to(s, s.get_local_name())

    def gen_symbol(self, arg):
	self.out.append(self.node_of_taci('symbol', arg))

    def gen_tag(self, tag, arg = '', children=()):
	self.out.append(self.node_of_taci(tag, arg, children))
    
    def gen_text(self, text):
	self.gen_tag('text', text)

    def get_arg_only(self, node):
	arg, rest = self.get_arg_rest(node)
	if rest:
	    self.error('Node has extra children, only 1 arg or child expected')
	return arg

    def get_arg_rest(self, node, optarg=0, optmore=0,nostrip=0):
	arg, rest = node.get_arg_rest(nostrip=nostrip)
	rest = self.expand_list(rest)
	if arg:
	    arg = self.expand_arg(arg)
	else:
	    if not (rest and rest[0].tag == 'symbol'):
		if not optarg:
		    self.error('Argument on line or as next children expected.', node)
	    else:
		arg = rest[0].arg.strip()
		rest = rest[1:]
	if rest and rest[0].tag == 'symbol':
	    if not optmore:
		self.error('More arguments than expected.', rest[0])
	return arg, rest

    def get_arg_subject(self, node):
	arg = self.get_arg_only(node)
	return self.get_subject(arg, node)

    def get_arg_subjects_rest(self, node):
	args, rest = self.get_arglist_rest(node)
	return [self.get_subject(a, node) for a in args], rest

    def get_arglist_only(self, node):
	args, rest = self.get_arglist_rest(node)
	if rest:
	    self.error_no_sub_element(node, rest[0])
	return args

    def get_arglist_rest(self, node):
	args = []
	for arg in node.get_arglist():
	    if not arg:
		self.error("Empty argument in arg list", node)
	    arg = self.expand_arg(arg)
	    args.append(arg)
	rest = []
	for a in self.expand_list(node.children) :
	    if a.tag == 'symbol':
		if rest:
		    self.error(
			'Argument elements must be first in subelements.',
			a,
			exception=None)
		args.append(a.arg.strip())
	    else:
		rest.append(a)
	return args, rest

    def get_cur_subject(self, node):
	sd = self.subdoc
	if not sd:
	    self.error('No subject defined in current environment.', node)
	return sd.subject

    def get_doc_name(self):
	return self.document_name

    def get_filers(self, output_dir):
	if not self.output_directives:
	    print 'Document %r: No output directives'%self.name
	filers = []
	r = self.get_result()
	name = self.get_doc_name()
	#print 'directives', self.output_directives
	for (handler, opts) in self.output_directives:
	    print 'processing', handler, opts, name
	    filers.append(handler.doc2filer(self, r, name, output_dir, opts, self.mod.IO))
	return filers
			 
    def get_link_name(self, a):
	return a.get_link_name()

    def get_macro_args(self, node):
	args = self.macro_args
	if args is None:
	    self.error('Is not in macro', node)
	return args

    def get_result(self):
	return self.result

    def get_subject(self, name, node=None):
	return self.env.get_descr_by_name(name, node)

    def node_of_taci(self, *args):
	return self.mod.node_of_taci(*args)

    def open(self, tag, arg=''):
	self.outstack.append((self.out, tag, arg))
	self.out = []
	return self.out

    def subdoc_do(self, m, f):
	sd = SubDoc(self, m)
	osd = self.subdoc
	self.subdoc = sd
	sd.subdoc = sd
	try:
	    f(sd)
	finally:
	    self.subdoc = osd

    def visit_args(self, node):
	if self.macro_args is None:
	    self.error('Not in macro', node)
	else:
	    names = self.get_arglist_only(node)
	    if len(names) != len(self.macro_args):
		self.error('%d args passed, here is %d names'%(len(self.macro_args),len(names)),
			   node)
	    self.localstack.append( dict([(x.strip(), self.macro_args[i])
					  for i, x in enumerate( names )]) )

    def visit_arguments_of(self, node):
	self._visit_gets(node, 'arguments')

    def visit_attr_name_of(self, node):
	self.gen_symbol(self.get_arg_subject(node).get_attr_name())

    def visit_attributes_of(self, node):
	self._visit_gets(node, 'attributes')

    def visit_block(self, node):
	self.out.append(self.expand_node(node, optarg=1))

    def visit_default(self, node):
	self.out.append(self.expand_node(node, optarg=1, optmore=1))

    def visit_define(self, node):
	arg, rest = self.get_arg_rest(node)

	arg = self.get_link_name(self.get_subject(arg, node))
	self.out.append(self.node_of_taci(node.tag, arg, rest, node.index, node.src))
	
    def visit_defines(self, node):
	sd = self.specified_definitions
	if sd is None:
	    sd = self.specified_definitions = []
	sd.extend(self.get_arglist_only(node))

    def visit_description_of(self, node):
	self.get_arg_subject(node).gen_description_doc(self)

    def visit_document(self, node):
	self.document_name = node.arg.strip()
	self.open('document')
	self._visit_children(node)
	if self.document_title is None:
	    self.open('document_title')
	    self.gen_text('GSL document %s'%self.document_name)
	    self.close()
	self.close()

    def visit_document_title(self, node):
	self.document_title = node
	self.out.append(self.document_title)

    def visit_for(self, node):
	varname = node.get_namearg()
	
	if not node.children:
	    self.error('For loop without subelements.', node)

	if not (node.children[0].tag == 'in'):
	    self.error("First subelement of for loop must be 'in'.", node.children[0])
	inode = node.children[0]

	names = self.get_arglist_only(inode)

	body = node.children[1:]
	if not body:
	    self.error('For loop without body.', node)
	for name in names:
	    self.localstack.append({
		varname: self.node_of_taci(
		    'symbol', 
		    name, (), node.index)})
	    try:
		for ch in body:
		    ch.accept(self)
	    finally:
		self.localstack.pop()

    def visit_gsml(self, node):
	arg, rest = node.get_arg_rest()
	if arg:
	    rest = [self.mod.node_of_taci('text', arg, (), node.index, node.src)]+list(rest)
	self.open('block')
	for a in rest:
	    if a.tag == 'text':
		a = self.mod.node_of_gsml(a.arg.strip())
	    a.accept(self)
	self.close()

    def visit_id_of(self, node):
	self.ap_text(self.get_arg_subject(node).get_id_name())

    def visit_in(self, node):
	assert 0
	set_trace()
	self.in_in += 1
	self.visit_default(node)
	self.in_in -= 1

    def visit_kind_of(self, node):
	self.gen_symbol(self.get_arg_subject(node).get_kind_name())

    def visit_label(self, node):
	subject = self.get_cur_subject(node)
	arg, rest = self.get_arg_rest(node)
	name = subject.get_link_name() + '.label:'+arg
	self.open('define', name)
	self.close()
	for r in rest:
	    self.out.append(r)
	
    def visit_link_to(self, node):
	arg, rest = self.get_arg_rest(node)
	self.gen_link_to(self.get_subject(arg, node), children=rest)

    def visit_man_page_of(self, node):
	self.open('to_document_only')
	self.open('man_page_mode')
	subjects, rest = self.get_arg_subjects_rest(node)
	if rest:
	    self.error_no_sub_element(node, rest[0])
	for subject in subjects:
	    self.subdoc_do(subject, lambda sd:sd.gen_man_page(subject))
	    
	self.close()
	self.close()

    def visit_mappings_of(self, node):
	self._visit_gets(node, 'mappings')

    def visit_meta(self, node):
	arg = node.arg.strip()
	if arg:
	    colon = arg.find(':')
	    if colon <= 0:
		self.error('Argument to meta, if any,  must be of the form <name>:<content>.',
			   node)
	    name = arg[:colon].strip()
	    content = arg[colon+1:].strip()
	    mknode = self.mod.node_of_taci
	    ch = (mknode('name', name), mknode('content', content) ) + node.children
	    node = mknode('meta', '', ch)
	self.out.append(node)

    def visit_name_of(self, node):
	self.gen_text(self.get_arg_subject(node).get_name())

    def visit_output(self, node):
	mode, rest = self.get_arg_rest(node)
	modes = [x.strip() for x in mode.split(',')]
	for mode in modes:
	    try:
		handler_name = self.mod.output_handlers[mode.lower()]
	    except KeyError:
		self.error('Unknown output mode: %r. Expected one of %r.'%(
		    mode, self.mod.output_handlers.keys()),
			   node,
			   exception=None)
	    else:
		handler = getattr(self.mod, handler_name)
		self.output_directives.append((handler, rest))

    def visit_ref(self, node):
	self.gen_text(' ')
	subject = self.get_cur_subject(node)
	arg, rest = self.get_arg_rest(node)
	text = arg
	if arg.startswith('.'):
	    dl = arg.find('.', 1)
	    if dl < 0:
		dl = len(arg)
	    tag = arg[1:dl].strip()
	    name = arg[dl+1:].strip()
	else:
	    tag = 'myfile'
	    name = arg
	if tag == 'mykind':
	    idn = subject.get_link_name()
	    if name:
		idn = idn + '.' + name
		text = name
	    else:
		text = idn.split('.')[-1]
	elif tag == 'myfile':
	    idn = subject.get_link_name()
	    idn = '.'.join(idn.split('.')[:2])
	    if name:
		idn = idn + '.' + name
		text = name
	else:
	    self.error('Invalid tag: %r in reference.'%tag, node)

	if not rest:
	    rest = [self.node_of_taci('text', text)]
	self.out.append(self.node_of_taci(
	    'link_to', idn, rest, node.index))
	

    def visit_specified_definitions(self, node):
	if node.arg.strip() or node.children:
	    self.error('No argument or subelement allowed for element %r.'%node.tag, node,
		       exception=None)
	if self.specified_definitions is None:
	    self.error('No definitions have been specified.', node)
	for s in self.specified_definitions:
	    self.out.append(self.node_of_taci('symbol', s, (), node.index, node.src))


    def visit_symbol(self, node):
	arg = self.get_arg_only(node)
	if arg != node.arg.strip():
	    node = self.node_of_taci(node.tag, arg, (), node.index, node.src)
	self.out.append(node)

    def visit_synopsis_of(self, node):
	self.open('to_document_only')
	self.open('man_page_mode')
	m = self.get_arg_subject(node)
	self.subdoc_do(m, lambda sd: sd.gen_mapping_doc(m))
	self.close()
	self.close()

    def visit_test_of(self, node):
	args, rest = self.get_arg_subjects_rest(node)
	for kind in args:
	    self.open('to_tester_only')
	    self.out.append(self.node_of_taci(node.tag, kind, rest, node.index, node.src))
	    self.close()
	
    def visit_take_all(self, node):
	for a in self.get_macro_args(node):
	    self.out.append(a)

    def visit_take_first(self, node):
	args = self.get_macro_args(node)
	if not args:
	    self.error('No argument passed', node)
	self.out.append(args[0])

    def visit_take_rest(self, node):
        args = self.get_macro_args(node)
	if not args:
	    self.error('No argument passed', node)
	for ch in args[1:]:
	    self.out.append(ch)
	
    def visit_text(self, node):
	self.out.append(node)

    def visit_use(self, node):
	macrocolonarg, args = self.get_arg_rest(node)
	colonpos = macrocolonarg.find(':')
	if colonpos <= 0:
	    macroname = macrocolonarg
	else:
	    macroname = macrocolonarg[:colonpos].strip()
	    macroarg = macrocolonarg[colonpos+1:].strip()
	    if not macroarg:
		self.error('Argument must be of form <macroname> or <macroname>:<macroarg>.',
			   node)
	    macroarg = self.expand_arg(macroarg)
	    args = [self.node_of_taci('symbol', macroarg)] + args
	macro = self.get_subject(macroname, node)

	o = (self.localstack, self.macro_args)
	try:
	    self.macro_stack.append([node])
	    self.localstack = []
	    self.macro_args = args
	    self._visit_children(macro.use(args))
	finally:
	    (self.localstack, self.macro_args) = o
	    self.macro_stack.pop()


class Attributes:
    d_tag = 'attributes'
    def __init__(self, as_):
	self.as_ = as_

    def find_kind_aspects(self):
	return self.as_[0].find_kind_aspects()
    
    def get_link_name(self):
	return self.as_[0].mod.tgt_prefix+'(%s)'%','.join([x.get_link_name() for x in self.as_])

    def get_name(self):
	return ', '.join([x.get_name() for x in self.as_])

    def get_kind(self):
	return self.as_[0].get_kind()

    def get_self_name(self):
	return self.as_[0].get_self_name()

    def find_aspects(self, tag):
	return self.as_[0].find_aspects(tag)
	
    def is_method(self):
	self.as_[0].is_method()


class SubDoc(Document):
    def __init__(self, parent, subject):
	self.__dict__.update(parent.__dict__)
	self.parent = parent
	self.subject = subject
	self.level = 0
	self.no_ret = 0
	self.use_self = None
    
    def combine_attrs_of_same_kind(self, kas):
	if len(kas) <= 1:
	    return kas
	nkas = []
	attrs = []
	for ka in kas:
	    t = ka.d_tag
	    if t != 'attribute':
		nkas.append(ka)
		continue
	    for (i, as_) in attrs:
		a = as_[0]
		if (a.src.node is ka.src.node
		    and len(a.aspects) == len(ka.aspects)):
		    as_.append(ka)
		    break
	    else:
		attrs.append((len(nkas), [ka]))
		nkas.append(ka)
	for (i, as_) in attrs:
	    if len(as_) > 1:
		nkas[i] = Attributes(as_)
	return nkas


    def combine_attrs_of_same_kind_and_description(self, kas):
	return self.combine_attrs_of_same_kind(kas)

    def gen_anything(self):
	self.open('strong')
	self.gen_text(' ' + self.anykind)
	self.close()

    def gen_argref(self, a):
	# a : kind
	# a = kind
	t = a.d_tag
	if t == 'arg':
	    self.gen_posarg_name(a)
	    self.gen_colon()
	elif t == 'key_arg':
	    self.gen_keyarg_name(a)
	    self.gen_assign()
	else:
	    assert 0
	self.gen_ref(a.get_kind())

    def gen_arguments(self, args):
	def flatten(args):
	    f = []
	    for a in args:
		if a.d_tag in ('args', 'seq'):
		    f.extend(flatten(a.find_arg_aspects()))
		else:
		    f.append(a)
	    return f

	def gen_sycomma():
	    if sycomma:
		self.gen_text(sycomma[0])
	    sycomma[:] = [', ']

	def clr_sycomma():
	    sycomma[:] = []

	def gen_lbracket(b):
	    if sycomma:
		self.gen_text(' ')
	    self.gen_text(b)
	    clr_sycomma()
	    
	def gen_rbracket(b):
	    self.gen_text(b)
	    sycomma[:] = [' ']

	def gen_su(text, sup='sup'):
	    self.open(sup)
	    self.open('strong')
	    self.gen_text(text)
	    self.close()
	    self.close()

	def gen_taggy(tag, args, func, brackets='[]'):
	    su = 'sup'
	    colon = ':'
	    if tag:
		self.gen_text(' ')
		gen_su(tag+colon, su)
		sycomma[:]=[]
	    if len(args) != 1:
		gen_lbracket(brackets[0])
		func(args)
		gen_rbracket(brackets[1])
	    else:
		clr_sycomma()
		func(args)


	def gen_or(asp, sep,
		   orparneed = False,	# Set to True if sequences needs parentheses between or
		   sup=1
		   ):

	    if asp:
		if len(asp) == 1:
		    gen_arg(asp[0])
		    return
		gen_arg(asp[0], parneed=orparneed)
		for ch in asp[1:]:
		    if sup:
			self.open('sup')
			self.open('strong')
		    if callable(sep):
			sep()
		    else:
			self.gen_text(sep)
		    if sup:
			self.close()
			self.close()
		    clr_sycomma()
		    gen_arg(ch, parneed=orparneed)



	def gen_arg(a, parneed = 0):
	    t = a.d_tag
	    if t in ('arg', 'key_arg'):
		gen_sycomma()
		self.gen_argref(a)
	    elif t == 'alt':
		args = a.find_arg_aspects()
		gen_taggy('alt', args, lambda args: gen_or(args, ' or '))
	    elif t == 'no_arg':
		self.gen_text('[]')
	    elif t == 'draw':
		args = a.find_arg_aspects()
		if len(args) <= 1:
		    gen_lbracket(' [')
		    gen_arg(args[0])
		    gen_rbracket(']')
		else:
		    gen_taggy('draw', args, lambda args: gen_or(args, ' , ', sup=0))
	    elif t == 'optionals':
		args = a.find_arg_aspects()
		for s in args:
		    gen_lbracket(' [')
		    gen_arg(s)
		gen_rbracket(']'*len(args))
		    
	    elif t == 'superkind':
		gen_sycomma()
		self.gen_localname(a)
	    elif t in ('seq', ):
		args = a.find_arg_aspects()
		gen_taggy('seq', args, lambda args: gen_or(args, ' , ', sup=0))
	    elif t in ('args', 'seq'):
		gen_args(a.find_arg_aspects(), parneed)
	    elif t == 'repeat':
		gen_taggy(a.get_arg(), a.find_arg_aspects(), gen_args)
		    
	    else:
		assert 0
		    

	def gen_args(args, parneed=0):
	    args = flatten(args)
	    def ga(args):
		for a in args:
		    gen_arg(a)
	    if parneed and len(args) > 1:
		#gen_taggy('', args, ga, brackets='<>')
		gen_taggy('1', args, ga)
	    else:
		ga(args)
	sycomma = []
	gen_args(args)
		
    def gen_assign(self):
	self.open('strong')
	self.gen_char('nbsp')
	self.gen_text('=')
	self.gen_char('nbsp')
	self.close()

    def gen_attribute_def(self, a):
	def gen_dt(do_kind = 0):
	    if dt_done:
		return
	    dt_done.append(1)
	    self.open('dd')
	    if not define_done:
		link_name = self.get_link_name(a)
		self.open('define', link_name)
	    if s:
		self.out.append(s)
	    if s:
		self.open('code')
		self.gen_text('.')
		self.close()
	    self.open('strong')
	    self.open('big')
	    self.gen_attribute_name(a)
	    self.close()
	    self.close()
	    if not define_done:
		self.close()
		define_done.append(1)
	    
	    if do_kind or not kas:
		if len(kas) == 1 and kas[0].d_tag == 'mapping':
		    self.gen_mapping_kind(kas[0], 1)
                    self.open('dl')
		    self.gen_mapping_description(kas[0])
                    self.close()
		else:
		    self.gen_colon()
		    self.gen_def(a.get_kind())
		kind_done.append(1)
	    self.close('dd')


	def gen_afterkind(a):
	    dt_done.pop()
	    gen_dt(1)
	    kind_done.append(1)

	define_done = []
	dt_done = []
	kind_done = []
	kas = a.find_kind_aspects()
	s = self.get_self_node(a)

	self.level += 1
	for d in a.find_aspects('*'):
	    t = d.d_tag
	    if t == 'description':
		gen_dt(0)
                self.open('dd')
                self.open('dl')
		self.gen_description_def(d)
                self.close()
                self.close()
		continue
	    if d in kas:
		if dt_done or kind_done:
		    pass
		if not dt_done:
		    gen_dt(do_kind = 1)
		elif not kind_done:
		    gen_afterkind(a)
	    elif t == 'self':
		pass
	    else:
		assert 0

	if not dt_done:
	    gen_dt(do_kind = 1)
	self.level -= 1

    def gen_attribute_name(self, a):
	self.gen_name(a)

    def gen_attribute_ref(self, a):

	s = self.get_self_node(a)
	if s:
	    self.out.append(s)
	self.open('big')
	if s:
	    self.open('code')
	    self.gen_text('.')
	    self.close()

	link_name = self.get_link_name(a)
	self.open('link_to', link_name)
	self.gen_attribute_name(a)
	self.close()
	self.close()

	kas = a.find_kind_aspects()

	if len(kas) == 1 and kas[0].d_tag == 'mapping':
	    self.gen_mapping_kind(kas[0])
	else:
	    self.gen_colon()
	    self.gen_ref(a.get_kind())

    def gen_attributes_def(self, a):
	self.gen_attribute_def(a)

    def gen_attributes_ref(self, a):
	self.gen_attribute_ref(a)

    def gen_colon(self):
	self.open('spc_colonkind')
	self.close()

    def gen_comment_def(self, d):
	pass

    def gen_comment_ref(self, d):
	pass

    def gen_condition_def(self, cond):
	self.open('dt')
	self.gen_condition_ref(cond, 1)
	self.close()
	self.level += 1

	for d in cond.find_aspects('*'):
	    t = d.d_tag
	    if t== 'description':
		self.gen_description_dd(d)
	    elif t == 'python_code':
		self.open('dd')
		self.open('dl')
		self.open('dt')
		self.open('strong')
		self.gen_text('Python code: ')
		self.close()
		self.open('code')
		self.gen_text(d.src.node.arg.strip())
		self.close()
		self.close()
		ctx = d.find_aspects('in context')
		if ctx:
		    self.open('dd')
		    self.open('dl')
		    for ct in ctx:
			self.open('dt')
			self.open('strong')
			self.gen_text('in context: ')
			self.close()
			self.open('code')
			self.gen_text(ct.src.node.arg.strip())
			self.close()
			self.close()
		    self.close()
		    self.close()
		self.close('dl')
		self.close('dd')

	self.level -= 1

    def gen_condition_ref(self, cond, define = 0):
	link_name = self.get_link_name(cond)
	if define:
	    self.open('define', link_name)
	else:
	    self.open('link_to', link_name)
	self.open('strong')
	self.open('big')
	self.gen_text(cond.get_def_name())
	self.close()
	self.close()
	self.close() # define

	self.gen_text('(')
	self.gen_text(', '.join(cond.get_arg_names()))
	self.gen_text(')')

	
    def gen_constructor_def(self, c):
	self.open('define', self.get_link_name(c))
	self.close()
	for cc in c.args:
	    self.open('dt')
	    self.gen_link_to(cc)
	    self.close()

	for d in c.find_aspects('description'):
	    self.gen_description_dd(d)

    def gen_constructor_ref(self, c):
	self.gen_self(c)
	self.gen_text(' = ')
	self.gen_ref(c.args[0])

    def gen_constructor_descriptions(self, li):
	self.gen_constructor_syn(li, 1)

    def gen_constructor_syn(self, li, desc=0):

	ccs = []
	descs = []
	cdccs = []
	for c in li:
	    ds = c.find_aspects('description') 
	    descs.extend( ds)
	    ccs.extend(c.args)
	    cdccs.append((c, ds, c.args))

	if desc and not descs:
	    return

	self.open('dt')
	if desc:
	    self.open('h2')
	else:
	    self.open('big')
	    self.open('strong')
	if descs:
	    if desc:
		self.open('define', li[0].get_link_name())
	    else:
		self.open('link_to', li[0].get_link_name())
	hd = 'Constructors'
	if len(ccs) == 1:
	    hd = hd.rstrip('s')
	self.gen_text(hd)
	if descs:
	    self.close()
		      
	self.close()
	if not desc:
	    self.close()
	self.close('dt')
	self.open('dd')
	self.open('dl')

	for c, ds, ccs in cdccs:
	    for cc in ccs:

		self.open('block')
		self.gen_ref(cc.env)
		conselfnode = self.close(get=1)

		self.open('dt')

		self.use_self = conselfnode
		self.gen_ref(cc)
		self.use_self = None

		self.close('dt')

	    if desc:
		for d in ds:
		    self.gen_description_dd(d)
	self.close('dl')
	self.close('dd')


    def gen_def(self, a):
	getattr(self, 'gen_%s_def'%a.d_tag)(a)
	
    def gen_delitem_def(self, op):
	self.open('dt')
	self.gen_delitem_ref(op, 1)
	self.close()
	self.gen_mapping_description(op)

    def gen_delitem_ref(self, op, subdescript=0):
	link_name = self.get_link_name(op)

	if subdescript:
	    self.open('define', link_name)
	    self.open('strong')
	    self.open('big')
	    self.gen_text('del ')
	    self.close()
	    self.close()
	    self.close()
	else:
	    self.open('link_to', link_name)
	    self.gen_text('del ')
	    self.close()

	self.gen_self(op)
	args = op.get_arguments()
	self.gen_text('[')
	self.gen_arguments(args)
	self.gen_text(']')
	
    def gen_description(self, k):
	ats = k.find_aspects('*')
	ats = self.combine_attrs_of_same_kind_and_description(ats)
	self.gen_descriptions(ats)

    def gen_description_dd(self, d):
	self.open('dd')
	d.gen_doc(self)
	self.close()

    def gen_description_def(self, d):
	self.gen_description_dd(d)

    def gen_description_descriptions(self, li):
	self.gen_outer_dt('Description')
	for d in li:
	    self.gen_description_dd(d)

    def gen_description_ref(self, d):
	pass
	
    def gen_description_syn(self, li):
	pass

    def gen_descriptions(self, ats, use_attr_header = 1):
	if not ats:
	    return
	tab = self.sortup_aspects(ats)

	for typ, li in tab:
	    try:
		try:
		    gen_desc = getattr(self, 'gen_%s_descriptions'%typ)
		except AttributeError:
		    hd = typ
		    if (len(li) > 1):
			hd = hd + 's'
		    hd = hd.capitalize().replace('_', ' ')
		    self.gen_outer_dt(hd)
		    for a in li:
			self.gen_def(a)
		else:
		    gen_desc(li)
	    except self.mod.ReportedError:
		pass


    def gen_either_def(self, k):
	self.gen_either_ref(k)

    def gen_either_ref(self, k):
	self.open('strong')
	self.open('sup')
	self.gen_text(' either:')
	self.close()
	self.close()
	self.gen_text(self.eitherbrackets[0])
	kas = k.get_alt_kinds()
	self.gen_ref(kas[0])
	for ka in kas[1:]:
	    self.open('strong')
	    self.open('sup')
	    self.gen_text(' or ')
	    self.close()
	    self.close()
	    self.gen_ref(ka)
	self.gen_text(self.eitherbrackets[1])

    def gen_example_descriptions(self, egs):
	e = 'Example'
	if len(egs) > 1:
	    e += 's'
	self.gen_outer_dt(e)
	for eg in egs:
	    self.open('dd')
	    self.open('pre')
	    ct = eg.get_ctx_text()
	    if ct:
		if not ct.endswith('\n'):
		    ct += '\n'
		self.gen_text(ct)
	    et = eg.get_ex_text()
	    self.open('strong')
	    self.gen_text('return ')
	    self.gen_text(eg.get_ex_text())
	    self.close()
	    self.close()
	    self.close()
	    continue



	    self.open('dd')
	    self.open('code')
	    self.gen_text(eg.get_ex_text())
	    ct = eg.get_ctx_text()
	    self.close()

	    if ct:
		self.open('em')
		self.gen_text(' # in context:')
		self.close()

	    self.close()
	    if ct:
		if '\n' in ct:
		    self.open('pre')
		    self.gen_text(ct)
		    self.close()
		else:
		    self.open('dd')
		    self.open('code')
		    self.gen_text(ct)
		    self.close()
		    self.close()

		return

		self.open('dd')
		self.open('dl')
		self.open('dt')
		self.open('strong')
		self.gen_text('In context')
		self.close()
		self.close()
		self.open('dd')
		if '\n' in ct:
		    self.open('pre')
		else:
		    self.open('code')
		self.gen_text(ct)
		self.close()
		self.close()
		self.close()
		self.close('dd')

    def gen_example_syn(self, eg):
	pass

    def gen_function_operator_def(self, op):
	self.open('dd')
	self.gen_function_operator_ref(op, 1)
        self.open('dl')
	self.gen_mapping_description(op)
	self.close()
	self.close()

    def gen_function_operator_ref(self, op, subdescript=0):
	link_name = self.get_link_name(op)

	if not subdescript:
	    self.open('link_to', link_name)
	else:
	    self.open('define', link_name)
	self.open('big')
	self.open('strong')
	self.gen_text(op.src.node.arg.strip())
	self.close()
	self.close()
	self.close()
	self.gen_text('(')
	self.gen_self(op)
	
	for a in op.get_arguments():
	    t = a.d_tag
	    if t == 'arg':
		self.gen_argref(a)
	    else:
		assert 0

	self.gen_text(')')

	self.gen_returns(op, subdescript)

    def gen_header(self, m):
	link_name = self.get_link_name(m)
	self.open('define', link_name)
	self.open('h1')
	self.gen_text(m.get_name())
	self.close()
	self.close()

    def gen_inplace_operator_def(self, op):
	self.gen_operator_def(op)

    def gen_inplace_operator_ref(self, op, subdescript=0):
	self.gen_operator_ref(op, subdescript)

    def gen_keyarg_name(self, a):
	self.open('code')
	self.gen_name(a)
	self.close()

    def gen_kind_aspects(self, ats, defi):
	if not ats:
	    self.gen_anything()
	    return
	self.gen_text(self.kindbrackets[0])
	self.open('dl')
	for a in ats:
	    if a.d_tag in ('kind',) and not a.is_synthetic:
		self.open('dd')
		self.open('em')
		self.gen_text('Subkind of: ')
		self.close()
		if defi:
		    self.gen_def(a)
		else:
		    self.gen_ref(a)
		self.close()
	    else:
		if defi:
                    self.open('dd')
		    self.gen_def(a)
                    self.close()
		else:
		    self.open('dd')
		    self.gen_ref(a)
		    self.close()
	self.open('dd')
	self.gen_text(self.kindbrackets[1])
	self.close()
	self.close()


    def gen_kind_def(self, k):
	kas = k.find_kind_aspects()
	self.gen_kind_refodef(k, 1)
	
    def gen_kind_of_def(self, k):
	self.gen_kind_of_ref(k)

    def gen_kind_of_ref(self, k):
	kas = k.find_kind_aspects()
	if len(kas) == 1:
	    self.gen_ref(kas[0])
	else:
	    assert 0 # to be tested

    def gen_kind_ref(self, k, defi=0):
	self.gen_kind_refodef(k, 0)

    def gen_kind_refodef(self, k, defi=0):
	if not k.is_synthetic:
	    self.gen_localname(k)
	    return

	kas = k.find_kind_aspects()
	kas = self.combine_attrs_of_same_kind(kas)
	self.gen_kind_aspects(kas, defi)

    def gen_man_page(self, m):
	self.gen_header(m)
	self.open('dl')
	self.gen_Name(m)
	self.gen_synopsis(m)
	self.gen_description(m)
	self.close()
	
    def gen_mapping_def(self, a):
	self.gen_mapping_tag(a, 1)
	self.gen_mapping_kind(a, 1, 1)

        self.open('dl')

	self.gen_mapping_description(a)

        self.close()

    def gen_mapping_description(self, m):
	def find_named_args(m):
	    na = []
	    asp = m.find_arg_aspects()
	    for a in asp:
		t = a.d_tag
		if t in ('arg', 'key_arg'):
		    na.append(a)
		else:
		    na.extend(find_named_args(a))
	    return na

	def gen_arguments_descriptions(m):
	    na = find_named_args(m)
	    if not na:
		return
	    namedesc = {}
	    ada = []
	    for a in na:
		t = a.d_tag
		if t in ('arg', 'key_arg'):
		    da = a.find_aspects('description')
		    ada.append((a, da))
		    if da:
			namedesc[(t, a.get_name())] = 1
		else:
		    assert 0

	    if namedesc:
		label = 'Argument'
		if len(namedesc) > 1:
		    label += 's'
		self.gen_outer_dt(label)
		self.open('dd')
		self.open('dl')
		for a, da in ada:
		    t = a.d_tag
		    if not da and (t, a.get_name()) in namedesc:
			# This arg is considered to be described elsewhere, Notes Aug 10 2005.
			# This is a bit sublte, may do for now...
			continue
		    self.open('dt')
		    self.gen_argref(a)
		    self.close()
		    for d in da:
			self.gen_description_dd(d)
		self.close()
		self.close('dd')

	def gen_condition_ref(a):
	    if a.is_not:
		self.gen_text('not ')

	    d = a.get_definition()

	    if d is None:
		self.gen_text(a.cond_doc_name)
	    else:
		self.open('link_to', self.get_link_name(d))
		self.gen_text(a.cond_doc_name)
		self.close()

	    if a.arg_names:
		self.gen_text('(')
		#self.open('var')
		comma = 0
		for an in a.arg_names:
		    if comma:
			self.gen_text(', ')
		    comma = 1
		    if an.startswith('<') and an.endswith('>'):
			self.open('em')
			self.gen_text(an[1:-1])
			self.close()
		    else:
			# I think it normally is clearer to not have
			# slanted argument names
			self.gen_text(an)
		#self.close()
		self.gen_text(')')

	def gen_condition_desc(a):
	    ds = a.find_aspects('description')
	    for d in ds:
		self.gen_description_dd(d)

	def gen_conditions_description(m, asp='precondition'):
	    self.open('dd')
	    self.open('dl')
	    pres = m.find_aspects(asp)
	    if pres:
		self.open('dt')
		self.open('strong')
		hd = asp.capitalize()
		if len(pres) > 1:
		    hd = hd + 's'
		self.gen_text(hd)
		self.close()
		self.close()
		self.open('dd')
		self.open('dl')
		for pre in pres:
		    self.open('dt')
		    gen_condition_ref(pre)
		    self.close()
		    gen_condition_desc(pre)
		self.close()
		self.close()
	    self.close()
	    self.close()

	def gen_description(m):
	    asp = m.find_aspects()
	    args_described = 0
	    pre_described = 0
	    post_described = 0
	    last_t = None
	    last_h = None
	    for a in asp:
		t = a.d_tag
		if t == 'description':
		    self.gen_description_dd(a)
		elif t == 'returns':
		    rds = a.find_aspects('description')
		    if rds:
			self.open('dd')
			self.open('dl')

			self.open('dt')
			self.open('strong')
			self.gen_text('Returns ')
			self.close()
			rds[0].gen_doc(self)
			rds = rds[1:]
			self.close('dt')

			for rd in rds:
			    self.gen_description_dd(rd)
			self.close('dl')
			self.close('dd')

		elif t in ('precondition', ):
		    if not pre_described:
			gen_conditions_description(m, t)
			pre_described = 1
		elif t in ('postcondition',):
		    if not post_described:
			gen_conditions_description(m, t)
			post_described = 1
			
		elif t in ('equation',):
		    self.open('dd')
		    self.open('dl')
		    self.open('dt')
		    self.open('strong')
		    self.gen_text('Equation')
		    self.close()
		    self.close()
		    self.open('dd')
		    self.open('dl')
		    eqconds_done = 0
		    for asp in a.find_aspects('*'):
			t = asp.d_tag
			if t == 'description':
			    self.gen_description_dd(asp)
			elif not eqconds_done:
			    eqconds_done = 1
			    self.open('dt')
			    cs = a.find_aspects('precondition', 'postcondition')
			    for cr in cs:
				if cr.d_tag == 'precondition':
				    self.open('strong')
				    self.open('sup')
				    self.gen_text('pre:')
				    self.close()
				    self.close()
				elif cr.d_tag == 'postcondition':
				    self.open('strong')
				    self.open('sup')
				    self.gen_text('post:')
				    self.close()
				    self.close()
				gen_condition_ref(cr)
				if cr is not cs[-1]:
				    self.open('big')
				    self.gen_text(' == ')
				    self.close()
			    self.close()
		    self.close()
		    self.close()
		    self.close()
		    self.close()

		    
		else:
		    if not args_described:
			self.open('dd')
			self.open('dl')
			gen_arguments_descriptions(m)
			args_described = 1
			self.close()
			self.close()
		    else:
			t = last_t
		last_t = t
		    

	self.level += 1
	gen_description(m)
	self.level -= 1

    def gen_getitem_def(self, op):
	self.open('dt')
	self.gen_getitem_ref(op, 1)
	self.close()
	self.gen_mapping_description(op)

    def gen_getitem_ref(self, op, subdescript=0):
	link_name = self.get_link_name(op)

	if subdescript:
	    self.open('define', link_name)

	if subdescript:
	    self.close()
	else:
	    self.open('link_to', link_name)
	    self.gen_text('# ')
	    self.close()

	self.gen_self(op)
	self.gen_index(op)
	self.gen_returns(op, subdescript)
	
    def gen_index(self, op):
	self.gen_text('[')
	self.gen_arguments(op.get_arguments())
	self.gen_text(']')

    def gen_link_to_operator(self, link_name):
        self.open('to_html_only')
        self.open('link_to', link_name)
        self.gen_text('# ')
        self.close()
        self.close()
        

    def gen_mapping_doc(self, m):
	def gen_synopsis(m):
	    self.gen_outer_dt('Synopsis')
	    self.open('dd')
	    self.gen_mapping_ref(m)
	    self.close()

	self.gen_header(m)
	self.open('dl')
	self.gen_Name(m)
	gen_synopsis(m)
	self.gen_mapping_description(m)
	self.close()

    def gen_mapping_kind(self, m, subdescript=0, withself=0):
	if withself and self.get_self_node(m):
	    self.gen_self(m)
	self.gen_text('(')
	self.gen_arguments(m.get_arguments())
	self.gen_text(')')
	self.gen_returns(m, subdescript)
	
    def gen_mapping_ref(self, m):
	self.gen_mapping_tag(m)
	self.gen_mapping_kind(m, 0, 1)

    def gen_mapping_tag(self, a, subdescript=0):
	link_name = self.get_link_name(a)
	if not subdescript:
	    self.open('link_to', link_name)
	else:
	    self.open('define', link_name)

	self.open('strong')
	self.gen_text('callable')
	self.close()
	self.close()
	self.gen_colon()
	
    def gen_Name(self, m):
	self.gen_outer_dt('Name')
	self.open('dd')
	self.open('h2')
	self.gen_text(m.get_Name())
	self.close()
	self.close()

    def gen_name(self, a):
	self.gen_text(a.get_name())

    def gen_operator_def(self, op):
	self.open('dd')
	self.gen_operator_ref(op, 1)
        self.open('dl')
	self.gen_mapping_description(op)
        self.close()
	self.close()

    def gen_operator_ref(self, op, subdescript=0):
	#self.gen_text('(')

	link_name = self.get_link_name(op)

	if subdescript:
	    self.open('define', link_name)

	if subdescript:
	    self.close()
	else:
            self.gen_link_to_operator(link_name)

	self.gen_self(op)
	self.gen_text(' ')
	self.open('big')
	self.open('strong')
	self.gen_text(op.src.node.arg.strip())
	self.close()
	self.close()
	
	for a in op.get_arguments():
	    self.gen_text(' ')
	    t = a.d_tag
	    if t == 'arg':
		self.gen_argref(a)
	    else:
		assert 0

	#self.gen_text(')')

	self.gen_returns(op, subdescript)

    def gen_outer_dt(self, text):
	# Synopsis, Description etc

	self.open('dt')
	if not self.level:
	    self.open('h2')
	else:
	    self.open('strong')
	    if self.level == 1:
		self.open('big')
	if callable(text):
	    text()
	else:
	    self.gen_text(text)
	if self.level == 1:
	    self.close('big')
	self.close()
	self.close()

    def gen_posarg_name(self, a):
	self.open('var')
	self.gen_name(a)
	self.close()

    def gen_ref(self, k):
	t = k.d_tag
	getattr(self, 'gen_%s_ref'%t)(k)

    def gen_returns(self, m, subdescript):
	if self.no_ret:
	    return
	ars = m.find_aspects('returns')
	if not ars:
	    return
	self.open('spc_mapsto')
	self.close()
	rk = m.get_return_kind()
	if subdescript:
	    t = rk.d_tag
	    if t in ('mapping',):
		self.gen_kind_aspects([rk], 1)
	    else:
		self.gen_def(rk)
	else:
	    self.gen_ref(rk)

    def gen_reverse_operator_def(self, op):
	self.open('dd')
	self.gen_reverse_operator_ref(op, 1)
        self.open('dl')
	self.gen_mapping_description(op)
	self.close()
	self.close()

    def gen_reverse_operator_ref(self, op, subdescript=0):
	#self.gen_text('(')

	link_name = self.get_link_name(op)

	if subdescript:
	    self.open('define', link_name)
            self.close()
	else:
            self.gen_link_to_operator(link_name)

	for a in op.get_arguments():
	    t = a.d_tag
	    if t == 'arg':
		self.gen_argref(a)
	    else:
		assert 0

	self.open('big')
	self.gen_text(' ')

	self.open('strong')
	self.gen_text(op.src.node.arg.strip())
	self.close()

	self.gen_text(' ')
	self.close()
	
	self.gen_self(op)

	#self.gen_text(')')

	self.gen_returns(op, subdescript)

    def gen_self(self, op):
	s = self.get_self_node(op)
	if not s:
	    self.open('em')
	    self.gen_text('self')
	    self.close()
	else:
	    self.out.append(s)

    def gen_self_def(self, k):
	pass

    def gen_self_descriptions(self, li):
	pass

    def gen_self_ref(self, k):
	self.open('h3')
	self.gen_text('For any object ')
	self.open('var')
	self.gen_text(k.src.node.arg.strip())
	self.close()
	self.gen_text(' of kind ')
	self.gen_localname(k.env)
	self.gen_text(':')
	self.close()

    def gen_self_syn(self, li):
	for k in li:
	    self.open('dt')
	    self.gen_self_ref(k)
	    self.close()

    def gen_setitem_def(self, op):
	self.open('dt')
	self.gen_setitem_ref(op, 1)
	self.close()
	self.gen_mapping_description(op)

    def gen_setitem_ref(self, op, subdescript=0):
	link_name = self.get_link_name(op)

	if subdescript:
	    self.open('define', link_name)

	if subdescript:
	    self.close()
	else:
            self.gen_link_to_operator(link_name)

	self.gen_self(op)
	args = op.get_arguments()
	self.gen_text('[')
	self.gen_arguments(args[:-1])
	self.gen_text(']')

	self.open('strong')
	self.open('big')
	self.gen_text(' = ')
	self.close()
	self.close()

	self.gen_arguments(args[-1:])
	
    def gen_subkind_of_def(self, k):
	ds = k.find_aspects('description')
	if not ds:
	    return
	self.open('dt')
	self.gen_subkind_of_ref(k, 1)
	self.close()
	self.level += 1
	for d in ds:
	    self.gen_description_dd(d)
	
	self.level -= 1

    def gen_subkind_of_descriptions(self, li):
	for a in li:
	    self.gen_outer_dt(lambda: self.gen_subkind_of_ref(a, 1))
	    for d in a.find_aspects('description'):
		self.gen_description_dd(d)

    def gen_subkind_of_ref(self, k, subdescript=0):
	link_name = self.get_link_name(k)
	if subdescript:
	    self.open('define', link_name)
	else:
	    self.open('link_to', link_name)
	self.gen_text('Subkind of')
	self.close()
	self.gen_colon()

	comma = 0
	for a in k.args:
	    if comma:
		self.gen_text(', ')
	    comma = 1
	    self.gen_localname(a)
	  
    def gen_subkind_of_syn(self, li):
	for a in li:
	    self.gen_outer_dt(lambda: self.gen_subkind_of_ref(a, 0))

    def gen_superkind_of_ref(self, k):
	kas = k.find_kind_aspects()
	if len(kas) == 1:
	    self.gen_ref(kas[0])
	else:
	    assert 0 # to be tested

    def gen_superkind_ref(self, k):
	self.gen_localname(k)

    def gen_synopsis(self, m):
	ats = m.find_aspects('*')
	ats = self.combine_attrs_of_same_kind(ats)
	tab = self.sortup_aspects(ats, synopsis=1)
	if tab:
	    self.gen_outer_dt('Synopsis')
	    self.open('dd')
	    self.open('dl')
	    self.level += 1
	    for typ, li in tab:
		try:
		    gen_syn = getattr(self, 'gen_%s_syn'%typ)
		except AttributeError:
		    name = typ.capitalize().replace('_', ' ')
		    if len(li) != 1:
			name = name+'s'
		    self.gen_outer_dt(name)
		    for a in li:
			self.open('dd')
			self.gen_ref(a)
			self.close()
		else:
		    gen_syn(li)

	    self.level -= 1
	    self.close()
	    self.close()
	    

    def get_self_node(self, a):
	sn = self.use_self
	if sn is None:
	    sn = a.get_self_name()
	    if sn is not None:
		sn = self.node_of_taci('text', sn)
	return sn


    def sortup_aspects(self, ats, synopsis=0):
	# Get aspects sorted up in the same order for synopsis and main description
    
	order = ('description', 'subkind_of', 'constructor', 'self', 'method',
		    'operator', 'mapping', 'attribute', 'condition', 'example', )
	tab = {}
	def gen_outer(what):
	    assert what in order
	    if what not in tab:
		tab[what] = []
	    tab[what].append(a)

	for a in ats:
	    t = a.d_tag
	    if t == 'comment' or t == 'description' and synopsis:
		pass
	    elif t in ('attribute', 'attributes', 'either'):
		if a.is_method():
		    gen_outer('method')
		else:
		    gen_outer('attribute')
	    elif a.d_type == 'operator' or t in ('getitem', 'delitem', 'setitem'):
		gen_outer('operator')
	    else:
		gen_outer(t)

	otab = []
	for typ in order:
	    if not typ in tab:
		continue
	    li = tab[typ]
	    otab.append((typ, li))
	return otab
			

class _GLUECLAMP_:
    _imports_ = (
	'_parent.FileIO:IO',
	'_parent.Gsml:node_of_gsml',
	'_parent:Html',
	'_parent:Latex',
	'_parent.Main:ReportedError',
	'_parent.SpecNodes:node_of_string',
	'_parent.SpecNodes:node_of_taci',
	'_parent.SpecNodes:node_aliases',
	'_parent:Tester',
        '_parent:XHTML'
	)

    # Map from output mode spelling in output directive to handler name
    # -- Why should we need to map anyway?
    # or should we just say they are case insensitive?
    # If they are case insenitive, we need to map here.
    # I hereby decide they are case insensitive!

    output_handlers = {'html': 'Html', 'xhtml': 'XHTML', 'latex': 'Latex', 'tester': 'Tester'}

    # Brackets to use when rendering kind references
    kindbrackets = ('[',']')
    #kindbrackets = ('{','\n}')
    kindbrackets = (' (',' )')
    #kindbrackets = '  '

    # Brackets to use when rendering either kinds

    eitherbrackets = '[]'

    # Text to use to render any kind
    anykind = 'anything'

    def document(self, node, env):
	return Document(self, node, env)

    def _test_main_(self):
	class TestSubject:
	    def __init__(self, mod, name):
		self.mod = mod
		self.name = name
		self.node_of_string = mod._parent.SpecNodes.node_of_string

	    def use(self, args):
		name = self.name
		if name == 'A':
		    return self.node_of_string("""\
.text: hello
""")

		elif name == 'reverse':
		    args.reverse()
		    return self.mod.node_of_taci('string', '', args, 0)
		else:
		    assert 0
		

	class TestEnv:
	    def __init__(self, mod):
		self.mod = mod
	    def get_subject(self, name):
		return TestSubject(self.mod, name)
		    

	env = TestEnv(self)
	x = """
.h1: Description of subject
..em
...use: A
.h1: Reversing arguments
.use: reverse
..text: A
..text: B
..text: C
"""
	node = self._parent.SpecNodes.node_of_string(x)
	y = self.document(node, env)
	r = y.get_result()
	print r
	h = self._parent.Html.doc2html(r)
	print h
	open('/tmp/d.html','w').write(h)



if 0 or __name__=='__main__':
    from guppy import Root
    Root().guppy.gsl.Document._test_main_()
