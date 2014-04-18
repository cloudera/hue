
# This is to see that the total memory usage doesn't increase with time
# i.e. no leakage / link between consecutive usages of hsp.
# This will run for ever, to be monitored by the printout and some external monitor.

def t():
    from guppy import hsp
    while 1:
	import guppy.heapy.UniSet
	import gc
	reload( guppy.heapy.UniSet )
	hp = hsp()
	x = None
	x = hp.heap()
	print x
	gc.collect()
	print x[0]
	print x[1]
	print x[2]
	gc.collect()
	print x&dict

