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

import torch
from transformers import pipeline, AutoTokenizer, StoppingCriteria, StoppingCriteriaList

from . import configs
from .classes import Input, Output

_tokenizer = AutoTokenizer.from_pretrained(configs.model)
_pipe = pipeline("text-generation", model=configs.model)

print(f'Model {configs.model} loaded successfully!')

# Models can have multiple token id combinations to represent a text.
# So the current stopping text implementation is experimental.
class StoppingText(StoppingCriteria):

    def __init__(self, text):
        super().__init__()
        self.tokens = self.tokenize(text)
        self.len = len(self.tokens)

    def __call__(self, input_ids: torch.LongTensor, scores: torch.FloatTensor):
        if torch.equal(self.tokens, input_ids[0][-self.len:]):
            return True

        return False

    def tokenize(self, text):
        tokens = _tokenizer(text, return_tensors=_pipe.framework, add_special_tokens=False)['input_ids'][0] # type: ignore
        if _tokenizer.decode(tokens[0].item()) == '':
            # Remove starting empty tokens if any
            tokens = tokens[1:]
        return tokens.to(_pipe.device)

def generator(input: Input) -> Output:
    stopping_criteria = StoppingCriteriaList([StoppingText(input.stopping_text)]) if input.stopping_text else None
    response = _pipe(
        input.prompt,
        stopping_criteria=stopping_criteria,
        temperature=0.0000001,
        num_return_sequences=1,
        max_new_tokens=configs.max_new_tokens,
        pad_token_id=_tokenizer.eos_token_id,
        return_full_text=False,
    )
    inference: str = response[0]['generated_text'] # type: ignore
    return Output(inference)
