# -*- encoding: utf-8 -*-
from __future__ import unicode_literals

from decimal import Decimal
from sys import float_info
from unittest import TestCase

from django.utils.numberformat import format as nformat


class TestNumberFormat(TestCase):

    def test_format_number(self):
        self.assertEqual(nformat(1234, '.'), '1234')
        self.assertEqual(nformat(1234.2, '.'), '1234.2')
        self.assertEqual(nformat(1234, '.', decimal_pos=2), '1234.00')
        self.assertEqual(nformat(1234, '.', grouping=2, thousand_sep=','), '1234')
        self.assertEqual(nformat(1234, '.', grouping=2, thousand_sep=',', force_grouping=True), '12,34')
        self.assertEqual(nformat(-1234.33, '.', decimal_pos=1), '-1234.3')

    def test_format_string(self):
        self.assertEqual(nformat('1234', '.'), '1234')
        self.assertEqual(nformat('1234.2', '.'), '1234.2')
        self.assertEqual(nformat('1234', '.', decimal_pos=2), '1234.00')
        self.assertEqual(nformat('1234', '.', grouping=2, thousand_sep=','), '1234')
        self.assertEqual(nformat('1234', '.', grouping=2, thousand_sep=',', force_grouping=True), '12,34')
        self.assertEqual(nformat('-1234.33', '.', decimal_pos=1), '-1234.3')
        self.assertEqual(nformat('10000', '.', grouping=3, thousand_sep='comma', force_grouping=True), '10comma000')

    def test_large_number(self):
        most_max = (
            '{}179769313486231570814527423731704356798070567525844996'
            '598917476803157260780028538760589558632766878171540458953'
            '514382464234321326889464182768467546703537516986049910576'
            '551282076245490090389328944075868508455133942304583236903'
            '222948165808559332123348274797826204144723168738177180919'
            '29988125040402618412485836{}'
        )
        most_max2 = (
            '{}35953862697246314162905484746340871359614113505168999'
            '31978349536063145215600570775211791172655337563430809179'
            '07028764928468642653778928365536935093407075033972099821'
            '15310256415249098018077865788815173701691026788460916647'
            '38064458963316171186642466965495956524082894463374763543'
            '61838599762500808052368249716736'
        )
        int_max = int(float_info.max)
        self.assertEqual(nformat(int_max, '.'), most_max.format('', '8'))
        self.assertEqual(nformat(int_max + 1, '.'), most_max.format('', '9'))
        self.assertEqual(nformat(int_max * 2, '.'), most_max2.format(''))
        self.assertEqual(nformat(0 - int_max, '.'), most_max.format('-', '8'))
        self.assertEqual(nformat(-1 - int_max, '.'), most_max.format('-', '9'))
        self.assertEqual(nformat(-2 * int_max, '.'), most_max2.format('-'))

    def test_decimal_numbers(self):
        self.assertEqual(nformat(Decimal('1234'), '.'), '1234')
        self.assertEqual(nformat(Decimal('1234.2'), '.'), '1234.2')
        self.assertEqual(nformat(Decimal('1234'), '.', decimal_pos=2), '1234.00')
        self.assertEqual(nformat(Decimal('1234'), '.', grouping=2, thousand_sep=','), '1234')
        self.assertEqual(nformat(Decimal('1234'), '.', grouping=2, thousand_sep=',', force_grouping=True), '12,34')
        self.assertEqual(nformat(Decimal('-1234.33'), '.', decimal_pos=1), '-1234.3')
        self.assertEqual(nformat(Decimal('0.00000001'), '.', decimal_pos=8), '0.00000001')
        # Very large & small numbers.
        tests = [
            ('9e9999', None, '9e+9999'),
            ('9e9999', 3, '9.000e+9999'),
            ('9e201', None, '9e+201'),
            ('9e200', None, '9e+200'),
            ('1.2345e999', 2, '1.23e+999'),
            ('9e-999', None, '9e-999'),
            ('1e-7', 8, '0.00000010'),
            ('1e-8', 8, '0.00000001'),
            ('1e-9', 8, '0.00000000'),
            ('1e-10', 8, '0.00000000'),
            ('1e-11', 8, '0.00000000'),
            ('1' + ('0' * 300), 3, '1.000e+300'),
            ('0.{}1234'.format('0' * 299), 3, '1.234e-300'),
        ]
        for value, decimal_pos, expected_value in tests:
            self.assertEqual(nformat(Decimal(value), '.', decimal_pos), expected_value)

    def test_decimal_subclass(self):
        class EuroDecimal(Decimal):
            """
            Wrapper for Decimal which prefixes each amount with the € symbol.
            """
            def __format__(self, specifier, **kwargs):
                amount = super(EuroDecimal, self).__format__(specifier, **kwargs)
                return '€ {}'.format(amount)

        price = EuroDecimal('1.23')
        self.assertEqual(nformat(price, ','), '€ 1,23')
