# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.utils.encoding import python_2_unicode_compatible


@python_2_unicode_compatible
class Foo(models.Model):
    name = models.CharField(max_length=50)
    friend = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return "Foo %s" % self.name


@python_2_unicode_compatible
class Bar(models.Model):
    name = models.CharField(max_length=50)
    normal = models.ForeignKey(Foo, models.CASCADE, related_name='normal_foo')
    fwd = models.ForeignKey("Whiz", models.CASCADE)
    back = models.ForeignKey("Foo", models.CASCADE)

    def __str__(self):
        return "Bar %s" % self.place.name


@python_2_unicode_compatible
class Whiz(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return "Whiz %s" % self.name


@python_2_unicode_compatible
class Child(models.Model):
    parent = models.OneToOneField('Base', models.CASCADE)
    name = models.CharField(max_length=50)

    def __str__(self):
        return "Child %s" % self.name


@python_2_unicode_compatible
class Base(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return "Base %s" % self.name


@python_2_unicode_compatible
class Article(models.Model):
    name = models.CharField(max_length=50)
    text = models.TextField()
    submitted_from = models.GenericIPAddressField(blank=True, null=True)

    def __str__(self):
        return "Article %s" % self.name
