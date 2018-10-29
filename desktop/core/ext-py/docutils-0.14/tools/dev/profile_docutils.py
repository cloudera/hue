#!/usr/bin/python -i

# $Id: profile_docutils.py 7442 2012-06-13 23:27:03Z milde $
# Author: Lea Wiemann <LeWiemann@gmail.com>
# Copyright: This script has been placed in the public domain.

import os.path
import docutils.core
import hotshot.stats

print('Profiler started.')

os.chdir(os.path.join(os.path.dirname(docutils.__file__), '..'))

print('Profiling...')

prof = hotshot.Profile('docutils.prof')
prof.runcall(docutils.core.publish_file, source_path='HISTORY.txt',
             destination_path='prof.HISTORY.html', writer_name='html')
prof.close()

print('Loading statistics...')

print("""
stats = hotshot.stats.load('docutils.prof')
stats.strip_dirs()
stats.sort_stats('time')  # 'cumulative'; 'calls'
stats.print_stats(40)
""")

stats = hotshot.stats.load('docutils.prof')
stats.strip_dirs()
stats.sort_stats('time')
stats.print_stats(40)

try:
    exec(open(os.environ['PYTHONSTARTUP']).read())
except:
    pass
