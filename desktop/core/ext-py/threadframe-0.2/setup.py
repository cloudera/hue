from distutils.core import setup
from distutils.extension import Extension

setup(
    name        = 'threadframe',
    version     = '0.2',
    description = "Advanced thread debugging extension",
    long_description = "Obtaining tracebacks on other threads than the current thread",
    url         = 'http://www.majid.info/mylos/stories/2004/06/10/threadframe.html',
    maintainer  = 'Fazal Majid',
    maintainer_email = 'threadframe@majid.info',
    license     = 'Python',
    platforms   = [],
    keywords    = ['threading', 'thread'],

    ext_modules=[
        Extension('threadframe',
            ['threadframemodule.c'],
        ),
    ],
)
