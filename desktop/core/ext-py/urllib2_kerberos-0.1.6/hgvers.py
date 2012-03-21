# Copyright 2008 Lime Nest LLC

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import re

repo = None
version = None

try:
    import hgversion as hgv

except ImportError:
    # either we couldn't find hgversion or
    # hgversion couldn't find mercurial libraries
    pass
else:
    repo = hgv.repository # could be None if we're not in an hg repository

if repo is None:

    try:
        f = open('PKG-INFO')
    except IOError:
        pass
    else:
        regex = re.compile('^Version:\s+(\S+)')
        for line in f:
            mo = regex.match(line)
            if mo is not None:
                version = mo.group(1)
                break
else:
    version = hgv.version()

if __name__ == '__main__':
    print version
