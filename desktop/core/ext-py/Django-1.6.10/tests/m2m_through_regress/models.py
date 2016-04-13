from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.db import models
from django.utils.encoding import python_2_unicode_compatible


# Forward declared intermediate model
@python_2_unicode_compatible
class Membership(models.Model):
    person = models.ForeignKey('Person')
    group = models.ForeignKey('Group')
    price = models.IntegerField(default=100)

    def __str__(self):
        return "%s is a member of %s" % (self.person.name, self.group.name)

# using custom id column to test ticket #11107
@python_2_unicode_compatible
class UserMembership(models.Model):
    id = models.AutoField(db_column='usermembership_id', primary_key=True)
    user = models.ForeignKey(User)
    group = models.ForeignKey('Group')
    price = models.IntegerField(default=100)

    def __str__(self):
        return "%s is a user and member of %s" % (self.user.username, self.group.name)

@python_2_unicode_compatible
class Person(models.Model):
    name = models.CharField(max_length=128)

    def __str__(self):
        return self.name

@python_2_unicode_compatible
class Group(models.Model):
    name = models.CharField(max_length=128)
    # Membership object defined as a class
    members = models.ManyToManyField(Person, through=Membership)
    user_members = models.ManyToManyField(User, through='UserMembership')

    def __str__(self):
        return self.name

# A set of models that use an non-abstract inherited model as the 'through' model.
class A(models.Model):
    a_text = models.CharField(max_length=20)

class ThroughBase(models.Model):
    a = models.ForeignKey(A)
    b = models.ForeignKey('B')

class Through(ThroughBase):
    extra = models.CharField(max_length=20)

class B(models.Model):
    b_text = models.CharField(max_length=20)
    a_list = models.ManyToManyField(A, through=Through)


# Using to_field on the through model
@python_2_unicode_compatible
class Car(models.Model):
    make = models.CharField(max_length=20, unique=True, null=True)
    drivers = models.ManyToManyField('Driver', through='CarDriver')

    def __str__(self):
        return "%s" % self.make

@python_2_unicode_compatible
class Driver(models.Model):
    name = models.CharField(max_length=20, unique=True, null=True)

    def __str__(self):
        return "%s" % self.name

    class Meta:
        ordering = ('name',)

@python_2_unicode_compatible
class CarDriver(models.Model):
    car = models.ForeignKey('Car', to_field='make')
    driver = models.ForeignKey('Driver', to_field='name')

    def __str__(self):
        return "pk=%s car=%s driver=%s" % (str(self.pk), self.car, self.driver)
