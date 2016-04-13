#._cv_part guppy.gsl.SpecNodes


##
# Specification entity object
#
# Collects information about a particular system entity or aspect.
#
# The entity is of a general kind
# It is defined by the particular aspects defined for it
# The aspects must be 'compatible', which can be relatively checked.
# The specobject is used for:
# * generating tests
# * generating docs
# * generating help
#   * by creating docstrings
#   * by providing interactive help
#
# For test generation, it will delegate to test implementators.
# For doc generation, it will delegate to doc implementators.
#
# The functionality needed here is therefore limited.
#
#  name
#  aspects
#
# There is one predefine root
# - should we call it Universe? 
#
# The name can be full, a dotted name, or the short, last part.
# 
# The name is treated as an aspect.
#
# Each aspect definition has a primary kind

# Aspect kinds


from guppy.gsl.Exceptions import *


class SpecObject:
    def __init__(self, mod):
	self.mod = mod
    
##
# Specification environment
# Collects specifications from several files
# Maps names to specification objects 

class SpecEnv:
    def __init__(self, mod):
	self.mod = mod
	self.unknown_nodes = []
	self.files = []

    def visit_default(self, node):
	print 'add_unknown', node.tag
	self.unknown_nodes.append(node)

    def visit_file(self, node):
	print 'visit_file'
	file = FileEnv(self, node)
	self.files.append(file)

    def get_predefined_subjects(self, env):
	return (GuppyWorld(env),)


class FileEnv:
    def __init__(self, env, node):
	mod = env.mod
	self.mod = mod
	self.name = self.filename = node.arg
	self.subjects = {}
	for s in env.get_predefined_subjects(self):
	    self.subjects[s.name] = s

	file = Subject(self, node, self.name)

	node.children_accept(file)


    def visit_aspects_of(self, node):
	name = node.arg
	subject = self.find_subject(node, name)
	subject.add_aspects(node)

    def def_subject(self, node, name, subject):
	if name in self.subjects:
	    self.error_node(node, 'Redefinition of %r.'%name)
	    self.error_node(self.subjects[name].node, 'Previous definition of %r.'%name)
	else:
	    self.subjects[name] = subject

    def error_node(self, node, msg, exception=None):
	index = node.index
	lineno = index + 1
	if 0:
	    print '%s:%d: %s,'%(self.filename, lineno, msg)
	    print 'in line %r.'%self.get_line(index)
	else:
	    print '%s:%s:'% (self.filename, lineno)
	    print '    %r'%self.get_line(index)
	    print '    %s'%msg
	    print

    def find_subject(self, node, name):
	subject = self.subjects.get(name)
	if subject is None:
	    self.error_node(node, 'No such subject: %r.'%name)
	return subject

    def get_line(self, index):
	try:
	    text = list(open(self.filename).readlines())[index].rstrip()
	except:
	    text = None
	return text

    def get_subject(self, name):
	subject = self.subjects.get(name)
	if subject is None:
	    subject = self.subjects[name] = Subject(self, name)
	return subject
	
    def get_aspect_subject(self, env, node):
	name = env.name+'::'+node.tag
	return self.get_subject(name)

class Subject:
    def __init__(self, file, node, name):
	self.file = file
	self.node = node
	self.name = name
	self.aspects = []


    def visit_default(self, node):
	of = node.tag.endswith('_of')
	name = node.arg
	define = name.startswith(':')
	if define:
	    if of:

		self.file.error_node(node, "Both 'of' and '::'.")
	    name = name[1:].strip()
	if of:
	    ofsubject = self.file.find_subject(node, name)
	    subject = self.new_subject_of(node, ofsubject)
	else:
	    subject = Subject(self.file, node, name)
	    if define:
		self.file.def_subject(node, name, subject)
	self.aspects.append(subject)
	node.children_accept(subject)
	    
    def new_subject_of(self, node, of):
	tag = node.tag
	if tag == 'aspects_of':
	    return AspectsOf(self.file, node, of)
	else:
	    return SubjectOf(self.file, node, of)

class AspectsOf(Subject):
    def __init__(self, file, node, of):
	self.node = node
	self.of = of
	self.aspects = []
    
    def visit_default(self, node):
	self.of.visit_default(node)

class SubjectOf(Subject):
    def __init__(self, file, node, of):
	self.node = node
	self.of = of
	self.aspects = []
    

class GuppyWorld(Subject):
    def __init__(self, env):
	self.file = env
	self.name = "Guppy World"
	self.node = None
	self.aspects = []


	

##
# A node represented with argument splitted in components of the form:
# .tag: arg
# text
# ..child
# ...
# ..child
# ...
#
# @param tag the text of the first line before the colon
# @param arg the text of the first line after the colon (stripped)
# @param text the text after the the first line before the first children
# @param children the child nodes
# @param index line index
# @param src describes the source

class SpecNode(object):
    __slots__ = 'tag', 'arg', 'children', 'index', 'src'
    def __init__(self, tag, arg, children=(), index=0, src=None):
	self.tag = tag
	self.arg = arg
	self.children = tuple(children)
	self.index = index
	self.src = src
	
    def __repr__(self):
	return '%s(%r,%r,%r)'%(
	    self.__class__.__name__, self.tag, self.arg, self.children)

    def __str__(self):
	return '%s(%r,%r,%s)'%(
	    self.__class__.__name__, self.tag, self.arg,
	    '(%s)'%(','.join([str(c) for c in self.children])))

    def arg_accept(self, visitor, prefix='visit_'):
	if self.arg:
	    node = SpecNode('text', self.arg, (), self.index)
	    node.accept(visitor, prefix)
	self.children_accept(visitor, prefix)

    def copy(self, tag=None, arg=None, children=None, index=None, src=None):
        if tag is None:
            tag = self.tag
        if arg is None:
            arg = self.arg
        if children is None:
            children = self.children
        if index is None:
            index = self.index
        if src is None:
            src = self.src
        return self.__class__(tag, arg, children, index, src)

    def children_accept(self, visitor, prefix='visit_'):
	for c in self.children:
	    c.accept(visitor, prefix)

    def accept(self, visitor, prefix='visit_'):
	m = getattr(visitor, (prefix+self.tag), None)
	if m is None:
	    m = getattr(visitor, (prefix+'default'), None)
	    if m is None:
		msg = 'accept: unknown: %r, %r  in %r'%(prefix, self.tag, visitor)
		print msg
		raise ValueError, msg
		return
	m(self)

    def error(self, msg, node=None):
        if node is None:
            node = self
        node.src.error(msg, node)
        

    def get_text(self):
	" Get the total text of all text children, joined with and ended with '\n' "
	text = []
	for c in self.children:
	    if c.tag == 'text':
		text.append(c.arg)
		if not c.arg.endswith('\n'):
		    text.append('\n')
	return ''.join(text)

    def get_arg(self):
        arg = self.arg.strip()
        if arg.startswith(':'):
            arg = arg[1:].strip()
        return arg

    def get_arglist(self):
	arg = self.arg
	if arg.startswith(':'):
	    arg = arg[1:]
	names = [x.strip() for x in arg.split(',')]
	if names == ['']:
	    names = []
	return names

    def get_arg_children(self):
        if self.arg:
            children = [SpecNode('text', self.arg, (), self.index, self.src)]
            children.extend(self.children)
        else:
            children = self.children
        return children


    def get_arg_rest(self, nostrip=0):
	arg = self.arg
	if not nostrip:
	    arg = arg.strip()
	return arg, self.children

    def get_arg_norest(self):
	''' Get the arg as by self.arg,
	    but make sure there are no more children.
	    '''
	if self.children:
	    raise SyntaxError, 'No children nodes expected in node: %s'%self
	return self.arg.strip()

    def get_namearg(self):
	''' Get the argument in the form of a name
	    It is the argument stripped.
	    And not allowed to contain : or , or new line.
        '''
	name = self.arg.strip()
	if '\n' in name or ':' in name or ',' in name:
	    raise SyntaxError, 'Invalid name: %r'%name
	return name

    def split_attrs(self, tag=None, attrdict=False):
	if tag is None:
	    tag = self.tag
        if attrdict:
            attrs = {}
            def addattr(tag, attr, node):
                if tag in attrs:
                    node.error('Duplicate attribute: %s'%attr)
                else:
                    attrs[tag] = attr
        else:
            attrs = []
            def addattr(tag, attr, node):
                attrs.append((tag, attr))
	children = []
	for ch in self.children:
	    if ch.tag == "with":
		for opt in ch.children:
		    if opt.arg:
			arg = opt.arg
		    else:
			self.error('Bad attribute, no argument.', opt)
		    if opt.children:
			self.error('Expected no children to attribute.', opt.children[0])
                    if opt.arg:
                        addattr(opt.tag, arg, opt)
	    elif ch.tag[-1:] == '=':
                addattr(ch.tag[:-1], ch.arg, ch)
	    else:
		children.append(ch)
	if len(children) == len(self.children):
	    node = self
	else:
	    node = self.__class__(
		tag, self.arg, children, self.index, self.src)
	return node, attrs


class Source:
    def __init__(self, name, lines=None, string=None, nostrip=0, debug=0, max_errors=10):
	self.filename = name
	self.lines = lines
	self.string = string
	self.nostrip = nostrip
        self.debug = debug
        self.error_reports = []
        self.max_errors = max_errors
        self.num_warnings = 0
        self.num_errors = 0

    def errmsg_context(self, context):
	linetext = ''
	filename = '<unknown file>'
	if context is not None:
            if hasattr(context, 'index'):
                index = context.index
                src = context.src
            else:
                index = context
                src = self
	    if src is not None:
		filename = src.filename
		linetext = src.get_line(index=index)
	    print '%s:%s:'% (filename, index+1)
	    if linetext:
		print '    %s'%linetext
	

    def error(self, message, context=None, exception=None, more=(), harmless = 0):
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


    def get_line(self, index):
	if self.lines is None:
	    if self.string is None:
                if self.filename:
                    try:
                        self.string = open(self.filename).read()
                    except:
                        return ''
                else:
                    return ''
	    self.lines = self.string.split('\n')
	return self.lines[index]
	

class _GLUECLAMP_:
    
    _chgable_ = 'nodemap', 'SpecNode'

    _imports_ = (
	'_parent:DottedTree',
	'_root:re',
        '_root:os',
	)

    node_aliases_defs = (
	('attr'	, 'attribute'),
	('c'	, 'comment'),
	('cond'	, 'condition'),
	('d'	, 'description'),
	('dwh'	, 'description_with_header'),
	('eg'	, 'example'),
	('fop'  , 'function_operator'),
	('iop'	, 'inplace_operator'),
	('ka'	, 'key_arg'),
	('op'	, 'operator'),
	('rop'	, 'reverse_operator'),
	('t'	, 'text'),
	)

    def _get_node_aliases(self):
	return dict(self.node_aliases_defs)

    def _get_reverse_node_aliases(self):
	# Used to make names shorter
	return dict([(v, k) for k, v in self.node_aliases_defs])

    def _get_is_not_ascii(self):
	return self.re.compile(eval(r'u"[\u0080-\uffff]"')).search

    ##
    # @return A tuple of predefined subjects.

    def get_predefined_subjects(self):
	return (GuppyWorld(self),)
	

    ##
    # Parses a file and makes a tree of nodes
    # @param file name of file containing a dotted tree
    # @return a SpecNode object
    # @more
    # First tag is special.
    # We don't interpret the first line of the file,
    # but uses a special file tag.

    def node_of_file(self, file, nostrip=0):
	src = Source(name=file, nostrip=nostrip)
	dtree = self.DottedTree.parse_file(file, src)
	tag = 'file'
	arg = file
	text = dtree.tag.strip()
        children = self.nodes_of_dforest(dtree.children, src)
	index = dtree.index
	return self.node_of_tatci(tag, arg, text, children, index, src)
 
    def node_of_string(self, string, name='<string>', nostrip=0):
	dtree = self.DottedTree.parse_string(string)
	tag = 'string'
	arg = name
	src = Source(name=name, string=string, nostrip=nostrip)
	text = dtree.tag.strip()
	index = dtree.index
        children = self.nodes_of_dforest(dtree.children, src)
	return self.node_of_tatci(tag, arg, text, children, index, src)

    def node_of_dtree(self, dtree, src):
	tag = dtree.tag
	textpos = tag.find('\n')
	if textpos == -1:
	    textpos = len(tag)

	equpos = tag.find('=', 0, textpos)
	colonpos = tag.find(':', 0, textpos)
	if equpos != -1 and (colonpos == -1 or equpos < colonpos):
	    tag, arg = (tag[:equpos].strip()+'=',
			tag[equpos+1:].strip())
	else:
	    if colonpos == -1:
		if not ' ' in tag[:textpos] or textpos >= len(tag.rstrip()):
		    colonpos = textpos
		else:
		    raise SyntaxError, 'No colon in spaced tag in node %s'%dtree
	    tag, arg = (tag[:colonpos].strip(),
			tag[colonpos+1:]
			)
	if tag in self.node_aliases:
	    tag = self.node_aliases[tag]
	tag = tag.replace(' ', '_')
	if tag != 'text' and not src.nostrip:
	    arg = arg.strip()

        children = self.nodes_of_dforest(dtree.children, src)
	return self.node_of_taci(tag, arg, children, dtree.index, src)
		    
    def nodes_of_dforest(self, dforest, src):
	onodes = [self.node_of_dtree(c, src) for c in dforest]
        nodes = []
        for node in onodes:
            if node.tag != 'include':
                nodes.append(node)
                continue
            filename = node.arg.strip()
            filename = self.os.path.join(self.os.path.dirname(src.filename),
                                         filename)
            node = self.node_of_file(filename, nostrip=src.nostrip)
            nodes.extend(node.children)
        return tuple(nodes)
        
        

    def _get_node_of_taci(self):
	return SpecNode

    def node_of_tatci(self, tag, arg, text, children=(), index=0, src=None):
	if text:
	    if tag == 'text':
		if arg:
		    arg = arg + '\n'+ text
		else:
		    arg = text
	    else:
		children  = (self.node_of_taci('text', text, (), index, src),) + children
	return self.node_of_taci(tag, arg, children, index, src)

    def node_of_text(self, text):
	# Returns a node that is either
	# - a 'text' node, if text was all ascii
	# - a 'char' node, if text was a single non-ascii
	# - a 'block' with children being a sequence of char and text nodes,
	#	if text contained ascii and non-ascii characters
	nodes = self.nodes_of_text(text)
	if len(nodes) == 1:
	    return nodes[0]
	else:
	    return self.node_of_taci('block', '', nodes)

    def nodes_of_text(self, text):
	# Returns a sequence of nodes, encoding text.
	nodes = []
	if self.is_not_ascii(text):
	    chars = []
	    for char in text:
		no = ord(char)
		if no < 128:
		    chars.append(char)
		else:
		    if chars:
			nodes.append(self.node_of_taci('text', ''.join(chars)))
			chars = []
		    nodes.append(self.node_of_taci('char', str(no)))
	    if chars:
		nodes.append(self.node_of_taci('text', ''.join(chars)))
	else:
	    nodes.append(self.node_of_taci('text', text))
	return nodes
	    
    def main(self, package):
	root = self._root

	specs = package.specs
	specdir = root.os.path.dirname(specs._module.__file__)
	print specdir
	main_dt_name = root.os.path.join(specdir, "main.gsl")


	env = self.SpecEnv(self)

	node = self.node_of_file(main_dt_name)

	node.accept(env)

	import __main__
	__main__.env = env

	return

    def print_doc(self, dt):
	self.print_doc()

    def unparse_head(self, level, tag, arg, text):
	head = tag
	if arg:
	    head = head + ': ' + arg
	if text:
	    head = head + '\n' + text
	tag = self.DottedTree.unparse_tag(level, head)
	return tag

	


def test_main():
    from guppy import Root
    root = Root()
    sp = root.guppy.gsl.SpecNodes

    root.guppy.gsl.SpecNodes.main(root.guppy)
    

if 0 or __name__ == '__main__':
    test_main()

