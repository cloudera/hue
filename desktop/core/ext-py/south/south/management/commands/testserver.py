from django.core.management.commands import testserver
import south.management.commands.syncdb

class Command(testserver.Command):
    def handle(self, *args, **kwargs):
        south.management.commands.syncdb.patch_for_test_db_setup()
        super(Command, self).handle(*args, **kwargs)
