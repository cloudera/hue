# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("migrations", "0001_initial")]

    operations = [

        migrations.CreateModel(
            "Something",
            [
                ("id", models.AutoField(primary_key=True)),
            ],
        )

    ]
