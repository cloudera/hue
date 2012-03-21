# Copyright 2008 Lime Nest LLC
# Copyright 2008 Lime Spot LLC

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from setuptools import setup
import hgvers

setup(
    name = "urllib2_kerberos",
    version = hgvers.version,
    py_modules = [ 'urllib2_kerberos' ],

#    install_requires = ['kerberos'],

    author = "Tim Olsen",
    author_email = "tolsen@limespot.com",
    description = "Kerberos over HTTP Negotiate/SPNEGO support for urllib2",
    license = "Apache 2.0",
    url = "http://limedav.com/hg/urllib2_kerberos/",
    keywords = "urllib2 kerberos http negotiate spnego",
    
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: System :: Systems Administration :: Authentication/Directory'
        ]
    
    )

