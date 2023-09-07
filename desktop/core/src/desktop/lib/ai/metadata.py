from sentence_transformers import SentenceTransformer, util
import torch

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
          embedding_dict[new_sentences[idx]] = embedding
          corpus_cache.put(sentence, embedding)

    embeddings = []
    for sentence in corpus:
        embeddings.append(embedding_dict[sentence])

    return torch.stack(embeddings)

# Perform semantic search on the corpus using the provided query
def semantic_search(corpus, query):
    embedder = SentenceTransformer(_embedding_model)
    query_embedding = embedder.encode(query, convert_to_tensor=True)
    corpus_embeddings = _get_cached_embeddings(embedder, corpus)

    cos_scores = util.cos_sim(query_embedding, corpus_embeddings)[0]
    top_results = torch.topk(cos_scores, k=min(len(corpus), 10))

    results = []
    for idx in top_results[1]:
        results.append(corpus[idx])

    return results
