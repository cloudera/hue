
.. _signals:

Signals
=======

South offers its own signals, if you want to write code which executes before
or after migrations. They're available from ``south.signals``.


pre_migrate
-----------

Sent just before South starts running migrations for an app.

Provides one argument, ``app``, a string containing the app's label.


post_migrate
------------

Sent just after South successfully finishes running migrations for an app. Note
that if the migrations fail in the middle of executing, this will not get called.

Provides one argument, ``app``, a string containing the app's label.


ran_migration
------------

Sent just after South successfully runs a single migration file; can easily be
sent multiple times in one run of South, possibly hundreds of times if you
have hundreds of migrations, and are doing a fresh install.

Provides three arguments, ``app``, a string containing the app's label,
``migration``, a string containing the name of the migration file without the
file extension, and ``method``, which is either ``"forwards"`` or ``"backwards"``.