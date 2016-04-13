from __future__ import absolute_import

from datetime import date

from django.db.models.query_utils import InvalidQuery
from django.test import TestCase, skipUnlessDBFeature

from .models import Author, Book, Coffee, Reviewer, FriendlyAuthor


class RawQueryTests(TestCase):
    fixtures = ['raw_query_books.json']

    def assertSuccessfulRawQuery(self, model, query, expected_results,
            expected_annotations=(), params=[], translations=None):
        """
        Execute the passed query against the passed model and check the output
        """
        results = list(model.objects.raw(query, params=params, translations=translations))
        self.assertProcessed(model, results, expected_results, expected_annotations)
        self.assertAnnotations(results, expected_annotations)

    def assertProcessed(self, model, results, orig, expected_annotations=()):
        """
        Compare the results of a raw query against expected results
        """
        self.assertEqual(len(results), len(orig))
        for index, item in enumerate(results):
            orig_item = orig[index]
            for annotation in expected_annotations:
                setattr(orig_item, *annotation)

            for field in model._meta.fields:
                # Check that all values on the model are equal
                self.assertEqual(getattr(item,field.attname),
                                  getattr(orig_item,field.attname))
                # This includes checking that they are the same type
                self.assertEqual(type(getattr(item,field.attname)),
                                  type(getattr(orig_item,field.attname)))

    def assertNoAnnotations(self, results):
        """
        Check that the results of a raw query contain no annotations
        """
        self.assertAnnotations(results, ())

    def assertAnnotations(self, results, expected_annotations):
        """
        Check that the passed raw query results contain the expected
        annotations
        """
        if expected_annotations:
            for index, result in enumerate(results):
                annotation, value = expected_annotations[index]
                self.assertTrue(hasattr(result, annotation))
                self.assertEqual(getattr(result, annotation), value)

    def testSimpleRawQuery(self):
        """
        Basic test of raw query with a simple database query
        """
        query = "SELECT * FROM raw_query_author"
        authors = Author.objects.all()
        self.assertSuccessfulRawQuery(Author, query, authors)

    def testRawQueryLazy(self):
        """
        Raw queries are lazy: they aren't actually executed until they're
        iterated over.
        """
        q = Author.objects.raw('SELECT * FROM raw_query_author')
        self.assertTrue(q.query.cursor is None)
        list(q)
        self.assertTrue(q.query.cursor is not None)

    def testFkeyRawQuery(self):
        """
        Test of a simple raw query against a model containing a foreign key
        """
        query = "SELECT * FROM raw_query_book"
        books = Book.objects.all()
        self.assertSuccessfulRawQuery(Book, query, books)

    def testDBColumnHandler(self):
        """
        Test of a simple raw query against a model containing a field with
        db_column defined.
        """
        query = "SELECT * FROM raw_query_coffee"
        coffees = Coffee.objects.all()
        self.assertSuccessfulRawQuery(Coffee, query, coffees)

    def testOrderHandler(self):
        """
        Test of raw raw query's tolerance for columns being returned in any
        order
        """
        selects = (
            ('dob, last_name, first_name, id'),
            ('last_name, dob, first_name, id'),
            ('first_name, last_name, dob, id'),
        )

        for select in selects:
            query = "SELECT %s FROM raw_query_author" % select
            authors = Author.objects.all()
            self.assertSuccessfulRawQuery(Author, query, authors)

    def testTranslations(self):
        """
        Test of raw query's optional ability to translate unexpected result
        column names to specific model fields
        """
        query = "SELECT first_name AS first, last_name AS last, dob, id FROM raw_query_author"
        translations = {'first': 'first_name', 'last': 'last_name'}
        authors = Author.objects.all()
        self.assertSuccessfulRawQuery(Author, query, authors, translations=translations)

    def testParams(self):
        """
        Test passing optional query parameters
        """
        query = "SELECT * FROM raw_query_author WHERE first_name = %s"
        author = Author.objects.all()[2]
        params = [author.first_name]
        qset = Author.objects.raw(query, params=params)
        results = list(qset)
        self.assertProcessed(Author, results, [author])
        self.assertNoAnnotations(results)
        self.assertEqual(len(results), 1)
        self.assertIsInstance(repr(qset), str)

    @skipUnlessDBFeature('supports_paramstyle_pyformat')
    def testPyformatParams(self):
        """
        Test passing optional query parameters
        """
        query = "SELECT * FROM raw_query_author WHERE first_name = %(first)s"
        author = Author.objects.all()[2]
        params = {'first': author.first_name}
        qset = Author.objects.raw(query, params=params)
        results = list(qset)
        self.assertProcessed(Author, results, [author])
        self.assertNoAnnotations(results)
        self.assertEqual(len(results), 1)
        self.assertIsInstance(repr(qset), str)

    def testManyToMany(self):
        """
        Test of a simple raw query against a model containing a m2m field
        """
        query = "SELECT * FROM raw_query_reviewer"
        reviewers = Reviewer.objects.all()
        self.assertSuccessfulRawQuery(Reviewer, query, reviewers)

    def testExtraConversions(self):
        """
        Test to insure that extra translations are ignored.
        """
        query = "SELECT * FROM raw_query_author"
        translations = {'something': 'else'}
        authors = Author.objects.all()
        self.assertSuccessfulRawQuery(Author, query, authors, translations=translations)

    def testMissingFields(self):
        query = "SELECT id, first_name, dob FROM raw_query_author"
        for author in Author.objects.raw(query):
            self.assertNotEqual(author.first_name, None)
            # last_name isn't given, but it will be retrieved on demand
            self.assertNotEqual(author.last_name, None)

    def testMissingFieldsWithoutPK(self):
        query = "SELECT first_name, dob FROM raw_query_author"
        try:
            list(Author.objects.raw(query))
            self.fail('Query without primary key should fail')
        except InvalidQuery:
            pass

    def testAnnotations(self):
        query = "SELECT a.*, count(b.id) as book_count FROM raw_query_author a LEFT JOIN raw_query_book b ON a.id = b.author_id GROUP BY a.id, a.first_name, a.last_name, a.dob ORDER BY a.id"
        expected_annotations = (
            ('book_count', 3),
            ('book_count', 0),
            ('book_count', 1),
            ('book_count', 0),
        )
        authors = Author.objects.all()
        self.assertSuccessfulRawQuery(Author, query, authors, expected_annotations)

    def testWhiteSpaceQuery(self):
        query = "    SELECT * FROM raw_query_author"
        authors = Author.objects.all()
        self.assertSuccessfulRawQuery(Author, query, authors)

    def testMultipleIterations(self):
        query = "SELECT * FROM raw_query_author"
        normal_authors = Author.objects.all()
        raw_authors = Author.objects.raw(query)

        # First Iteration
        first_iterations = 0
        for index, raw_author in enumerate(raw_authors):
            self.assertEqual(normal_authors[index], raw_author)
            first_iterations += 1

        # Second Iteration
        second_iterations = 0
        for index, raw_author in enumerate(raw_authors):
            self.assertEqual(normal_authors[index], raw_author)
            second_iterations += 1

        self.assertEqual(first_iterations, second_iterations)

    def testGetItem(self):
        # Indexing on RawQuerySets
        query = "SELECT * FROM raw_query_author ORDER BY id ASC"
        third_author = Author.objects.raw(query)[2]
        self.assertEqual(third_author.first_name, 'Bob')

        first_two = Author.objects.raw(query)[0:2]
        self.assertEqual(len(first_two), 2)

        self.assertRaises(TypeError, lambda: Author.objects.raw(query)['test'])

    def test_inheritance(self):
        # date is the end of the Cuban Missile Crisis, I have no idea when
        # Wesley was bron
        f = FriendlyAuthor.objects.create(first_name="Wesley", last_name="Chun",
            dob=date(1962, 10, 28))
        query = "SELECT * FROM raw_query_friendlyauthor"
        self.assertEqual(
            [o.pk for o in FriendlyAuthor.objects.raw(query)], [f.pk]
        )

    def test_query_count(self):
        self.assertNumQueries(1,
            list, Author.objects.raw("SELECT * FROM raw_query_author")
        )
