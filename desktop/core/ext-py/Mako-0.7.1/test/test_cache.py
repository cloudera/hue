from mako.template import Template
from mako.lookup import TemplateLookup
from mako import lookup
import shutil, unittest, os, time
from util import result_lines
from test import TemplateTest, template_base, module_base
from test import eq_

try:
    import beaker
    import beaker.cache
except:
    from nose import SkipTest
    raise SkipTest("Beaker is required for these tests.")

from mako.cache import register_plugin, CacheImpl

class MockCacheImpl(CacheImpl):
    realcacheimpl = None

    def __init__(self, cache):
        self.cache = cache
        use_beaker = self.cache.\
                    template.cache_args.\
                    get('use_beaker', True)
        if use_beaker:
            self.realcacheimpl = cache._load_impl("beaker")

    def get_or_create(self, key, creation_function, **kw):
        self.key = key
        self.kwargs = kw.copy()
        if self.realcacheimpl:
            return self.realcacheimpl.\
                    get_or_create(key, creation_function, **kw)
        else:
            return creation_function()

    def put(self, key, value, **kw):
        self.key = key
        self.kwargs = kw.copy()
        if self.realcacheimpl:
            self.realcacheimpl.put(key, value, **kw)

    def get(self, key, **kw):
        self.key = key
        self.kwargs = kw.copy()
        if self.realcacheimpl:
            return self.realcacheimpl.get(key, **kw)

    def invalidate(self, key, **kw):
        self.key = key
        self.kwargs = kw.copy()
        if self.realcacheimpl:
            self.realcacheimpl.invalidate(key, **kw)


register_plugin("mock", __name__, "MockCacheImpl")

class BeakerCacheTest(TemplateTest):
    def _regions(self):
        return beaker.cache.CacheManager(
            cache_regions = {
                'short':{
                    'expire':1,
                    'type':'memory'
                },
                'long':{
                    'expire':60,
                    'type':'memory'
                }
            }
        )

    def test_region(self):
        t = Template("""
            <%block name="foo" cached="True" cache_region="short">
                short term ${x}
            </%block>
            <%block name="bar" cached="True" cache_region="long">
                long term ${x}
            </%block>
            <%block name="lala">
                none ${x}
            </%block>
        """, cache_args={"manager":self._regions()})

        r1 = result_lines(t.render(x=5))
        time.sleep(2)
        r2 = result_lines(t.render(x=6))
        r3 = result_lines(t.render(x=7))
        eq_(r1, ["short term 5", "long term 5", "none 5"])
        eq_(r2, ["short term 6", "long term 5", "none 6"])
        eq_(r3, ["short term 6", "long term 5", "none 7"])

class CacheTest(TemplateTest):
    def _install_mock_cache(self, template):
        template.cache_impl = 'mock'
        return template.cache.impl

    def test_def(self):
        t = Template("""
        <%!
            callcount = [0]
        %>
        <%def name="foo()" cached="True">
            this is foo
            <%
            callcount[0] += 1
            %>
        </%def>

        ${foo()}
        ${foo()}
        ${foo()}
        callcount: ${callcount}
""")
        m = self._install_mock_cache(t)
        assert result_lines(t.render()) == [
            'this is foo',
            'this is foo',
            'this is foo',
            'callcount: [1]',
        ]
        assert m.kwargs == {}

    def test_cache_enable(self):
        t = Template("""
            <%!
                callcount = [0]
            %>
            <%def name="foo()" cached="True">
                <% callcount[0] += 1 %>
            </%def>
            ${foo()}
            ${foo()}
            callcount: ${callcount}
        """, cache_enabled=False)
        m = self._install_mock_cache(t)

        eq_(t.render().strip(), "callcount: [2]")

    def test_nested_def(self):
        t = Template("""
        <%!
            callcount = [0]
        %>
        <%def name="foo()">
            <%def name="bar()" cached="True">
                this is foo
                <%
                callcount[0] += 1
                %>
            </%def>
            ${bar()}
        </%def>

        ${foo()}
        ${foo()}
        ${foo()}
        callcount: ${callcount}
""")
        m = self._install_mock_cache(t)
        assert result_lines(t.render()) == [
            'this is foo',
            'this is foo',
            'this is foo',
            'callcount: [1]',
        ]
        assert m.kwargs == {}

    def test_page(self):
        t = Template("""
        <%!
            callcount = [0]
        %>
        <%page cached="True"/>
        this is foo
        <%
        callcount[0] += 1
        %>
        callcount: ${callcount}
""")
        m = self._install_mock_cache(t)
        t.render()
        t.render()
        assert result_lines(t.render()) == [
            "this is foo",
            "callcount: [1]"
        ]
        assert m.kwargs == {}

    def test_dynamic_key_with_context(self):
        t = Template("""
            <%block name="foo" cached="True" cache_key="${mykey}">
                some block
            </%block>
        """)
        m = self._install_mock_cache(t)
        t.render(mykey="thekey")
        t.render(mykey="thekey")
        eq_(
            result_lines(t.render(mykey="thekey")),
            ["some block"]
        )
        eq_(m.key, "thekey")

        t = Template("""
            <%def name="foo()" cached="True" cache_key="${mykey}">
                some def
            </%def>
            ${foo()}
        """)
        m = self._install_mock_cache(t)
        t.render(mykey="thekey")
        t.render(mykey="thekey")
        eq_(
            result_lines(t.render(mykey="thekey")),
            ["some def"]
        )
        eq_(m.key, "thekey")


    def test_dynamic_key_with_funcargs(self):
        t = Template("""
            <%def name="foo(num=5)" cached="True" cache_key="foo_${str(num)}">
             hi
            </%def>

            ${foo()}
        """)
        m = self._install_mock_cache(t)
        t.render()
        t.render()
        assert result_lines(t.render()) == ['hi']
        assert m.key == "foo_5"

        t = Template("""
            <%def name="foo(*args, **kwargs)" cached="True" cache_key="foo_${kwargs['bar']}">
             hi
            </%def>

            ${foo(1, 2, bar='lala')}
        """)
        m = self._install_mock_cache(t)
        t.render()
        assert result_lines(t.render()) == ['hi']
        assert m.key == "foo_lala"

        t = Template('''
        <%page args="bar='hi'" cache_key="foo_${bar}" cached="True"/>
         hi
        ''')
        m = self._install_mock_cache(t)
        t.render()
        assert result_lines(t.render()) == ['hi']
        assert m.key == "foo_hi"


    def test_dynamic_key_with_imports(self):
        lookup = TemplateLookup()
        lookup.put_string("foo.html", """
        <%!
            callcount = [0]
        %>
        <%namespace file="ns.html" import="*"/>
        <%page cached="True" cache_key="${foo}"/>
        this is foo
        <%
        callcount[0] += 1
        %>
        callcount: ${callcount}
""")
        lookup.put_string("ns.html", """""")
        t = lookup.get_template("foo.html")
        m = self._install_mock_cache(t)
        t.render(foo='somekey')
        t.render(foo='somekey')
        assert result_lines(t.render(foo='somekey')) == [
            "this is foo",
            "callcount: [1]"
        ]
        assert m.kwargs == {}

    def test_fileargs_implicit(self):
        l = lookup.TemplateLookup(module_directory=module_base)
        l.put_string("test","""
                <%!
                    callcount = [0]
                %>
                <%def name="foo()" cached="True" cache_type='dbm'>
                    this is foo
                    <%
                    callcount[0] += 1
                    %>
                </%def>

                ${foo()}
                ${foo()}
                ${foo()}
                callcount: ${callcount}
        """)

        m = self._install_mock_cache(l.get_template('test'))
        assert result_lines(l.get_template('test').render()) == [
            'this is foo',
            'this is foo',
            'this is foo',
            'callcount: [1]',
        ]
        eq_(m.kwargs, {'type':'dbm'})

    def test_fileargs_deftag(self):
        t = Template("""
        <%%!
            callcount = [0]
        %%>
        <%%def name="foo()" cached="True" cache_type='file' cache_dir='%s'>
            this is foo
            <%%
            callcount[0] += 1
            %%>
        </%%def>

        ${foo()}
        ${foo()}
        ${foo()}
        callcount: ${callcount}
""" % module_base)
        m = self._install_mock_cache(t)
        assert result_lines(t.render()) == [
            'this is foo',
            'this is foo',
            'this is foo',
            'callcount: [1]',
        ]
        assert m.kwargs == {'type':'file','dir':module_base}

    def test_fileargs_pagetag(self):
        t = Template("""
        <%%page cache_dir='%s' cache_type='dbm'/>
        <%%!
            callcount = [0]
        %%>
        <%%def name="foo()" cached="True">
            this is foo
            <%%
            callcount[0] += 1
            %%>
        </%%def>

        ${foo()}
        ${foo()}
        ${foo()}
        callcount: ${callcount}
""" % module_base)
        m = self._install_mock_cache(t)
        assert result_lines(t.render()) == [
            'this is foo',
            'this is foo',
            'this is foo',
            'callcount: [1]',
        ]
        eq_(m.kwargs, {'dir':module_base, 'type':'dbm'})

    def test_args_complete(self):
        t = Template("""
        <%%def name="foo()" cached="True" cache_timeout="30" cache_dir="%s" cache_type="file" cache_key='somekey'>
            this is foo
        </%%def>

        ${foo()}
""" % module_base)
        m = self._install_mock_cache(t)
        t.render()
        eq_(m.kwargs, {'dir':module_base, 'type':'file', 'timeout':30})

        t2 = Template("""
        <%%page cached="True" cache_timeout="30" cache_dir="%s" cache_type="file" cache_key='somekey'/>
        hi
        """ % module_base)
        m = self._install_mock_cache(t2)
        t2.render()
        eq_(m.kwargs, {'dir':module_base, 'type':'file', 'timeout':30})

    def test_fileargs_lookup(self):
        l = lookup.TemplateLookup(cache_dir=module_base, cache_type='file')
        l.put_string("test","""
                <%!
                    callcount = [0]
                %>
                <%def name="foo()" cached="True">
                    this is foo
                    <%
                    callcount[0] += 1
                    %>
                </%def>

                ${foo()}
                ${foo()}
                ${foo()}
                callcount: ${callcount}
        """)

        t = l.get_template('test')
        m = self._install_mock_cache(t)
        assert result_lines(l.get_template('test').render()) == [
            'this is foo',
            'this is foo',
            'this is foo',
            'callcount: [1]',
        ]
        eq_(m.kwargs, {'dir':module_base, 'type':'file'})

    def test_buffered(self):
        t = Template("""
        <%!
            def a(text):
                return "this is a " + text.strip()
        %>
        ${foo()}
        ${foo()}
        <%def name="foo()" cached="True" buffered="True">
            this is a test
        </%def>
        """, buffer_filters=["a"])
        assert result_lines(t.render()) == ["this is a this is a test", "this is a this is a test"]

    def test_load_from_expired(self):
        """test that the cache callable can be called safely after the
        originating template has completed rendering.

        """
        t = Template("""
        ${foo()}
        <%def name="foo()" cached="True" cache_timeout="2">
            foo
        </%def>
        """)

        x1 = t.render()
        time.sleep(3)
        x2 = t.render()
        assert x1.strip() == x2.strip() == "foo"

    def test_cache_uses_current_context(self):
        t = Template("""
        ${foo()}
        <%def name="foo()" cached="True" cache_timeout="2">
            foo: ${x}
        </%def>
        """)

        x1 = t.render(x=1)
        time.sleep(3)
        x2 = t.render(x=2)
        eq_(x1.strip(), "foo: 1")
        eq_(x2.strip(), "foo: 2")

    def test_namespace_access(self):
        t = Template("""
            <%def name="foo(x)" cached="True">
                foo: ${x}
            </%def>

            <%
                foo(1)
                foo(2)
                local.cache.invalidate_def('foo')
                foo(3)
                foo(4)
            %>
        """)
        assert result_lines(t.render()) == ['foo: 1', 'foo: 1', 'foo: 3', 'foo: 3']

    def test_lookup(self):
        l = TemplateLookup(cache_impl='mock')
        l.put_string("x", """
            <%page cached="True" />
            ${y}
        """)
        t = l.get_template("x")
        assert result_lines(t.render(y=5)) == ["5"]
        assert result_lines(t.render(y=7)) == ["5"]
        assert isinstance(t.cache.impl, MockCacheImpl)

    def test_invalidate(self):
        t = Template("""
            <%%def name="foo()" cached="True">
                foo: ${x}
            </%%def>

            <%%def name="bar()" cached="True" cache_type='dbm' cache_dir='%s'>
                bar: ${x}
            </%%def>
            ${foo()} ${bar()}
        """ % module_base)
        assert result_lines(t.render(x=1)) == ["foo: 1", "bar: 1"]
        assert result_lines(t.render(x=2)) == ["foo: 1", "bar: 1"]
        t.cache.invalidate_def('foo')
        assert result_lines(t.render(x=3)) == ["foo: 3", "bar: 1"]
        t.cache.invalidate_def('bar')
        assert result_lines(t.render(x=4)) == ["foo: 3", "bar: 4"]

        t = Template("""
            <%%page cached="True" cache_type="dbm" cache_dir="%s"/>

            page: ${x}
        """ % module_base)
        assert result_lines(t.render(x=1)) == ["page: 1"]
        assert result_lines(t.render(x=2)) == ["page: 1"]
        t.cache.invalidate_body()
        assert result_lines(t.render(x=3)) == ["page: 3"]
        assert result_lines(t.render(x=4)) == ["page: 3"]

    def test_custom_args_def(self):
        t = Template("""
            <%def name="foo()" cached="True" cache_region="myregion"
                    cache_timeout="50" cache_foo="foob">
            </%def>
            ${foo()}
        """, cache_args={'use_beaker':False})
        m = self._install_mock_cache(t)
        t.render()
        eq_(m.kwargs, {'use_beaker':False,'region':'myregion', 'timeout':50, 'foo':'foob'})

    def test_custom_args_block(self):
        t = Template("""
            <%block name="foo" cached="True" cache_region="myregion"
                    cache_timeout="50" cache_foo="foob">
            </%block>
        """, cache_args={'use_beaker':False})
        m = self._install_mock_cache(t)
        t.render()
        eq_(m.kwargs, {'use_beaker':False, 'region':'myregion', 'timeout':50, 'foo':'foob'})

    def test_custom_args_page(self):
        t = Template("""
            <%page cached="True" cache_region="myregion"
                    cache_timeout="50" cache_foo="foob"/>
        """, cache_args={'use_beaker':False})
        m = self._install_mock_cache(t)
        t.render()
        eq_(m.kwargs, {'use_beaker':False, 'region':'myregion', 'timeout':50, 'foo':'foob'})

    def test_pass_context(self):
        t = Template("""
            <%page cached="True"/>
        """)
        m = self._install_mock_cache(t)
        t.render()
        assert 'context' not in m.kwargs

        m.pass_context = True
        t.render(x="bar")
        assert 'context' in m.kwargs
        assert m.kwargs['context'].get('x') == 'bar'

