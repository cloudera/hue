from django.core.management.commands import test
import south.management.commands.syncdb

class Command(test.Command):
    def handle(self, *args, **kwargs):
        south.management.commands.syncdb.patch_for_test_db_setup()
        super(Command, self).handle(*args, **kwargs)
