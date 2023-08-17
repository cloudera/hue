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

from asyncio import Queue, create_task

from .gen import generator
from .classes import Input, Output

async def infinite_loop(in_queue: Queue):
    while True:
        (input, out_queue) = await in_queue.get()
        output = generator(input)
        await out_queue.put(output)

class Scheduler:
    def __init__(self):
        self.in_queue = Queue()

    def start(self):
        self.task = create_task(infinite_loop(self.in_queue))

    def stop(self):
        self.task.cancel()

    async def process(self, input: Input) -> Output:
        out_queue = Queue()
        await self.in_queue.put((input, out_queue))
        return await out_queue.get()
