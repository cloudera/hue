from __future__ import absolute_import, unicode_literals

import datetime
from decimal import Decimal

from django import test
from django import forms
from django.core.exceptions import ValidationError
from django.db import connection, models, IntegrityError
from django.db.models.fields import (
    AutoField, BigIntegerField, BinaryField, BooleanField, CharField,
    CommaSeparatedIntegerField, DateField, DateTimeField, DecimalField,
    EmailField, FilePathField, FloatField, IntegerField, IPAddressField,
    GenericIPAddressField, NullBooleanField, PositiveIntegerField,
    PositiveSmallIntegerField, SlugField, SmallIntegerField, TextField,
    TimeField, URLField)
from django.db.models.fields.files import FileField, ImageField
from django.utils import six
from django.utils import unittest

from .models import (Foo, Bar, Whiz, BigD, BigS, Image, BigInt, Post,
    NullBooleanModel, BooleanModel, DataModel, Document, RenamedField,
    DateTimeModel, VerboseNameField, FksToBooleans)


class BasicFieldTests(test.TestCase):
    def test_show_hidden_initial(self):
        """
        Regression test for #12913. Make sure fields with choices respect
        show_hidden_initial as a kwarg to models.Field.formfield()
        """
        choices = [(0, 0), (1, 1)]
        model_field = models.Field(choices=choices)
        form_field = model_field.formfield(show_hidden_initial=True)
        self.assertTrue(form_field.show_hidden_initial)

        form_field = model_field.formfield(show_hidden_initial=False)
        self.assertFalse(form_field.show_hidden_initial)

    def test_nullbooleanfield_blank(self):
        """
        Regression test for #13071: NullBooleanField should not throw
        a validation error when given a value of None.

        """
        nullboolean = NullBooleanModel(nbfield=None)
        try:
            nullboolean.full_clean()
        except ValidationError as e:
            self.fail("NullBooleanField failed validation with value of None: %s" % e.messages)

    def test_field_repr(self):
        """
        Regression test for #5931: __repr__ of a field also displays its name
        """
        f = Foo._meta.get_field('a')
        self.assertEqual(repr(f), '<django.db.models.fields.CharField: a>')
        f = models.fields.CharField()
        self.assertEqual(repr(f), '<django.db.models.fields.CharField>')

    def test_field_name(self):
        """
        Regression test for #14695: explicitly defined field name overwritten
        by model's attribute name.
        """
        instance = RenamedField()
        self.assertTrue(hasattr(instance, 'get_fieldname_display'))
        self.assertFalse(hasattr(instance, 'get_modelname_display'))

    def test_field_verbose_name(self):
        m = VerboseNameField
        for i in range(1, 23):
            self.assertEqual(m._meta.get_field('field%d' % i).verbose_name,
                    'verbose field%d' % i)

        self.assertEqual(m._meta.get_field('id').verbose_name, 'verbose pk')

    def test_choices_form_class(self):
        """Can supply a custom choices form class. Regression for #20999."""
        choices = [('a', 'a')]
        field = models.CharField(choices=choices)
        klass = forms.TypedMultipleChoiceField
        self.assertIsInstance(field.formfield(choices_form_class=klass), klass)


class DecimalFieldTests(test.TestCase):
    def test_to_python(self):
        f = models.DecimalField(max_digits=4, decimal_places=2)
        self.assertEqual(f.to_python(3), Decimal("3"))
        self.assertEqual(f.to_python("3.14"), Decimal("3.14"))
        self.assertRaises(ValidationError, f.to_python, "abc")

    def test_default(self):
        f = models.DecimalField(default=Decimal("0.00"))
        self.assertEqual(f.get_default(), Decimal("0.00"))

    def test_format(self):
        f = models.DecimalField(max_digits=5, decimal_places=1)
        self.assertEqual(f._format(f.to_python(2)), '2.0')
        self.assertEqual(f._format(f.to_python('2.6')), '2.6')
        self.assertEqual(f._format(None), None)

    def test_get_db_prep_lookup(self):
        from django.db import connection
        f = models.DecimalField(max_digits=5, decimal_places=1)
        self.assertEqual(f.get_db_prep_lookup('exact', None, connection=connection), [None])

    def test_filter_with_strings(self):
        """
        We should be able to filter decimal fields using strings (#8023)
        """
        Foo.objects.create(id=1, a='abc', d=Decimal("12.34"))
        self.assertEqual(list(Foo.objects.filter(d='1.23')), [])

    def test_save_without_float_conversion(self):
        """
        Ensure decimals don't go through a corrupting float conversion during
        save (#5079).
        """
        bd = BigD(d="12.9")
        bd.save()
        bd = BigD.objects.get(pk=bd.pk)
        self.assertEqual(bd.d, Decimal("12.9"))

    def test_lookup_really_big_value(self):
        """
        Ensure that really big values can be used in a filter statement, even
        with older Python versions.
        """
        # This should not crash. That counts as a win for our purposes.
        Foo.objects.filter(d__gte=100000000000)

class ForeignKeyTests(test.TestCase):
    def test_callable_default(self):
        """Test the use of a lazy callable for ForeignKey.default"""
        a = Foo.objects.create(id=1, a='abc', d=Decimal("12.34"))
        b = Bar.objects.create(b="bcd")
        self.assertEqual(b.a, a)

class DateTimeFieldTests(unittest.TestCase):
    def test_datetimefield_to_python_usecs(self):
        """DateTimeField.to_python should support usecs"""
        f = models.DateTimeField()
        self.assertEqual(f.to_python('2001-01-02 03:04:05.000006'),
                         datetime.datetime(2001, 1, 2, 3, 4, 5, 6))
        self.assertEqual(f.to_python('2001-01-02 03:04:05.999999'),
                         datetime.datetime(2001, 1, 2, 3, 4, 5, 999999))

    def test_timefield_to_python_usecs(self):
        """TimeField.to_python should support usecs"""
        f = models.TimeField()
        self.assertEqual(f.to_python('01:02:03.000004'),
                         datetime.time(1, 2, 3, 4))
        self.assertEqual(f.to_python('01:02:03.999999'),
                         datetime.time(1, 2, 3, 999999))

    @test.skipUnlessDBFeature("supports_microsecond_precision")
    def test_datetimes_save_completely(self):
        dat = datetime.date(2014, 3, 12)
        datetim = datetime.datetime(2014, 3, 12, 21, 22, 23, 240000)
        tim = datetime.time(21, 22, 23, 240000)
        DateTimeModel.objects.create(d=dat, dt=datetim, t=tim)
        obj = DateTimeModel.objects.first()
        self.assertTrue(obj)
        self.assertEqual(obj.d, dat)
        self.assertEqual(obj.dt, datetim)
        self.assertEqual(obj.t, tim)

class BooleanFieldTests(unittest.TestCase):
    def _test_get_db_prep_lookup(self, f):
        from django.db import connection
        self.assertEqual(f.get_db_prep_lookup('exact', True, connection=connection), [True])
        self.assertEqual(f.get_db_prep_lookup('exact', '1', connection=connection), [True])
        self.assertEqual(f.get_db_prep_lookup('exact', 1, connection=connection), [True])
        self.assertEqual(f.get_db_prep_lookup('exact', False, connection=connection), [False])
        self.assertEqual(f.get_db_prep_lookup('exact', '0', connection=connection), [False])
        self.assertEqual(f.get_db_prep_lookup('exact', 0, connection=connection), [False])
        self.assertEqual(f.get_db_prep_lookup('exact', None, connection=connection), [None])

    def _test_to_python(self, f):
        self.assertTrue(f.to_python(1) is True)
        self.assertTrue(f.to_python(0) is False)

    def test_booleanfield_get_db_prep_lookup(self):
        self._test_get_db_prep_lookup(models.BooleanField())

    def test_nullbooleanfield_get_db_prep_lookup(self):
        self._test_get_db_prep_lookup(models.NullBooleanField())

    def test_booleanfield_to_python(self):
        self._test_to_python(models.BooleanField())

    def test_nullbooleanfield_to_python(self):
        self._test_to_python(models.NullBooleanField())

    def test_booleanfield_choices_blank(self):
        """
        Test that BooleanField with choices and defaults doesn't generate a
        formfield with the blank option (#9640, #10549).
        """
        choices = [(1, 'Si'), (2, 'No')]
        f = models.BooleanField(choices=choices, default=1, null=True)
        self.assertEqual(f.formfield().choices, [('', '---------')] + choices)

        f = models.BooleanField(choices=choices, default=1, null=False)
        self.assertEqual(f.formfield().choices, choices)

    def test_return_type(self):
        b = BooleanModel()
        b.bfield = True
        b.save()
        b2 = BooleanModel.objects.get(pk=b.pk)
        self.assertIsInstance(b2.bfield, bool)
        self.assertEqual(b2.bfield, True)

        b3 = BooleanModel()
        b3.bfield = False
        b3.save()
        b4 = BooleanModel.objects.get(pk=b3.pk)
        self.assertIsInstance(b4.bfield, bool)
        self.assertEqual(b4.bfield, False)

        b = NullBooleanModel()
        b.nbfield = True
        b.save()
        b2 = NullBooleanModel.objects.get(pk=b.pk)
        self.assertIsInstance(b2.nbfield, bool)
        self.assertEqual(b2.nbfield, True)

        b3 = NullBooleanModel()
        b3.nbfield = False
        b3.save()
        b4 = NullBooleanModel.objects.get(pk=b3.pk)
        self.assertIsInstance(b4.nbfield, bool)
        self.assertEqual(b4.nbfield, False)

        # http://code.djangoproject.com/ticket/13293
        # Verify that when an extra clause exists, the boolean
        # conversions are applied with an offset
        b5 = BooleanModel.objects.all().extra(
            select={'string_col': 'string'})[0]
        self.assertFalse(isinstance(b5.pk, bool))

    def test_select_related(self):
        """
        Test type of boolean fields when retrieved via select_related() (MySQL,
        #15040)
        """
        bmt = BooleanModel.objects.create(bfield=True)
        bmf = BooleanModel.objects.create(bfield=False)
        nbmt = NullBooleanModel.objects.create(nbfield=True)
        nbmf = NullBooleanModel.objects.create(nbfield=False)

        m1 = FksToBooleans.objects.create(bf=bmt, nbf=nbmt)
        m2 = FksToBooleans.objects.create(bf=bmf, nbf=nbmf)

        # Test select_related('fk_field_name')
        ma = FksToBooleans.objects.select_related('bf').get(pk=m1.id)
        # verify types -- should't be 0/1
        self.assertIsInstance(ma.bf.bfield, bool)
        self.assertIsInstance(ma.nbf.nbfield, bool)
        # verify values
        self.assertEqual(ma.bf.bfield, True)
        self.assertEqual(ma.nbf.nbfield, True)

        # Test select_related()
        mb = FksToBooleans.objects.select_related().get(pk=m1.id)
        mc = FksToBooleans.objects.select_related().get(pk=m2.id)
        # verify types -- shouldn't be 0/1
        self.assertIsInstance(mb.bf.bfield, bool)
        self.assertIsInstance(mb.nbf.nbfield, bool)
        self.assertIsInstance(mc.bf.bfield, bool)
        self.assertIsInstance(mc.nbf.nbfield, bool)
        # verify values
        self.assertEqual(mb.bf.bfield, True)
        self.assertEqual(mb.nbf.nbfield, True)
        self.assertEqual(mc.bf.bfield, False)
        self.assertEqual(mc.nbf.nbfield, False)

    def test_null_default(self):
        """
        Check that a BooleanField defaults to None -- which isn't
        a valid value (#15124).
        """
        # Patch the boolean field's default value. We give it a default
        # value when defining the model to satisfy the check tests
        # #20895.
        boolean_field = BooleanModel._meta.get_field('bfield')
        self.assertTrue(boolean_field.has_default())
        old_default = boolean_field.default
        try:
            boolean_field.default = models.NOT_PROVIDED
            # check patch was succcessful
            self.assertFalse(boolean_field.has_default())
            b = BooleanModel()
            self.assertIsNone(b.bfield)
            with self.assertRaises(IntegrityError):
                b.save()
        finally:
            boolean_field.default = old_default

        nb = NullBooleanModel()
        self.assertIsNone(nb.nbfield)
        nb.save()           # no error

class ChoicesTests(test.TestCase):
    def test_choices_and_field_display(self):
        """
        Check that get_choices and get_flatchoices interact with
        get_FIELD_display to return the expected values (#7913).
        """
        self.assertEqual(Whiz(c=1).get_c_display(), 'First')    # A nested value
        self.assertEqual(Whiz(c=0).get_c_display(), 'Other')    # A top level value
        self.assertEqual(Whiz(c=9).get_c_display(), 9)          # Invalid value
        self.assertEqual(Whiz(c=None).get_c_display(), None)    # Blank value
        self.assertEqual(Whiz(c='').get_c_display(), '')        # Empty value

class SlugFieldTests(test.TestCase):
    def test_slugfield_max_length(self):
        """
        Make sure SlugField honors max_length (#9706)
        """
        bs = BigS.objects.create(s = 'slug'*50)
        bs = BigS.objects.get(pk=bs.pk)
        self.assertEqual(bs.s, 'slug'*50)


class ValidationTest(test.TestCase):
    def test_charfield_raises_error_on_empty_string(self):
        f = models.CharField()
        self.assertRaises(ValidationError, f.clean, "", None)

    def test_charfield_cleans_empty_string_when_blank_true(self):
        f = models.CharField(blank=True)
        self.assertEqual('', f.clean('', None))

    def test_integerfield_cleans_valid_string(self):
        f = models.IntegerField()
        self.assertEqual(2, f.clean('2', None))

    def test_integerfield_raises_error_on_invalid_intput(self):
        f = models.IntegerField()
        self.assertRaises(ValidationError, f.clean, "a", None)

    def test_charfield_with_choices_cleans_valid_choice(self):
        f = models.CharField(max_length=1, choices=[('a','A'), ('b','B')])
        self.assertEqual('a', f.clean('a', None))

    def test_charfield_with_choices_raises_error_on_invalid_choice(self):
        f = models.CharField(choices=[('a','A'), ('b','B')])
        self.assertRaises(ValidationError, f.clean, "not a", None)

    def test_choices_validation_supports_named_groups(self):
        f = models.IntegerField(choices=(('group',((10,'A'),(20,'B'))),(30,'C')))
        self.assertEqual(10, f.clean(10, None))

    def test_nullable_integerfield_raises_error_with_blank_false(self):
        f = models.IntegerField(null=True, blank=False)
        self.assertRaises(ValidationError, f.clean, None, None)

    def test_nullable_integerfield_cleans_none_on_null_and_blank_true(self):
        f = models.IntegerField(null=True, blank=True)
        self.assertEqual(None, f.clean(None, None))

    def test_integerfield_raises_error_on_empty_input(self):
        f = models.IntegerField(null=False)
        self.assertRaises(ValidationError, f.clean, None, None)
        self.assertRaises(ValidationError, f.clean, '', None)

    def test_integerfield_validates_zero_against_choices(self):
        f = models.IntegerField(choices=((1, 1),))
        self.assertRaises(ValidationError, f.clean, '0', None)

    def test_charfield_raises_error_on_empty_input(self):
        f = models.CharField(null=False)
        self.assertRaises(ValidationError, f.clean, None, None)

    def test_datefield_cleans_date(self):
        f = models.DateField()
        self.assertEqual(datetime.date(2008, 10, 10), f.clean('2008-10-10', None))

    def test_boolean_field_doesnt_accept_empty_input(self):
        f = models.BooleanField()
        self.assertRaises(ValidationError, f.clean, None, None)


class BigIntegerFieldTests(test.TestCase):
    def test_limits(self):
        # Ensure that values that are right at the limits can be saved
        # and then retrieved without corruption.
        maxval = 9223372036854775807
        minval = -maxval - 1
        BigInt.objects.create(value=maxval)
        qs = BigInt.objects.filter(value__gte=maxval)
        self.assertEqual(qs.count(), 1)
        self.assertEqual(qs[0].value, maxval)
        BigInt.objects.create(value=minval)
        qs = BigInt.objects.filter(value__lte=minval)
        self.assertEqual(qs.count(), 1)
        self.assertEqual(qs[0].value, minval)

    def test_types(self):
        b = BigInt(value = 0)
        self.assertIsInstance(b.value, six.integer_types)
        b.save()
        self.assertIsInstance(b.value, six.integer_types)
        b = BigInt.objects.all()[0]
        self.assertIsInstance(b.value, six.integer_types)

    def test_coercing(self):
        BigInt.objects.create(value ='10')
        b = BigInt.objects.get(value = '10')
        self.assertEqual(b.value, 10)

class TypeCoercionTests(test.TestCase):
    """
    Test that database lookups can accept the wrong types and convert
    them with no error: especially on Postgres 8.3+ which does not do
    automatic casting at the DB level. See #10015.

    """
    def test_lookup_integer_in_charfield(self):
        self.assertEqual(Post.objects.filter(title=9).count(), 0)

    def test_lookup_integer_in_textfield(self):
        self.assertEqual(Post.objects.filter(body=24).count(), 0)

class FileFieldTests(unittest.TestCase):
    def test_clearable(self):
        """
        Test that FileField.save_form_data will clear its instance attribute
        value if passed False.

        """
        d = Document(myfile='something.txt')
        self.assertEqual(d.myfile, 'something.txt')
        field = d._meta.get_field('myfile')
        field.save_form_data(d, False)
        self.assertEqual(d.myfile, '')

    def test_unchanged(self):
        """
        Test that FileField.save_form_data considers None to mean "no change"
        rather than "clear".

        """
        d = Document(myfile='something.txt')
        self.assertEqual(d.myfile, 'something.txt')
        field = d._meta.get_field('myfile')
        field.save_form_data(d, None)
        self.assertEqual(d.myfile, 'something.txt')

    def test_changed(self):
        """
        Test that FileField.save_form_data, if passed a truthy value, updates
        its instance attribute.

        """
        d = Document(myfile='something.txt')
        self.assertEqual(d.myfile, 'something.txt')
        field = d._meta.get_field('myfile')
        field.save_form_data(d, 'else.txt')
        self.assertEqual(d.myfile, 'else.txt')

    def test_delete_when_file_unset(self):
        """
        Calling delete on an unset FileField should not call the file deletion
        process, but fail silently (#20660).
        """
        d = Document()
        try:
            d.myfile.delete()
        except OSError:
            self.fail("Deleting an unset FileField should not raise OSError.")


class BinaryFieldTests(test.TestCase):
    binary_data = b'\x00\x46\xFE'

    def test_set_and_retrieve(self):
        data_set = (self.binary_data, six.memoryview(self.binary_data))
        for bdata in data_set:
            dm = DataModel(data=bdata)
            dm.save()
            dm = DataModel.objects.get(pk=dm.pk)
            self.assertEqual(bytes(dm.data), bytes(bdata))
            # Resave (=update)
            dm.save()
            dm = DataModel.objects.get(pk=dm.pk)
            self.assertEqual(bytes(dm.data), bytes(bdata))
            # Test default value
            self.assertEqual(bytes(dm.short_data), b'\x08')

    if connection.vendor == 'mysql' and six.PY3:
        # Existing MySQL DB-API drivers fail on binary data.
        test_set_and_retrieve = unittest.expectedFailure(test_set_and_retrieve)

    def test_max_length(self):
        dm = DataModel(short_data=self.binary_data*4)
        self.assertRaises(ValidationError, dm.full_clean)

class GenericIPAddressFieldTests(test.TestCase):
    def test_genericipaddressfield_formfield_protocol(self):
        """
        Test that GenericIPAddressField with a specified protocol does not
        generate a formfield with no specified protocol. See #20740.
        """
        model_field = models.GenericIPAddressField(protocol='IPv4')
        form_field = model_field.formfield()
        self.assertRaises(ValidationError, form_field.clean, '::1')
        model_field = models.GenericIPAddressField(protocol='IPv6')
        form_field = model_field.formfield()
        self.assertRaises(ValidationError, form_field.clean, '127.0.0.1')


class PrepValueTest(test.TestCase):
    def test_AutoField(self):
        self.assertIsInstance(AutoField(primary_key=True).get_prep_value(1), int)

    @unittest.skipIf(six.PY3, "Python 3 has no `long` type.")
    def test_BigIntegerField(self):
        self.assertIsInstance(BigIntegerField().get_prep_value(long(9999999999999999999)), long)

    def test_BinaryField(self):
        self.assertIsInstance(BinaryField().get_prep_value(b''), bytes)

    def test_BooleanField(self):
        self.assertIsInstance(BooleanField().get_prep_value(True), bool)

    def test_CharField(self):
        self.assertIsInstance(CharField().get_prep_value(''), six.text_type)
        self.assertIsInstance(CharField().get_prep_value(0), six.text_type)

    def test_CommaSeparatedIntegerField(self):
        self.assertIsInstance(CommaSeparatedIntegerField().get_prep_value('1,2'), six.text_type)
        self.assertIsInstance(CommaSeparatedIntegerField().get_prep_value(0), six.text_type)

    def test_DateField(self):
        self.assertIsInstance(DateField().get_prep_value(datetime.date.today()), datetime.date)

    def test_DateTimeField(self):
        self.assertIsInstance(DateTimeField().get_prep_value(datetime.datetime.now()), datetime.datetime)

    def test_DecimalField(self):
        self.assertIsInstance(DecimalField().get_prep_value(Decimal('1.2')), Decimal)

    def test_EmailField(self):
        self.assertIsInstance(EmailField().get_prep_value('mailbox@domain.com'), six.text_type)

    def test_FileField(self):
        self.assertIsInstance(FileField().get_prep_value('filename.ext'), six.text_type)
        self.assertIsInstance(FileField().get_prep_value(0), six.text_type)

    def test_FilePathField(self):
        self.assertIsInstance(FilePathField().get_prep_value('tests.py'), six.text_type)
        self.assertIsInstance(FilePathField().get_prep_value(0), six.text_type)

    def test_FloatField(self):
        self.assertIsInstance(FloatField().get_prep_value(1.2), float)

    def test_ImageField(self):
        self.assertIsInstance(ImageField().get_prep_value('filename.ext'), six.text_type)

    def test_IntegerField(self):
        self.assertIsInstance(IntegerField().get_prep_value(1), int)

    def test_IPAddressField(self):
        self.assertIsInstance(IPAddressField().get_prep_value('127.0.0.1'), six.text_type)
        self.assertIsInstance(IPAddressField().get_prep_value(0), six.text_type)

    def test_GenericIPAddressField(self):
        self.assertIsInstance(GenericIPAddressField().get_prep_value('127.0.0.1'), six.text_type)
        self.assertIsInstance(GenericIPAddressField().get_prep_value(0), six.text_type)

    def test_NullBooleanField(self):
        self.assertIsInstance(NullBooleanField().get_prep_value(True), bool)

    def test_PositiveIntegerField(self):
        self.assertIsInstance(PositiveIntegerField().get_prep_value(1), int)

    def test_PositiveSmallIntegerField(self):
        self.assertIsInstance(PositiveSmallIntegerField().get_prep_value(1), int)

    def test_SlugField(self):
        self.assertIsInstance(SlugField().get_prep_value('slug'), six.text_type)
        self.assertIsInstance(SlugField().get_prep_value(0), six.text_type)

    def test_SmallIntegerField(self):
        self.assertIsInstance(SmallIntegerField().get_prep_value(1), int)

    def test_TextField(self):
        self.assertIsInstance(TextField().get_prep_value('Abc'), six.text_type)
        self.assertIsInstance(TextField().get_prep_value(0), six.text_type)

    def test_TimeField(self):
        self.assertIsInstance(
            TimeField().get_prep_value(datetime.datetime.now().time()),
            datetime.time)

    def test_URLField(self):
        self.assertIsInstance(URLField().get_prep_value('http://domain.com'), six.text_type)


class CustomFieldTests(unittest.TestCase):

    def test_14786(self):
        """
        Regression test for #14786 -- Test that field values are not prepared
        twice in get_db_prep_lookup().
        """
        prepare_count = [0]
        class NoopField(models.TextField):
            def get_prep_value(self, value):
                prepare_count[0] += 1
                return super(NoopField, self).get_prep_value(value)

        field = NoopField()
        field.get_db_prep_lookup('exact', 'TEST', connection=connection, prepared=False)
        self.assertEqual(prepare_count[0], 1)
