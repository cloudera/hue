#._cv_part guppy.gsl.DottedTree

"""
Handling of tree structures given in a special 'dotted' syntax.
This represents trees of nodes with strings as tags,
in a readable and writable and easy to parse syntax.

There are two main functions, unparse_sexpr and parse_string.
When parsing, the result is by default given in 'sexpr' format:
each node is a tuple of the form

    (tag, ) or (tag, node) or (tag, node, node) ...

The following invariant is intended to hold for every node x, 

    parse_string(unparse_sexpr(x)) == x

Currently the following invariant has been tested for some strings:

    unparse_sexpr(parse_string(s)).strip() == s.strip()

[It only holds on stripped results but may be fixed sometime.]

"""

class Node(object):
    __slots__ = 'tag', 'children', 'index', 
    def __init__(self, tag, children, index):
	self.tag = tag
	self.children = children
	self.index = index
	
    def as_sexpr(self):
	return (self.tag,) + tuple([c.as_sexpr() for c in self.children])

    def __repr__(self):
	return '%s(%r, %r, %r)'%(
	    self.__class__.__name__,
	    self.tag,
	    self.children,
	    self.index)




class _GLUECLAMP_:

    _imports_ = (
	'_parent.FileIO:IO',
	)

    ##
    # The name of attributes that are configurable in instances.
    #
    _chgable_ = 'node', 'dotchar'

    ##
    # The character that begins the 'dotted' indentation.
    dotchar = '.'

    ##
    # The character that quotes lines beginning with dots and itself.
    quotechar = '\\'

    ##
    # Construct a new node.
    # @return 
    # This variant returns a tuple in s-expression form.
    # @param tag a string
    # @param children a sequence of nodes
    # @param lineindex line index of tag, not used in s-expressions

    def node_sexpr(self, tag, children, lineindex):
	return (tag,) + tuple(children)

    ##
    # Construct a new node.
    # @return
    # This variant returns a Node object.
    # @param tag a string
    # @param children a sequence of nodes
    # @param lineindex line index of beginning tag, first line = 0

    def node_node(self, tag, children, lineindex):
	return Node(tag, tuple(children), lineindex)

    node = node_node

    def parse_file(self, file, src=None):
	return self.parse_string(self.IO.read_file(file), src)

    ##
    # Parse a dotted tree text given as a sequence of lines.
    # @param pos
    # @param tag     list with first line of tag, if any
    # @param lineindex line index of tag
    # @param it	     iterator yielding remaining lines
    # @return a triple (index, next, node) where
    # index is the index of line 'next',
    # next is the first line of next node to parse, and
    # node is the resulting node of this parse.

    def parse_iter(self, pos, tag, lineindex, it, src=None):
	dotchar = self.dotchar
	quotechar = self.quotechar
	children = []
	firstline = lineindex
    
	while 1:
	    try:
		lineindex, next = it.next()
	    except StopIteration:
		next = None
		break
	    if not next.startswith(dotchar):
		tag.append(next)
	    else:
		break
	for (i, t) in enumerate(tag):
	    if (t.startswith(quotechar+dotchar) or
		t.startswith(quotechar+quotechar+dotchar)):
		tag[i] = t[len(quotechar):]
	if tag == ['']:
	    tag = '\n'
	else:
	    tag = '\n'.join(tag)
	while 1:
	    if (next is None or len(next) <= pos
		or next[pos] != dotchar or
		not next.startswith(dotchar*(pos+1))):
		return lineindex, next, self.node(tag, children, firstline)
	    if len(next) > pos+1 and next[pos+1] == dotchar:
                if src is None:
                    raise SyntaxError, 'Level must increase with 1 max'
                else:
                    src.error('Level must increase with 1 max', lineindex)
	    lineindex, next, child = self.parse_iter(pos+1, [next[pos+1:]],
                                                     lineindex, it, src)
	    children.append(child)


    def parse_lines(self, lines, src=None):
	it = enumerate(lines)
	lineindex, next, node = self.parse_iter(0, [], 0, it, src)
	assert next is None
	return node

    def parse_string(self, string, src=None):
	if string:
	    lines = string.split('\n')
	else:
	    lines = []
	return self.parse_lines(lines, src)


    ##
    # Unparse a tree given on Node form
    def unparse_node(self, node):
	return self.unparse_sexpr(node.as_sexpr())

    ##
    # Unparse a tree given on sexpr form
    # @return a string in dotted-tree form
    def unparse_sexpr(self, sexpr):
	li = []

	def unparse(depth, sexpr):
	    li.append(self.unparse_tag(depth, sexpr[0]))
	    for x in sexpr[1:]:
		unparse(depth+1, x)
	
	unparse(0, sexpr)
	return '\n'.join(li)

    def unparse_tag(self, depth, tag):
	dotchar, quotechar = self.dotchar, self.quotechar
	tag = tag.split('\n')
	for (i, t) in enumerate(tag):
	    if (t.startswith(dotchar) or
		t.startswith(quotechar + dotchar)):
		tag[i] = quotechar + t
	tag = '\n'.join(tag)
	tag = dotchar*depth+tag
	return tag

def test_1():
    # Test parsing to sexpr's and back
    # for a variety of cases
    from guppy import Root
    dt = Root().guppy.gsl.DottedTree
    dt.node = dt.node_sexpr
    parse = dt.parse_string
    unparse = dt.unparse_sexpr
    
    for x, y in [
	['', ('',)],
	['a', ('a',)],
	['.a', ('',('a',))],
	['a\n.b', ('a',('b',))],
	['a\nb\n.c', ('a\nb',('c',))],
	["""\n.a\n..a""", ('\n', ('a', ('a',)))],
	["""hello\n.a\n.b\n..ba\nx\n..bb""", ('hello', ('a',), ('b', ('ba\nx',), ('bb',)))],
	# Quoting dots
	[r'\.', ('.',)],
	[r'.\.', ('',('.',))],
	# Preserving quote
	['\\', ('\\',)],
	['.\n\\', ('', ('\n\\',))],
	# Quoting quote-dots
	[r'\\.', (r'\.',)],
	# Preserving whitespace starting a tag
	# Or should it be stripped? I think better not, it would complicate transparency.
	[r'. tag', ('',(' tag', ))],
	
	# Preserving initial whitespace
	[' ', (' ',)],
	# Preserving initial newline
	['\n', ('\n',)],
	['\na', ('\na',)],

	# A n intended usage example
	['''
initial
text
.aspect for guppy.hsp
..returns
...type A
...latex
~\\
\..~|begincolorbox|~raw::~LaTeX~\\
~\\
~~~{\textbackslash}{\textbackslash}begin{\{}center{\}}~\\
.aspect for guppy.gsl
..contains DottedTree
''',

('\ninitial\ntext',
 ('aspect for guppy.hsp',
  ('returns',
   ('type A',),
   ('latex\n~\\\n..~|begincolorbox|~raw::~LaTeX~\\\n~\\\n~~~{\textbackslash}{\textbackslash}begin{\\{}center{\\}}~\\',))),
 ('aspect for guppy.gsl',
  ('contains DottedTree\n',)))]

	]:
	z = parse(x)
	if y is not None:
	    assert z == y
	assert unparse(z).strip() == x.strip()

    # Unparsing x and then parsing should give back x transparently
    # for any tree x, involving any combination of dots, quotes and other characters.

    # List of special chars and one normal
    chars = [dt.quotechar, dt.dotchar, '\n', ' ', 'a']

    import random

    ##
    # Generate a random node with random number of children.
    # Shuffles the chars list to make the tag string.
    # @param maxchild maximum number of children
    def randnode(maxchild):
	numchild = random.randint(0, maxchild)
	random.shuffle(chars)
	tag = ''.join(chars)
	children = [randnode(maxchild-1) for i in range(numchild)]
	return dt.node(tag, children, 0)
	
    for i in range(10):
	y = randnode(3)
	x = unparse(y)
	z = parse(x)
	assert z == y
    
def test_2():
    # Test parsing to Node
    # that the line lineindex are correct
    # They start from 0, since enumerate() generates them,
    # It seemed inconsistent to change them to start from 1.
    # Which will be made in error prints.
    
    from guppy import Root
    dt = Root().guppy.gsl.DottedTree
    parse = dt.parse_string
    unparse = dt.unparse_node
    
    node = parse("""\
line 0
.line 1
..line 2
line 3
.line 4
""")

    exp = Node('line 0', (
	 	Node('line 1',
			(Node('line 2\nline 3', (), 2),), 1),
		Node('line 4\n', (), 4)), 0)
    assert repr(node) == repr(exp)
    print node

def test_doctest():
    import doctest, guppy.gsl.DottedTree
    return doctest.testmod(guppy.gsl.DottedTree)

def test_main():
    test_1()
    test_2()
    #test_doctest()

if 0 or __name__ == '__main__':
    test_main()
