#
# Copyright 2013 Metamarkets Group Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import csv
import codecs
import six
# A special CSV writer which will write rows to TSV file "f", which is encoded in utf-8.
# this is necessary because the values in druid are not all ASCII.


class UnicodeWriter(object):

    # delimiter="\t"
    def __init__(self, f, dialect="excel-tab", encoding="utf-8", **kwds):
        self.stream = f
        self.writer = csv.writer(self.stream, dialect=dialect, **kwds)
        self.encoder = codecs.getincrementalencoder(encoding)()

    def __encode(self, data):
        data = str(data) if isinstance(data, six.integer_types) else data
        if not six.PY3:
            data = data.encode('utf-8') \
                if isinstance(data, unicode) else data  # noqa
            data = data.decode('utf-8')
            return self.encoder.encode(data)
        return data

    def writerow(self, row):
        row = [self.__encode(s) for s in row]
        self.writer.writerow(row)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)
