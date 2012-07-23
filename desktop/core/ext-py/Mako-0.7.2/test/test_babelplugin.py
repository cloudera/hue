
from test import TemplateTest, template_base, skip_if

try:
    import babel
    from mako.ext.babelplugin import extract
except:
    babel = None
 
import os


class ExtractMakoTestCase(TemplateTest):
    @skip_if(lambda: not babel, 'babel not installed: skipping babelplugin test')
 
    def test_extract(self):
        mako_tmpl = open(os.path.join(template_base, 'gettext.mako'))
        messages = list(extract(mako_tmpl, {'_': None, 'gettext': None,
                                            'ungettext': (1, 2)},
                                ['TRANSLATOR:'], {}))
        expected = \
            [(1, '_', u'Page arg 1', []),
             (1, '_', u'Page arg 2', []),
             (10, 'gettext', u'Begin', []),
             (14, '_', u'Hi there!', [u'TRANSLATOR: Hi there!']),
             (19, '_', u'Hello', []),
             (22, '_', u'Welcome', []),
             (25, '_', u'Yo', []),
             (36, '_', u'The', [u'TRANSLATOR: Ensure so and', u'so, thanks']),
             (36, 'ungettext', (u'bunny', u'bunnies', None), []),
             (41, '_', u'Goodbye', [u'TRANSLATOR: Good bye']),
             (44, '_', u'Babel', []),
             (45, 'ungettext', (u'hella', u'hellas', None), []),
            (62, '_', u'The', [u'TRANSLATOR: Ensure so and', u'so, thanks']),
            (62, 'ungettext', (u'bunny', u'bunnies', None), []),
            (68, '_', u'Goodbye, really!', [u'TRANSLATOR: HTML comment']),
            (71, '_', u'P.S. byebye', []),
            (77, '_', u'Top', []),
            (83, '_', u'foo', []),
            (83, '_', u'baz', []),
            (85, '_', u'bar', [])
             ]
        self.assertEqual(expected, messages)

