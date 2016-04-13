from __future__ import absolute_import

from django import forms
from django.contrib import admin
from django.core.exceptions import ImproperlyConfigured
from django.test import TestCase

from .models import Song, Book, Album, TwoAlbumFKAndAnE, State, City


class SongForm(forms.ModelForm):
    pass

class ValidFields(admin.ModelAdmin):
    form = SongForm
    fields = ['title']

class ValidFormFieldsets(admin.ModelAdmin):
    def get_form(self, request, obj=None, **kwargs):
        class ExtraFieldForm(SongForm):
            name = forms.CharField(max_length=50)
        return ExtraFieldForm

    fieldsets = (
        (None, {
            'fields': ('name',),
        }),
    )

class ValidationTestCase(TestCase):

    def test_readonly_and_editable(self):
        class SongAdmin(admin.ModelAdmin):
            readonly_fields = ["original_release"]
            fieldsets = [
                (None, {
                    "fields": ["title", "original_release"],
                }),
            ]
        SongAdmin.validate(Song)

    def test_custom_modelforms_with_fields_fieldsets(self):
        """
        # Regression test for #8027: custom ModelForms with fields/fieldsets
        """
        ValidFields.validate(Song)

    def test_custom_get_form_with_fieldsets(self):
        """
        Ensure that the fieldsets validation is skipped when the ModelAdmin.get_form() method
        is overridden.
        Refs #19445.
        """
        ValidFormFieldsets.validate(Song)

    def test_exclude_values(self):
        """
        Tests for basic validation of 'exclude' option values (#12689)
        """
        class ExcludedFields1(admin.ModelAdmin):
            exclude = ('foo')
        self.assertRaisesMessage(ImproperlyConfigured,
            "'ExcludedFields1.exclude' must be a list or tuple.",
            ExcludedFields1.validate,
            Book)

    def test_exclude_duplicate_values(self):
        class ExcludedFields2(admin.ModelAdmin):
            exclude = ('name', 'name')
        self.assertRaisesMessage(ImproperlyConfigured,
            "There are duplicate field(s) in ExcludedFields2.exclude",
            ExcludedFields2.validate,
            Book)

    def test_exclude_in_inline(self):
        class ExcludedFieldsInline(admin.TabularInline):
            model = Song
            exclude = ('foo')

        class ExcludedFieldsAlbumAdmin(admin.ModelAdmin):
            model = Album
            inlines = [ExcludedFieldsInline]

        self.assertRaisesMessage(ImproperlyConfigured,
            "'ExcludedFieldsInline.exclude' must be a list or tuple.",
            ExcludedFieldsAlbumAdmin.validate,
            Album)

    def test_exclude_inline_model_admin(self):
        """
        # Regression test for #9932 - exclude in InlineModelAdmin
        # should not contain the ForeignKey field used in ModelAdmin.model
        """
        class SongInline(admin.StackedInline):
            model = Song
            exclude = ['album']

        class AlbumAdmin(admin.ModelAdmin):
            model = Album
            inlines = [SongInline]

        self.assertRaisesMessage(ImproperlyConfigured,
            "SongInline cannot exclude the field 'album' - this is the foreign key to the parent model admin_validation.Album.",
            AlbumAdmin.validate,
            Album)

    def test_app_label_in_admin_validation(self):
        """
        Regression test for #15669 - Include app label in admin validation messages
        """
        class RawIdNonexistingAdmin(admin.ModelAdmin):
            raw_id_fields = ('nonexisting',)

        self.assertRaisesMessage(ImproperlyConfigured,
            "'RawIdNonexistingAdmin.raw_id_fields' refers to field 'nonexisting' that is missing from model 'admin_validation.Album'.",
            RawIdNonexistingAdmin.validate,
            Album)

    def test_fk_exclusion(self):
        """
        Regression test for #11709 - when testing for fk excluding (when exclude is
        given) make sure fk_name is honored or things blow up when there is more
        than one fk to the parent model.
        """
        class TwoAlbumFKAndAnEInline(admin.TabularInline):
            model = TwoAlbumFKAndAnE
            exclude = ("e",)
            fk_name = "album1"
        class MyAdmin(admin.ModelAdmin):
            inlines = [TwoAlbumFKAndAnEInline]
        MyAdmin.validate(Album)


    def test_inline_self_validation(self):
        class TwoAlbumFKAndAnEInline(admin.TabularInline):
            model = TwoAlbumFKAndAnE
        class MyAdmin(admin.ModelAdmin):
            inlines = [TwoAlbumFKAndAnEInline]

        self.assertRaisesMessage(Exception,
            "<class 'admin_validation.models.TwoAlbumFKAndAnE'> has more than 1 ForeignKey to <class 'admin_validation.models.Album'>",
            MyAdmin.validate, Album)

    def test_inline_with_specified(self):
        class TwoAlbumFKAndAnEInline(admin.TabularInline):
            model = TwoAlbumFKAndAnE
            fk_name = "album1"

        class MyAdmin(admin.ModelAdmin):
            inlines = [TwoAlbumFKAndAnEInline]
        MyAdmin.validate(Album)

    def test_readonly(self):
        class SongAdmin(admin.ModelAdmin):
            readonly_fields = ("title",)

        SongAdmin.validate(Song)

    def test_readonly_on_method(self):
        def my_function(obj):
            pass

        class SongAdmin(admin.ModelAdmin):
            readonly_fields = (my_function,)

        SongAdmin.validate(Song)

    def test_readonly_on_modeladmin(self):
        class SongAdmin(admin.ModelAdmin):
            readonly_fields = ("readonly_method_on_modeladmin",)

            def readonly_method_on_modeladmin(self, obj):
                pass

        SongAdmin.validate(Song)

    def test_readonly_method_on_model(self):
        class SongAdmin(admin.ModelAdmin):
            readonly_fields = ("readonly_method_on_model",)

        SongAdmin.validate(Song)

    def test_nonexistant_field(self):
        class SongAdmin(admin.ModelAdmin):
            readonly_fields = ("title", "nonexistant")

        self.assertRaisesMessage(ImproperlyConfigured,
            "SongAdmin.readonly_fields[1], 'nonexistant' is not a callable or an attribute of 'SongAdmin' or found in the model 'Song'.",
            SongAdmin.validate,
            Song)

    def test_nonexistant_field_on_inline(self):
        class CityInline(admin.TabularInline):
            model = City
            readonly_fields=['i_dont_exist'] # Missing attribute

        self.assertRaisesMessage(ImproperlyConfigured,
            "CityInline.readonly_fields[0], 'i_dont_exist' is not a callable or an attribute of 'CityInline' or found in the model 'City'.",
            CityInline.validate,
            City)

    def test_extra(self):
        class SongAdmin(admin.ModelAdmin):
            def awesome_song(self, instance):
                if instance.title == "Born to Run":
                    return "Best Ever!"
                return "Status unknown."
        SongAdmin.validate(Song)

    def test_readonly_lambda(self):
        class SongAdmin(admin.ModelAdmin):
            readonly_fields = (lambda obj: "test",)

        SongAdmin.validate(Song)

    def test_graceful_m2m_fail(self):
        """
        Regression test for #12203/#12237 - Fail more gracefully when a M2M field that
        specifies the 'through' option is included in the 'fields' or the 'fieldsets'
        ModelAdmin options.
        """

        class BookAdmin(admin.ModelAdmin):
            fields = ['authors']

        self.assertRaisesMessage(ImproperlyConfigured,
            "'BookAdmin.fields' can't include the ManyToManyField field 'authors' because 'authors' manually specifies a 'through' model.",
            BookAdmin.validate,
            Book)

    def test_cannot_include_through(self):
        class FieldsetBookAdmin(admin.ModelAdmin):
            fieldsets = (
                ('Header 1', {'fields': ('name',)}),
                ('Header 2', {'fields': ('authors',)}),
            )
        self.assertRaisesMessage(ImproperlyConfigured,
            "'FieldsetBookAdmin.fieldsets[1][1]['fields']' can't include the ManyToManyField field 'authors' because 'authors' manually specifies a 'through' model.",
            FieldsetBookAdmin.validate,
            Book)

    def test_nested_fields(self):
        class NestedFieldsAdmin(admin.ModelAdmin):
           fields = ('price', ('name', 'subtitle'))
        NestedFieldsAdmin.validate(Book)

    def test_nested_fieldsets(self):
        class NestedFieldsetAdmin(admin.ModelAdmin):
           fieldsets = (
               ('Main', {'fields': ('price', ('name', 'subtitle'))}),
           )
        NestedFieldsetAdmin.validate(Book)

    def test_explicit_through_override(self):
        """
        Regression test for #12209 -- If the explicitly provided through model
        is specified as a string, the admin should still be able use
        Model.m2m_field.through
        """

        class AuthorsInline(admin.TabularInline):
            model = Book.authors.through

        class BookAdmin(admin.ModelAdmin):
            inlines = [AuthorsInline]

        # If the through model is still a string (and hasn't been resolved to a model)
        # the validation will fail.
        BookAdmin.validate(Book)

    def test_non_model_fields(self):
        """
        Regression for ensuring ModelAdmin.fields can contain non-model fields
        that broke with r11737
        """
        class SongForm(forms.ModelForm):
            extra_data = forms.CharField()

        class FieldsOnFormOnlyAdmin(admin.ModelAdmin):
            form = SongForm
            fields = ['title', 'extra_data']

        FieldsOnFormOnlyAdmin.validate(Song)

    def test_non_model_first_field(self):
        """
        Regression for ensuring ModelAdmin.field can handle first elem being a
        non-model field (test fix for UnboundLocalError introduced with r16225).
        """
        class SongForm(forms.ModelForm):
            extra_data = forms.CharField()
            class Meta:
                model = Song
                fields = '__all__'


        class FieldsOnFormOnlyAdmin(admin.ModelAdmin):
            form = SongForm
            fields = ['extra_data', 'title']

        FieldsOnFormOnlyAdmin.validate(Song)
