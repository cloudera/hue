import unittest

from mako.lexer import Lexer
from mako import exceptions, util
from util import flatten_result, result_lines
from mako.template import Template
import re
from test import TemplateTest, template_base, skip_if, eq_, assert_raises_message

# create fake parsetree classes which are constructed
# exactly as the repr() of a real parsetree object.
# this allows us to use a Python construct as the source
# of a comparable repr(), which is also hit by the 2to3 tool.

def repr_arg(x):
    if isinstance(x, dict):
        return util.sorted_dict_repr(x)
    else:
        return repr(x)

from mako import parsetree
for cls in parsetree.__dict__.values():
    if isinstance(cls, type) and \
        issubclass(cls, parsetree.Node):
        clsname = cls.__name__
        exec ("""
class %s(object):
    def __init__(self, *args):
        self.args = args
    def __repr__(self):
        return "%%s(%%s)" %% (
            self.__class__.__name__,
            ", ".join(repr_arg(x) for x in self.args)
            )
""" % clsname) in locals()

# NOTE: most assertion expressions were generated, then formatted
# by PyTidy, hence the dense formatting.

class LexerTest(TemplateTest):

    def _compare(self, node, expected):
        eq_(repr(node), repr(expected))

    def test_text_and_tag(self):
        template = """
<b>Hello world</b>
        <%def name="foo()">
                this is a def.
        </%def>
        
        and some more text.
"""
        node = Lexer(template).parse()
        self._compare(node, TemplateNode({},
                      [Text(u'''\n<b>Hello world</b>\n        ''', (1,
                      1)), DefTag(u'def', {u'name': u'foo()'}, (3, 9),
                      [Text(u'''\n                this is a def.\n        ''',
                      (3, 28))]),
                      Text(u'''\n        \n        and some more text.\n''',
                      (5, 16))]))

    def test_unclosed_tag(self):
        template = """
        
            <%def name="foo()">
             other text
        """
        try:
            nodes = Lexer(template).parse()
            assert False
        except exceptions.SyntaxException, e:
            assert str(e) == "Unclosed tag: <%def> at line: 5 char: 9"

    def test_onlyclosed_tag(self):
        template = \
            """
            <%def name="foo()">
                foo
            </%def>
            
            </%namespace>
            
            hi.
        """
        self.assertRaises(exceptions.SyntaxException,
                          Lexer(template).parse)

    def test_noexpr_allowed(self):
        template = \
            """
            <%namespace name="${foo}"/>
        """
        self.assertRaises(exceptions.CompileException,
                          Lexer(template).parse)

    def test_unmatched_tag(self):
        template = \
            """
        <%namespace name="bar">
        <%def name="foo()">
            foo
            </%namespace>
        </%def>
        
        
        hi.
"""
        self.assertRaises(exceptions.SyntaxException,
                          Lexer(template).parse)

    def test_nonexistent_tag(self):
        template = """
            <%lala x="5"/>
        """
        self.assertRaises(exceptions.CompileException,
                          Lexer(template).parse)

    def test_wrongcase_tag(self):
        template = \
            """
            <%DEF name="foo()">
            </%def>
        
        """
        self.assertRaises(exceptions.CompileException,
                          Lexer(template).parse)

    def test_percent_escape(self):
        template = \
            """
        
%% some whatever.

    %% more some whatever
    % if foo:
    % endif
        """
        node = Lexer(template).parse()
        self._compare(node, TemplateNode({}, [Text(u'''\n        \n''',
                      (1, 1)), Text(u'''% some whatever.\n\n''', (3, 2)),
                      Text(u'   %% more some whatever\n', (5, 2)),
                      ControlLine(u'if', u'if foo:', False, (6, 1)),
                      ControlLine(u'if', u'endif', True, (7, 1)),
                      Text(u'        ', (8, 1))]))

    def test_text_tag(self):
        template = \
            """
        ## comment
        % if foo:
            hi
        % endif
        <%text>
            # more code
            
            % more code
            <%illegal compionent>/></>
            <%def name="laal()">def</%def>
            
            
        </%text>

        <%def name="foo()">this is foo</%def>
        
        % if bar:
            code
        % endif
        """
        node = Lexer(template).parse()
        self._compare(node, 
            TemplateNode({}, [Text(u'\n', (1, 1)),
              Comment(u'comment', (2, 1)), 
              ControlLine(u'if', u'if foo:', False, (3, 1)),
              Text(u'            hi\n', (4, 1)),
              ControlLine(u'if', u'endif', True, (5, 1)),
              Text(u'        ', (6, 1)), TextTag(u'text', {},
              (6, 9),
              [Text(u'''\n            # more code\n            '''
              '''\n            % more code\n            '''
              '''<%illegal compionent>/></>\n            '''
              '''<%def name="laal()">def</%def>\n       '''
              '''     \n            \n        ''',
                      (6, 16))]), Text(u'''

        ''', (14, 17)),
                      DefTag(u'def', {u'name': u'foo()'}, (16, 9),
                      [Text(u'this is foo', (16, 28))]),
                      Text(u'''\n        \n''', (16, 46)),
                      ControlLine(u'if', u'if bar:', False, (18, 1)),
                      Text(u'            code\n', (19, 1)),
                      ControlLine(u'if', u'endif', True, (20, 1)),
                      Text(u'        ', (21, 1))]))

    def test_def_syntax(self):
        template = \
            """
        <%def lala>
            hi
        </%def>
"""
        self.assertRaises(exceptions.CompileException,
                          Lexer(template).parse)

    def test_def_syntax_2(self):
        template = \
            """
        <%def name="lala">
            hi
        </%def>
    """
        self.assertRaises(exceptions.CompileException,
                          Lexer(template).parse)

    def test_whitespace_equals(self):
        template = \
            """
            <%def name = "adef()" >
              adef
            </%def>
        """
        node = Lexer(template).parse()
        self._compare(node, TemplateNode({}, [Text(u'\n            ',
                      (1, 1)), DefTag(u'def', {u'name': u'adef()'}, (2,
                      13),
                      [Text(u'''\n              adef\n            ''',
                      (2, 36))]), Text(u'\n        ', (4, 20))]))

    def test_ns_tag_closed(self):
        template = \
            """
        
            <%self:go x="1" y="2" z="${'hi' + ' ' + 'there'}"/>
        """
        nodes = Lexer(template).parse()
        self._compare(nodes, TemplateNode({},
                      [Text(u'''
        
            ''', (1, 1)),
                      CallNamespaceTag(u'self:go', {u'x': u'1', u'y'
                      : u'2', u'z': u"${'hi' + ' ' + 'there'}"}, (3,
                      13), []), Text(u'\n        ', (3, 64))]))

    def test_ns_tag_empty(self):
        template = \
            """
            <%form:option value=""></%form:option>
        """
        nodes = Lexer(template).parse()
        self._compare(nodes, TemplateNode({}, [Text(u'\n            ',
                      (1, 1)), CallNamespaceTag(u'form:option',
                      {u'value': u''}, (2, 13), []), Text(u'\n        '
                      , (2, 51))]))

    def test_ns_tag_open(self):
        template = \
            """
        
            <%self:go x="1" y="${process()}">
                this is the body
            </%self:go>
        """
        nodes = Lexer(template).parse()
        self._compare(nodes, TemplateNode({},
                      [Text(u'''
        
            ''', (1, 1)),
                      CallNamespaceTag(u'self:go', {u'x': u'1', u'y'
                      : u'${process()}'}, (3, 13),
                      [Text(u'''
                this is the body
            ''',
                      (3, 46))]), Text(u'\n        ', (5, 24))]))

    def test_expr_in_attribute(self):
        """test some slightly trickier expressions.
        
        you can still trip up the expression parsing, though, unless we
        integrated really deeply somehow with AST."""

        template = \
            """
            <%call expr="foo>bar and 'lala' or 'hoho'"/>
            <%call expr='foo<bar and hoho>lala and "x" + "y"'/>
        """
        nodes = Lexer(template).parse()
        self._compare(nodes, TemplateNode({}, [Text(u'\n            ',
                      (1, 1)), CallTag(u'call', {u'expr'
                      : u"foo>bar and 'lala' or 'hoho'"}, (2, 13), []),
                      Text(u'\n            ', (2, 57)), CallTag(u'call'
                      , {u'expr': u'foo<bar and hoho>lala and "x" + "y"'
                      }, (3, 13), []), Text(u'\n        ', (3, 64))]))

    def test_pagetag(self):
        template = \
            """
            <%page cached="True", args="a, b"/>
            
            some template
        """
        nodes = Lexer(template).parse()
        self._compare(nodes, TemplateNode({}, [Text(u'\n            ',
                      (1, 1)), PageTag(u'page', {u'args': u'a, b',
                      u'cached': u'True'}, (2, 13), []),
                      Text(u'''
            
            some template
        ''',
                      (2, 48))]))

    def test_nesting(self):
        template = \
            """
        
        <%namespace name="ns">
            <%def name="lala(hi, there)">
                <%call expr="something()"/>
            </%def>
        </%namespace>
        
        """
        nodes = Lexer(template).parse()
        self._compare(nodes, TemplateNode({},
                      [Text(u'''
        
        ''', (1, 1)),
                      NamespaceTag(u'namespace', {u'name': u'ns'}, (3,
                      9), [Text(u'\n            ', (3, 31)),
                      DefTag(u'def', {u'name': u'lala(hi, there)'}, (4,
                      13), [Text(u'\n                ', (4, 42)),
                      CallTag(u'call', {u'expr': u'something()'}, (5,
                      17), []), Text(u'\n            ', (5, 44))]),
                      Text(u'\n        ', (6, 20))]),
                      Text(u'''
        
        ''', (7, 22))]))

    if util.py3k:
        def test_code(self):
            template = \
"""text
    <%
        print("hi")
        for x in range(1,5):
            print(x)
    %>
more text
    <%!
        import foo
    %>
"""
            nodes = Lexer(template).parse()
            self._compare(nodes, 
            TemplateNode({}, [
                Text(u'text\n    ', (1, 1)), 
                Code(u'\nprint("hi")\nfor x in range(1,5):\n    '
                            'print(x)\n    \n', False, (2, 5)), 
                Text(u'\nmore text\n    ', (6, 7)), 
                Code(u'\nimport foo\n    \n', True, (8, 5)), 
                Text(u'\n', (10, 7))])
            )


    else:

        def test_code(self):
            template = \
"""text
    <%
        print "hi"
        for x in range(1,5):
            print x
    %>
more text
    <%!
        import foo
    %>
"""
            nodes = Lexer(template).parse()
            self._compare(nodes, 
            TemplateNode({}, [
                Text(u'text\n    ', (1, 1)), 
                Code(u'\nprint "hi"\nfor x in range(1,5):\n    '
                            'print x\n    \n', False, (2, 5)), 
                Text(u'\nmore text\n    ', (6, 7)), 
                Code(u'\nimport foo\n    \n', True, (8, 5)), 
                Text(u'\n', (10, 7))])
            )

    def test_code_and_tags(self):
        template = \
            """
<%namespace name="foo">
    <%def name="x()">
        this is x
    </%def>
    <%def name="y()">
        this is y
    </%def>
</%namespace>

<%
    result = []
    data = get_data()
    for x in data:
        result.append(x+7)
%>

    result: <%call expr="foo.x(result)"/>
"""
        nodes = Lexer(template).parse()
        self._compare(nodes, TemplateNode({}, [Text(u'\n', (1, 1)),
                      NamespaceTag(u'namespace', {u'name': u'foo'}, (2,
                      1), [Text(u'\n    ', (2, 24)), DefTag(u'def',
                      {u'name': u'x()'}, (3, 5),
                      [Text(u'''\n        this is x\n    ''', (3, 22))]),
                      Text(u'\n    ', (5, 12)), DefTag(u'def', {u'name'
                      : u'y()'}, (6, 5),
                      [Text(u'''\n        this is y\n    ''', (6, 22))]),
                      Text(u'\n', (8, 12))]), Text(u'''\n\n''', (9, 14)),
                      Code(u'''\nresult = []\ndata = get_data()\n'''
                      '''for x in data:\n    result.append(x+7)\n\n''',
                      False, (11, 1)), Text(u'''\n\n    result: ''', (16,
                      3)), CallTag(u'call', {u'expr': u'foo.x(result)'
                      }, (18, 13), []), Text(u'\n', (18, 42))]))

    def test_expression(self):
        template = \
            """
        this is some ${text} and this is ${textwith | escapes, moreescapes}
        <%def name="hi()">
            give me ${foo()} and ${bar()}
        </%def>
        ${hi()}
"""
        nodes = Lexer(template).parse()
        self._compare(nodes, TemplateNode({},
                      [Text(u'\n        this is some ', (1, 1)),
                      Expression(u'text', [], (2, 22)),
                      Text(u' and this is ', (2, 29)),
                      Expression(u'textwith ', ['escapes', 'moreescapes'
                      ], (2, 42)), Text(u'\n        ', (2, 76)),
                      DefTag(u'def', {u'name': u'hi()'}, (3, 9),
                      [Text(u'\n            give me ', (3, 27)),
                      Expression(u'foo()', [], (4, 21)), Text(u' and ',
                      (4, 29)), Expression(u'bar()', [], (4, 34)),
                      Text(u'\n        ', (4, 42))]), Text(u'\n        '
                      , (5, 16)), Expression(u'hi()', [], (6, 9)),
                      Text(u'\n', (6, 16))]))


    def test_tricky_expression(self):
        template = """
        
            ${x and "|" or "hi"}
        """
        nodes = Lexer(template).parse()
        self._compare(
            nodes,
            TemplateNode({}, [
                Text(u'\n        \n            ', (1, 1)), 
                Expression(u'x and "|" or "hi"', [], (3, 13)), 
                Text(u'\n        ', (3, 33))
            ])
        )

        template = """
        
            ${hello + '''heres '{|}' text | | }''' | escape1}
        """
        nodes = Lexer(template).parse()
        self._compare(
            nodes,
            TemplateNode({}, [
                Text(u'\n        \n            ', (1, 1)), 
                Expression(u"hello + '''heres '{|}' text | | }''' ", 
                                ['escape1'], (3, 13)), 
                Text(u'\n        ', (3, 62))
            ])
        )

    def test_tricky_code(self):
        if util.py3k:
            template = """<% print('hi %>') %>"""
            nodes = Lexer(template).parse()
            self._compare(nodes, TemplateNode({},
                          [Code(u"print('hi %>') \n", False, (1, 1))]))
        else:
            template = """<% print 'hi %>' %>"""
            nodes = Lexer(template).parse()
            self._compare(nodes, TemplateNode({},
                          [Code(u"print 'hi %>' \n", False, (1, 1))]))

    def test_tricky_code_2(self):
        template = \
            """<% 
        # someone's comment
        %>
        """
        nodes = Lexer(template).parse()
        self._compare(nodes, TemplateNode({},
                      [Code(u""" 
        # someone's comment
        
""",
                      False, (1, 1)), Text(u'\n        ', (3, 11))]))

    if util.py3k:
        def test_tricky_code_3(self):
            template = \
                """<%
            print('hi')
            # this is a comment
            # another comment
            x = 7 # someone's '''comment
            print('''
        there
        ''')
            # someone else's comment
        %> '''and now some text '''"""
            nodes = Lexer(template).parse()
            self._compare(nodes, TemplateNode({},
                          [Code(u"""
print('hi')
# this is a comment
# another comment
x = 7 # someone's '''comment
print('''
        there
        ''')
# someone else's comment
        
""",
                          False, (1, 1)),
                          Text(u" '''and now some text '''", (10,
                          11))]))
    else:
        def test_tricky_code_3(self):
            template = \
                """<%
            print 'hi'
            # this is a comment
            # another comment
            x = 7 # someone's '''comment
            print '''
        there
        '''
            # someone else's comment
        %> '''and now some text '''"""
            nodes = Lexer(template).parse()
            self._compare(nodes, TemplateNode({},
                      [Code(u"""\nprint 'hi'\n# this is a comment\n"""
                      """# another comment\nx = 7 """
                      """# someone's '''comment\nprint '''\n        """
                      """there\n        '''\n# someone else's """
                      """comment\n        \n""",
                      False, (1, 1)),
                      Text(u" '''and now some text '''", (10,11))]))

    def test_tricky_code_4(self):
        template = \
            """<% foo = "\\"\\\\" %>"""
        nodes = Lexer(template).parse()
        self._compare(nodes, TemplateNode({},
                      [Code(u"""foo = "\\"\\\\" \n""",
                      False, (1, 1))]))

    def test_tricky_code_5(self):
        template = \
            """before ${ {'key': 'value'} } after"""
        nodes = Lexer(template).parse()
        self._compare(nodes, TemplateNode({},
                      [Text(u'before ', (1, 1)),
                      Expression(u" {'key': 'value'} ", [], (1, 8)),
                      Text(u' after', (1, 29))]))

    def test_control_lines(self):
        template = \
            """
text text la la
% if foo():
 mroe text la la blah blah
% endif

        and osme more stuff
        % for l in range(1,5):
    tex tesl asdl l is ${l} kfmas d
      % endfor
    tetx text
    
"""
        nodes = Lexer(template).parse()
        self._compare(nodes, TemplateNode({},
                      [Text(u'''\ntext text la la\n''', (1, 1)),
                      ControlLine(u'if', u'if foo():', False, (3, 1)),
                      Text(u' mroe text la la blah blah\n', (4, 1)),
                      ControlLine(u'if', u'endif', True, (5, 1)),
                      Text(u'''\n        and osme more stuff\n''', (6,
                      1)), ControlLine(u'for', u'for l in range(1,5):',
                      False, (8, 1)), Text(u'    tex tesl asdl l is ',
                      (9, 1)), Expression(u'l', [], (9, 24)),
                      Text(u' kfmas d\n', (9, 28)), ControlLine(u'for',
                      u'endfor', True, (10, 1)),
                      Text(u'''    tetx text\n    \n''', (11, 1))]))

    def test_control_lines_2(self):
        template = \
"""% for file in requestattr['toc'].filenames:
    x
% endfor
"""
        nodes = Lexer(template).parse()
        self._compare(nodes, TemplateNode({}, [ControlLine(u'for',
                      u"for file in requestattr['toc'].filenames:",
                      False, (1, 1)), Text(u'    x\n', (2, 1)),
                      ControlLine(u'for', u'endfor', True, (3, 1))]))

    def test_long_control_lines(self):
        template = \
        """
    % for file in \\
        requestattr['toc'].filenames:
        x
    % endfor
        """
        nodes = Lexer(template).parse()
        self._compare(
            nodes,
            TemplateNode({}, [
                Text(u'\n', (1, 1)), 
                ControlLine(u'for', u"for file in \\\n        "
                                "requestattr['toc'].filenames:", 
                                False, (2, 1)), 
                Text(u'        x\n', (4, 1)), 
                ControlLine(u'for', u'endfor', True, (5, 1)), 
                Text(u'        ', (6, 1))
            ])
        )

    def test_unmatched_control(self):
        template = """

        % if foo:
            % for x in range(1,5):
        % endif
"""
        assert_raises_message(
            exceptions.SyntaxException,
            "Keyword 'endif' doesn't match keyword 'for' at line: 5 char: 1",
            Lexer(template).parse
        )

    def test_unmatched_control_2(self):
        template = """

        % if foo:
            % for x in range(1,5):
            % endfor
"""

        assert_raises_message(
            exceptions.SyntaxException,
            "Unterminated control keyword: 'if' at line: 3 char: 1",
            Lexer(template).parse
        )

    def test_unmatched_control_3(self):
        template = """

        % if foo:
            % for x in range(1,5):
            % endlala
        % endif
"""
        assert_raises_message(
            exceptions.SyntaxException,
            "Keyword 'endlala' doesn't match keyword 'for' at line: 5 char: 1",
            Lexer(template).parse
        )

    def test_ternary_control(self):
        template = \
            """
        % if x:
            hi
        % elif y+7==10:
            there
        % elif lala:
            lala
        % else:
            hi
        % endif
"""
        nodes = Lexer(template).parse()
        self._compare(nodes, TemplateNode({}, [Text(u'\n', (1, 1)),
                      ControlLine(u'if', u'if x:', False, (2, 1)),
                      Text(u'            hi\n', (3, 1)),
                      ControlLine(u'elif', u'elif y+7==10:', False, (4,
                      1)), Text(u'            there\n', (5, 1)),
                      ControlLine(u'elif', u'elif lala:', False, (6,
                      1)), Text(u'            lala\n', (7, 1)),
                      ControlLine(u'else', u'else:', False, (8, 1)),
                      Text(u'            hi\n', (9, 1)),
                      ControlLine(u'if', u'endif', True, (10, 1))]))

    def test_integration(self):
        template = \
            """<%namespace name="foo" file="somefile.html"/>
 ## inherit from foobar.html
<%inherit file="foobar.html"/>

<%def name="header()">
     <div>header</div>
</%def>
<%def name="footer()">
    <div> footer</div>
</%def>

<table>
    % for j in data():
    <tr>
        % for x in j:
            <td>Hello ${x| h}</td>
        % endfor
    </tr>
    % endfor
</table>
"""
        nodes = Lexer(template).parse()
        self._compare(nodes, TemplateNode({}, [NamespaceTag(u'namespace'
                      , {u'file': u'somefile.html', u'name': u'foo'},
                      (1, 1), []), Text(u'\n', (1, 46)),
                      Comment(u'inherit from foobar.html', (2, 1)),
                      InheritTag(u'inherit', {u'file': u'foobar.html'},
                      (3, 1), []), Text(u'''\n\n''', (3, 31)),
                      DefTag(u'def', {u'name': u'header()'}, (5, 1),
                      [Text(u'''\n     <div>header</div>\n''', (5,
                      23))]), Text(u'\n', (7, 8)), DefTag(u'def',
                      {u'name': u'footer()'}, (8, 1),
                      [Text(u'''\n    <div> footer</div>\n''', (8,
                      23))]), Text(u'''\n\n<table>\n''', (10, 8)),
                      ControlLine(u'for', u'for j in data():', False,
                      (13, 1)), Text(u'    <tr>\n', (14, 1)),
                      ControlLine(u'for', u'for x in j:', False, (15,
                      1)), Text(u'            <td>Hello ', (16, 1)),
                      Expression(u'x', ['h'], (16, 23)), Text(u'</td>\n'
                      , (16, 30)), ControlLine(u'for', u'endfor', True,
                      (17, 1)), Text(u'    </tr>\n', (18, 1)),
                      ControlLine(u'for', u'endfor', True, (19, 1)),
                      Text(u'</table>\n', (20, 1))]))

    def test_comment_after_statement(self):
        template = \
            """
        % if x: #comment
            hi
        % else: #next
            hi
        % endif #end
"""
        nodes = Lexer(template).parse()
        self._compare(nodes, TemplateNode({}, [Text(u'\n', (1, 1)),
                      ControlLine(u'if', u'if x: #comment', False, (2,
                      1)), Text(u'            hi\n', (3, 1)),
                      ControlLine(u'else', u'else: #next', False, (4,
                      1)), Text(u'            hi\n', (5, 1)),
                      ControlLine(u'if', u'endif #end', True, (6, 1))]))

    def test_crlf(self):
        template = open(self._file_path("crlf.html"), 'rb').read()
        nodes = Lexer(template).parse()
        self._compare(
            nodes,
            TemplateNode({}, [
                Text(u'<html>\r\n\r\n', (1, 1)), 
                PageTag(u'page', {
                            u'args': u"a=['foo',\n                'bar']"
                        }, (3, 1), []), 
                Text(u'\r\n\r\nlike the name says.\r\n\r\n', (4, 26)), 
                ControlLine(u'for', u'for x in [1,2,3]:', False, (8, 1)), 
                Text(u'        ', (9, 1)), 
                Expression(u'x', [], (9, 9)), 
                ControlLine(u'for', u'endfor', True, (10, 1)), 
                Text(u'\r\n', (11, 1)), 
                Expression(u"trumpeter == 'Miles' and "
                                "trumpeter or \\\n      'Dizzy'", 
                                [], (12, 1)), 
                Text(u'\r\n\r\n', (13, 15)), 
                DefTag(u'def', {u'name': u'hi()'}, (15, 1), [
                    Text(u'\r\n    hi!\r\n', (15, 19))]), 
                    Text(u'\r\n\r\n</html>\r\n', (17, 8))
                ])
        )
        assert flatten_result(Template(template).render()) \
            == """<html> like the name says. 1 2 3 Dizzy </html>"""

    def test_comments(self):
        template = \
            """
<style>
 #someselector
 # other non comment stuff
</style>
## a comment

# also not a comment

   ## this is a comment
   
this is ## not a comment

<%doc> multiline
comment
</%doc>

hi
"""
        nodes = Lexer(template).parse()
        self._compare(nodes, TemplateNode({},
                      [Text(u'''\n<style>\n #someselector\n # '''
                        '''other non comment stuff\n</style>\n''',
                      (1, 1)), Comment(u'a comment', (6, 1)),
                      Text(u'''\n# also not a comment\n\n''', (7, 1)),
                      Comment(u'this is a comment', (10, 1)),
                      Text(u'''   \nthis is ## not a comment\n\n''', (11,
                      1)), Comment(u''' multiline\ncomment\n''', (14,
                      1)), Text(u'''

hi
''', (16, 8))]))

    def test_docs(self):
        template = \
            """
        <%doc>
            this is a comment
        </%doc>
        <%def name="foo()">
            <%doc>
                this is the foo func
            </%doc>
        </%def>
        """
        nodes = Lexer(template).parse()
        self._compare(nodes, 
            TemplateNode({}, [Text(u'\n        ', (1,
              1)),
              Comment(u'''\n            this is a comment\n        ''',
              (2, 9)), Text(u'\n        ', (4, 16)),
              DefTag(u'def', {u'name': u'foo()'}, (5, 9),
              [Text(u'\n            ', (5, 28)),
              Comment(u'''\n                this is the foo func\n'''
                '''            ''',
              (6, 13)), Text(u'\n        ', (8, 20))]),
              Text(u'\n        ', (9, 16))]))

    def test_preprocess(self):

        def preproc(text):
            return re.sub(r'(?<=\n)\s*#[^#]', '##', text)

        template = \
            """
    hi
    # old style comment
# another comment
"""
        nodes = Lexer(template, preprocessor=preproc).parse()
        self._compare(nodes, TemplateNode({}, [Text(u'''\n    hi\n''',
                      (1, 1)), Comment(u'old style comment', (3, 1)),
                      Comment(u'another comment', (4, 1))]))
