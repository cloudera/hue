from __future__ import absolute_import

import datetime

from django.db import models
from django.utils.translation import ugettext_lazy as _


def standalone_number():
    return 1

class Numbers(object):
    @staticmethod
    def get_static_number():
        return 2

    @classmethod
    def get_class_number(cls):
        return 3

    def get_member_number(self):
        return 4

nn = Numbers()

class Group(models.Model):
    name = models.CharField(_('name'), max_length=100)

class Event(models.Model):
    group = models.ForeignKey(Group)

class Happening(models.Model):
    when = models.DateTimeField(blank=True, default=datetime.datetime.now)
    name = models.CharField(blank=True, max_length=100, default=lambda:"test")
    number1 = models.IntegerField(blank=True, default=standalone_number)
    number2 = models.IntegerField(blank=True, default=Numbers.get_static_number)
    number3 = models.IntegerField(blank=True, default=Numbers.get_class_number)
    number4 = models.IntegerField(blank=True, default=nn.get_member_number)

class Container(object):
    # To test pickling we need a class that isn't defined on module, but
    # is still available from app-cache. So, the Container class moves
    # SomeModel outside of module level
    class SomeModel(models.Model):
        somefield = models.IntegerField()

class M2MModel(models.Model):
    groups = models.ManyToManyField(Group)
