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

from transformers import pipeline, AutoTokenizer
from dataclasses import dataclass

from .configs import model, max_new_tokens

@dataclass
class Inference:
    inference: str

_tokenizer = AutoTokenizer.from_pretrained(model)
_pipe = pipeline("text-generation", model=model)

print(f'Model {model} loaded successfully!')

def generator(prompt: str) -> Inference:
    response = _pipe(
        prompt,
        max_new_tokens=max_new_tokens,
        pad_token_id=_tokenizer.eos_token_id,
        return_full_text=False,
    )
    return Inference(response[0]['generated_text'])
