
.. _tutorial-part-3:

Part 3: Advanced Commands and Data Migrations
=============================================

Listing current migrations
--------------------------

It can be very useful to know what migrations you currently have applied, and
which ones are available. For this reason, there's ``./manage.py migrate --list``.

Run against our project from before, we get::

 $ ./manage.py migrate --list

 southtut
  (*) 0001_initial
  (*) 0002_auto__add_field_knight_dances_whenever_able
  (*) 0003_auto__add_field_knight_shrubberies
  (*) 0004_auto__add_unique_knight_name
  
The output has an asterisk ``(*)`` next to a migration name if it has been
applied, and an empty space ``( )`` if not [#]_.
 
If you have a lot of apps or migrations, you can also specify an app name
to show just the migrations from that app.

.. [#] An interesting side effect of this is that you can run the command
       ``./manage.py migrate --list |grep -v "*"`` to see which migrations
       are unapplied, and need running.

Data migrations
---------------

The previous parts have only covered *schema migrations* - migrations which
change the layout of your columns and indexes. There's also another kind of
migration, the so-called *data migration*.

Data migrations are used to change the data stored in your database to match
a new schema, or feature. For example, if you've been storing passwords in
plain text [#]_, and you're moving to salted and hashed passwords, you might
have these three steps (where each step corresponds to a migration):

 - Create two new columns, ``password_salt`` and ``password_hash`` (a schema
   migration).
 - Using the contents of the old ``password`` column, calculate salts and hashes
   for each user (a data migration)
 - Remove the old ``password`` column (a schema migration).
 
.. [#] If you're actually storing passwords in plaintext, please convert. Now.
 
The first and last migrations you already know how to do; make the relevant
changes in the models.py file, and run ``./manage.py schemamigration --auto
myapp``. Remember that you need to add the two columns separately to deleting
the old column, as otherwise the old column won't be around for us to get data
out of, and you'll have lost all your users' passwords [#]_.

.. [#] Always, always, backup your database before doing any kind of potentially
       destructive migration. One time, it *will* go wrong.

Let's follow a real example. Make a new app, and call it ``southtut2``. Add it
to ``INSTALLED_APPS``, and then give it this model::

 from django.db import models
 
 class User(models.Model):
    
     username = models.CharField(max_length=255)
     password = models.CharField(max_length=60)
     name = models.TextField()

Make an initial migration for it, apply it, and then add a record::

 $ ./manage.py schemamigration --initial southtut2
 Creating migrations directory at '/home/andrew/Programs/litret/southtut2/migrations'...
 Creating __init__.py in '/home/andrew/Programs/litret/southtut2/migrations'...
 + Added model southtut2.User
 Created 0001_initial.py. You can now apply this migration with: ./manage.py migrate southtut2
 
 $ ./manage.py migrate southtut2
 Running migrations for southtut2:
  - Migrating forwards to 0001_initial.
  > southtut2:0001_initial
  - Loading initial data for southtut2.
 
 $ ./manage.py shell
 In [1]: from southtut2.models import User

 In [2]: User.objects.create(username="andrew", password="ihopetheycantseethis", name="Andrew Godwin")
 Out[2]: <User: User object>

 In [3]: User.objects.get(id=1).password
 Out[3]: u'ihopetheycantseethis'

As you can see, the password is clearly visible, which isn't good. Let's move
to password hashing, while keeping everyone's password valid. Firstly,
modify the model so it looks like this::

 from django.db import models
 import sha
 
 class User(models.Model):
     
     username = models.CharField(max_length=255)
     password = models.CharField(max_length=60)
     password_salt = models.CharField(max_length=8, null=True)
     password_hash = models.CharField(max_length=40, null=True)
     name = models.TextField()
    
     def check_password(self, password):
         return sha.sha(self.password_salt + password).hexdigest() == self.password_hash
 
Make a schema migration that will create our two new columns (notice that
they've both been added as ``null=True``; once they have data, we'll 
alter them to be ``null=False``)::

 $ ./manage.py schemamigration southtut2 --auto
  + Added field password_salt on southtut2.User
  + Added field password_hash on southtut2.User
 Created 0002_auto__add_field_user_password_salt__add_field_user_password_hash.py. You can now apply this migration with: ./manage.py migrate southtut2
 
Now, the second migration is more interesting. Firstly, we need to create a
skeleton data migration (unlike schema migrations, South can't write these for
you)::

 $ ./manage.py datamigration southtut2 hash_passwords
 Created 0003_hash_passwords.py.
 
If you open up the file, you'll see that South has made the shell of a migration;
the models definitions are there, the forwards() and backwards() functions are
these, but there's no code in either. We'll write some code to port the
passwords over in the forwards function::

 def forwards(self, orm):
     import random, sha, string
     for user in orm.User.objects.all():
         user.password_salt = "".join([random.choice(string.letters) for i in range(8)])
         user.password_hash = sha.sha(user.password_salt + user.password).hexdigest()
         user.save()

Notice that we use ``orm.User`` to access the User model - this gives us the
version of User from when this migration was created, so if we want to run
the migration in future, it won't get a completely different, new, User model.

If you want to access models from other apps in your data migration, use a
syntax like ``orm['contenttypes.ContentType']``. Models will be available if you
can somehow get to them via ForeignKey or ManyToMany traversal from your app's
models; if you want to freeze other models, simply pass ``--freeze appname`` on
the ``datamigration`` command line.

We should also raise an error in the ``backwards()`` method, since this process
is by its very nature irreversible::

 def backwards(self, orm):
     raise RuntimeError("Cannot reverse this migration.")

That looks good. Finally, remove the ``password`` field from your model, and 
run ``schemamigration`` one last time to make a migration to remove that field::

 $ ./manage.py schemamigration southtut2 --auto
  ? The field 'User.password' does not have a default specified, yet is NOT NULL.
  ? Since you are adding or removing this field, you MUST specify a default
  ? value to use for existing rows. Would you like to:
  ?  1. Quit now, and add a default to the field in models.py
  ?  2. Specify a one-off value to use for existing columns now
  ? Please select a choice: 2
  ? Please enter Python code for your one-off default value.
  ? The datetime module is available, so you can do e.g. datetime.date.today()
  >>> ""
  - Deleted field password on southtut2.User
 Created 0004_auto__del_field_user_password.py. You can now apply this migration with: ./manage.py migrate southtut2
 
Notice that South is asking for a default value for ``password``; if you were to
reverse this migration, it tries to re-add the ``password`` column, and thus
needs either a default value or for the field to be ``null=True``. Here, I've
fed it the empty string, as that's a reasonable default in this case.

Finally, let's apply all three migrations::

 $ ./manage.py migrate southtut2
 Running migrations for southtut2:
  - Migrating forwards to 0004_auto__del_field_user_password.
  > southtut2:0002_auto__add_field_user_password_salt__add_field_user_password_hash
  > southtut2:0003_hash_passwords
  > southtut2:0004_auto__del_field_user_password
  - Loading initial data for southtut2.

Looks good - we've added the new columns, migrated the passwords over, and then
deleted the old column. Let's check our data was preserved::

 $ ./manage.py shell
 In [1]: from southtut2.models import User

 In [2]: User.objects.get(id=1).check_password("ihopetheycantseethis")
 Out[2]: True
 
 In [3]: User.objects.get(id=1).check_password("fakepass")
 Out[3]: False
 
That looks like a successful data migration!

You can do a lot more with this inside a data migration; any model can be
available to you. The only caveat is that you won't have access to any custom
methods or managers on your models, as they're not preserved as part of the
freezing process (there's no way to do this generally); you'll have to copy any
code you want into the migration itself. Feel free to make them methods on
the ``Migration`` class; South ignores everything apart from ``forwards`` and
``backwards``.