import os
import tempfile

from django.conf import settings
from django.template import TemplateDoesNotExist, TemplateSyntaxError
from django.test import TestCase, RequestFactory
from mako.exceptions import SyntaxException
from mako.template import Template as MakoTemplate

from djangomako.backends import MakoEngine, Template, MakoBackend


class MakoEngineTests(TestCase):
    def setUp(self):
        tmp_dir = tempfile.gettempdir()
        self.template_name = 'good_template.html'
        template_string = '<% name="Jazzar" %> My name is ${name}.'

        tmp_template = os.path.join(tmp_dir, self.template_name)
        with open(tmp_template, 'w') as f:
            f.write(template_string)

        options = {'directories': [tmp_dir]}
        self.engine = MakoEngine(**options)

    def test_get_template(self):
        template = self.engine.get_template(self.template_name)
        self.assertIsNotNone(template)
        self.assertIsInstance(template, MakoTemplate)

    def test_from_string(self):
        template_code = '1+1 = ${ value }'

        template = self.engine.from_string(template_code)
        self.assertIsNotNone(template)
        self.assertIsInstance(template, MakoTemplate)


class TemplateStaticTests(TestCase):
    def setUp(self):
        tmp_dir = tempfile.gettempdir()
        template_name = 'good_template.html'

        self.template_string = 'My name is ${name}, and my static ' \
                               'url is ${ static(\'image.png\') }'
        tmp_template = os.path.join(tmp_dir, template_name)
        with open(tmp_template, 'w') as f:
            f.write(self.template_string)

        options = {'directories': [tmp_dir]}
        self.engine = MakoEngine(**options)

        template = self.engine.get_template(template_name)
        self.template = Template(template)

    def test_render(self):
        request_factory = RequestFactory()
        request = request_factory.get('/mako')

        context = {'name': 'Jazzar'}
        result = self.template.render(context=context, request=request)

        self.assertIn('My name is Jazzar', result)
        self.assertIn('image.png', result)
        self.assertIn(settings.STATIC_URL, result)


class TemplateTests(TestCase):
    def setUp(self):
        tmp_dir = tempfile.gettempdir()
        template_name = 'good_template.html'
        self.template_string = 'My name is ${name}.'

        tmp_template = os.path.join(tmp_dir, template_name)
        with open(tmp_template, 'w') as f:
            f.write(self.template_string)

        options = {'directories': [tmp_dir]}
        self.engine = MakoEngine(**options)

        template = self.engine.get_template(template_name)
        self.template = Template(template)

    def test_render(self):
        request_factory = RequestFactory()
        request = request_factory.get('/mako')

        context = {'name': 'Jazzar'}
        result = self.template.render(context=context, request=request)
        self.assertEqual(result, 'My name is Jazzar.')

    def test_render_request_only(self):
        template_string = '<% name = "Jazzar" %>My name is ${ name }.'
        template = self.engine.from_string(template_string)
        template = Template(template)

        self.assertEqual(template.render(), 'My name is Jazzar.')

    def test_render_error(self):
        with self.assertRaises(NameError):
            # This should fail because the variables defined in the
            # template aren't passed in the context.
            self.template.render()


class MakoBackendTests(TestCase):
    def setUp(self):
        self.tmp_dir = tempfile.gettempdir()
        self.template_name = 'good_template.html'
        self.bad_string = '<% name="Jazzar" My name is ${name}.'
        self.template_string = '<% name="Jazzar" %> My name is ${name}.'

        tmp_template = os.path.join(self.tmp_dir, self.template_name)
        with open(tmp_template, 'w') as f:
            f.write(self.template_string)

        parameters = {
            'NAME': 'mako',
            'DIRS': [self.tmp_dir],
            'APP_DIRS': False,
            'OPTIONS': {}
        }

        self.mako_backend = MakoBackend(parameters)

    def test_from_string(self):
        template = self.mako_backend.from_string(self.template_string)
        self.assertIsNotNone(template)
        self.assertIsInstance(template, Template)

    def test_get_template(self):
        template = self.mako_backend.get_template(self.template_name)
        self.assertIsNotNone(self.template_name)
        self.assertIsInstance(template, Template)

    def test_from_string_error(self):
        with self.assertRaises(TemplateSyntaxError):
            self.mako_backend.from_string(self.bad_string)

    def test_get_template_error(self):
        with self.assertRaises(TemplateDoesNotExist):
            self.mako_backend.get_template('wow.html')

        # Mocj a new bad template
        template_name = 'bad.html'
        bad_template = os.path.join(self.tmp_dir, template_name)
        with open(bad_template, 'w') as f:
            f.write(self.bad_string)

        with self.assertRaises(SyntaxException):
            self.mako_backend.get_template(template_name)
