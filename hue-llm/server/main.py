from os import path
from fastapi import FastAPI, Body
from fastapi.responses import JSONResponse

from configs import model_paths

from hue_llm_interface.inferrer import inferrer_factory

server_dir = path.dirname(__file__)

app = FastAPI()

@app.exception_handler(Exception)
async def validation_exception_handler(request, err):
    return JSONResponse(status_code=500, content={"error": f"{err}"})

@app.get("/")
@app.post("/")
def read_root():
    return {"Hello": "From Hue LLM Server"}

@app.post("/api/infer")
def read_item(payload: dict = Body(...)):
    model = payload["model"]
    prompt = payload["prompt"]

    model_path = path.join(server_dir, model_paths[model])
    infer = inferrer_factory(model, model_path)
    return infer(prompt)
