# -*- coding: utf-8 -*-
import unittest

import pytest

from babel.messages import extract
from babel._compat import BytesIO

import django
from django_babel.extract import extract_django


default_keys = extract.DEFAULT_KEYWORDS.keys()


class ExtractDjangoTestCase(unittest.TestCase):
    # TODO: translator comments are not yet supported!

    def test_extract_no_tags(self):
        buf = BytesIO(b'nothing')
        messages = list(extract_django(buf, default_keys, [], {}))
        self.assertEqual([], messages)

    def test_extract_simple_double_quotes(self):
        buf = BytesIO(b'{% trans "Bunny" %}')
        messages = list(extract_django(buf, default_keys, [], {}))
        self.assertEqual([(1, None, u'Bunny', [])], messages)

    def test_extract_simple_single_quotes(self):
        buf = BytesIO(b"{% trans 'Bunny' %}")
        messages = list(extract_django(buf, default_keys, [], {}))
        self.assertEqual([(1, None, u'Bunny', [])], messages)

    def test_extract_simple_with_context_single_quotes(self):
        buf = BytesIO(b"{% trans 'Bunny' context 'carrot' %}")
        messages = list(extract_django(buf, default_keys, [], {}))
        self.assertEqual([(1, 'pgettext',
                           [u'carrot', u'Bunny'], [])], messages)

    def test_extract_simple_with_context_double_quotes(self):
        buf = BytesIO(b"{% trans 'Bunny' context \"carrot\" %}")
        messages = list(extract_django(buf, default_keys, [], {}))
        self.assertEqual([(1, 'pgettext',
                           [u'carrot', u'Bunny'], [])], messages)

    def test_extract_simple_with_context_with_single_quotes(self):
        buf = BytesIO(b"{% trans 'Bunny' context \"'carrot'\" %}")
        messages = list(extract_django(buf, default_keys, [], {}))
        self.assertEqual([(1, 'pgettext',
                           [u'\'carrot\'', u'Bunny'], [])], messages)

    def test_extract_simple_with_context_with_double_quotes(self):
        buf = BytesIO(b"{% trans 'Bunny' context '\"carrot\"' %}")
        messages = list(extract_django(buf, default_keys, [], {}))
        self.assertEqual([(1, 'pgettext',
                           [u'"carrot"', u'Bunny'], [])], messages)

    def test_extract_var(self):
        buf = BytesIO(b'{% blocktrans %}{{ anton }}{% endblocktrans %}')
        messages = list(extract_django(buf, default_keys, [], {}))
        self.assertEqual([(1, None, u'%(anton)s', [])], messages)

    def test_extract_filter_with_filter(self):
        test_tmpl = (
            b'{% blocktrans with berta=anton|lower %}'
            b'{{ berta }}{% endblocktrans %}'
        )
        buf = BytesIO(test_tmpl)
        messages = list(extract_django(buf, default_keys, [], {}))
        self.assertEqual([(1, None, u'%(berta)s', [])], messages)

    def test_extract_with_interpolation(self):
        buf = BytesIO(b'{% blocktrans %}xxx{{ anton }}xxx{% endblocktrans %}')
        messages = list(extract_django(buf, default_keys, [], {}))
        self.assertEqual([(1, None, u'xxx%(anton)sxxx', [])], messages)

    def test_extract_unicode(self):
        buf = BytesIO(u'{% trans "@ſðæ314“ſſ¶ÐĐÞ→SÆ^ĸŁ" %}'.encode('utf8'))
        messages = list(extract_django(buf, default_keys, [], {}))
        self.assertEqual([(1, None, u'@ſðæ314“ſſ¶ÐĐÞ→SÆ^ĸŁ', [])], messages)

    def test_extract_unicode_blocktrans(self):
        test_tmpl = u'{% blocktrans %}@ſðæ314“ſſ¶ÐĐÞ→SÆ^ĸŁ{% endblocktrans %}'
        buf = BytesIO(test_tmpl.encode('utf8'))
        messages = list(extract_django(buf, default_keys, [], {}))
        self.assertEqual([(1, None, u'@ſðæ314“ſſ¶ÐĐÞ→SÆ^ĸŁ', [])], messages)

    # TODO: Yet expected to not extract the comments.
    def test_extract_ignored_comment(self):
        buf = BytesIO(
            b'{# ignored comment #1 #}{% trans "Translatable literal #9a" %}',
        )
        messages = list(extract_django(buf, default_keys, [], {}))
        self.assertEqual(
            [(1, None, u'Translatable literal #9a', [])], messages
        )

    def test_extract_ignored_comment2(self):
        test_tmpl = (
            b'{# Translators: ignored i18n comment #1 #}'
            b'{% trans "Translatable literal #9a" %}'
        )
        buf = BytesIO(test_tmpl)
        messages = list(extract_django(buf, default_keys, [], {}))
        self.assertEqual(
            [(1, None, u'Translatable literal #9a', [])], messages
        )

    def test_extract_valid_comment(self):
        test_tmpl = (
            b'{# ignored comment #6 #}'
            b'{% trans "Translatable literal #9h" %}'
            b'{# Translators: valid i18n comment #7 #}'
        )
        buf = BytesIO(test_tmpl)
        messages = list(extract_django(buf, default_keys, [], {}))
        self.assertEqual(
            [(1, None, u'Translatable literal #9h', [])], messages
        )

    def test_extract_singular_form(self):
        test_tmpl = (
            b'{% blocktrans count counter=number %}'
            b'singular{% plural %}{{ counter }} plural'
            b'{% endblocktrans %}'
        )
        buf = BytesIO(test_tmpl)
        messages = list(extract_django(buf, default_keys, [], {}))
        self.assertEqual(
            [(1, 'ngettext', (u'singular', u'%(counter)s plural'), [])],
            messages
        )

    def test_trans_blocks_must_not_include_other_block_tags(self):
        buf = BytesIO(b'{% blocktrans %}{% other_tag %}{% endblocktrans %}')
        gen = extract_django(buf, default_keys, [], {})
        with pytest.raises(SyntaxError):
            next(gen)

    def test_extract_var_other(self):
        buf = BytesIO(b'{{ book }}')
        messages = list(extract_django(buf, default_keys, [], {}))
        self.assertEqual([], messages)

    def test_extract_filters_default_translatable(self):
        buf = BytesIO(b'{{ book.author|default:_("Unknown") }}')
        messages = list(extract_django(buf, default_keys, [], {}))
        self.assertEqual([(1, None, u'Unknown', [])], messages)

    def test_extract_filters_default_translatable_single_quotes(self):
        buf = BytesIO(b"{{ book.author|default:_('Unknown') }}")
        messages = list(extract_django(buf, default_keys, [], {}))
        self.assertEqual([(1, None, u'Unknown', [])], messages)

    def test_extract_constant_single_quotes(self):
        buf = BytesIO(b"{{ _('constant') }}")
        messages = list(extract_django(buf, default_keys, [], {}))
        self.assertEqual([(1, None, u'constant', [])], messages)

    def test_extract_constant_double_quotes(self):
        buf = BytesIO(b'{{ _("constant") }}')
        messages = list(extract_django(buf, default_keys, [], {}))
        self.assertEqual([(1, None, u'constant', [])], messages)

    def test_extract_constant_block(self):
        buf = BytesIO(b'{% _("constant") %}')
        messages = list(extract_django(buf, default_keys, [], {}))
        self.assertEqual([(1, None, u'constant', [])], messages)

    def test_extract_constant_in_block(self):
        test_tmpl = (
            b'{% blocktrans foo=_("constant") %}{{ foo }}{% endblocktrans %}'
        )
        buf = BytesIO(test_tmpl)
        messages = list(extract_django(buf, default_keys, [], {}))
        self.assertEqual(
            [(1, None, u'constant', []), (1, None, u'%(foo)s', [])],
            messages,
        )

    def test_extract_context_in_block(self):
        test_tmpl = (
            b'{% blocktrans context "banana" %}{{ foo }}{% endblocktrans %}'
        )
        buf = BytesIO(test_tmpl)
        messages = list(extract_django(buf, default_keys, [], {}))
        self.assertEqual(
            [(1, 'pgettext', [u'banana', u'%(foo)s'], [])],
            messages,
        )

    def test_extract_context_in_plural_block(self):
        test_tmpl = (
            b'{% blocktrans context "banana" %}{{ foo }}'
            b'{% plural %}{{ bar }}{% endblocktrans %}'
        )
        buf = BytesIO(test_tmpl)
        messages = list(extract_django(buf, default_keys, [], {}))
        self.assertEqual(
            [(1, 'npgettext', [u'banana', u'%(foo)s', u'%(bar)s'], [])],
            messages,
        )

    def test_blocktrans_with_whitespace_not_trimmed(self):
        test_tmpl = (
            b'{% blocktrans %}\n\tfoo\n\tbar\n{% endblocktrans %}'
        )
        buf = BytesIO(test_tmpl)
        messages = list(extract_django(buf, default_keys, [], {}))
        self.assertEqual([(4, None, u'\n\tfoo\n\tbar\n', [])], messages)

    @pytest.mark.skipif(django.VERSION < (1, 7),
                        reason='Trimmed whitespace is a Django >= 1.7 feature')
    def test_blocktrans_with_whitespace_trimmed(self):
        test_tmpl = (
            b'{% blocktrans trimmed %}\n\tfoo\n\tbar\n{% endblocktrans %}'
        )
        buf = BytesIO(test_tmpl)
        messages = list(extract_django(buf, default_keys, [], {}))
        self.assertEqual([(4, None, u'foo bar', [])], messages)
