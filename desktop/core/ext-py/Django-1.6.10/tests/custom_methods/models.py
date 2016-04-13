"""
3. Giving models custom methods

Any method you add to a model will be available to instances.
"""

import datetime

from django.db import models
from django.utils.encoding import python_2_unicode_compatible


@python_2_unicode_compatible
class Article(models.Model):
    headline = models.CharField(max_length=100)
    pub_date = models.DateField()

    def __str__(self):
        return self.headline

    def was_published_today(self):
        return self.pub_date == datetime.date.today()

    def articles_from_same_day_1(self):
        return Article.objects.filter(pub_date=self.pub_date).exclude(id=self.id)

    def articles_from_same_day_2(self):
        """
        Verbose version of get_articles_from_same_day_1, which does a custom
        database query for the sake of demonstration.
        """
        from django.db import connection
        cursor = connection.cursor()
        cursor.execute("""
            SELECT id, headline, pub_date
            FROM custom_methods_article
            WHERE pub_date = %s
                AND id != %s""", [connection.ops.value_to_db_date(self.pub_date),
                                  self.id])
        return [self.__class__(*row) for row in cursor.fetchall()]
