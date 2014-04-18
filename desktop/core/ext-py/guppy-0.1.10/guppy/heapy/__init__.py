#._cv_part guppy.heapy

class _GLUECLAMP_:
    uniset_imports = ('UniSet', 'View', 'Path', 'RefPat')

    #
    # allocation_behaves_as_originally
    #
    # System configuration flag:
    # This flag, if true, indicates that memory sizes of objects are as
    # in the original system. This is checked in some tests.
    # (Disabling (or, better, generalizing) some comparisons.)
    # The original system can be characterized as:
    # Python 2.3.3 (#2, Mar 11 2004, 19:45:43) 
    # [GCC 2.95.2 20000220 (Debian GNU/Linux)] on linux2

    # This flag should be cleared on systems with different memory sizes,
    # otherwise some size-dependent tests will fail.

    import sys
    allocation_behaves_as_originally = sys.maxint==0x7fffffff

    #

    def _get_fa(self):
	us = self.UniSet
	us.out_reach_module_names = self.uniset_imports
	return us.fromargs
