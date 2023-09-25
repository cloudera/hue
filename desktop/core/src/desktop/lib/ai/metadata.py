from sentence_transformers import SentenceTransformer, util
import torch
import re

from ..utils.cache import LRUCache
from desktop.conf import SEMANTIC_SEARCH

_embedding_model = SEMANTIC_SEARCH.EMBEDDING_MODEL.get()
corpus_cache = LRUCache(SEMANTIC_SEARCH.CACHE_SIZE.get())
# Could create a similar cache for query, but might be an overkill

def _get_cached_embeddings(embedder, corpus):
    embedding_dict = {}
    new_sentences = []
    for sentence in corpus:
        embedding = corpus_cache.get(sentence)
        if embedding != None:
            embedding_dict[sentence] = embedding
        else:
            new_sentences.append(sentence)

    if new_sentences:
      sentence_embeddings = embedder.encode(new_sentences, convert_to_tensor=True)
      for idx, embedding in enumerate(sentence_embeddings):
          sentence = new_sentences[idx]
          embedding_dict[sentence] = embedding
          corpus_cache.put(sentence, embedding)

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
def semantic_search(corpus, query, limit = 10):
    if len(corpus) < limit:
        return corpus

    corpus = list(set(corpus))
    k = min(len(corpus), limit)
    embedder = SentenceTransformer(_embedding_model)

    corpus_embeddings = _get_cached_embeddings(embedder, corpus)

    # Calculating embeddings for queries and each words, as embeddings can get lost in
    query_embeddings = embedder.encode([query] + _get_words(query), convert_to_tensor=True)
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
