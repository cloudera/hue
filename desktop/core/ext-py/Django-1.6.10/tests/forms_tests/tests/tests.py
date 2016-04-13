# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import datetime

from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import models
from django.forms import Form, ModelForm, FileField, ModelChoiceField, CharField
from django.forms.models import ModelFormMetaclass
from django.test import TestCase
from django.utils import six

from ..models import (ChoiceOptionModel, ChoiceFieldModel, FileModel, Group,
    BoundaryModel, Defaults, OptionalMultiChoiceModel)


class ChoiceFieldForm(ModelForm):
    class Meta:
        model = ChoiceFieldModel
        fields = '__all__'


class OptionalMultiChoiceModelForm(ModelForm):
    class Meta:
        model = OptionalMultiChoiceModel
        fields = '__all__'


class ChoiceFieldExclusionForm(ModelForm):
    multi_choice = CharField(max_length=50)

    class Meta:
        exclude = ['multi_choice']
        model = ChoiceFieldModel


class FileForm(Form):
    file1 = FileField()


class TestTicket12510(TestCase):
    ''' It is not necessary to generate choices for ModelChoiceField (regression test for #12510). '''
    def setUp(self):
        self.groups = [Group.objects.create(name=name) for name in 'abc']

    def test_choices_not_fetched_when_not_rendering(self):
        # only one query is required to pull the model from DB
        with self.assertNumQueries(1):
            field = ModelChoiceField(Group.objects.order_by('-name'))
            self.assertEqual('a', field.clean(self.groups[0].pk).name)


class TestTicket14567(TestCase):
    """
    Check that the return values of ModelMultipleChoiceFields are QuerySets
    """
    def test_empty_queryset_return(self):
        "If a model's ManyToManyField has blank=True and is saved with no data, a queryset is returned."
        option = ChoiceOptionModel.objects.create(name='default')
        form = OptionalMultiChoiceModelForm({'multi_choice_optional': '', 'multi_choice': [option.pk]})
        self.assertTrue(form.is_valid())
        # Check that the empty value is a QuerySet
        self.assertIsInstance(form.cleaned_data['multi_choice_optional'], models.query.QuerySet)
        # While we're at it, test whether a QuerySet is returned if there *is* a value.
        self.assertIsInstance(form.cleaned_data['multi_choice'], models.query.QuerySet)


class ModelFormCallableModelDefault(TestCase):
    def test_no_empty_option(self):
        "If a model's ForeignKey has blank=False and a default, no empty option is created (Refs #10792)."
        option = ChoiceOptionModel.objects.create(name='default')

        choices = list(ChoiceFieldForm().fields['choice'].choices)
        self.assertEqual(len(choices), 1)
        self.assertEqual(choices[0], (option.pk, six.text_type(option)))

    def test_callable_initial_value(self):
        "The initial value for a callable default returning a queryset is the pk (refs #13769)"
        obj1 = ChoiceOptionModel.objects.create(id=1, name='default')
        obj2 = ChoiceOptionModel.objects.create(id=2, name='option 2')
        obj3 = ChoiceOptionModel.objects.create(id=3, name='option 3')
        self.assertHTMLEqual(ChoiceFieldForm().as_p(), """<p><label for="id_choice">Choice:</label> <select name="choice" id="id_choice">
<option value="1" selected="selected">ChoiceOption 1</option>
<option value="2">ChoiceOption 2</option>
<option value="3">ChoiceOption 3</option>
</select><input type="hidden" name="initial-choice" value="1" id="initial-id_choice" /></p>
<p><label for="id_choice_int">Choice int:</label> <select name="choice_int" id="id_choice_int">
<option value="1" selected="selected">ChoiceOption 1</option>
<option value="2">ChoiceOption 2</option>
<option value="3">ChoiceOption 3</option>
</select><input type="hidden" name="initial-choice_int" value="1" id="initial-id_choice_int" /></p>
<p><label for="id_multi_choice">Multi choice:</label> <select multiple="multiple" name="multi_choice" id="id_multi_choice">
<option value="1" selected="selected">ChoiceOption 1</option>
<option value="2">ChoiceOption 2</option>
<option value="3">ChoiceOption 3</option>
</select><input type="hidden" name="initial-multi_choice" value="1" id="initial-id_multi_choice_0" /> <span class="helptext"> Hold down "Control", or "Command" on a Mac, to select more than one.</span></p>
<p><label for="id_multi_choice_int">Multi choice int:</label> <select multiple="multiple" name="multi_choice_int" id="id_multi_choice_int">
<option value="1" selected="selected">ChoiceOption 1</option>
<option value="2">ChoiceOption 2</option>
<option value="3">ChoiceOption 3</option>
</select><input type="hidden" name="initial-multi_choice_int" value="1" id="initial-id_multi_choice_int_0" /> <span class="helptext"> Hold down "Control", or "Command" on a Mac, to select more than one.</span></p>""")

    def test_initial_instance_value(self):
        "Initial instances for model fields may also be instances (refs #7287)"
        obj1 = ChoiceOptionModel.objects.create(id=1, name='default')
        obj2 = ChoiceOptionModel.objects.create(id=2, name='option 2')
        obj3 = ChoiceOptionModel.objects.create(id=3, name='option 3')
        self.assertHTMLEqual(ChoiceFieldForm(initial={
                'choice': obj2,
                'choice_int': obj2,
                'multi_choice': [obj2,obj3],
                'multi_choice_int': ChoiceOptionModel.objects.exclude(name="default"),
            }).as_p(), """<p><label for="id_choice">Choice:</label> <select name="choice" id="id_choice">
<option value="1">ChoiceOption 1</option>
<option value="2" selected="selected">ChoiceOption 2</option>
<option value="3">ChoiceOption 3</option>
</select><input type="hidden" name="initial-choice" value="2" id="initial-id_choice" /></p>
<p><label for="id_choice_int">Choice int:</label> <select name="choice_int" id="id_choice_int">
<option value="1">ChoiceOption 1</option>
<option value="2" selected="selected">ChoiceOption 2</option>
<option value="3">ChoiceOption 3</option>
</select><input type="hidden" name="initial-choice_int" value="2" id="initial-id_choice_int" /></p>
<p><label for="id_multi_choice">Multi choice:</label> <select multiple="multiple" name="multi_choice" id="id_multi_choice">
<option value="1">ChoiceOption 1</option>
<option value="2" selected="selected">ChoiceOption 2</option>
<option value="3" selected="selected">ChoiceOption 3</option>
</select><input type="hidden" name="initial-multi_choice" value="2" id="initial-id_multi_choice_0" />
<input type="hidden" name="initial-multi_choice" value="3" id="initial-id_multi_choice_1" /> <span class="helptext"> Hold down "Control", or "Command" on a Mac, to select more than one.</span></p>
<p><label for="id_multi_choice_int">Multi choice int:</label> <select multiple="multiple" name="multi_choice_int" id="id_multi_choice_int">
<option value="1">ChoiceOption 1</option>
<option value="2" selected="selected">ChoiceOption 2</option>
<option value="3" selected="selected">ChoiceOption 3</option>
</select><input type="hidden" name="initial-multi_choice_int" value="2" id="initial-id_multi_choice_int_0" />
<input type="hidden" name="initial-multi_choice_int" value="3" id="initial-id_multi_choice_int_1" /> <span class="helptext"> Hold down "Control", or "Command" on a Mac, to select more than one.</span></p>""")


class FormsModelTestCase(TestCase):
    def test_unicode_filename(self):
        # FileModel with unicode filename and data #########################
        f = FileForm(data={}, files={'file1': SimpleUploadedFile('我隻氣墊船裝滿晒鱔.txt', 'मेरी मँडराने वाली नाव सर्पमीनों से भरी ह'.encode('utf-8'))}, auto_id=False)
        self.assertTrue(f.is_valid())
        self.assertTrue('file1' in f.cleaned_data)
        m = FileModel.objects.create(file=f.cleaned_data['file1'])
        self.assertEqual(m.file.name, 'tests/\u6211\u96bb\u6c23\u588a\u8239\u88dd\u6eff\u6652\u9c54.txt')
        m.delete()

    def test_boundary_conditions(self):
        # Boundary conditions on a PostitiveIntegerField #########################
        class BoundaryForm(ModelForm):
            class Meta:
                model = BoundaryModel
                fields = '__all__'

        f = BoundaryForm({'positive_integer': 100})
        self.assertTrue(f.is_valid())
        f = BoundaryForm({'positive_integer': 0})
        self.assertTrue(f.is_valid())
        f = BoundaryForm({'positive_integer': -100})
        self.assertFalse(f.is_valid())

    def test_formfield_initial(self):
        # Formfield initial values ########
        # If the model has default values for some fields, they are used as the formfield
        # initial values.
        class DefaultsForm(ModelForm):
            class Meta:
                model = Defaults
                fields = '__all__'

        self.assertEqual(DefaultsForm().fields['name'].initial, 'class default value')
        self.assertEqual(DefaultsForm().fields['def_date'].initial, datetime.date(1980, 1, 1))
        self.assertEqual(DefaultsForm().fields['value'].initial, 42)
        r1 = DefaultsForm()['callable_default'].as_widget()
        r2 = DefaultsForm()['callable_default'].as_widget()
        self.assertNotEqual(r1, r2)

        # In a ModelForm that is passed an instance, the initial values come from the
        # instance's values, not the model's defaults.
        foo_instance = Defaults(name='instance value', def_date=datetime.date(1969, 4, 4), value=12)
        instance_form = DefaultsForm(instance=foo_instance)
        self.assertEqual(instance_form.initial['name'], 'instance value')
        self.assertEqual(instance_form.initial['def_date'], datetime.date(1969, 4, 4))
        self.assertEqual(instance_form.initial['value'], 12)

        from django.forms import CharField

        class ExcludingForm(ModelForm):
            name = CharField(max_length=255)

            class Meta:
                model = Defaults
                exclude = ['name', 'callable_default']

        f = ExcludingForm({'name': 'Hello', 'value': 99, 'def_date': datetime.date(1999, 3, 2)})
        self.assertTrue(f.is_valid())
        self.assertEqual(f.cleaned_data['name'], 'Hello')
        obj = f.save()
        self.assertEqual(obj.name, 'class default value')
        self.assertEqual(obj.value, 99)
        self.assertEqual(obj.def_date, datetime.date(1999, 3, 2))

class RelatedModelFormTests(TestCase):
    def test_invalid_loading_order(self):
        """
        Test for issue 10405
        """
        class A(models.Model):
            ref = models.ForeignKey("B")

        class Meta:
            model = A
            fields = '__all__'

        self.assertRaises(ValueError, ModelFormMetaclass, str('Form'), (ModelForm,), {'Meta': Meta})

        class B(models.Model):
            pass

    def test_valid_loading_order(self):
        """
        Test for issue 10405
        """
        class A(models.Model):
            ref = models.ForeignKey("B")

        class B(models.Model):
            pass

        class Meta:
            model = A
            fields = '__all__'

        self.assertTrue(issubclass(ModelFormMetaclass(str('Form'), (ModelForm,), {'Meta': Meta}), ModelForm))


class ManyToManyExclusionTestCase(TestCase):
    def test_m2m_field_exclusion(self):
        # Issue 12337. save_instance should honor the passed-in exclude keyword.
        opt1 = ChoiceOptionModel.objects.create(id=1, name='default')
        opt2 = ChoiceOptionModel.objects.create(id=2, name='option 2')
        opt3 = ChoiceOptionModel.objects.create(id=3, name='option 3')
        initial = {
            'choice': opt1,
            'choice_int': opt1,
        }
        data = {
            'choice': opt2.pk,
            'choice_int': opt2.pk,
            'multi_choice': 'string data!',
            'multi_choice_int': [opt1.pk],
        }
        instance = ChoiceFieldModel.objects.create(**initial)
        instance.multi_choice = instance.multi_choice_int = [opt2, opt3]
        form = ChoiceFieldExclusionForm(data=data, instance=instance)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['multi_choice'], data['multi_choice'])
        form.save()
        self.assertEqual(form.instance.choice.pk, data['choice'])
        self.assertEqual(form.instance.choice_int.pk, data['choice_int'])
        self.assertEqual(list(form.instance.multi_choice.all()), [opt2, opt3])
        self.assertEqual([obj.pk for obj in form.instance.multi_choice_int.all()], data['multi_choice_int'])
