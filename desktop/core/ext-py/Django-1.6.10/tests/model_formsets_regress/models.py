from django.db import models
from django.utils.encoding import python_2_unicode_compatible


class User(models.Model):
    username = models.CharField(max_length=12, unique=True)
    serial = models.IntegerField()

class UserSite(models.Model):
    user = models.ForeignKey(User, to_field="username")
    data = models.IntegerField()

class UserProfile(models.Model):
    user = models.ForeignKey(User, unique=True, to_field="username")
    about = models.TextField()

class ProfileNetwork(models.Model):
    profile = models.ForeignKey(UserProfile, to_field="user")
    network = models.IntegerField()
    identifier = models.IntegerField()

class Place(models.Model):
    name = models.CharField(max_length=50)

class Restaurant(Place):
    pass

class Manager(models.Model):
    retaurant = models.ForeignKey(Restaurant)
    name = models.CharField(max_length=50)

class Network(models.Model):
    name = models.CharField(max_length=15)

@python_2_unicode_compatible
class Host(models.Model):
    network = models.ForeignKey(Network)
    hostname = models.CharField(max_length=25)

    def __str__(self):
        return self.hostname
