#._cv_part guppy.gsl.Gsml

class GsmlHandler:
    # To be mixed in with something like HTMLParser.HTMLParser

    def handle_starttag(self, tag, attrs):
	# print 'starttag', tag, attrs
	self.stack.append(self.out)
	self.out = []
	if attrs:
	    at = []
	    for k, v in attrs:
		at.append(self.mod.node_of_taci(k, v))
	    self.out.append(self.mod.node_of_taci('with', '', at))
	    
    def handle_endtag(self, tag):
	# print 'endtag', tag
	node = self.mod.node_of_taci(tag, '', self.out)
	self.out = self.stack.pop()
	self.out.append(node)

    def handle_charref(self, name):
	#print 'charref', name
        if name[:1] == "x":
            char = int(name[1:], 16)
	    name = '0'+name
        else:
            char = int(name)
        if 0 <= char < 128:
	    char = chr(char)
	    self.handle_data(char)
	else:
	    self.out.append(self.mod.node_of_taci('char', name))

    def handle_entityref(self, name):
	#print 'handle entityref', name
	if name not in self.mod.entitydefs:
            self.unknown_entityref(name)
	self.out.append(self.mod.node_of_taci('char', name))

    def unknown_entityref(self, name):
	raise SyntaxError, 'Unknown entity ref: %r'%name

    def handle_data(self, data):
	# print 'data', data
	# data = data.strip()
	if data.strip():
	    self.out.extend( self.mod.nodes_of_text(data) )

    def handle_comment(self, data):
	self.out.append( self.mod.node_of_taci('comment', data, (), 0))
	
    def handle_decl(self, decl):
	# print 'handle_decl', decl
	self.out.append( self.mod.node_of_taci('html_declaration', decl))

    def handle_pi(self, data):
	self.out.append( self.mod.node_of_taci('processing_instruction', data))

class _GLUECLAMP_:
    _imports_ = (
	'_root.HTMLParser:HTMLParser',
	'_parent.SpecNodes:node_of_taci',
	'_parent.SpecNodes:nodes_of_text',
	'_root.htmlentitydefs:entitydefs',
	)

    encoding = "iso-8859-1"

    def node_of_gsml(self, text):
	class Parser(GsmlHandler, self.HTMLParser):
	    def __init__(self, mod):
		mod.HTMLParser.__init__(self)
		self.mod = mod
		self.out = []
		self.stack = []
		
	
	p = Parser(self)
	p.feed(text)
	p.close()
	if p.stack:
	    raise SyntaxError, 'Missing end tag'
	node = self.node_of_taci('block', '', p.out, 0)
	return node

    def _test_main_(self):
	x = """
<!DOCTYPE html...>
This is an <em> emphasized </em> word.
See also <a href="guppy-pe.sf.net"> Guppy. </a>
Defined as <use_my_macro/>.

Handle char ref: &#100;.
Handle char ref: &lt;.

<!-- A comment -->

<?A processing instruction>

<namespace:tag />
	"""

	node = self.node_of_gsml(x)
	print node


if 0 or __name__=='__main__':
    from guppy import Root
    Root().guppy.gsl.Gsml._test_main_()
