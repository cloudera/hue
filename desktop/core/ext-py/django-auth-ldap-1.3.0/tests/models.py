from __future__ import absolute_import, division, print_function, unicode_literals

from django.contrib.auth.models import AbstractBaseUser
from django.db import models


class TestUser(AbstractBaseUser):
    identifier = models.CharField(max_length=40, unique=True, db_index=True)
    uid_number = models.IntegerField()

    USERNAME_FIELD = 'identifier'

    def get_full_name(self):
        return self.identifier

    def get_short_name(self):
        return self.identifier

    def get_first_name(self):
        return 'Alice'

    def set_first_name(self, value):
        raise Exception('Oops...')

    first_name = property(get_first_name, set_first_name)
