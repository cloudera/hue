import os
import json

def _load_configs(file_path):
    with open(file_path, "r") as f:
        return json.load(f)

server_dir = os.path.dirname(__file__)
_configs = _load_configs(f'{server_dir}/configs.json')

model_paths = _configs["model_paths"]
