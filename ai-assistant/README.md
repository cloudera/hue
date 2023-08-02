# Hue AI Assistant

## Dependency

- Python 3.9 or higher

## Running Hue AI Assistant

1. Configure in `./server/configs.json`. Default values are as follows.
```
{
  "model": "gpt2", # Huggingface model name
  "max_new_tokens": 100
}
```

2. Activate python environment. Python 3.9 or higher should be available.
```
source ./activate.sh
```
This would activate a virtual python environment with the dependencies. Once the server is finished running, make sure the environment is deactivated with the following command.
```
deactivate
```

3. Start server
```
uvicorn main:app --reload
```
Hue AI Server should now be available at http://localhost:8000

Start with `--log-level trace` option to get all logs

### Inferance API
- Path: /api/v1/infer
- Method: POST
- Payload:
```
{
  "prompt": "<prompt_text>"
}
```

### Development Notes
requirements.txt should be updated after adding a new pip dependency.
```
pip freeze > requirements.txt
```
