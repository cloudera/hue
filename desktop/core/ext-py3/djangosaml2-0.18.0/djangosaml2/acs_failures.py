# -*- coding: utf-8 -*-
#
# This module defines a set of useful ACS failure functions that are used to
# produce an output suitable for end user in case of SAML failure.
#
from __future__ import unicode_literals

from django.core.exceptions import PermissionDenied
from django.shortcuts import render


def template_failure(request, status=403, **kwargs):
    """ Renders a SAML-specific template with general authentication error description. """
    return render(request, 'djangosaml2/login_error.html', status=status, using='django')


def exception_failure(request, exc_class=PermissionDenied, **kwargs):
    """ Rather than using a custom SAML specific template that is rendered on failure,
    this makes use of a standard exception handling machinery present in Django
    and thus ends up rendering a project-wide error page for Permission Denied exceptions.
    """
    raise exc_class
