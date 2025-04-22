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
#

from contextlib import contextmanager

from puresasl.client import SASLClient, SASLError


@contextmanager
def error_catcher(self, Exc=Exception):
    try:
        self.error = None
        yield
    except Exc as e:
        self.error = e.message


class PureSASLClient(SASLClient):
    def __init__(self, *args, **kwargs):
        self.error = None
        super(PureSASLClient, self).__init__(*args, **kwargs)

    def start(self, mechanism):
        with error_catcher(self, SASLError):
            if isinstance(mechanism, list):
                self.choose_mechanism(mechanism)
            else:
                self.choose_mechanism([mechanism])
            return True, self.mechanism, self.process()
        # else
        return False, mechanism, None

    def encode(self, incoming):
        with error_catcher(self):
            return True, self.unwrap(incoming)
        # else
        return False, None

    def decode(self, outgoing):
        with error_catcher(self):
            return True, self.wrap(outgoing)
        # else
        return False, None

    def step(self, challenge):
        with error_catcher(self):
            return True, self.process(challenge)
        # else
        return False, None

    def getError(self):
        return self.error
