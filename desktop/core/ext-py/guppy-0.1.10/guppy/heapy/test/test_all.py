import sys

autotests = (
        'dependencies',
        'Classifiers',
	'heapyc',
	'ER',
	'OutputHandling',
	'Part',
	'Path',
	'RefPat',
	'UniSet',
	'View',
	)
	
# These are not tested here

others = (
    'menuleak',
    'sf',
    )

def test_main(debug=False):
    for name in autotests:
	testname = 'guppy.heapy.test.test_'+name
	try:
	    del sys.modules[testname]
	except KeyError:
	    pass
	exec 'import %s as x'%testname
	print 'imported:', testname
	f = x.test_main
	f(debug=debug)
	del sys.modules[testname]

if __name__=='__main__':
    test_main()
