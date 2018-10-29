from django.conf import settings
from django.contrib.auth.models import Group
from django.db import models


class UserGroup(models.Model):

    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    group = models.ForeignKey(Group)
