# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Nonce',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('issuer_url', models.URLField()),
                ('state', models.CharField(unique=True, max_length=255)),
                ('redirect_url', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='OpenIDProvider',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('issuer', models.URLField(unique=True)),
                ('authorization_endpoint', models.URLField()),
                ('token_endpoint', models.URLField()),
                ('userinfo_endpoint', models.URLField()),
                ('jwks_uri', models.URLField(null=True, blank=True)),
                ('signing_alg', models.CharField(default=b'HS256', max_length=5, choices=[(b'RS256', b'RS256'), (b'HS256', b'HS256')])),
                ('client_id', models.CharField(max_length=255)),
                ('client_secret', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='OpenIDUser',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('sub', models.CharField(unique=True, max_length=255)),
                ('access_token', models.CharField(max_length=255)),
                ('refresh_token', models.CharField(max_length=255)),
                ('issuer', models.ForeignKey(to='oidc_auth.OpenIDProvider')),
                ('user', models.OneToOneField(related_name='oidc_account', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
