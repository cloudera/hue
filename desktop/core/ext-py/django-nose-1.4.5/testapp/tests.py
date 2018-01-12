"""Django model tests."""

from datetime import datetime

from django.test import TestCase
from testapp.models import Question, Choice


class NoDatabaseTestCase(TestCase):
    """Tests that don't read or write to the database."""

    def test_question_str(self):
        """Test Question.__str__ method."""
        question = Question(question_text="What is your name?")
        self.assertEqual("What is your name?", str(question))

    def test_choice_str(self):
        """Test Choice.__str__ method."""
        choice = Choice(choice_text='My name is Sir Lancelot of Camelot.')
        self.assertEqual('My name is Sir Lancelot of Camelot.', str(choice))


class UsesDatabaseTestCase(TestCase):
    """Tests that read and write to the database."""

    def test_question(self):
        """Test that votes is initialized to 0."""
        question = Question.objects.create(
            question_text="What is your quest?", pub_date=datetime(1975, 4, 9))
        Choice.objects.create(
            question=question, choice_text="To seek the Holy Grail.")
        self.assertTrue(question.choice_set.exists())
        the_choice = question.choice_set.get()
        self.assertEqual(0, the_choice.votes)


class UsesFixtureTestCase(TestCase):
    """Tests that use a test fixture."""

    fixtures = ["testdata.json"]

    def test_fixture_loaded(self):
        """Test that fixture was loaded."""
        question = Question.objects.get()
        self.assertEqual(
            'What is your favorite color?', question.question_text)
        self.assertEqual(datetime(1975, 4, 9), question.pub_date)
        choice = question.choice_set.get()
        self.assertEqual("Blue.", choice.choice_text)
        self.assertEqual(3, choice.votes)
