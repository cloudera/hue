""" Convenience module for running standard library tests with nose.  The standard
tests are not especially homogeneous, but they mostly expose a test_main method that
does the work of selecting which tests to run based on what is supported by the
platform.  On its own, Nose would run all possible tests and many would fail; therefore
we collect all of the test_main methods here in one module and Nose can run it.

Hopefully in the future the standard tests get rewritten to be more nosey.

Many of these tests make connections to external servers, and all.py tries to skip these
tests rather than failing them, so you can get some work done on a plane.
"""

from eventlet import debug
debug.hub_prevent_multiple_readers(False)


def restart_hub():
    from eventlet import hubs
    hub = hubs.get_hub()
    hub_shortname = hub.__module__.split('.')[-1]
    # don't restart the pyevent hub; it's not necessary
    if hub_shortname != 'pyevent':
        hub.abort()
        hubs.use_hub(hub_shortname)


def assimilate_patched(name):
    try:
        modobj = __import__(name, globals(), locals(), ['test_main'])
        restart_hub()
    except ImportError:
        print("Not importing %s, it doesn't exist in this installation/version of Python" % name)
        return
    else:
        method_name = name + "_test_main"
        try:
            test_method = modobj.test_main

            def test_main():
                restart_hub()
                test_method()
                restart_hub()
            globals()[method_name] = test_main
            test_main.__name__ = name + '.test_main'
        except AttributeError:
            print("No test_main for %s, assuming it tests on import" % name)

import all_modules

for m in all_modules.get_modules():
    assimilate_patched(m)
