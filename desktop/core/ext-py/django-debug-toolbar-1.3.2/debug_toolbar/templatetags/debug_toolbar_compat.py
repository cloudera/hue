from django.template.base import Library

from ..compat import url as url_compat

"""
https://github.com/jazzband/django-debug-toolbar/commit/fe437aaca243aef4fa1d65eb916009ca5be3d655#diff-7da931685952c08fceacc7d0f71f1a46
	modified:   desktop/core/ext-py/django-debug-toolbar-1.3.2/debug_toolbar/templates/debug_toolbar/base.html
	modified:   desktop/core/ext-py/django-debug-toolbar-1.3.2/debug_toolbar/templates/debug_toolbar/panels/sql.html
	modified:   desktop/core/ext-py/django-debug-toolbar-1.3.2/debug_toolbar/templates/debug_toolbar/panels/templates.html
	renamed:    desktop/core/ext-py/django-debug-toolbar-1.3.2/debug_toolbar/templatetags/compat.py -> desktop/core/ext-py/django-debug-toolbar-1.3.2/debug_toolbar/templatetags/debug_toolbar_compat.py
	modified:   desktop/core/src/desktop/settings.py
	modified:   desktop/core/src/desktop/templates/debug_toolbar/base.html
	modified:   desktop/core/src/desktop/templates/debug_toolbar/panels/sql.html
	modified:   desktop/core/src/desktop/templates/debug_toolbar/panels/templates.html
"""

register = Library()


@register.tag
def url(parser, token):
    return url_compat(parser, token)
