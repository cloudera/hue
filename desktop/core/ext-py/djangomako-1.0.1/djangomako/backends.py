"""
Mako Template Backend

This is the implementation of Mako template backend in order to use
it as a Django Template Backend alternative in this project template
system. This backend is a class that inherits
django.template.backends.base.BaseEngine. It must implement
get_template() and optionally from_string().
"""

import tempfile

from django.urls import reverse
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.template.base import TemplateDoesNotExist, TemplateSyntaxError
from django.template.backends.base import BaseEngine
from django.template.backends.utils import csrf_input_lazy, \
    csrf_token_lazy

from django.utils.module_loading import import_string
from mako.template import Template as MakoTemplate
from mako import exceptions as mako_exceptions


class MakoEngine(object):
    """
    This is the engine that handles getting the template and
    compiling the template the code.
    """
    def __init__(self, **options):
        """
        :param options: The template options that are passed to the
        template lookup class.
        """
        environment = options.pop(
            'environment', 'mako.lookup.TemplateLookup')
        # Just to get a dotted module path as an/a attribute/class
        Environment = import_string(environment)
        self.context_processors = options.pop('context_processors', [])
        self.lookup = Environment(**options)

    def get_template(self, name):
        """
        Locates template source files from the local filesystem given
        a template name.
        :param name: The template name.
        :return: the located template.
        """
        return self.lookup.get_template(name)

    def from_string(self, template_code):
        """
        Compiles the template code and return the compiled version.

        :param template_code: Textual template source.
        :return: Returns a compiled Mako template.
        """
        return MakoTemplate(template_code, lookup=self.lookup)


class MakoBackend(BaseEngine):
    """
    Mako Template Backend
    """

    # Name of the subdirectory containing the templates for Mako engine
    # inside an installed application.
    app_dirname = 'mako'

    def __init__(self, parameters):
        """
        Fetches template options, initializing BaseEngine properties,
        and assigning our Mako default settings.

        Note that OPTIONS contains backend-specific settings.

        :param params: This is simply the template dict you
                       define in your settings file.
        """
        params = parameters.copy()
        options = params.pop('OPTIONS').copy()
        super(MakoBackend, self).__init__(params)

        # Approximate size of the collection used to store templates.
        options.setdefault('collection_size', 5000)
        options.setdefault('module_directory', tempfile.gettempdir())
        options.setdefault('output_encoding', 'utf-8')
        options.setdefault('input_encoding', 'utf-8')
        options.setdefault('encoding_errors', 'replace')
        options.setdefault('filesystem_checks', True)
        # A list of directory names which will be searched for a
        # particular template URI
        options.setdefault('directories', self.template_dirs)

        self.engine = MakoEngine(**options)

    def from_string(self, template_code):
        """
        Trying to compile and return the compiled template code.

        :raises: TemplateSyntaxError if there's a syntax error in
        the template.
        :param template_code: Textual template source.
        :return: Returns a compiled Mako template.
        """
        try:
            return Template(self.engine.from_string(template_code))
        except mako_exceptions.SyntaxException as exc:
            raise TemplateSyntaxError(exc.args)

    def get_template(self, template_name):
        """
        Trying to get a compiled template given a template name
        :param template_name: The template name.
        :raises: - TemplateDoesNotExist if no such template exists.
                 - TemplateSyntaxError  if we couldn't compile the
                    template using Mako syntax.
        :return: Compiled Template.
        """
        try:
            return Template(self.engine.get_template(template_name))
        except mako_exceptions.TemplateLookupException as exc:
            raise TemplateDoesNotExist(exc.args)
        except mako_exceptions.CompileException as exc:
            raise TemplateSyntaxError(exc.args)


class Template(object):
    """
    This is an implementation of template objects returned by our
    backend that must conform to the following interface. Django
    won't provide a BaseTemplate class because it would have only one
    abstract method.
    """
    def __init__(self, template):
        self.template = template

    def render(self, context=None, request=None):
        """
        Render the template with a given context. Here we're adding
        some context variables that are required for all templates in
        the system like the statix url and the CSRF tokens, etc.

        :param context: It must be a dict if provided
        :param request: It must be a django.http.HttpRequest if provided
        :return: A rendered template
        """
        if context is None:
            context = {}

        if request is not None:
            # As Django doesn't have a global request object,
            # it's useful to put it in the context.
            context['request'] = request
            # Passing the CSRF token is mandatory.
            context['csrf_input'] = csrf_input_lazy(request)
            context['csrf_token'] = csrf_token_lazy(request)

            context['static'] = static
            context['url'] = reverse

        return self.template.render(**context)
