from __future__ import unicode_literals

from django.db import models
from django.utils.encoding import python_2_unicode_compatible


@python_2_unicode_compatible
class Poll(models.Model):
    question = models.CharField(max_length=200)

    def __str__(self):
        return "Q: %s " % self.question


@python_2_unicode_compatible
class Choice(models.Model):
    poll = models.ForeignKey(Poll, models.CASCADE)
    choice = models.CharField(max_length=200)

    def __str__(self):
        return "Choice: %s in poll %s" % (self.choice, self.poll)

# A set of models with an inner one pointing to two outer ones.


class OuterA(models.Model):
    pass


class OuterB(models.Model):
    data = models.CharField(max_length=10)


class Inner(models.Model):
    first = models.ForeignKey(OuterA, models.CASCADE)
    # second would clash with the __second lookup.
    third = models.ForeignKey(OuterB, models.SET_NULL, null=True)
