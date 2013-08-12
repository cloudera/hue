
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
            [(1, '_', 'Page arg 1', []),
             (1, '_', 'Page arg 2', []),
             (10, 'gettext', 'Begin', []),
             (14, '_', 'Hi there!', ['TRANSLATOR: Hi there!']),
             (19, '_', 'Hello', []),
             (22, '_', 'Welcome', []),
             (25, '_', 'Yo', []),
             (36, '_', 'The', ['TRANSLATOR: Ensure so and', 'so, thanks']),
             (36, 'ungettext', ('bunny', 'bunnies', None), []),
             (41, '_', 'Goodbye', ['TRANSLATOR: Good bye']),
             (44, '_', 'Babel', []),
             (45, 'ungettext', ('hella', 'hellas', None), []),
            (62, '_', 'The', ['TRANSLATOR: Ensure so and', 'so, thanks']),
            (62, 'ungettext', ('bunny', 'bunnies', None), []),
            (68, '_', 'Goodbye, really!', ['TRANSLATOR: HTML comment']),
            (71, '_', 'P.S. byebye', []),
            (77, '_', 'Top', []),
            (83, '_', 'foo', []),
            (83, '_', 'baz', []),
            (85, '_', 'bar', [])
             ]
        self.assertEqual(expected, messages)

