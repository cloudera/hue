MarkupSafe
==========

Implements a unicode subclass that supports HTML strings:

>>> from markupsafe import Markup, escape
>>> escape("<script>alert(document.cookie);</script>")
Markup(u'&lt;script&gt;alert(document.cookie);&lt;/script&gt;')
>>> tmpl = Markup("<em>%s</em>")
>>> tmpl % "Peter > Lustig"
Markup(u'<em>Peter &gt; Lustig</em>')

If you want to make an object unicode that is not yet unicode
but don't want to lose the taint information, you can use the
`soft_unicode` function:

>>> from markupsafe import soft_unicode
>>> soft_unicode(42)
u'42'
>>> soft_unicode(Markup('foo'))
Markup(u'foo')

Objects can customize their HTML markup equivalent by overriding
the `__html__` function:

>>> class Foo(object):
...  def __html__(self):
...   return '<strong>Nice</strong>'
...
>>> escape(Foo())
Markup(u'<strong>Nice</strong>')
>>> Markup(Foo())
Markup(u'<strong>Nice</strong>')
