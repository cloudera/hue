from django.contrib.gis.db import models
from django.contrib.gis.tests.utils import mysql, spatialite
from django.utils.encoding import python_2_unicode_compatible

# MySQL spatial indices can't handle NULL geometries.
null_flag = not mysql

@python_2_unicode_compatible
class Country(models.Model):
    name = models.CharField(max_length=30)
    mpoly = models.MultiPolygonField() # SRID, by default, is 4326
    objects = models.GeoManager()
    def __str__(self): return self.name

@python_2_unicode_compatible
class City(models.Model):
    name = models.CharField(max_length=30)
    point = models.PointField()
    objects = models.GeoManager()
    def __str__(self): return self.name

# This is an inherited model from City
class PennsylvaniaCity(City):
    county = models.CharField(max_length=30)
    founded = models.DateTimeField(null=True)
    objects = models.GeoManager() # TODO: This should be implicitly inherited.

@python_2_unicode_compatible
class State(models.Model):
    name = models.CharField(max_length=30)
    poly = models.PolygonField(null=null_flag) # Allowing NULL geometries here.
    objects = models.GeoManager()
    def __str__(self): return self.name

@python_2_unicode_compatible
class Track(models.Model):
    name = models.CharField(max_length=30)
    line = models.LineStringField()
    objects = models.GeoManager()
    def __str__(self): return self.name

class Truth(models.Model):
    val = models.BooleanField(default=False)
    objects = models.GeoManager()

if not spatialite:
    @python_2_unicode_compatible
    class Feature(models.Model):
        name = models.CharField(max_length=20)
        geom = models.GeometryField()
        objects = models.GeoManager()
        def __str__(self): return self.name

    class MinusOneSRID(models.Model):
        geom = models.PointField(srid=-1) # Minus one SRID.
        objects = models.GeoManager()
