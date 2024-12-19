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

from typing import List

from sentence_transformers import SentenceTransformer, util
import torch
import re

from desktop.lib.utils.cache import LRUCache
from desktop.conf import SEMANTIC_SEARCH


TOP_K = SEMANTIC_SEARCH.TOP_K.get()
CACHE_SIZE = SEMANTIC_SEARCH.CACHE_SIZE.get()
EMBEDDING_MODEL = SEMANTIC_SEARCH.EMBEDDING_MODEL.get()


_embedder: SentenceTransformer = None
def encode(sentences: List[str]):
  global _embedder
  if not _embedder:
    _embedder = SentenceTransformer(EMBEDDING_MODEL)

  return _embedder.encode(sentences, convert_to_tensor=True)


# Could create a similar cache for query, but might be an overkill
_corpus_cache = LRUCache(CACHE_SIZE)
def _get_cached_embeddings(corpus):
  embedding_dict = {}
  new_sentences = []
  for sentence in corpus:
    embedding = _corpus_cache.get(sentence)
    if embedding != None:
      embedding_dict[sentence] = embedding
    else:
      new_sentences.append(sentence)

  if new_sentences:
    sentence_embeddings = encode(new_sentences)
    for idx, embedding in enumerate(sentence_embeddings):
      sentence = new_sentences[idx]
      embedding_dict[sentence] = embedding
      _corpus_cache.put(sentence, embedding)

  embeddings = []
  for sentence in corpus:
    embeddings.append(embedding_dict[sentence])

  return torch.stack(embeddings)


def _get_words(text) -> list:
  words = re.findall(r'\b\w+\b', text)
  # Remove 1 or 2 letter words
  words = list(filter(lambda w : len(w) >= 3, words))
  return list(set(words))

# Perform semantic search on the corpus using the provided query
def semantic_search(corpus, query, limit = TOP_K):
  if len(corpus) < limit:
    return corpus

  corpus = list(set(corpus))
  k = min(len(corpus), limit)

  corpus_embeddings = _get_cached_embeddings(corpus)

  # Calculating embeddings for queries and each words, as embeddings can get lost in
  query_embeddings = encode([query] + _get_words(query))
  cos_scores = util.cos_sim(query_embeddings, corpus_embeddings)

  scores_dict = {}
  distances, indexes = torch.topk(cos_scores[0], k)
  for i, dist in enumerate(distances):
    scores_dict[indexes[i].item()] = dist.item()

  for scores in cos_scores[1:]:
    dist, index = torch.topk(scores, 1)
    idx = index.item()
    scores_dict[idx] = max(scores_dict[idx], dist.item()) if idx in scores_dict else dist.item()

  scores = sorted(scores_dict.items(), key=lambda score: score[1], reverse=True)[:k]

  results = []
  for idx, dist in scores:
    results.append(corpus[idx])

  return results
