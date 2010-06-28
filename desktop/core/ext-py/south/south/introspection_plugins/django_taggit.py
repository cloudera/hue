"""
South introspection rules for django-taggit
"""

from south.modelsinspector import add_ignored_fields

try:
    from taggit.managers import TaggableManager
except ImportError:
    pass
else:
    add_ignored_fields(["^taggit\.managers"])
