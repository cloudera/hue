from __future__ import absolute_import, unicode_literals

from datetime import date
import warnings

from django import forms
from django.core.exceptions import FieldError, ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.forms.models import (modelform_factory, ModelChoiceField,
    fields_for_model, construct_instance, ModelFormMetaclass)
from django.utils import six
from django.utils import unittest
from django.test import TestCase

from .models import (Person, RealPerson, Triple, FilePathModel, Article,
    Publication, CustomFF, Author, Author1, Homepage, Document, Edition)


class ModelMultipleChoiceFieldTests(TestCase):
    def test_model_multiple_choice_number_of_queries(self):
        """
        Test that ModelMultipleChoiceField does O(1) queries instead of
        O(n) (#10156).
        """
        persons = [Person.objects.create(name="Person %s" % i) for i in range(30)]

        f = forms.ModelMultipleChoiceField(queryset=Person.objects.all())
        self.assertNumQueries(1, f.clean, [p.pk for p in persons[1:11:2]])

    def test_model_multiple_choice_run_validators(self):
        """
        Test that ModelMultipleChoiceField run given validators (#14144).
        """
        for i in range(30):
            Person.objects.create(name="Person %s" % i)

        self._validator_run = False
        def my_validator(value):
            self._validator_run = True

        f = forms.ModelMultipleChoiceField(queryset=Person.objects.all(),
                                           validators=[my_validator])

        f.clean([p.pk for p in Person.objects.all()[8:9]])
        self.assertTrue(self._validator_run)

    def test_model_multiple_choice_show_hidden_initial(self):
        """
        Test support of show_hidden_initial by ModelMultipleChoiceField.
        """
        class PersonForm(forms.Form):
            persons = forms.ModelMultipleChoiceField(show_hidden_initial=True,
                                                     queryset=Person.objects.all())

        person1 = Person.objects.create(name="Person 1")
        person2 = Person.objects.create(name="Person 2")

        form = PersonForm(initial={'persons': [person1, person2]},
                          data={'initial-persons': [str(person1.pk), str(person2.pk)],
                                'persons': [str(person1.pk), str(person2.pk)]})
        self.assertTrue(form.is_valid())
        self.assertFalse(form.has_changed())

        form = PersonForm(initial={'persons': [person1, person2]},
                          data={'initial-persons': [str(person1.pk), str(person2.pk)],
                                'persons': [str(person2.pk)]})
        self.assertTrue(form.is_valid())
        self.assertTrue(form.has_changed())


class TripleForm(forms.ModelForm):
    class Meta:
        model = Triple
        fields = '__all__'


class UniqueTogetherTests(TestCase):
    def test_multiple_field_unique_together(self):
        """
        When the same field is involved in multiple unique_together
        constraints, we need to make sure we don't remove the data for it
        before doing all the validation checking (not just failing after
        the first one).
        """
        Triple.objects.create(left=1, middle=2, right=3)

        form = TripleForm({'left': '1', 'middle': '2', 'right': '3'})
        self.assertFalse(form.is_valid())

        form = TripleForm({'left': '1', 'middle': '3', 'right': '1'})
        self.assertTrue(form.is_valid())


class TripleFormWithCleanOverride(forms.ModelForm):
    class Meta:
        model = Triple
        fields = '__all__'

    def clean(self):
        if not self.cleaned_data['left'] == self.cleaned_data['right']:
            raise forms.ValidationError('Left and right should be equal')
        return self.cleaned_data


class OverrideCleanTests(TestCase):
    def test_override_clean(self):
        """
        Regression for #12596: Calling super from ModelForm.clean() should be
        optional.
        """
        form = TripleFormWithCleanOverride({'left': 1, 'middle': 2, 'right': 1})
        self.assertTrue(form.is_valid())
        # form.instance.left will be None if the instance was not constructed
        # by form.full_clean().
        self.assertEqual(form.instance.left, 1)



class PartiallyLocalizedTripleForm(forms.ModelForm):
    class Meta:
        model = Triple
        localized_fields = ('left', 'right',)
        fields = '__all__'


class FullyLocalizedTripleForm(forms.ModelForm):
    class Meta:
        model = Triple
        localized_fields = '__all__'
        fields = '__all__'

class LocalizedModelFormTest(TestCase):
    def test_model_form_applies_localize_to_some_fields(self):
        f = PartiallyLocalizedTripleForm({'left': 10, 'middle': 10, 'right': 10})
        self.assertTrue(f.is_valid())
        self.assertTrue(f.fields['left'].localize)
        self.assertFalse(f.fields['middle'].localize)
        self.assertTrue(f.fields['right'].localize)

    def test_model_form_applies_localize_to_all_fields(self):
        f = FullyLocalizedTripleForm({'left': 10, 'middle': 10, 'right': 10})
        self.assertTrue(f.is_valid())
        self.assertTrue(f.fields['left'].localize)
        self.assertTrue(f.fields['middle'].localize)
        self.assertTrue(f.fields['right'].localize)

    def test_model_form_refuses_arbitrary_string(self):
        with self.assertRaises(TypeError):
            class BrokenLocalizedTripleForm(forms.ModelForm):
                class Meta:
                    model = Triple
                    localized_fields = "foo"


# Regression test for #12960.
# Make sure the cleaned_data returned from ModelForm.clean() is applied to the
# model instance.

class PublicationForm(forms.ModelForm):
    def clean(self):
        self.cleaned_data['title'] = self.cleaned_data['title'].upper()
        return self.cleaned_data

    class Meta:
        model = Publication
        fields = '__all__'


class ModelFormCleanTest(TestCase):
    def test_model_form_clean_applies_to_model(self):
        data = {'title': 'test', 'date_published': '2010-2-25'}
        form = PublicationForm(data)
        publication = form.save()
        self.assertEqual(publication.title, 'TEST')


class FPForm(forms.ModelForm):
    class Meta:
        model = FilePathModel
        fields = '__all__'


class FilePathFieldTests(TestCase):
    def test_file_path_field_blank(self):
        """
        Regression test for #8842: FilePathField(blank=True)
        """
        form = FPForm()
        names = [p[1] for p in form['path'].field.choices]
        names.sort()
        self.assertEqual(names, ['---------', '__init__.py', 'models.py', 'tests.py'])

class ManyToManyCallableInitialTests(TestCase):
    def test_callable(self):
        "Regression for #10349: A callable can be provided as the initial value for an m2m field"

        # Set up a callable initial value
        def formfield_for_dbfield(db_field, **kwargs):
            if db_field.name == 'publications':
                kwargs['initial'] = lambda: Publication.objects.all().order_by('date_published')[:2]
            return db_field.formfield(**kwargs)

        # Set up some Publications to use as data
        book1 = Publication.objects.create(title="First Book", date_published=date(2007,1,1))
        book2 = Publication.objects.create(title="Second Book", date_published=date(2008,1,1))
        book3 = Publication.objects.create(title="Third Book", date_published=date(2009,1,1))

        # Create a ModelForm, instantiate it, and check that the output is as expected
        ModelForm = modelform_factory(Article, fields="__all__",
                                      formfield_callback=formfield_for_dbfield)
        form = ModelForm()
        self.assertHTMLEqual(form.as_ul(), """<li><label for="id_headline">Headline:</label> <input id="id_headline" type="text" name="headline" maxlength="100" /></li>
<li><label for="id_publications">Publications:</label> <select multiple="multiple" name="publications" id="id_publications">
<option value="%d" selected="selected">First Book</option>
<option value="%d" selected="selected">Second Book</option>
<option value="%d">Third Book</option>
</select> <span class="helptext"> Hold down "Control", or "Command" on a Mac, to select more than one.</span></li>"""
            % (book1.pk, book2.pk, book3.pk))


class CFFForm(forms.ModelForm):
    class Meta:
        model = CustomFF
        fields = '__all__'


class CustomFieldSaveTests(TestCase):
    def test_save(self):
        "Regression for #11149: save_form_data should be called only once"

        # It's enough that the form saves without error -- the custom save routine will
        # generate an AssertionError if it is called more than once during save.
        form = CFFForm(data = {'f': None})
        form.save()

class ModelChoiceIteratorTests(TestCase):
    def test_len(self):
        class Form(forms.ModelForm):
            class Meta:
                model = Article
                fields = ["publications"]

        Publication.objects.create(title="Pravda",
            date_published=date(1991, 8, 22))
        f = Form()
        self.assertEqual(len(f.fields["publications"].choices), 1)


class RealPersonForm(forms.ModelForm):
    class Meta:
        model = RealPerson
        fields = '__all__'


class CustomModelFormSaveMethod(TestCase):
    def test_string_message(self):
        data = {'name': 'anonymous'}
        form = RealPersonForm(data)
        self.assertEqual(form.is_valid(), False)
        self.assertEqual(form.errors['__all__'], ['Please specify a real name.'])

class ModelClassTests(TestCase):
    def test_no_model_class(self):
        class NoModelModelForm(forms.ModelForm):
            pass
        self.assertRaises(ValueError, NoModelModelForm)

class OneToOneFieldTests(TestCase):
    def test_assignment_of_none(self):
        class AuthorForm(forms.ModelForm):
            class Meta:
                model = Author
                fields = ['publication', 'full_name']

        publication = Publication.objects.create(title="Pravda",
            date_published=date(1991, 8, 22))
        author = Author.objects.create(publication=publication, full_name='John Doe')
        form = AuthorForm({'publication':'', 'full_name':'John Doe'}, instance=author)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['publication'], None)
        author = form.save()
        # author object returned from form still retains original publication object
        # that's why we need to retreive it from database again
        new_author = Author.objects.get(pk=author.pk)
        self.assertEqual(new_author.publication, None)

    def test_assignment_of_none_null_false(self):
        class AuthorForm(forms.ModelForm):
            class Meta:
                model = Author1
                fields = ['publication', 'full_name']

        publication = Publication.objects.create(title="Pravda",
            date_published=date(1991, 8, 22))
        author = Author1.objects.create(publication=publication, full_name='John Doe')
        form = AuthorForm({'publication':'', 'full_name':'John Doe'}, instance=author)
        self.assertTrue(not form.is_valid())


class ModelChoiceForm(forms.Form):
    person = ModelChoiceField(Person.objects.all())


class TestTicket11183(TestCase):
    def test_11183(self):
        form1 = ModelChoiceForm()
        field1 = form1.fields['person']
        # To allow the widget to change the queryset of field1.widget.choices correctly,
        # without affecting other forms, the following must hold:
        self.assertTrue(field1 is not ModelChoiceForm.base_fields['person'])
        self.assertTrue(field1.widget.choices.field is field1)


class HomepageForm(forms.ModelForm):
    class Meta:
        model = Homepage
        fields = '__all__'


class URLFieldTests(TestCase):
    def test_url_on_modelform(self):
        "Check basic URL field validation on model forms"
        self.assertFalse(HomepageForm({'url': 'foo'}).is_valid())
        self.assertFalse(HomepageForm({'url': 'http://'}).is_valid())
        self.assertFalse(HomepageForm({'url': 'http://example'}).is_valid())
        self.assertFalse(HomepageForm({'url': 'http://example.'}).is_valid())
        self.assertFalse(HomepageForm({'url': 'http://com.'}).is_valid())

        self.assertTrue(HomepageForm({'url': 'http://localhost'}).is_valid())
        self.assertTrue(HomepageForm({'url': 'http://example.com'}).is_valid())
        self.assertTrue(HomepageForm({'url': 'http://www.example.com'}).is_valid())
        self.assertTrue(HomepageForm({'url': 'http://www.example.com:8000'}).is_valid())
        self.assertTrue(HomepageForm({'url': 'http://www.example.com/test'}).is_valid())
        self.assertTrue(HomepageForm({'url': 'http://www.example.com:8000/test'}).is_valid())
        self.assertTrue(HomepageForm({'url': 'http://example.com/foo/bar'}).is_valid())

    def test_http_prefixing(self):
        "If the http:// prefix is omitted on form input, the field adds it again. (Refs #13613)"
        form = HomepageForm({'url': 'example.com'})
        form.is_valid()
        # self.assertTrue(form.is_valid())
        # self.assertEqual(form.cleaned_data['url'], 'http://example.com/')

        form = HomepageForm({'url': 'example.com/test'})
        form.is_valid()
        # self.assertTrue(form.is_valid())
        # self.assertEqual(form.cleaned_data['url'], 'http://example.com/test')


class FormFieldCallbackTests(TestCase):

    def test_baseform_with_widgets_in_meta(self):
        """Regression for #13095: Using base forms with widgets defined in Meta should not raise errors."""
        widget = forms.Textarea()

        class BaseForm(forms.ModelForm):
            class Meta:
                model = Person
                widgets = {'name': widget}
                fields = "__all__"

        Form = modelform_factory(Person, form=BaseForm)
        self.assertTrue(Form.base_fields['name'].widget is widget)

    def test_factory_with_widget_argument(self):
        """ Regression for #15315: modelform_factory should accept widgets
            argument
        """
        widget = forms.Textarea()

        # Without a widget should not set the widget to textarea
        Form = modelform_factory(Person, fields="__all__")
        self.assertNotEqual(Form.base_fields['name'].widget.__class__, forms.Textarea)

        # With a widget should not set the widget to textarea
        Form = modelform_factory(Person, fields="__all__", widgets={'name':widget})
        self.assertEqual(Form.base_fields['name'].widget.__class__, forms.Textarea)

    def test_custom_callback(self):
        """Test that a custom formfield_callback is used if provided"""

        callback_args = []

        def callback(db_field, **kwargs):
            callback_args.append((db_field, kwargs))
            return db_field.formfield(**kwargs)

        widget = forms.Textarea()

        class BaseForm(forms.ModelForm):
            class Meta:
                model = Person
                widgets = {'name': widget}
                fields = "__all__"

        _ = modelform_factory(Person, form=BaseForm,
                              formfield_callback=callback)
        id_field, name_field = Person._meta.fields

        self.assertEqual(callback_args,
                         [(id_field, {}), (name_field, {'widget': widget})])

    def test_bad_callback(self):
        # A bad callback provided by user still gives an error
        self.assertRaises(TypeError, modelform_factory, Person, fields="__all__",
                          formfield_callback='not a function or callable')


class InvalidFieldAndFactory(TestCase):
    """ Tests for #11905 """

    def test_extra_field_model_form(self):
        try:
            class ExtraPersonForm(forms.ModelForm):
                """ ModelForm with an extra field """

                age = forms.IntegerField()

                class Meta:
                    model = Person
                    fields = ('name', 'no-field')
        except FieldError as e:
            # Make sure the exception contains some reference to the
            # field responsible for the problem.
            self.assertTrue('no-field' in e.args[0])
        else:
            self.fail('Invalid "no-field" field not caught')

    def test_extra_declared_field_model_form(self):
        try:
            class ExtraPersonForm(forms.ModelForm):
                """ ModelForm with an extra field """

                age = forms.IntegerField()

                class Meta:
                    model = Person
                    fields = ('name', 'age')
        except FieldError:
            self.fail('Declarative field raised FieldError incorrectly')

    def test_extra_field_modelform_factory(self):
        self.assertRaises(FieldError, modelform_factory,
                          Person, fields=['no-field', 'name'])


class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = '__all__'


class FileFieldTests(unittest.TestCase):
    def test_clean_false(self):
        """
        If the ``clean`` method on a non-required FileField receives False as
        the data (meaning clear the field value), it returns False, regardless
        of the value of ``initial``.

        """
        f = forms.FileField(required=False)
        self.assertEqual(f.clean(False), False)
        self.assertEqual(f.clean(False, 'initial'), False)

    def test_clean_false_required(self):
        """
        If the ``clean`` method on a required FileField receives False as the
        data, it has the same effect as None: initial is returned if non-empty,
        otherwise the validation catches the lack of a required value.

        """
        f = forms.FileField(required=True)
        self.assertEqual(f.clean(False, 'initial'), 'initial')
        self.assertRaises(ValidationError, f.clean, False)

    def test_full_clear(self):
        """
        Integration happy-path test that a model FileField can actually be set
        and cleared via a ModelForm.

        """
        form = DocumentForm()
        self.assertTrue('name="myfile"' in six.text_type(form))
        self.assertTrue('myfile-clear' not in six.text_type(form))
        form = DocumentForm(files={'myfile': SimpleUploadedFile('something.txt', b'content')})
        self.assertTrue(form.is_valid())
        doc = form.save(commit=False)
        self.assertEqual(doc.myfile.name, 'something.txt')
        form = DocumentForm(instance=doc)
        self.assertTrue('myfile-clear' in six.text_type(form))
        form = DocumentForm(instance=doc, data={'myfile-clear': 'true'})
        doc = form.save(commit=False)
        self.assertEqual(bool(doc.myfile), False)

    def test_clear_and_file_contradiction(self):
        """
        If the user submits a new file upload AND checks the clear checkbox,
        they get a validation error, and the bound redisplay of the form still
        includes the current file and the clear checkbox.

        """
        form = DocumentForm(files={'myfile': SimpleUploadedFile('something.txt', b'content')})
        self.assertTrue(form.is_valid())
        doc = form.save(commit=False)
        form = DocumentForm(instance=doc,
                            files={'myfile': SimpleUploadedFile('something.txt', b'content')},
                            data={'myfile-clear': 'true'})
        self.assertTrue(not form.is_valid())
        self.assertEqual(form.errors['myfile'],
                         ['Please either submit a file or check the clear checkbox, not both.'])
        rendered = six.text_type(form)
        self.assertTrue('something.txt' in rendered)
        self.assertTrue('myfile-clear' in rendered)


class EditionForm(forms.ModelForm):
    author = forms.ModelChoiceField(queryset=Person.objects.all())
    publication = forms.ModelChoiceField(queryset=Publication.objects.all())
    edition = forms.IntegerField()
    isbn = forms.CharField(max_length=13)

    class Meta:
        model = Edition
        fields = '__all__'


class UniqueErrorsTests(TestCase):
    def setUp(self):
        self.author1 = Person.objects.create(name='Author #1')
        self.author2 = Person.objects.create(name='Author #2')
        self.pub1 = Publication.objects.create(title='Pub #1', date_published=date(2000, 10, 31))
        self.pub2 = Publication.objects.create(title='Pub #2', date_published=date(2004, 1, 5))
        form = EditionForm(data={'author': self.author1.pk, 'publication': self.pub1.pk, 'edition': 1, 'isbn': '9783161484100'})
        form.save()

    def test_unique_error_message(self):
        form = EditionForm(data={'author': self.author1.pk, 'publication': self.pub2.pk, 'edition': 1, 'isbn': '9783161484100'})
        self.assertEqual(form.errors, {'isbn': ['Edition with this Isbn already exists.']})

    def test_unique_together_error_message(self):
        form = EditionForm(data={'author': self.author1.pk, 'publication': self.pub1.pk, 'edition': 2, 'isbn': '9783161489999'})
        self.assertEqual(form.errors, {'__all__': ['Edition with this Author and Publication already exists.']})
        form = EditionForm(data={'author': self.author2.pk, 'publication': self.pub1.pk, 'edition': 1, 'isbn': '9783161487777'})
        self.assertEqual(form.errors, {'__all__': ['Edition with this Publication and Edition already exists.']})


class EmptyFieldsTestCase(TestCase):
    "Tests for fields=() cases as reported in #14119"
    class EmptyPersonForm(forms.ModelForm):
        class Meta:
            model = Person
            fields = ()

    def test_empty_fields_to_fields_for_model(self):
        "An argument of fields=() to fields_for_model should return an empty dictionary"
        field_dict = fields_for_model(Person, fields=())
        self.assertEqual(len(field_dict), 0)

    def test_empty_fields_on_modelform(self):
        "No fields on a ModelForm should actually result in no fields"
        form = self.EmptyPersonForm()
        self.assertEqual(len(form.fields), 0)

    def test_empty_fields_to_construct_instance(self):
        "No fields should be set on a model instance if construct_instance receives fields=()"
        form = modelform_factory(Person, fields="__all__")({'name': 'John Doe'})
        self.assertTrue(form.is_valid())
        instance = construct_instance(form, Person(), fields=())
        self.assertEqual(instance.name, '')


class CustomMetaclass(ModelFormMetaclass):
    def __new__(cls, name, bases, attrs):
        new = super(CustomMetaclass, cls).__new__(cls, name, bases, attrs)
        new.base_fields = {}
        return new


class CustomMetaclassForm(six.with_metaclass(CustomMetaclass, forms.ModelForm)):
    pass


class CustomMetaclassTestCase(TestCase):
    def test_modelform_factory_metaclass(self):
        new_cls = modelform_factory(Person, fields="__all__", form=CustomMetaclassForm)
        self.assertEqual(new_cls.base_fields, {})


class TestTicket19733(TestCase):
    def test_modelform_factory_without_fields(self):
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always", PendingDeprecationWarning)
            # This should become an error once deprecation cycle is complete.
            form = modelform_factory(Person)
        self.assertEqual(w[0].category, PendingDeprecationWarning)

    def test_modelform_factory_with_all_fields(self):
        form = modelform_factory(Person, fields="__all__")
        self.assertEqual(list(form.base_fields), ["name"])
