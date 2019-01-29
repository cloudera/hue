#!/usr/bin/env python
# Licensed to Cloudera, Inc. under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  Cloudera, Inc. licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import time
import re

class Timer:
    def __enter__(self):
        self.start = time.clock()
        return self

    def __exit__(self, *args):
        self.end = time.clock()
        self.interval = self.end - self.start


def parse_exec_summary(summary_string):
    """Given an exec summary string parses the rows and organizes it by node id"""
    cleaned = [re.sub(r'^[-|\s]+', "", m)
               for m in summary_string.split("\n")[3:]]
    cleaned = map(
        lambda x: map(
            lambda y: y.strip(),
            re.split(
                '\s\s+',
                x,
                maxsplit=8)),
        cleaned)
    result = {}
    for c in cleaned:
        # Key 0 is id and type
        fid, ftype = c[0].split(":")
        if len(c) < 9:
          index_bytes = False
          for i in range(len(c) - 1, 0, -1):
            if re.search('\d*.?b', c[i], re.IGNORECASE):
              index_bytes = i
          if index_bytes:
            c.insert(index_bytes, '')
            c.insert(index_bytes, '')
          else:
            c.append('')
            c.append('')
        if re.search('F\d*', fid):
          cleaned_fid = fid
        else:
          cleaned_fid = int(fid)
        result[cleaned_fid] = {
            "type": ftype,
            "hosts": int(c[1]),
            "avg": c[2],
            "max": c[3],
            "rows": c[4],
            "est_rows": c[5],
            "peak_mem": c[6],
            "est_mem": c[7],
            "detail": c[8],
            "broadcast": "BROADCAST" in c[8],
            "has_stats": "-1" in "est_rows"
        }
    return result


def parse_plan_details(plan_string):
    """Given a query plan, extracts the query details per node"""
    result = {}
    last_id = -1
    for line in plan_string.split("\n"):
        match = re.search(r'(?!F)[|-]?(\d+):.*?\[(.*?)\]', line.strip())
        if match:
          last_id = str(int(match.group(1)))
          result[last_id] = {'detail': match.group(2)}
        elif result.get(last_id):
          match = re.search(r'[\|\s]*(.*?):\s?(.*)', line.strip())
          if match:
            result[last_id][match.group(1)] = match.group(2)

    return result
