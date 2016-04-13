#._cv_part guppy.gsl.Latex


class Doc2Latex:
    sizes = ('tiny', 'scriptsize', 'footnotesize', 'small',
	     'normalsize', 'large', 'Large', 'LARGE', 'huge', 'Huge')
    def __init__(self, mod, doc, node):
	self.mod = mod
	self.doc = doc
	self.encoder = Encoder(mod)
	self.encode = self.encoder.encode
	self.node = node
	self.out = []
	self.ms = []
	self.mode = None
	self.cur_style = 'rm'
	self.cur_size = list(self.sizes).index('normalsize')
	self.document_lang = None
	self.document_title = None
	self.document_metas = []
	self.latex_list_nesting = 0
        self.latex_mode = 0
	self.noindent = 0
	self.authors = []

	node.accept(self)

    def _visit_children(self, node):
	E = self.mod.ReportedError
	for ch in node.children:
	    try:
		ch.accept(self)
	    except E:
		pass

    def abs_size(self, size, node):
	osize = self.cur_size
	si = size
	if si < 0:
	    si = 0
	elif si >= len(self.sizes):
	    si = len(self.sizes) - 1
	self.append('{\\%s '%self.sizes[si])
	self.cur_size = si
	if self.cur_style != 'rm':
	    self.style(self.cur_style, node)
	else:
	    node.arg_accept(self)
	self.append('}')
	self.cur_size = osize
	

    def append(self, x):
	self.out.append(x)


    def changed_size(self, delta, node):
	self.abs_size(self.cur_size + delta, node)
	
    def error(self, msg, *args, **kwds):
	msg = 'Doc2Latex: ' + msg
	self.doc.env.error(msg, *args, **kwds)

    def get_latex(self):
	return ''.join(self.out)

    def no_children(self, node):
	if node.children:
	    self.error('No children allowed for %r.'%node.tag, node.children[0])

    def style(self, style, node):
	self.append('{\\%s '%style)
	ostyle = self.cur_style
	self.cur_style = style
	node.arg_accept(self)
	self.cur_style = ostyle
	if style == 'em':
	    self.append('\\/}')
	else:
	    self.append('\\/}')

    def visit_a(self, node):
        pass

    def visit_author(self, node):
	self.authors.append(node.arg)
	self.no_children(node)

    def visit_big(self, node):
	self.changed_size(1, node)
		    

    def visit_block(self, node):
	self._visit_children(node)

    def visit_blockquote(self, node):
	self.append('\\begin{quote}\n')
	self.latex_list_nesting += 1

	node.arg_accept(self)

	self.latex_list_nesting -= 1
	self.append('\\end{quote}\n')

    char_table = {
	'nbsp'	: '~',
	}

    def visit_char(self, node):
        char = node.arg.strip()
	c = self.char_table.get(char)
	if c is None:
	    self.error('No such character: %r.'%char, node)
	    c = char
	self.append(c)

    def visit_code(self, node):
	self.style('tt', node)

    def visit_comment(self, node):
	pass

    def visit_dd(self, node):
	self.ms.append('dd')
	step = 24
	ls = (self.ms.count('dd') + self.latex_list_nesting) * step
	self.append('{\\par \\noindent  \\leftskip = %d pt '%ls)
	for i, v in enumerate(('i', 'ii', 'iii', 'iv', 'v', 'vi')[self.latex_list_nesting:]):
	    self.append(' \\leftmargin%s = %d pt '%(v, ls + (i + 1) * step))
	node.arg_accept(self)
	self.append('\\par}\n')
	self.ms.pop()

    def visit_default(self, node):
	self.error('I don\'t know what to generate for the tag %r.'%node.tag, node)
	

    def visit_define(self, node):
	# xxx
	self._visit_children(node)

    def visit_dl(self, node):
	if self.ms and self.ms[-1] == 'dt':
	    self.visit_dd(node)
	else:
	    self.append('{\\par \\noindent\n')
	    self._visit_children(node)
	    self.append('\\par}\n')

    def visit_dt(self, node):
	self.ms.append('dt')
	self.append('{\\par \\pagebreak[%f] \\noindent \\hangindent = 12 pt \\hangafter = 1 \n'%(
		    3.4-0.1*len(self.ms),
		    ))
	node.arg_accept(self)
	self.append('\\par}\n')
	self.ms.pop()

    def visit_document(self, node):
	self._visit_children(node)

    def visit_document_lang(self, node):
	if self.document_lang is not None:
	    self.error('Duplicate document lang directive.', node)
	self.document_lang = node

    def visit_document_title(self, node):
	if self.document_title is not None:
	    self.error('Duplicate document title directive.', node)
	self.document_title = node

    def visit_exdefs(self, node):
	self.symplace = {}
	for ch in node.children:
	    syms = [x.strip() for x in ch.arg.split(',')]
	    for sym in syms:
		self.symplace[sym] = ch.tag
	
	
    def visit_em(self, node):
	self.style('em', node)

    def visit_enumerate(self, node):
	self.append('\\begin{enumerate}\n')
	for c in node.children:
	    self.append('\\item ')
	    c.accept(self)
	self.append('\\end{enumerate}\n')

    def visit_h0(self, node):
	# Not a html header,
	# we may treat this as 'new page' or chapter here
	# and some larger divisor in html.
	self.visit_hx(node)

    def visit_h1(self, node):
	self.visit_hx(node)

    def visit_h2(self, node):
	self.visit_hx(node)

    def visit_h3(self, node):
	self.visit_hx(node)

    def visit_h4(self, node):
	self.visit_hx(node)

    def visit_h5(self, node):
	self.visit_hx(node)

    def visit_h6(self, node):
	self.visit_hx(node)

    def visit_hx(self, node):
	n = int(node.tag[1:])
	if self.mode == 'man_page':
	    self.append('{\\par \\pagebreak[%d] \\vskip %d pt \\noindent\n' % (
		[4,3,3,2,2,1,1][n],
		(12 - 2 * n)))
	    self.abs_size(len(self.sizes) - n - 2, self.mod.node_of_taci(
		'', '',
		[self.mod.node_of_taci('strong', node.arg, node.children)]))
	    self.append('\\par \\vskip %d pt\n} \\noindent\n'%(12 - 2 * n))
	    self.noindent = 1
	    #self.append('\\end{list}\n')
	else:
	    self.append('\\%s{'%self.mod.section_table[n])
	    node.arg_accept(self)
	    self.append('}\n')

    def visit_itemize(self, node):
	self.append('\\begin{itemize}\n')
	self.latex_list_nesting += 1
	for c in node.children:
	    self.append('\\item ')
	    c.accept(self)

	self.latex_list_nesting -= 1
	self.append('\\end{itemize}\n')

    def visit_latex(self, node):
        self.latex_mode += 1
        node.arg_accept(self)
        self.latex_mode -= 1

    def visit_li(self, node):
	self.append('\\item ')
	node.arg_accept(self)

    def visit_link_to(self, node):
	# xxx
	name = node.arg
	self.append(' {\\em ')
	if not node.children:
	    self.append(self.encode(name))
	else:
	    self._visit_children(node)
	self.append('\\/}')

    def visit_link_to_extern(self, node):
	# xxx
	name = node.arg
	doc = node.children[0].arg
	children = node.children[1:]
	self.append(' {\\em ')
	if not children:
	    self.append(self.encode(name))
	else:
	    for ch in children:
		ch.accept(self)
	self.append('\\/}')

    def visit_link_to_local(self, node):
	# xxx
	name = node.arg
	self.append(' {\\em ')
	if not node.children:
	    self.append(self.encode(name))
	else:
	    self._visit_children(node)
	self.append('\\/}')

    def visit_link_to_unresolved(self, node):
	# xxx
	name = node.arg
	self.append(' {\\em ')
	if not node.children:
	    self.append(self.encode(name))
	else:
	    self._visit_children(node)
	self.append('\\/}')

    def visit_literal_block(self, node):
	self.append('{\\ttfamily \\raggedright \\noindent')
	self.encoder.literal_block = 1
	self.encoder.insert_none_breaking_blanks = 1

	node.arg_accept(self)
	self.encoder.literal_block = 0
	self.encoder.insert_none_breaking_blanks = 0
	self.append('}\n')

    def visit_lp(self, node):
        self.latex_mode += 1
	self.visit_paragraph(node)
        self.latex_mode -= 1
        

    def visit_man_page_mode(self, node):
	omode = self.mode
	self.mode = 'man_page'
	self._visit_children(node)
	self.mode = omode

    def visit_meta(self, node):
	self.document_metas.append(node)

    def visit_ol(self, node):
	self.append('\\begin{enumerate}\n')
        self._visit_children(node)
	self.append('\\end{enumerate}\n')
        

    def visit_p(self, node):
	self.visit_paragraph(node)

    def visit_paragraph(self, node):
	self.append('{\\par ')
	if self.noindent:
	    self.append('\\parindent = 0 pt ')
	    self.noindent = 0
	self.append('\n')
	node.arg_accept(self)
	self.append(' \\par}\n')

    def visit_pre(self, node):
        # I couldn't use Latex verbatim environment
        # since it didn't respected leftskip
        # so the environment became misplaced (within dd)

        text = node.arg.strip()
        if text:
            text += '\n'
        text = text + node.get_text()
        text = text.expandtabs()
        lines = text.split('\n')
        if lines and not lines[-1]:
            lines.pop()
        if not lines:
            return
        self.append('\\par\n')
        self.encoder.insert_none_breaking_blanks += 1
        self.encoder.literal+=1
        first = 1
        self.append('{\\tt{%s}}\n'%self.encode(lines[0]))
        for line in lines[1:]:
            self.append(
                '{ \\par \\parindent = 0 pt \\parskip = 0 pt \\tt{%s} }\n'%
                self.encode(line))
        self.encoder.insert_none_breaking_blanks -= 1
        self.encoder.literal -= 1
        self.append('\\par\n')


    def visit_small(self, node):
	self.changed_size(-1, node)
		    
    def visit_spc_colonkind(self, node):
	self.append('~{\\bf :} ')
	
    def visit_spc_mapsto(self, node):
	self.append(' \\(\mapsto \\) ')

    def visit_string(self, node):
	self._visit_children(node)

    def visit_strong(self, node):
	self.style('bf', node)

    def visit_sub(self, node):
	self.append('\\raisebox{-.6ex}{')
	self.changed_size(-1, node)
	self.append('}')

    def visit_sup(self, node):
	self.append('\\raisebox{.6ex}{')
	self.changed_size(-1, node)
	self.append('}')

    def visit_symbol(self, node):
	self.visit_text(node)

    def visit_table(self, node):
	Table(self, node)

    def visit_text(self, node):
        if self.latex_mode:
            self.append(node.arg)
        elif 1:
	    text = node.arg
	    text = self.encoder.encode(text)
	    self.append(text)
	else:
	    for ch in node.arg:
		if ch == '\\':
		    ch = '{\\textbackslash}'
		elif ch in '{}#~':
		    ch = '\\'+ch
		self.append(ch)
	    self.append('\n')
	self._visit_children(node)

    def visit_to_document_only(self, node):
	self._visit_children(node)

    def visit_to_html_only(self, node):
	pass

    def visit_to_tester_only(self, node):
	pass

    def visit_tt(self, node):

	self.append('\\texttt{')
	self.encoder.literal = 1
	node.arg_accept(self)
	self.encoder.literal = 0
	self.append('}')

    def visit_ul(self, node):
	self.append('\\begin{itemize}\n')
	self._visit_children(node)
	self.append('\\end{itemize}\n')

    def visit_var(self, node):
	self.style('em', node)


class Table(Doc2Latex):
    many_hlines = 1 # Use extra many hlines.. looks good, a matter of taste.
    def __init__(self, d2l, node):
	self.d2l = d2l
        self.__dict__.update(d2l.__dict__)
	self.node = node
	self.out = []
	self.rows = []
	self.colwidth = None

	self._visit_children(node)

	maxcols = 0
	for row in self.rows:
	    if len(row.columns) > maxcols:
		maxcols = len(row.columns)

	if not maxcols:
	    return # Empty table
	if self.colwidth is not None:
	    if not len(self.colwidth) == maxcols:
		self.error("Wrong number of column width specifications (%d) vs\n"
			   "    max columns in table (%d)."%(len(self.colwidth), maxcols),
			   node)
	else:
	    self.colwidth = [1.0/maxcols]*maxcols
	ap = self.d2l.append
	ap('\n\\begin{longtable}[c]{|%s|}\n'%('|'.join(['p{%.2g\\linewidth}'%cw
						     for cw in self.colwidth])))
	if self.many_hlines:
	    ap('\\hline\n')
	for row in self.rows:
	    for col in row.columns:
		ap(''.join(col.data))
		if col is row.columns[-1]:
		    if self.many_hlines:
			ap('\\\\\n')
			ap('\\hline\n')
		    else:
			if row is not self.rows[-1]:
			    ap('\\\\\n')
		else:
		    ap('&\n')
	    if row.is_head:
		ap('\\hline\n')
		ap('\\endhead\n')
	ap('\n\\end{longtable}\n')


    def visit_colgroup(self, node):
	colwidth = []
	
	for c in node.children:
	    if c.tag != "col_width":
		self.error('Unrecognized colgroup option: %r'%c.tag, c)
	    cg = c.arg
	    if cg.endswith('%'):
		cg = cg[:-1]
		cg = float(cg)/100.0
	    else:
		cg = float(cg)
	    colwidth.append(cg)
	self.colwidth = colwidth

    def visit_options(self, node):
	pass

    def visit_thead(self, node):
	self._visit_children(node)
	self.rows[-1].is_head = 1

    def visit_tr(self, node):
	self.rows.append(Row(self, node))
	
class Row(Doc2Latex):
    is_head = 0
    def __init__(self, table, node):
        self.__dict__.update(table.__dict__)
	self.columns = []
	self._visit_children(node)

    def visit_td(self, node):
	self.columns.append(Column(self, node))

    def visit_th(self, node):
	self.columns.append(Column(self, node))

class Column(Doc2Latex):
    def __init__(self, row, node):
        self.__dict__.update(row.__dict__)
	self.data = []
	self.append = self.data.append
	node.arg_accept(self)

    

class Babel:
    """Language specifics for LaTeX."""
    # country code by a.schlock.
    # partly manually converted from iso and babel stuff, dialects and some
    _ISO639_TO_BABEL = {
        'no': 'norsk',     #XXX added by hand ( forget about nynorsk?)
        'gd': 'scottish',  #XXX added by hand
        'hu': 'magyar',    #XXX added by hand
        'pt': 'portuguese',#XXX added by hand
        'sl': 'slovenian',
        'af': 'afrikaans',
        'bg': 'bulgarian',
        'br': 'breton',
        'ca': 'catalan',
        'cs': 'czech',
        'cy': 'welsh',
        'da': 'danish',
        'fr': 'french',
        # french, francais, canadien, acadian
        'de': 'ngerman',  #XXX rather than german
        # ngerman, naustrian, german, germanb, austrian
        'el': 'greek',
        'en': 'english',
        # english, USenglish, american, UKenglish, british, canadian
        'eo': 'esperanto',
        'es': 'spanish',
        'et': 'estonian',
        'eu': 'basque',
        'fi': 'finnish',
        'ga': 'irish',
        'gl': 'galician',
        'he': 'hebrew',
        'hr': 'croatian',
        'hu': 'hungarian',
        'is': 'icelandic',
        'it': 'italian',
        'la': 'latin',
        'nl': 'dutch',
        'pl': 'polish',
        'pt': 'portuguese',
        'ro': 'romanian',
        'ru': 'russian',
        'sk': 'slovak',
        'sr': 'serbian',
        'sv': 'swedish',
        'tr': 'turkish',
        'uk': 'ukrainian'
    }

    def __init__(self, mod):
        self.language = mod.language_code
	self.re = mod.re

        # pdflatex does not produce double quotes for ngerman in tt.
        self.double_quote_replacment = None
        if self.re.search('^de',self.language):
            #self.quotes = ("\"`", "\"'")
            self.quotes = ('{\\glqq}', '{\\grqq}')
            self.double_quote_replacment = "{\\dq}"
        else:
            self.quotes = ("``", "''")
        self.quote_index = 0

    def next_quote(self):
        q = self.quotes[self.quote_index]
        self.quote_index = (self.quote_index+1)%2
        return q

    def quote_quotes(self,text):
        t = None
        for part in text.split('"'):
            if t == None:
                t = part
            else:
                t += self.next_quote() + part
        return t

    def double_quotes_in_tt (self,text):
        if not self.double_quote_replacment:
            return text
        return text.replace('"', self.double_quote_replacment)

    def get_language(self):
        if self._ISO639_TO_BABEL.has_key(self.language):
            return self._ISO639_TO_BABEL[self.language]
        else:
            # support dialects.
            l = self.language.split("_")[0]
            if self._ISO639_TO_BABEL.has_key(l):
                return self._ISO639_TO_BABEL[l]
        return None




class Encoder:
    literal_block = 0
    literal = 0
    mathmode = 0
    verbatim = 0
    insert_newline = 0
    mbox_newline = 0
    insert_none_breaking_blanks = 0

    latex_equivalents = {
        u'\u00A0' : '~',
        u'\u2013' : '{--}',
        u'\u2014' : '{---}',
        u'\u2018' : '`',
        u'\u2019' : '\'',
        u'\u201A' : ',',
        u'\u201C' : '``',
        u'\u201D' : '\'\'',
        u'\u201E' : ',,',
        u'\u2020' : '{\\dag}',
        u'\u2021' : '{\\ddag}',
        u'\u2026' : '{\\dots}',
        u'\u2122' : '{\\texttrademark}',
        u'\u21d4' : '{$\\Leftrightarrow$}',
    }

    def __init__(self, mod):
	self.mod = mod
	self.re = mod.re
        self.babel = Babel(mod)
	self.font_encoding = mod.font_encoding
        self.latex_encoding = self.to_latex_encoding(mod.output_encoding)

    def to_latex_encoding(self,docutils_encoding):
        """
        Translate docutils encoding name into latex's.

        Default fallback method is remove "-" and "_" chars from docutils_encoding.

        """
        tr = {  "iso-8859-1": "latin1",     # west european
                "iso-8859-2": "latin2",     # east european
                "iso-8859-3": "latin3",     # esperanto, maltese
                "iso-8859-4": "latin4",     # north european,scandinavian, baltic
                "iso-8859-5": "iso88595",   # cyrillic (ISO)
                "iso-8859-9": "latin5",     # turkish
                "iso-8859-15": "latin9",    # latin9, update to latin1.
                "mac_cyrillic": "maccyr",   # cyrillic (on Mac)
                "windows-1251": "cp1251",   # cyrillic (on Windows)
                "koi8-r": "koi8-r",         # cyrillic (Russian)
                "koi8-u": "koi8-u",         # cyrillic (Ukrainian)
                "windows-1250": "cp1250",   #
                "windows-1252": "cp1252",   #
                "us-ascii": "ascii",        # ASCII (US)
                # unmatched encodings
                #"": "applemac",
                #"": "ansinew",  # windows 3.1 ansi
                #"": "ascii",    # ASCII encoding for the range 32--127.
                #"": "cp437",    # dos latine us
                #"": "cp850",    # dos latin 1
                #"": "cp852",    # dos latin 2
                #"": "decmulti",
                #"": "latin10",
                #"iso-8859-6": ""   # arabic
                #"iso-8859-7": ""   # greek
                #"iso-8859-8": ""   # hebrew
                #"iso-8859-10": ""   # latin6, more complete iso-8859-4
             }
        if tr.has_key(docutils_encoding.lower()):
            return tr[docutils_encoding.lower()]
        return docutils_encoding.translate(self.mod.string.maketrans("",""),"_-").lower()


    def unicode_to_latex(self,text):
        # see LaTeX codec
        # http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/252124
        # Only some special chracters are translated, for documents with many
        # utf-8 chars one should use the LaTeX unicode package.
        for uchar in self.latex_equivalents.keys():
            text = text.replace(uchar,self.latex_equivalents[uchar])
        return text

    def encode(self, text):
        """
        Encode special characters in `text` & return.
            # $ % & ~ _ ^ \ { }
        Escaping with a backslash does not help with backslashes, ~ and ^.

            < > are only available in math-mode or tt font. (really ?)
            $ starts math- mode.
        AND quotes:

        """
        if self.verbatim:
            return text
        # compile the regexps once. do it here so one can see them.
        #
        # first the braces.
        if not self.__dict__.has_key('encode_re_braces'):
            self.encode_re_braces = self.re.compile(r'([{}])')
        text = self.encode_re_braces.sub(r'{\\\1}',text)
        if not self.__dict__.has_key('encode_re_bslash'):
            # find backslash: except in the form '{\{}' or '{\}}'.
            self.encode_re_bslash = self.re.compile(r'(?<!{)(\\)(?![{}]})')
        # then the backslash: except in the form from line above:
        # either '{\{}' or '{\}}'.
        text = self.encode_re_bslash.sub(r'{\\textbackslash}', text)

        # then dollar
        text = text.replace("$", '{\\$}')
        if not ( self.literal_block or self.literal or self.mathmode ):
            # the vertical bar: in mathmode |,\vert or \mid
            #   in textmode \textbar
            text = text.replace("|", '{\\textbar}')
            text = text.replace("<", '{\\textless}')
            text = text.replace(">", '{\\textgreater}')
        # then
        text = text.replace("&", '{\\&}')
        # the ^:
        # * verb|^| does not work in mbox.
        # * mathmode has wedge. hat{~} would also work.
        # text = text.replace("^", '{\\ensuremath{^\\wedge}}')
        text = text.replace("^", '{\\textasciicircum}')
        text = text.replace("%", '{\\%}')
        text = text.replace("#", '{\\#}')
        text = text.replace("~", '{\\textasciitilde}')
        # Separate compound characters, e.g. "--" to "-{}-".  (The
        # actual separation is done later; see below.)
        separate_chars = '-'
        if self.literal_block or self.literal:
            # In monospace-font, we also separate ",,", "``" and "''"
            # and some other characters which can't occur in
            # non-literal text.
            separate_chars += ',`\'"<>'
            # pdflatex does not produce doublequotes for ngerman.
            text = self.babel.double_quotes_in_tt(text)
            if self.font_encoding == 'OT1':
                # We're using OT1 font-encoding and have to replace
                # underscore by underlined blank, because this has
                # correct width.
                text = text.replace('_', '{\\underline{ }}')
                # And the tt-backslash doesn't work in OT1, so we use
                # a mirrored slash.
                text = text.replace('\\textbackslash', '\\reflectbox{/}')
            else:
                text = text.replace('_', '{\\_}')
        else:
            text = self.babel.quote_quotes(text)
            text = text.replace("_", '{\\_}')
        for char in separate_chars * 2:
            # Do it twice ("* 2") becaues otherwise we would replace
            # "---" by "-{}--".
            text = text.replace(char + char, char + '{}' + char)
        if self.insert_newline or self.literal_block:
            # Insert a blank before the newline, to avoid
            # ! LaTeX Error: There's no line here to end.
            text = text.replace("\n", '~\\\\\n')
        elif self.mbox_newline:
            if self.literal_block:
                closings = "}" * len(self.literal_block_stack)
                openings = "".join(self.literal_block_stack)
            else:
                closings = ""
                openings = ""
            text = text.replace("\n", "%s}\\\\\n\\mbox{%s" % (closings,openings))
        # lines starting with "[" give errors.
        text = text.replace('[', '{[}')
        if self.insert_none_breaking_blanks:
            text = text.replace(' ', '~')
        if self.latex_encoding != 'utf8':
            text = self.unicode_to_latex(text)
        return text



class _GLUECLAMP_:
    _imports_ = (
	'_parent:SpecNodes',
	'_parent.SpecNodes:node_of_taci',
	'_parent.Main:ReportedError',
	'_root:re',
	'_root:string',
	)

    font_encoding = ''
    double_quote_replacment = ''
    language_code = ''
    output_encoding = ''

    section_table = {
	0:'part',
	1:'chapter',
	2:'section',
	3:'subsection',
	4:'subsubsection',
	5:'paragraph',
	6:'subparagraph'
	}

    def doc2text(self, doc, node):
	d2l = Doc2Latex(self, doc, node)
	return d2l.get_latex()

    def doc2filer(self, doc, node, name, dir, opts, IO):
	text = self.doc2text(doc, node)
	path = IO.path.join(dir, '%s.tex'%name)
	node = self.node_of_taci('write_file', path, [self.node_of_taci('text', text)])
	return node



