from __future__ import unicode_literals

from django.core.management.base import BaseCommand

from axes.models import AccessAttempt


class Command(BaseCommand):
    args = ''
    help = ('List registered login attempts')

    def handle(self, *args, **kwargs):  # pylint: disable=unused-argument
        for obj in AccessAttempt.objects.all():
            self.stdout.write('{ip}\t{username}\t{failures}'.format(
                ip=obj.ip_address,
                username=obj.username,
                failures=obj.failures,
            ))
