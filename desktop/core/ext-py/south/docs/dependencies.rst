
.. _dependencies:

Dependencies
============

Migrations for apps are nice 'n all, but when you start writing a large project,
with a lot of apps, you realise you have foreign key relationships between apps
and working out what order migrations would need to be applied in for each app
is just painful.

Luckily, we also had this problem, so South has a dependency system. Inside a
migration, you can declare that it depends on having another app having run a
certain migration first; for example, if my app "forum" depends on the
"accounts" app having created its user profile table, we can do::

    # forum/migrations/0002_post.py
    class Migration:
        
        depends_on = (
            ("accounts", "0003_add_user_profile"),
        )
    
        def forwards(self):
            ....

Then, if you try and migrate to or beyond 0002_post in the forum app, it will
first make sure accounts is migrated at least up to 0003_add_user_profile,
and if not will migrate it for you.

Dependencies also work in reverse; South knows not to undo that
0003_add_user_profile migration until it has undone the 0002_post migration.

You can have multiple dependencies, and all sorts of wacky structures;
there are, however, two rules:

 - No circular dependencies (two or more migrations depending on each other)
 - No upwards dependencies in the same app (so you can't make 0002_post in the forum app depend on 0003_room in the same app, either directly or through a dependency chain.

Reverse Dependencies
--------------------

South also supports "reverse dependencies" - a dependecy where you say your
migration must be run before another, rather than vice-versa. This is useful
if you're trying to run a migration before another in a separate, third-party
(or unchangeable) code.

Declaring these is just like the other kind, except you use needed_by::

    class Migration:
        
        needed_by = (
            ("accounts", "0005_make_fks"),
        )
    
        def forwards(self):
            ....