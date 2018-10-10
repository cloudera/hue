History
-------

Eventlet began life as Donovan Preston was talking to Bob Ippolito about coroutine-based non-blocking networking frameworks in Python. Most non-blocking frameworks require you to run the "main loop" in order to perform all network operations, but Donovan wondered if a library written using a trampolining style could get away with transparently running the main loop any time i/o was required, stopping the main loop once no more i/o was scheduled. Bob spent a few days during PyCon 2006 writing a proof-of-concept. He named it eventlet, after the coroutine implementation it used, `greenlet <http://cheeseshop.python.org/pypi/greenlet greenlet>`_. Donovan began using eventlet as a light-weight network library for his spare-time project `Pavel <http://soundfarmer.com/Pavel/trunk/ Pavel>`_, and also began writing some unittests.

* http://svn.red-bean.com/bob/eventlet/trunk/

When Donovan started at Linden Lab in May of 2006, he added eventlet as an svn external in the ``indra/lib/python directory``, to be a dependency of the yet-to-be-named backbone project (at the time, it was named restserv). However, including eventlet as an svn external meant that any time the externally hosted project had hosting issues, Linden developers were not able to perform svn updates. Thus, the eventlet source was imported into the linden source tree at the same location, and became a fork.

Bob Ippolito has ceased working on eventlet and has stated his desire for Linden to take it's fork forward to the open source world as "the" eventlet.
