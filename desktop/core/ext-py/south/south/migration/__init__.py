"""
Main migration logic.
"""

import sys

from django.core.exceptions import ImproperlyConfigured

import south.db
from south import exceptions
from south.models import MigrationHistory
from south.db import db, DEFAULT_DB_ALIAS
from south.migration.migrators import (Backwards, Forwards,
                                       DryRunMigrator, FakeMigrator,
                                       LoadInitialDataMigrator)
from south.migration.base import Migration, Migrations
from south.migration.utils import SortedSet
from south.migration.base import all_migrations
from south.signals import pre_migrate, post_migrate


def to_apply(forwards, done):
    return [m for m in forwards if m not in done]

def to_unapply(backwards, done):
    return [m for m in backwards if m in done]

def problems(pending, done):
    last = None
    if not pending:
        raise StopIteration()
    for migration in pending:
        if migration in done:
            last = migration
            continue
        if last and migration not in done:
            yield last, migration

def problems(pending, done):
    last = None
    if not pending:
        raise StopIteration()
    for migration in pending:
        if migration in done:
            last = migration
            continue
        if last and migration not in done:
            yield last, migration

def forwards_problems(pending, done, verbosity):
    """
    Takes the list of linearised pending migrations, and the set of done ones,
    and returns the list of problems, if any.
    """
    return inner_problem_check(problems(reversed(pending), done), done, verbosity)

def backwards_problems(pending, done, verbosity):
    return inner_problem_check(problems(pending, done), done, verbosity)

def inner_problem_check(problems, done, verbosity):
    "Takes a set of possible problems and gets the actual issues out of it."
    result = []
    for last, migration in problems:
        # 'Last' is the last applied migration. Step back from it until we
        # either find nothing wrong, or we find something.
        to_check = list(last.dependencies)
        while to_check:
            checking = to_check.pop()
            if checking not in done:
                # That's bad. Error.
                if verbosity:
                    print (" ! Migration %s should not have been applied "
                           "before %s but was." % (last, checking))
                result.append((last, checking))
            else:
                to_check.extend(checking.dependencies)
    return result

def check_migration_histories(histories, delete_ghosts=False):
    "Checks that there's no 'ghost' migrations in the database."
    exists = SortedSet()
    ghosts = []
    for h in histories:
        try:
            m = h.get_migration()
            m.migration()
        except exceptions.UnknownMigration:
            ghosts.append(h)
        except ImproperlyConfigured:
            pass                        # Ignore missing applications
        else:
            exists.add(m)
    if ghosts:
        # They may want us to delete ghosts.
        if delete_ghosts:
            for h in ghosts:
                h.delete()
        else:
            raise exceptions.GhostMigrations(ghosts)
    return exists

def get_dependencies(target, migrations):
    forwards = list
    backwards = list
    if target is None:
        backwards = migrations[0].backwards_plan
    else:
        forwards = target.forwards_plan
        # When migrating backwards we want to remove up to and
        # including the next migration up in this app (not the next
        # one, that includes other apps)
        migration_before_here = target.next()
        if migration_before_here:
            backwards = migration_before_here.backwards_plan
    return forwards, backwards

def get_direction(target, applied, migrations, verbosity):
    # Get the forwards and reverse dependencies for this target
    forwards, backwards = get_dependencies(target, migrations)
    # Is the whole forward branch applied?
    problems = None
    forwards = forwards()
    workplan = to_apply(forwards, applied)
    if not workplan:
        # If they're all applied, we only know it's not backwards
        direction = None
    else:
        # If the remaining migrations are strictly a right segment of
        # the forwards trace, we just need to go forwards to our
        # target (and check for badness)
        problems = forwards_problems(forwards, applied, verbosity)
        direction = Forwards(verbosity=verbosity)
    if not problems:
        # What about the whole backward trace then?
        backwards = backwards()
        missing_backwards = to_apply(backwards, applied)
        if missing_backwards != backwards:
            # If what's missing is a strict left segment of backwards (i.e.
            # all the higher migrations) then we need to go backwards
            workplan = to_unapply(backwards, applied)
            problems = backwards_problems(backwards, applied, verbosity)
            direction = Backwards(verbosity=verbosity)
    return direction, problems, workplan

def get_migrator(direction, db_dry_run, fake, load_initial_data):
    if not direction:
        return direction
    if db_dry_run:
        direction = DryRunMigrator(migrator=direction, ignore_fail=False)
    elif fake:
        direction = FakeMigrator(migrator=direction)
    elif load_initial_data:
        direction = LoadInitialDataMigrator(migrator=direction)
    return direction

def migrate_app(migrations, target_name=None, merge=False, fake=False, db_dry_run=False, yes=False, verbosity=0, load_initial_data=False, skip=False, database=DEFAULT_DB_ALIAS, delete_ghosts=False):
    app_label = migrations.app_label()

    verbosity = int(verbosity)
    # Fire off the pre-migrate signal
    pre_migrate.send(None, app=app_label)
    
    # If there aren't any, quit quizically
    if not migrations:
        print "? You have no migrations for the '%s' app. You might want some." % app_label
        return
    
    # Load the entire dependency graph
    Migrations.calculate_dependencies()
    
    # Check there's no strange ones in the database
    applied = MigrationHistory.objects.filter(applied__isnull=False)
    # If we're using a different database, use that
    if database != DEFAULT_DB_ALIAS:
        applied = applied.using(database)
        south.db.db = south.db.dbs[database]
        # We now have to make sure the migrations are all reloaded, as they'll
        # have imported the old value of south.db.db.
        Migrations.invalidate_all_modules()
    
    south.db.db.debug = (verbosity > 1)
    applied = check_migration_histories(applied, delete_ghosts)
    
    # Guess the target_name
    target = migrations.guess_migration(target_name)
    if verbosity:
        if target_name not in ('zero', None) and target.name() != target_name:
            print " - Soft matched migration %s to %s." % (target_name,
                                                           target.name())
        print "Running migrations for %s:" % app_label
    
    # Get the forwards and reverse dependencies for this target
    direction, problems, workplan = get_direction(target, applied,
                                                  migrations, verbosity)
    if problems and not (merge or skip):
        raise exceptions.InconsistentMigrationHistory(problems)
    
    # Perform the migration
    migrator = get_migrator(direction, db_dry_run, fake, load_initial_data)
    if migrator:
        migrator.print_title(target)
        success = migrator.migrate_many(target, workplan, database)
        # Finally, fire off the post-migrate signal
        if success:
            post_migrate.send(None, app=app_label)
    elif verbosity:
        print '- Nothing to migrate.'
        post_migrate.send(None, app=app_label)
