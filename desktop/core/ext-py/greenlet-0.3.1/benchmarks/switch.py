#!/usr/bin/env python

"""Switch to a greenlet, which switches back to it's parent over and over again,
and report the elapsed CPU time."""

import optparse
import time

import greenlet

def run_test(n):
    def f(*args, **kwargs):
        greenlet.getcurrent().parent.switch(*args, **kwargs)
    g = greenlet.greenlet(f)
    for i in xrange(n):
        g.switch(1, 2, 3, a=5, b=6)

if __name__ == '__main__':
    p = optparse.OptionParser(
        usage='%prog [-n NUM_SWITCHES]', description=__doc__)
    p.add_option('-n', type='int', dest='num_switches', default=10000000)
    options, args = p.parse_args()

    if len(args) != 0:
        p.error('unexpected arguments: %s' % ', '.join(args))

    start_time = time.clock()
    run_test(options.num_switches)
    print options.num_switches, 'switches:', time.clock() - start_time, 'sec'
