# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import json
from datetime import datetime
from xml.dom import minidom

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False

from django.conf import settings
from django.core import management, serializers
from django.db import transaction, connection
from django.test import TestCase, TransactionTestCase, Approximate
from django.utils import six
from django.utils.six import StringIO
from django.utils import unittest
from django.utils import importlib

from .models import (Category, Author, Article, AuthorProfile, Actor, Movie,
    Score, Player, Team)


class SerializerRegistrationTests(unittest.TestCase):
    def setUp(self):
        self.old_SERIALIZATION_MODULES = getattr(settings, 'SERIALIZATION_MODULES', None)
        self.old_serializers = serializers._serializers

        serializers._serializers = {}
        settings.SERIALIZATION_MODULES = {
            "json2" : "django.core.serializers.json",
        }

    def tearDown(self):
        serializers._serializers = self.old_serializers
        if self.old_SERIALIZATION_MODULES:
            settings.SERIALIZATION_MODULES = self.old_SERIALIZATION_MODULES
        else:
            delattr(settings, 'SERIALIZATION_MODULES')

    def test_register(self):
        "Registering a new serializer populates the full registry. Refs #14823"
        serializers.register_serializer('json3', 'django.core.serializers.json')

        public_formats = serializers.get_public_serializer_formats()
        self.assertIn('json3', public_formats)
        self.assertIn('json2', public_formats)
        self.assertIn('xml', public_formats)

    def test_unregister(self):
        "Unregistering a serializer doesn't cause the registry to be repopulated. Refs #14823"
        serializers.unregister_serializer('xml')
        serializers.register_serializer('json3', 'django.core.serializers.json')

        public_formats = serializers.get_public_serializer_formats()

        self.assertNotIn('xml', public_formats)
        self.assertIn('json3', public_formats)

    def test_builtin_serializers(self):
        "Requesting a list of serializer formats popuates the registry"
        all_formats = set(serializers.get_serializer_formats())
        public_formats = set(serializers.get_public_serializer_formats())

        self.assertIn('xml', all_formats),
        self.assertIn('xml', public_formats)

        self.assertIn('json2', all_formats)
        self.assertIn('json2', public_formats)

        self.assertIn('python', all_formats)
        self.assertNotIn('python', public_formats)

class SerializersTestBase(object):
    @staticmethod
    def _comparison_value(value):
        return value

    def setUp(self):
        sports = Category.objects.create(name="Sports")
        music = Category.objects.create(name="Music")
        op_ed = Category.objects.create(name="Op-Ed")

        self.joe = Author.objects.create(name="Joe")
        self.jane = Author.objects.create(name="Jane")

        self.a1 = Article(
            author=self.jane,
            headline="Poker has no place on ESPN",
            pub_date=datetime(2006, 6, 16, 11, 00)
        )
        self.a1.save()
        self.a1.categories = [sports, op_ed]

        self.a2 = Article(
            author=self.joe,
            headline="Time to reform copyright",
            pub_date=datetime(2006, 6, 16, 13, 00, 11, 345)
        )
        self.a2.save()
        self.a2.categories = [music, op_ed]

    def test_serialize(self):
        """Tests that basic serialization works."""
        serial_str = serializers.serialize(self.serializer_name,
                                           Article.objects.all())
        self.assertTrue(self._validate_output(serial_str))

    def test_serializer_roundtrip(self):
        """Tests that serialized content can be deserialized."""
        serial_str = serializers.serialize(self.serializer_name,
                                           Article.objects.all())
        models = list(serializers.deserialize(self.serializer_name, serial_str))
        self.assertEqual(len(models), 2)

    def test_altering_serialized_output(self):
        """
        Tests the ability to create new objects by
        modifying serialized content.
        """
        old_headline = "Poker has no place on ESPN"
        new_headline = "Poker has no place on television"
        serial_str = serializers.serialize(self.serializer_name,
                                           Article.objects.all())
        serial_str = serial_str.replace(old_headline, new_headline)
        models = list(serializers.deserialize(self.serializer_name, serial_str))

        # Prior to saving, old headline is in place
        self.assertTrue(Article.objects.filter(headline=old_headline))
        self.assertFalse(Article.objects.filter(headline=new_headline))

        for model in models:
            model.save()

        # After saving, new headline is in place
        self.assertTrue(Article.objects.filter(headline=new_headline))
        self.assertFalse(Article.objects.filter(headline=old_headline))

    def test_one_to_one_as_pk(self):
        """
        Tests that if you use your own primary key field
        (such as a OneToOneField), it doesn't appear in the
        serialized field list - it replaces the pk identifier.
        """
        profile = AuthorProfile(author=self.joe,
                                date_of_birth=datetime(1970,1,1))
        profile.save()
        serial_str = serializers.serialize(self.serializer_name,
                                           AuthorProfile.objects.all())
        self.assertFalse(self._get_field_values(serial_str, 'author'))

        for obj in serializers.deserialize(self.serializer_name, serial_str):
            self.assertEqual(obj.object.pk, self._comparison_value(self.joe.pk))

    def test_serialize_field_subset(self):
        """Tests that output can be restricted to a subset of fields"""
        valid_fields = ('headline','pub_date')
        invalid_fields = ("author", "categories")
        serial_str = serializers.serialize(self.serializer_name,
                                    Article.objects.all(),
                                    fields=valid_fields)
        for field_name in invalid_fields:
            self.assertFalse(self._get_field_values(serial_str, field_name))

        for field_name in valid_fields:
            self.assertTrue(self._get_field_values(serial_str, field_name))

    def test_serialize_unicode(self):
        """Tests that unicode makes the roundtrip intact"""
        actor_name = "Za\u017c\u00f3\u0142\u0107"
        movie_title = 'G\u0119\u015bl\u0105 ja\u017a\u0144'
        ac = Actor(name=actor_name)
        mv = Movie(title=movie_title, actor=ac)
        ac.save()
        mv.save()

        serial_str = serializers.serialize(self.serializer_name, [mv])
        self.assertEqual(self._get_field_values(serial_str, "title")[0], movie_title)
        self.assertEqual(self._get_field_values(serial_str, "actor")[0], actor_name)

        obj_list = list(serializers.deserialize(self.serializer_name, serial_str))
        mv_obj = obj_list[0].object
        self.assertEqual(mv_obj.title, movie_title)

    def test_serialize_superfluous_queries(self):
        """Ensure no superfluous queries are made when serializing ForeignKeys

        #17602
        """
        ac = Actor(name='Actor name')
        ac.save()
        mv = Movie(title='Movie title', actor_id=ac.pk)
        mv.save()

        with self.assertNumQueries(0):
            serial_str = serializers.serialize(self.serializer_name, [mv])

    def test_serialize_with_null_pk(self):
        """
        Tests that serialized data with no primary key results
        in a model instance with no id
        """
        category = Category(name="Reference")
        serial_str = serializers.serialize(self.serializer_name, [category])
        pk_value = self._get_pk_values(serial_str)[0]
        self.assertFalse(pk_value)

        cat_obj = list(serializers.deserialize(self.serializer_name,
                                               serial_str))[0].object
        self.assertEqual(cat_obj.id, None)

    def test_float_serialization(self):
        """Tests that float values serialize and deserialize intact"""
        sc = Score(score=3.4)
        sc.save()
        serial_str = serializers.serialize(self.serializer_name, [sc])
        deserial_objs = list(serializers.deserialize(self.serializer_name,
                                                serial_str))
        self.assertEqual(deserial_objs[0].object.score, Approximate(3.4, places=1))

    def test_custom_field_serialization(self):
        """Tests that custom fields serialize and deserialize intact"""
        team_str = "Spartak Moskva"
        player = Player()
        player.name = "Soslan Djanaev"
        player.rank = 1
        player.team = Team(team_str)
        player.save()
        serial_str = serializers.serialize(self.serializer_name,
                                           Player.objects.all())
        team = self._get_field_values(serial_str, "team")
        self.assertTrue(team)
        self.assertEqual(team[0], team_str)

        deserial_objs = list(serializers.deserialize(self.serializer_name, serial_str))
        self.assertEqual(deserial_objs[0].object.team.to_string(),
                         player.team.to_string())

    def test_pre_1000ad_date(self):
        """Tests that year values before 1000AD are properly formatted"""
        # Regression for #12524 -- dates before 1000AD get prefixed
        # 0's on the year
        a = Article.objects.create(
        author = self.jane,
        headline = "Nobody remembers the early years",
        pub_date = datetime(1, 2, 3, 4, 5, 6))

        serial_str = serializers.serialize(self.serializer_name, [a])
        date_values = self._get_field_values(serial_str, "pub_date")
        self.assertEqual(date_values[0].replace('T', ' '), "0001-02-03 04:05:06")

    def test_pkless_serialized_strings(self):
        """
        Tests that serialized strings without PKs
        can be turned into models
        """
        deserial_objs = list(serializers.deserialize(self.serializer_name,
                                                     self.pkless_str))
        for obj in deserial_objs:
            self.assertFalse(obj.object.id)
            obj.save()
        self.assertEqual(Category.objects.all().count(), 5)


class SerializersTransactionTestBase(object):

    available_apps = ['serializers']

    def test_forward_refs(self):
        """
        Tests that objects ids can be referenced before they are
        defined in the serialization data.
        """
        # The deserialization process needs to be contained
        # within a transaction in order to test forward reference
        # handling.
        transaction.enter_transaction_management()
        objs = serializers.deserialize(self.serializer_name, self.fwd_ref_str)
        with connection.constraint_checks_disabled():
            for obj in objs:
                obj.save()
        transaction.commit()
        transaction.leave_transaction_management()

        for model_cls in (Category, Author, Article):
            self.assertEqual(model_cls.objects.all().count(), 1)
        art_obj = Article.objects.all()[0]
        self.assertEqual(art_obj.categories.all().count(), 1)
        self.assertEqual(art_obj.author.name, "Agnes")


class XmlSerializerTestCase(SerializersTestBase, TestCase):
    serializer_name = "xml"
    pkless_str = """<?xml version="1.0" encoding="utf-8"?>
<django-objects version="1.0">
    <object model="serializers.category">
        <field type="CharField" name="name">Reference</field>
    </object>
    <object model="serializers.category">
        <field type="CharField" name="name">Non-fiction</field>
    </object>
</django-objects>"""

    @staticmethod
    def _comparison_value(value):
        # The XML serializer handles everything as strings, so comparisons
        # need to be performed on the stringified value
        return six.text_type(value)

    @staticmethod
    def _validate_output(serial_str):
        try:
            minidom.parseString(serial_str)
        except Exception:
            return False
        else:
            return True

    @staticmethod
    def _get_pk_values(serial_str):
        ret_list = []
        dom = minidom.parseString(serial_str)
        fields = dom.getElementsByTagName("object")
        for field in fields:
            ret_list.append(field.getAttribute("pk"))
        return ret_list

    @staticmethod
    def _get_field_values(serial_str, field_name):
        ret_list = []
        dom = minidom.parseString(serial_str)
        fields = dom.getElementsByTagName("field")
        for field in fields:
            if field.getAttribute("name") == field_name:
                temp = []
                for child in field.childNodes:
                    temp.append(child.nodeValue)
                ret_list.append("".join(temp))
        return ret_list

class XmlSerializerTransactionTestCase(SerializersTransactionTestBase, TransactionTestCase):
    serializer_name = "xml"
    fwd_ref_str = """<?xml version="1.0" encoding="utf-8"?>
<django-objects version="1.0">
    <object pk="1" model="serializers.article">
        <field to="serializers.author" name="author" rel="ManyToOneRel">1</field>
        <field type="CharField" name="headline">Forward references pose no problem</field>
        <field type="DateTimeField" name="pub_date">2006-06-16T15:00:00</field>
        <field to="serializers.category" name="categories" rel="ManyToManyRel">
            <object pk="1"></object>
        </field>
    </object>
    <object pk="1" model="serializers.author">
        <field type="CharField" name="name">Agnes</field>
    </object>
    <object pk="1" model="serializers.category">
        <field type="CharField" name="name">Reference</field></object>
</django-objects>"""


class JsonSerializerTestCase(SerializersTestBase, TestCase):
    serializer_name = "json"
    pkless_str = """[
    {
        "pk": null,
        "model": "serializers.category",
        "fields": {"name": "Reference"}
    }, {
        "model": "serializers.category",
        "fields": {"name": "Non-fiction"}
    }]"""

    @staticmethod
    def _validate_output(serial_str):
        try:
            json.loads(serial_str)
        except Exception:
            return False
        else:
            return True

    @staticmethod
    def _get_pk_values(serial_str):
        ret_list = []
        serial_list = json.loads(serial_str)
        for obj_dict in serial_list:
            ret_list.append(obj_dict["pk"])
        return ret_list

    @staticmethod
    def _get_field_values(serial_str, field_name):
        ret_list = []
        serial_list = json.loads(serial_str)
        for obj_dict in serial_list:
            if field_name in obj_dict["fields"]:
                ret_list.append(obj_dict["fields"][field_name])
        return ret_list

class JsonSerializerTransactionTestCase(SerializersTransactionTestBase, TransactionTestCase):
    serializer_name = "json"
    fwd_ref_str = """[
    {
        "pk": 1,
        "model": "serializers.article",
        "fields": {
            "headline": "Forward references pose no problem",
            "pub_date": "2006-06-16T15:00:00",
            "categories": [1],
            "author": 1
        }
    },
    {
        "pk": 1,
        "model": "serializers.category",
        "fields": {
            "name": "Reference"
        }
    },
    {
        "pk": 1,
        "model": "serializers.author",
        "fields": {
            "name": "Agnes"
        }
    }]"""


YAML_IMPORT_ERROR_MESSAGE = r'No module named yaml'
class YamlImportModuleMock(object):
    """Provides a wrapped import_module function to simulate yaml ImportError

    In order to run tests that verify the behavior of the YAML serializer
    when run on a system that has yaml installed (like the django CI server),
    mock import_module, so that it raises an ImportError when the yaml
    serializer is being imported.  The importlib.import_module() call is
    being made in the serializers.register_serializer().

    Refs: #12756
    """
    def __init__(self):
        self._import_module = importlib.import_module

    def import_module(self, module_path):
        if module_path == serializers.BUILTIN_SERIALIZERS['yaml']:
            raise ImportError(YAML_IMPORT_ERROR_MESSAGE)

        return self._import_module(module_path)


class NoYamlSerializerTestCase(TestCase):
    """Not having pyyaml installed provides a misleading error

    Refs: #12756
    """
    @classmethod
    def setUpClass(cls):
        """Removes imported yaml and stubs importlib.import_module"""
        super(NoYamlSerializerTestCase, cls).setUpClass()

        cls._import_module_mock = YamlImportModuleMock()
        importlib.import_module = cls._import_module_mock.import_module

        # clear out cached serializers to emulate yaml missing
        serializers._serializers = {}

    @classmethod
    def tearDownClass(cls):
        """Puts yaml back if necessary"""
        super(NoYamlSerializerTestCase, cls).tearDownClass()

        importlib.import_module = cls._import_module_mock._import_module

        # clear out cached serializers to clean out BadSerializer instances
        serializers._serializers = {}

    def test_serializer_pyyaml_error_message(self):
        """Using yaml serializer without pyyaml raises ImportError"""
        jane = Author(name="Jane")
        self.assertRaises(ImportError, serializers.serialize, "yaml", [jane])

    def test_deserializer_pyyaml_error_message(self):
        """Using yaml deserializer without pyyaml raises ImportError"""
        self.assertRaises(ImportError, serializers.deserialize, "yaml", "")

    def test_dumpdata_pyyaml_error_message(self):
        """Calling dumpdata produces an error when yaml package missing"""
        with six.assertRaisesRegex(self, management.CommandError, YAML_IMPORT_ERROR_MESSAGE):
            management.call_command('dumpdata', format='yaml')


@unittest.skipUnless(HAS_YAML, "No yaml library detected")
class YamlSerializerTestCase(SerializersTestBase, TestCase):
    serializer_name = "yaml"
    fwd_ref_str = """- fields:
    headline: Forward references pose no problem
    pub_date: 2006-06-16 15:00:00
    categories: [1]
    author: 1
  pk: 1
  model: serializers.article
- fields:
    name: Reference
  pk: 1
  model: serializers.category
- fields:
    name: Agnes
  pk: 1
  model: serializers.author"""

    pkless_str = """- fields:
    name: Reference
  pk: null
  model: serializers.category
- fields:
    name: Non-fiction
  model: serializers.category"""

    @staticmethod
    def _validate_output(serial_str):
        try:
            yaml.safe_load(StringIO(serial_str))
        except Exception:
            return False
        else:
            return True

    @staticmethod
    def _get_pk_values(serial_str):
        ret_list = []
        stream = StringIO(serial_str)
        for obj_dict in yaml.safe_load(stream):
            ret_list.append(obj_dict["pk"])
        return ret_list

    @staticmethod
    def _get_field_values(serial_str, field_name):
        ret_list = []
        stream = StringIO(serial_str)
        for obj_dict in yaml.safe_load(stream):
            if "fields" in obj_dict and field_name in obj_dict["fields"]:
                field_value = obj_dict["fields"][field_name]
                # yaml.safe_load will return non-string objects for some
                # of the fields we are interested in, this ensures that
                # everything comes back as a string
                if isinstance(field_value, six.string_types):
                    ret_list.append(field_value)
                else:
                    ret_list.append(str(field_value))
        return ret_list


@unittest.skipUnless(HAS_YAML, "No yaml library detected")
class YamlSerializerTransactionTestCase(SerializersTransactionTestBase, TransactionTestCase):
    serializer_name = "yaml"
    fwd_ref_str = """- fields:
    headline: Forward references pose no problem
    pub_date: 2006-06-16 15:00:00
    categories: [1]
    author: 1
  pk: 1
  model: serializers.article
- fields:
    name: Reference
  pk: 1
  model: serializers.category
- fields:
    name: Agnes
  pk: 1
  model: serializers.author"""
