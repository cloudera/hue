# Copyright (c) 2008, Donovan Preston
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to
# deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import commands
import os
import optparse
import signal
import sys
import time


MEMORY_WATCH_INTERVAL = 60


def watch_memory(controller_pid, max_memory, max_age):
    if max_age:
        end_time = time.time() + max_age
    else:
        end_time = None

    process_group = os.getpgrp()
    while True:
        if max_age:
            now = time.time()
            if now + MEMORY_WATCH_INTERVAL > end_time:
                time.sleep(end_time - now)
                print "(%s) *** watcher restarting processes! Time limit exceeded." % (
                    os.getpid(), )
                os.kill(controller_pid, signal.SIGHUP)
                end_time = time.time() + max_age
                continue

        time.sleep(MEMORY_WATCH_INTERVAL)
        if max_memory:
            out = commands.getoutput('ps -o rss -g %s' % (process_group, ))
            used_mem = sum(int(x) for x in out.split('\n')[1:])
            if used_mem > max_memory:
                print "(%s) *** memory watcher restarting processes! Memory usage of %s exceeded %s." % (
                    os.getpid(), used_mem, max_memory)
                os.kill(controller_pid, signal.SIGHUP)


if __name__ == '__main__':
    parser = optparse.OptionParser(
        description="Watch all the processes in the process group"
        " and if the total memory used goes over a configurable amount, send a SIGHUP"
        " to a given pid.")
    parser.add_option('-a', '--max-age', dest='max_age', type='int',
        help='If given, the maximum amount of time (in seconds) to run before sending a  '
            'SIGHUP to the given pid.')

    options, positional_args = parser.parse_args()

    if len(positional_args) < 2:
        parser.error("Usage: %s controller_pid max_memory_in_megabytes")

    controller_pid = int(positional_args[0])
    max_memory = int(positional_args[1])
    if max_memory:
        info = 'memory to %s' % (max_memory, )
    else:
        info = ''

    if options.max_age:
        if info:
            info += ' and'
        info = " time to %s" % (options.max_age, )

    print "(%s) watcher starting up, limiting%s." % (
        os.getpid(), info)

    try:
        watch_memory(controller_pid, max_memory, options.max_age)
    except KeyboardInterrupt:
        pass
