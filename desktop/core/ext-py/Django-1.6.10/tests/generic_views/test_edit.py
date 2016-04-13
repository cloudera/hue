from __future__ import absolute_import

import warnings

from django.core.exceptions import ImproperlyConfigured
from django.core.urlresolvers import reverse
from django import forms
from django.test import TestCase
from django.utils.unittest import expectedFailure
from django.test.client import RequestFactory
from django.views.generic.base import View
from django.views.generic.edit import FormMixin, CreateView

from . import views
from .models import Artist, Author


class FormMixinTests(TestCase):
    def test_initial_data(self):
        """ Test instance independence of initial data dict (see #16138) """
        initial_1 = FormMixin().get_initial()
        initial_1['foo'] = 'bar'
        initial_2 = FormMixin().get_initial()
        self.assertNotEqual(initial_1, initial_2)

    def test_get_prefix(self):
        """ Test prefix can be set (see #18872) """
        test_string = 'test'

        rf = RequestFactory()
        get_request = rf.get('/')

        class TestFormMixin(FormMixin):
            request = get_request

        default_kwargs = TestFormMixin().get_form_kwargs()
        self.assertEqual(None, default_kwargs.get('prefix'))

        set_mixin = TestFormMixin()
        set_mixin.prefix = test_string
        set_kwargs = set_mixin.get_form_kwargs()
        self.assertEqual(test_string, set_kwargs.get('prefix'))


class BasicFormTests(TestCase):
    urls = 'generic_views.urls'

    def test_post_data(self):
        res = self.client.post('/contact/', {'name': "Me", 'message': "Hello"})
        self.assertRedirects(res, 'http://testserver/list/authors/')


class ModelFormMixinTests(TestCase):
    def test_get_form(self):
        form_class = views.AuthorGetQuerySetFormView().get_form_class()
        self.assertEqual(form_class._meta.model, Author)


class CreateViewTests(TestCase):
    urls = 'generic_views.urls'

    def test_create(self):
        res = self.client.get('/edit/authors/create/')
        self.assertEqual(res.status_code, 200)
        self.assertIsInstance(res.context['form'], forms.ModelForm)
        self.assertIsInstance(res.context['view'], View)
        self.assertFalse('object' in res.context)
        self.assertFalse('author' in res.context)
        self.assertTemplateUsed(res, 'generic_views/author_form.html')

        res = self.client.post('/edit/authors/create/',
                        {'name': 'Randall Munroe', 'slug': 'randall-munroe'})
        self.assertEqual(res.status_code, 302)
        self.assertRedirects(res, 'http://testserver/list/authors/')
        self.assertQuerysetEqual(Author.objects.all(), ['<Author: Randall Munroe>'])

    def test_create_invalid(self):
        res = self.client.post('/edit/authors/create/',
                        {'name': 'A' * 101, 'slug': 'randall-munroe'})
        self.assertEqual(res.status_code, 200)
        self.assertTemplateUsed(res, 'generic_views/author_form.html')
        self.assertEqual(len(res.context['form'].errors), 1)
        self.assertEqual(Author.objects.count(), 0)

    def test_create_with_object_url(self):
        res = self.client.post('/edit/artists/create/',
                        {'name': 'Rene Magritte'})
        self.assertEqual(res.status_code, 302)
        artist = Artist.objects.get(name='Rene Magritte')
        self.assertRedirects(res, 'http://testserver/detail/artist/%d/' % artist.pk)
        self.assertQuerysetEqual(Artist.objects.all(), ['<Artist: Rene Magritte>'])

    def test_create_with_redirect(self):
        res = self.client.post('/edit/authors/create/redirect/',
                            {'name': 'Randall Munroe', 'slug': 'randall-munroe'})
        self.assertEqual(res.status_code, 302)
        self.assertRedirects(res, 'http://testserver/edit/authors/create/')
        self.assertQuerysetEqual(Author.objects.all(), ['<Author: Randall Munroe>'])

    def test_create_with_interpolated_redirect(self):
        res = self.client.post('/edit/authors/create/interpolate_redirect/',
                            {'name': 'Randall Munroe', 'slug': 'randall-munroe'})
        self.assertQuerysetEqual(Author.objects.all(), ['<Author: Randall Munroe>'])
        self.assertEqual(res.status_code, 302)
        pk = Author.objects.all()[0].pk
        self.assertRedirects(res, 'http://testserver/edit/author/%d/update/' % pk)

    def test_create_with_special_properties(self):
        res = self.client.get('/edit/authors/create/special/')
        self.assertEqual(res.status_code, 200)
        self.assertIsInstance(res.context['form'], views.AuthorForm)
        self.assertFalse('object' in res.context)
        self.assertFalse('author' in res.context)
        self.assertTemplateUsed(res, 'generic_views/form.html')

        res = self.client.post('/edit/authors/create/special/',
                            {'name': 'Randall Munroe', 'slug': 'randall-munroe'})
        self.assertEqual(res.status_code, 302)
        obj = Author.objects.get(slug='randall-munroe')
        self.assertRedirects(res, reverse('author_detail', kwargs={'pk': obj.pk}))
        self.assertQuerysetEqual(Author.objects.all(), ['<Author: Randall Munroe>'])

    def test_create_without_redirect(self):
        try:
            res = self.client.post('/edit/authors/create/naive/',
                            {'name': 'Randall Munroe', 'slug': 'randall-munroe'})
            self.fail('Should raise exception -- No redirect URL provided, and no get_absolute_url provided')
        except ImproperlyConfigured:
            pass

    def test_create_restricted(self):
        res = self.client.post('/edit/authors/create/restricted/',
                        {'name': 'Randall Munroe', 'slug': 'randall-munroe'})
        self.assertEqual(res.status_code, 302)
        self.assertRedirects(res, 'http://testserver/accounts/login/?next=/edit/authors/create/restricted/')

    def test_create_view_with_restricted_fields(self):

        class MyCreateView(CreateView):
            model = Author
            fields = ['name']

        self.assertEqual(list(MyCreateView().get_form_class().base_fields),
                         ['name'])

    def test_create_view_all_fields(self):

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always", PendingDeprecationWarning)

            class MyCreateView(CreateView):
                model = Author
                fields = '__all__'

            self.assertEqual(list(MyCreateView().get_form_class().base_fields),
                             ['name', 'slug'])
        self.assertEqual(len(w), 0)


    def test_create_view_without_explicit_fields(self):

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always", PendingDeprecationWarning)

            class MyCreateView(CreateView):
                model = Author

            # Until end of the deprecation cycle, should still create the form
            # as before:
            self.assertEqual(list(MyCreateView().get_form_class().base_fields),
                             ['name', 'slug'])

        # but with a warning:
        self.assertEqual(w[0].category, PendingDeprecationWarning)


class UpdateViewTests(TestCase):
    urls = 'generic_views.urls'

    def test_update_post(self):
        a = Author.objects.create(
            name='Randall Munroe',
            slug='randall-munroe',
        )
        res = self.client.get('/edit/author/%d/update/' % a.pk)
        self.assertEqual(res.status_code, 200)
        self.assertIsInstance(res.context['form'], forms.ModelForm)
        self.assertEqual(res.context['object'], Author.objects.get(pk=a.pk))
        self.assertEqual(res.context['author'], Author.objects.get(pk=a.pk))
        self.assertTemplateUsed(res, 'generic_views/author_form.html')

        # Modification with both POST and PUT (browser compatible)
        res = self.client.post('/edit/author/%d/update/' % a.pk,
                        {'name': 'Randall Munroe (xkcd)', 'slug': 'randall-munroe'})
        self.assertEqual(res.status_code, 302)
        self.assertRedirects(res, 'http://testserver/list/authors/')
        self.assertQuerysetEqual(Author.objects.all(), ['<Author: Randall Munroe (xkcd)>'])

    @expectedFailure
    def test_update_put(self):
        a = Author.objects.create(
            name='Randall Munroe',
            slug='randall-munroe',
        )
        res = self.client.get('/edit/author/%d/update/' % a.pk)
        self.assertEqual(res.status_code, 200)
        self.assertTemplateUsed(res, 'generic_views/author_form.html')

        res = self.client.put('/edit/author/%d/update/' % a.pk,
                        {'name': 'Randall Munroe (author of xkcd)', 'slug': 'randall-munroe'})
        # Here is the expected failure. PUT data are not processed in any special
        # way by django. So the request will equal to a POST without data, hence
        # the form will be invalid and redisplayed with errors (status code 200).
        # See also #12635
        self.assertEqual(res.status_code, 302)
        self.assertRedirects(res, 'http://testserver/list/authors/')
        self.assertQuerysetEqual(Author.objects.all(), ['<Author: Randall Munroe (author of xkcd)>'])

    def test_update_invalid(self):
        a = Author.objects.create(
            name='Randall Munroe',
            slug='randall-munroe',
        )
        res = self.client.post('/edit/author/%d/update/' % a.pk,
                        {'name': 'A' * 101, 'slug': 'randall-munroe'})
        self.assertEqual(res.status_code, 200)
        self.assertTemplateUsed(res, 'generic_views/author_form.html')
        self.assertEqual(len(res.context['form'].errors), 1)
        self.assertQuerysetEqual(Author.objects.all(), ['<Author: Randall Munroe>'])

    def test_update_with_object_url(self):
        a = Artist.objects.create(name='Rene Magritte')
        res = self.client.post('/edit/artists/%d/update/' % a.pk,
                        {'name': 'Rene Magritte'})
        self.assertEqual(res.status_code, 302)
        self.assertRedirects(res, 'http://testserver/detail/artist/%d/' % a.pk)
        self.assertQuerysetEqual(Artist.objects.all(), ['<Artist: Rene Magritte>'])

    def test_update_with_redirect(self):
        a = Author.objects.create(
            name='Randall Munroe',
            slug='randall-munroe',
        )
        res = self.client.post('/edit/author/%d/update/redirect/' % a.pk,
                        {'name': 'Randall Munroe (author of xkcd)', 'slug': 'randall-munroe'})
        self.assertEqual(res.status_code, 302)
        self.assertRedirects(res, 'http://testserver/edit/authors/create/')
        self.assertQuerysetEqual(Author.objects.all(), ['<Author: Randall Munroe (author of xkcd)>'])

    def test_update_with_interpolated_redirect(self):
        a = Author.objects.create(
            name='Randall Munroe',
            slug='randall-munroe',
        )
        res = self.client.post('/edit/author/%d/update/interpolate_redirect/' % a.pk,
                        {'name': 'Randall Munroe (author of xkcd)', 'slug': 'randall-munroe'})
        self.assertQuerysetEqual(Author.objects.all(), ['<Author: Randall Munroe (author of xkcd)>'])
        self.assertEqual(res.status_code, 302)
        pk = Author.objects.all()[0].pk
        self.assertRedirects(res, 'http://testserver/edit/author/%d/update/' % pk)

    def test_update_with_special_properties(self):
        a = Author.objects.create(
            name='Randall Munroe',
            slug='randall-munroe',
        )
        res = self.client.get('/edit/author/%d/update/special/' % a.pk)
        self.assertEqual(res.status_code, 200)
        self.assertIsInstance(res.context['form'], views.AuthorForm)
        self.assertEqual(res.context['object'], Author.objects.get(pk=a.pk))
        self.assertEqual(res.context['thingy'], Author.objects.get(pk=a.pk))
        self.assertFalse('author' in res.context)
        self.assertTemplateUsed(res, 'generic_views/form.html')

        res = self.client.post('/edit/author/%d/update/special/' % a.pk,
                        {'name': 'Randall Munroe (author of xkcd)', 'slug': 'randall-munroe'})
        self.assertEqual(res.status_code, 302)
        self.assertRedirects(res, 'http://testserver/detail/author/%d/' % a.pk)
        self.assertQuerysetEqual(Author.objects.all(), ['<Author: Randall Munroe (author of xkcd)>'])

    def test_update_without_redirect(self):
        try:
            a = Author.objects.create(
                name='Randall Munroe',
                slug='randall-munroe',
            )
            res = self.client.post('/edit/author/%d/update/naive/' % a.pk,
                            {'name': 'Randall Munroe (author of xkcd)', 'slug': 'randall-munroe'})
            self.fail('Should raise exception -- No redirect URL provided, and no get_absolute_url provided')
        except ImproperlyConfigured:
            pass

    def test_update_get_object(self):
        a = Author.objects.create(
            pk=1,
            name='Randall Munroe',
            slug='randall-munroe',
        )
        res = self.client.get('/edit/author/update/')
        self.assertEqual(res.status_code, 200)
        self.assertIsInstance(res.context['form'], forms.ModelForm)
        self.assertIsInstance(res.context['view'], View)
        self.assertEqual(res.context['object'], Author.objects.get(pk=a.pk))
        self.assertEqual(res.context['author'], Author.objects.get(pk=a.pk))
        self.assertTemplateUsed(res, 'generic_views/author_form.html')

        # Modification with both POST and PUT (browser compatible)
        res = self.client.post('/edit/author/update/',
                        {'name': 'Randall Munroe (xkcd)', 'slug': 'randall-munroe'})
        self.assertEqual(res.status_code, 302)
        self.assertRedirects(res, 'http://testserver/list/authors/')
        self.assertQuerysetEqual(Author.objects.all(), ['<Author: Randall Munroe (xkcd)>'])


class DeleteViewTests(TestCase):
    urls = 'generic_views.urls'

    def test_delete_by_post(self):
        a = Author.objects.create(**{'name': 'Randall Munroe', 'slug': 'randall-munroe'})
        res = self.client.get('/edit/author/%d/delete/' % a.pk)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.context['object'], Author.objects.get(pk=a.pk))
        self.assertEqual(res.context['author'], Author.objects.get(pk=a.pk))
        self.assertTemplateUsed(res, 'generic_views/author_confirm_delete.html')

        # Deletion with POST
        res = self.client.post('/edit/author/%d/delete/' % a.pk)
        self.assertEqual(res.status_code, 302)
        self.assertRedirects(res, 'http://testserver/list/authors/')
        self.assertQuerysetEqual(Author.objects.all(), [])

    def test_delete_by_delete(self):
        # Deletion with browser compatible DELETE method
        a = Author.objects.create(**{'name': 'Randall Munroe', 'slug': 'randall-munroe'})
        res = self.client.delete('/edit/author/%d/delete/' % a.pk)
        self.assertEqual(res.status_code, 302)
        self.assertRedirects(res, 'http://testserver/list/authors/')
        self.assertQuerysetEqual(Author.objects.all(), [])

    def test_delete_with_redirect(self):
        a = Author.objects.create(**{'name': 'Randall Munroe', 'slug': 'randall-munroe'})
        res = self.client.post('/edit/author/%d/delete/redirect/' % a.pk)
        self.assertEqual(res.status_code, 302)
        self.assertRedirects(res, 'http://testserver/edit/authors/create/')
        self.assertQuerysetEqual(Author.objects.all(), [])

    def test_delete_with_interpolated_redirect(self):
        a = Author.objects.create(**{'name': 'Randall Munroe', 'slug': 'randall-munroe'})
        res = self.client.post('/edit/author/%d/delete/interpolate_redirect/' % a.pk)
        self.assertEqual(res.status_code, 302)
        self.assertRedirects(res, 'http://testserver/edit/authors/create/?deleted=%d' % a.pk)
        self.assertQuerysetEqual(Author.objects.all(), [])

    def test_delete_with_special_properties(self):
        a = Author.objects.create(**{'name': 'Randall Munroe', 'slug': 'randall-munroe'})
        res = self.client.get('/edit/author/%d/delete/special/' % a.pk)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.context['object'], Author.objects.get(pk=a.pk))
        self.assertEqual(res.context['thingy'], Author.objects.get(pk=a.pk))
        self.assertFalse('author' in res.context)
        self.assertTemplateUsed(res, 'generic_views/confirm_delete.html')

        res = self.client.post('/edit/author/%d/delete/special/' % a.pk)
        self.assertEqual(res.status_code, 302)
        self.assertRedirects(res, 'http://testserver/list/authors/')
        self.assertQuerysetEqual(Author.objects.all(), [])

    def test_delete_without_redirect(self):
        try:
            a = Author.objects.create(
                name='Randall Munroe',
                slug='randall-munroe',
            )
            res = self.client.post('/edit/author/%d/delete/naive/' % a.pk)
            self.fail('Should raise exception -- No redirect URL provided, and no get_absolute_url provided')
        except ImproperlyConfigured:
            pass

