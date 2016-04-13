from __future__ import absolute_import, unicode_literals

from django.contrib.auth.models import User
from django.db import models
from django.utils import six
from django.utils.encoding import python_2_unicode_compatible


@python_2_unicode_compatible
class Animal(models.Model):
    name = models.CharField(max_length=150)
    latin_name = models.CharField(max_length=150)
    count = models.IntegerField()
    weight = models.FloatField()

    # use a non-default name for the default manager
    specimens = models.Manager()

    def __str__(self):
        return self.name


class Plant(models.Model):
    name = models.CharField(max_length=150)

    class Meta:
        # For testing when upper case letter in app name; regression for #4057
        db_table = "Fixtures_regress_plant"

@python_2_unicode_compatible
class Stuff(models.Model):
    name = models.CharField(max_length=20, null=True)
    owner = models.ForeignKey(User, null=True)

    def __str__(self):
        return six.text_type(self.name) + ' is owned by ' + six.text_type(self.owner)


class Absolute(models.Model):
    name = models.CharField(max_length=40)


class Parent(models.Model):
    name = models.CharField(max_length=10)

    class Meta:
        ordering = ('id',)


class Child(Parent):
    data = models.CharField(max_length=10)


# Models to regression test #7572
class Channel(models.Model):
    name = models.CharField(max_length=255)


class Article(models.Model):
    title = models.CharField(max_length=255)
    channels = models.ManyToManyField(Channel)

    class Meta:
        ordering = ('id',)


# Subclass of a model with a ManyToManyField for test_ticket_20820
class SpecialArticle(Article):
    pass


# Models to regression test #11428
@python_2_unicode_compatible
class Widget(models.Model):
    name = models.CharField(max_length=255)

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return self.name


class WidgetProxy(Widget):
    class Meta:
        proxy = True


# Check for forward references in FKs and M2Ms with natural keys
class TestManager(models.Manager):
    def get_by_natural_key(self, key):
        return self.get(name=key)


@python_2_unicode_compatible
class Store(models.Model):
    objects = TestManager()
    name = models.CharField(max_length=255)
    main = models.ForeignKey('self', null=True)

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return self.name

    def natural_key(self):
        return (self.name,)


@python_2_unicode_compatible
class Person(models.Model):
    objects = TestManager()
    name = models.CharField(max_length=255)

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return self.name

    # Person doesn't actually have a dependency on store, but we need to define
    # one to test the behavior of the dependency resolution algorithm.
    def natural_key(self):
        return (self.name,)
    natural_key.dependencies = ['fixtures_regress.store']


@python_2_unicode_compatible
class Book(models.Model):
    name = models.CharField(max_length=255)
    author = models.ForeignKey(Person)
    stores = models.ManyToManyField(Store)

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return '%s by %s (available at %s)' % (
            self.name,
            self.author.name,
            ', '.join(s.name for s in self.stores.all())
        )


class NKManager(models.Manager):
    def get_by_natural_key(self, data):
        return self.get(data=data)


@python_2_unicode_compatible
class NKChild(Parent):
    data = models.CharField(max_length=10, unique=True)
    objects = NKManager()

    def natural_key(self):
        return self.data

    def __str__(self):
        return 'NKChild %s:%s' % (self.name, self.data)


@python_2_unicode_compatible
class RefToNKChild(models.Model):
    text = models.CharField(max_length=10)
    nk_fk = models.ForeignKey(NKChild, related_name='ref_fks')
    nk_m2m = models.ManyToManyField(NKChild, related_name='ref_m2ms')

    def __str__(self):
        return '%s: Reference to %s [%s]' % (
            self.text,
            self.nk_fk,
            ', '.join(str(o) for o in self.nk_m2m.all())
        )


# ome models with pathological circular dependencies
class Circle1(models.Model):
    name = models.CharField(max_length=255)

    def natural_key(self):
        return self.name
    natural_key.dependencies = ['fixtures_regress.circle2']


class Circle2(models.Model):
    name = models.CharField(max_length=255)

    def natural_key(self):
        return self.name
    natural_key.dependencies = ['fixtures_regress.circle1']


class Circle3(models.Model):
    name = models.CharField(max_length=255)

    def natural_key(self):
        return self.name
    natural_key.dependencies = ['fixtures_regress.circle3']


class Circle4(models.Model):
    name = models.CharField(max_length=255)

    def natural_key(self):
        return self.name
    natural_key.dependencies = ['fixtures_regress.circle5']


class Circle5(models.Model):
    name = models.CharField(max_length=255)

    def natural_key(self):
        return self.name
    natural_key.dependencies = ['fixtures_regress.circle6']


class Circle6(models.Model):
    name = models.CharField(max_length=255)

    def natural_key(self):
        return self.name
    natural_key.dependencies = ['fixtures_regress.circle4']


class ExternalDependency(models.Model):
    name = models.CharField(max_length=255)

    def natural_key(self):
        return self.name
    natural_key.dependencies = ['fixtures_regress.book']


# Model for regression test of #11101
class Thingy(models.Model):
    name = models.CharField(max_length=255)
