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

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from core.classes import Input, Output
from core.configs import model
from core.scheduler import Scheduler

from utils.docs import init_docs

app = FastAPI()
scheduler = Scheduler()

@app.exception_handler(Exception)
async def validation_exception_handler(request, err):
    return JSONResponse(status_code=500, content={"error": f"{err}"})

@app.on_event("startup")
def startup():
    print("Starting scheduler")
    scheduler.start()

@app.on_event("shutdown")
def shutdown():
    print("Stoping scheduler")
    scheduler.stop()

# --- APIs ----------------------------------------------------------

@app.get("/")
def default():
    return {
        "service": "AI Assistant",
        "model": model
    }

@app.post("/api/infer")
async def infer(input: Input) -> Output:
    return await scheduler.process(input)

# --- APIs ----------------------------------------------------------

# Must come after API section
init_docs(app)
