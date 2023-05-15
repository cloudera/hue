# Hue LLM Interface & Server

This project provides a wrapper around LLMs so that they can be easily used from Hue. There are two parts to it.
1. Hue LLM Interface - hue_llm_interface
1. Hue LLM Server

**Hue LLM Interface** is a python package that encapsulates the complexities of running various LLMs supported by Hue. The interface can be used on any host infra that meets the hardware requirements of the LLM to be used.

The host infra could be:
1. CM based cluster
1. CML workspace
1. Your local machine
1. or anywhere you can start a python process.

**Hue LLM Server** on the other hand is a python application built using the Hue LLM Interface. It can be configured to use an LLM of choice and it provides a set of APIs that can be accessed from Hue. It is required as the interface cannot run on its own. The server provides a way to self-host LLMs.

## Architecture

The design keeps the Hue LLM Interface separate from the actual Hue server to cater the specific hardware needs of the LLMs. As the LLMs need custom hardware, it won't be practical to expect a Hue server machine to satisfy those needs.

## Dependency

- Python 3.9 or higher

## Running Hue LLM Server Locally

1. Download the model file into `.server/models` directory. Add the model and path to it in `./server/configs.json`.

2. Activate python environment with the requirements. Python 3.9 or higher must be available.
```
source ./activate.sh
```

3. Start server
```
uvicorn --app-dir ./server main:app
```
The api must now start runing at

### Additional dependencies for each model
LLaMA:
```
pip install llama-cpp-python
```

### Development Notes
requirements.txt must be updated after adding a new pip dependency.
```
pip freeze > requirements.txt
```
