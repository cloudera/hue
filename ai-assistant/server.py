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

import asyncio

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from core.gen import generator, Inference
from core.configs import model

app = FastAPI()

@app.exception_handler(Exception)
async def validation_exception_handler(request, err):
    return JSONResponse(status_code=500, content={"error": f"{err}"})

# --- Queue Mechanism -----------------------------------------------

async def infinite_loop(in_queue):
    while True:
        (string, out_queue) = await in_queue.get()
        inference = generator(string)
        await out_queue.put(inference)

@app.on_event("startup")
async def start():
    app.in_queue = asyncio.Queue()
    asyncio.create_task(infinite_loop(app.in_queue))

# --- APIs ----------------------------------------------------------

@app.get("/")
def default():
    return {
        "service": "AI Assistant",
        "model": model
    }

@app.post("/api/infer")
async def infer(prompt: str) -> Inference:
    out_queue = asyncio.Queue()
    await app.in_queue.put((prompt, out_queue))
    return await out_queue.get()
