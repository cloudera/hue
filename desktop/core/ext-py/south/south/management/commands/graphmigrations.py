"""
Outputs a graphviz dot file of the dependencies.
"""

from optparse import make_option

from django.core.management.base import BaseCommand
from django.core.management.color import no_style

from south.migration import Migrations, all_migrations

class Command(BaseCommand):

    help = "Outputs a GraphViz dot file of all migration dependencies to stdout."
    
    def handle(self, **options):
        
        # Resolve dependencies
        Migrations.calculate_dependencies()
        
        print "digraph G {"
        
        # Print each app in a cluster
        #for migrations in all_migrations():
        #    print "  subgraph %s {" % migrations.app_label()
        #    # Nodes inside here are linked
        #    print (" -> ".join(['"%s.%s"' % (migration.app_label(), migration.name()) for migration in migrations])) + ";"
        #    print "  }"
    
        # For every migration, print its links.
        for migrations in all_migrations():
            for migration in migrations:
                for other in migration.dependencies:
                    print '"%s.%s" -> "%s.%s"' % (
                        other.app_label(), other.name(),
                        migration.app_label(), migration.name(),
                    )
            
        print "}";