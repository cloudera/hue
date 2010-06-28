import unittest

from south.tests import Monkeypatcher
from south.modelsinspector import *
from fakeapp.models import HorribleModel

class TestModelInspector(Monkeypatcher):

    """
    Tests if the various parts of the modelinspector work.
    """
    
    def test_get_value(self):
        
        # Let's start nicely.
        name = HorribleModel._meta.get_field_by_name("name")[0]
        slug = HorribleModel._meta.get_field_by_name("slug")[0]
        user = HorribleModel._meta.get_field_by_name("user")[0]
        
        # Simple int retrieval
        self.assertEqual(
            get_value(name, ["max_length", {}]),
            "255",
        )
        
        # Bool retrieval
        self.assertEqual(
            get_value(slug, ["unique", {}]),
            "True",
        )
        
        # String retrieval
        self.assertEqual(
            get_value(user, ["rel.related_name", {}]),
            "'horribles'",
        )
        
        # Default triggering
        self.assertEqual(
            get_value(slug, ["unique", {"default": False}]),
            "True",
        )
        self.assertRaises(
            IsDefault,
            get_value,
            slug,
            ["unique", {"default": True}],
        )
    