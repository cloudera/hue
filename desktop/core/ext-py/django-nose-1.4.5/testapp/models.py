"""Models for django-nose test application.

Based on the Django tutorial:
https://docs.djangoproject.com/en/1.8/intro/tutorial01/
"""

from django.db import models


class Question(models.Model):
    """A poll question."""

    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date published')

    def __str__(self):
        """Return string representation."""
        return self.question_text


class Choice(models.Model):
    """A poll answer."""

    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)

    def __str__(self):
        """Return string representation."""
        return self.choice_text
