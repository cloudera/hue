from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.encoding import python_2_unicode_compatible

## Basic tests

@python_2_unicode_compatible
class Author(models.Model):
    name = models.CharField(max_length=50, unique=True)
    first_book = models.ForeignKey('Book', related_name='first_time_authors')
    favorite_authors = models.ManyToManyField(
        'self', through='FavoriteAuthors', symmetrical=False, related_name='favors_me')

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['id']


class AuthorWithAge(Author):
    author = models.OneToOneField(Author, parent_link=True)
    age = models.IntegerField()


class FavoriteAuthors(models.Model):
    author = models.ForeignKey(Author, to_field='name', related_name='i_like')
    likes_author = models.ForeignKey(Author, to_field='name', related_name='likes_me')

    class Meta:
         ordering = ['id']


@python_2_unicode_compatible
class AuthorAddress(models.Model):
    author = models.ForeignKey(Author, to_field='name', related_name='addresses')
    address = models.TextField()

    class Meta:
        ordering = ['id']

    def __str__(self):
        return self.address


@python_2_unicode_compatible
class Book(models.Model):
    title = models.CharField(max_length=255)
    authors = models.ManyToManyField(Author, related_name='books')

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['id']

class BookWithYear(Book):
    book = models.OneToOneField(Book, parent_link=True)
    published_year = models.IntegerField()
    aged_authors = models.ManyToManyField(
        AuthorWithAge, related_name='books_with_year')


@python_2_unicode_compatible
class Reader(models.Model):
    name = models.CharField(max_length=50)
    books_read = models.ManyToManyField(Book, related_name='read_by')

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['id']

class BookReview(models.Model):
    book = models.ForeignKey(BookWithYear)
    notes = models.TextField(null=True, blank=True)

## Models for default manager tests

class Qualification(models.Model):
    name = models.CharField(max_length=10)

    class Meta:
        ordering = ['id']


class TeacherManager(models.Manager):
    def get_queryset(self):
        return super(TeacherManager, self).get_queryset().prefetch_related('qualifications')


@python_2_unicode_compatible
class Teacher(models.Model):
    name = models.CharField(max_length=50)
    qualifications = models.ManyToManyField(Qualification)

    objects = TeacherManager()

    def __str__(self):
        return "%s (%s)" % (self.name, ", ".join(q.name for q in self.qualifications.all()))

    class Meta:
        ordering = ['id']


class Department(models.Model):
    name = models.CharField(max_length=50)
    teachers = models.ManyToManyField(Teacher)

    class Meta:
        ordering = ['id']


## GenericRelation/GenericForeignKey tests

@python_2_unicode_compatible
class TaggedItem(models.Model):
    tag = models.SlugField()
    content_type = models.ForeignKey(ContentType, related_name="taggeditem_set2")
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')
    created_by_ct = models.ForeignKey(ContentType, null=True,
                                      related_name='taggeditem_set3')
    created_by_fkey = models.PositiveIntegerField(null=True)
    created_by = generic.GenericForeignKey('created_by_ct', 'created_by_fkey',)
    favorite_ct = models.ForeignKey(ContentType, null=True,
                                    related_name='taggeditem_set4')
    favorite_fkey = models.CharField(max_length=64, null=True)
    favorite = generic.GenericForeignKey('favorite_ct', 'favorite_fkey')

    def __str__(self):
        return self.tag


class Bookmark(models.Model):
    url = models.URLField()
    tags = generic.GenericRelation(TaggedItem, related_name='bookmarks')
    favorite_tags = generic.GenericRelation(TaggedItem,
                                    content_type_field='favorite_ct',
                                    object_id_field='favorite_fkey',
                                    related_name='favorite_bookmarks')


class Comment(models.Model):
    comment = models.TextField()

    # Content-object field
    content_type   = models.ForeignKey(ContentType)
    object_pk      = models.TextField()
    content_object = generic.GenericForeignKey(ct_field="content_type", fk_field="object_pk")


## Models for lookup ordering tests


class House(models.Model):
    address = models.CharField(max_length=255)

    class Meta:
        ordering = ['id']

class Room(models.Model):
    name = models.CharField(max_length=50)
    house = models.ForeignKey(House, related_name='rooms')

    class Meta:
        ordering = ['id']


class Person(models.Model):
    name = models.CharField(max_length=50)
    houses = models.ManyToManyField(House, related_name='occupants')

    @property
    def primary_house(self):
        # Assume business logic forces every person to have at least one house.
        return sorted(self.houses.all(), key=lambda house: -house.rooms.count())[0]

    class Meta:
        ordering = ['id']


## Models for nullable FK tests

@python_2_unicode_compatible
class Employee(models.Model):
    name = models.CharField(max_length=50)
    boss = models.ForeignKey('self', null=True,
                             related_name='serfs')

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['id']


### Ticket 19607

@python_2_unicode_compatible
class LessonEntry(models.Model):
    name1 = models.CharField(max_length=200)
    name2 = models.CharField(max_length=200)

    def __str__(self):
        return "%s %s" % (self.name1, self.name2)


@python_2_unicode_compatible
class WordEntry(models.Model):
    lesson_entry = models.ForeignKey(LessonEntry)
    name = models.CharField(max_length=200)

    def __str__(self):
        return "%s (%s)" % (self.name, self.id)


## Ticket #21410: Regression when related_name="+"

@python_2_unicode_compatible
class Author2(models.Model):
    name = models.CharField(max_length=50, unique=True)
    first_book = models.ForeignKey('Book', related_name='first_time_authors+')
    favorite_books = models.ManyToManyField('Book', related_name='+')

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['id']
