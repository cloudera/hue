#._cv_part guppy

"""\
Top level package of Guppy, a library and programming environment
currently providing in particular the Heapy subsystem, which supports
object and heap memory sizing, profiling and debugging.

What is exported is the following:

hpy()	Create an object that provides a Heapy entry point.
Root()	Create an object that provides a top level entry point.

"""

__all__ = ('hpy', 'Root')

import guppy.etc.Compat			# Do one-time compatibility adjustments
from guppy.etc.Glue import Root		# Get main Guppy entry point

def hpy(ht = None):
    """\
Main entry point to the Heapy system.
Returns an object that provides a session context and will import
required modules on demand. Some commononly used methods are:

.heap() 		get a view of the current reachable heap
.iso(obj..) 	get information about specific objects 

The optional argument, useful for debugging heapy itself, is:

    ht     an alternative hiding tag

"""
    r = Root()
    if ht is not None:
	r.guppy.heapy.View._hiding_tag_ = ht
    return r.guppy.heapy.Use

