import os
import tempfile

from django.core.exceptions import ImproperlyConfigured

try:
    from django.utils.image import Image
except ImproperlyConfigured:
    Image = None

from django.core.files.storage import FileSystemStorage
from django.db import models
from django.db.models.fields.files import ImageFieldFile, ImageField


class Foo(models.Model):
    a = models.CharField(max_length=10)
    d = models.DecimalField(max_digits=5, decimal_places=3)

def get_foo():
    return Foo.objects.get(id=1)

class Bar(models.Model):
    b = models.CharField(max_length=10)
    a = models.ForeignKey(Foo, default=get_foo)

class Whiz(models.Model):
    CHOICES = (
        ('Group 1', (
                (1,'First'),
                (2,'Second'),
            )
        ),
        ('Group 2', (
                (3,'Third'),
                (4,'Fourth'),
            )
        ),
        (0,'Other'),
    )
    c = models.IntegerField(choices=CHOICES, null=True)

class BigD(models.Model):
    d = models.DecimalField(max_digits=38, decimal_places=30)

class BigS(models.Model):
    s = models.SlugField(max_length=255)

class BigInt(models.Model):
    value = models.BigIntegerField()
    null_value = models.BigIntegerField(null = True, blank = True)

class Post(models.Model):
    title = models.CharField(max_length=100)
    body = models.TextField()

class NullBooleanModel(models.Model):
    nbfield = models.NullBooleanField()

class BooleanModel(models.Model):
    bfield = models.BooleanField(default=None)
    string = models.CharField(max_length=10, default='abc')

class DateTimeModel(models.Model):
    d = models.DateField()
    dt = models.DateTimeField()
    t = models.TimeField()


class FksToBooleans(models.Model):
    """Model wih FKs to models with {Null,}BooleanField's, #15040"""
    bf = models.ForeignKey(BooleanModel)
    nbf = models.ForeignKey(NullBooleanModel)

class RenamedField(models.Model):
    modelname = models.IntegerField(name="fieldname", choices=((1,'One'),))

class VerboseNameField(models.Model):
    id = models.AutoField("verbose pk", primary_key=True)
    field1 = models.BigIntegerField("verbose field1")
    field2 = models.BooleanField("verbose field2", default=False)
    field3 = models.CharField("verbose field3", max_length=10)
    field4 = models.CommaSeparatedIntegerField("verbose field4", max_length=99)
    field5 = models.DateField("verbose field5")
    field6 = models.DateTimeField("verbose field6")
    field7 = models.DecimalField("verbose field7", max_digits=6, decimal_places=1)
    field8 = models.EmailField("verbose field8")
    field9 = models.FileField("verbose field9", upload_to="unused")
    field10 = models.FilePathField("verbose field10")
    field11 = models.FloatField("verbose field11")
    # Don't want to depend on Pillow/PIL in this test
    #field_image = models.ImageField("verbose field")
    field12 = models.IntegerField("verbose field12")
    field13 = models.IPAddressField("verbose field13")
    field14 = models.GenericIPAddressField("verbose field14", protocol="ipv4")
    field15 = models.NullBooleanField("verbose field15")
    field16 = models.PositiveIntegerField("verbose field16")
    field17 = models.PositiveSmallIntegerField("verbose field17")
    field18 = models.SlugField("verbose field18")
    field19 = models.SmallIntegerField("verbose field19")
    field20 = models.TextField("verbose field20")
    field21 = models.TimeField("verbose field21")
    field22 = models.URLField("verbose field22")

# This model isn't used in any test, just here to ensure it validates successfully.
# See ticket #16570.
class DecimalLessThanOne(models.Model):
    d = models.DecimalField(max_digits=3, decimal_places=3)

class DataModel(models.Model):
    short_data = models.BinaryField(max_length=10, default=b'\x08')
    data = models.BinaryField()

###############################################################################
# FileField

class Document(models.Model):
    myfile = models.FileField(upload_to='unused')

###############################################################################
# ImageField

# If Pillow/PIL available, do these tests.
if Image:
    class TestImageFieldFile(ImageFieldFile):
        """
        Custom Field File class that records whether or not the underlying file
        was opened.
        """
        def __init__(self, *args, **kwargs):
            self.was_opened = False
            super(TestImageFieldFile, self).__init__(*args,**kwargs)
        def open(self):
            self.was_opened = True
            super(TestImageFieldFile, self).open()

    class TestImageField(ImageField):
        attr_class = TestImageFieldFile

    # Set up a temp directory for file storage.
    temp_storage_dir = tempfile.mkdtemp(dir=os.environ['DJANGO_TEST_TEMP_DIR'])
    temp_storage = FileSystemStorage(temp_storage_dir)
    temp_upload_to_dir = os.path.join(temp_storage.location, 'tests')

    class Person(models.Model):
        """
        Model that defines an ImageField with no dimension fields.
        """
        name = models.CharField(max_length=50)
        mugshot = TestImageField(storage=temp_storage, upload_to='tests')

    class PersonWithHeight(models.Model):
        """
        Model that defines an ImageField with only one dimension field.
        """
        name = models.CharField(max_length=50)
        mugshot = TestImageField(storage=temp_storage, upload_to='tests',
                                 height_field='mugshot_height')
        mugshot_height = models.PositiveSmallIntegerField()

    class PersonWithHeightAndWidth(models.Model):
        """
        Model that defines height and width fields after the ImageField.
        """
        name = models.CharField(max_length=50)
        mugshot = TestImageField(storage=temp_storage, upload_to='tests',
                                 height_field='mugshot_height',
                                 width_field='mugshot_width')
        mugshot_height = models.PositiveSmallIntegerField()
        mugshot_width = models.PositiveSmallIntegerField()

    class PersonDimensionsFirst(models.Model):
        """
        Model that defines height and width fields before the ImageField.
        """
        name = models.CharField(max_length=50)
        mugshot_height = models.PositiveSmallIntegerField()
        mugshot_width = models.PositiveSmallIntegerField()
        mugshot = TestImageField(storage=temp_storage, upload_to='tests',
                                 height_field='mugshot_height',
                                 width_field='mugshot_width')

    class PersonTwoImages(models.Model):
        """
        Model that:
        * Defines two ImageFields
        * Defines the height/width fields before the ImageFields
        * Has a nullalble ImageField
        """
        name = models.CharField(max_length=50)
        mugshot_height = models.PositiveSmallIntegerField()
        mugshot_width = models.PositiveSmallIntegerField()
        mugshot = TestImageField(storage=temp_storage, upload_to='tests',
                                 height_field='mugshot_height',
                                 width_field='mugshot_width')
        headshot_height = models.PositiveSmallIntegerField(
                blank=True, null=True)
        headshot_width = models.PositiveSmallIntegerField(
                blank=True, null=True)
        headshot = TestImageField(blank=True, null=True,
                                  storage=temp_storage, upload_to='tests',
                                  height_field='headshot_height',
                                  width_field='headshot_width')

###############################################################################
