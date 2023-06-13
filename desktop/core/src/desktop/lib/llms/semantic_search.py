from sentence_transformers import SentenceTransformer, util
import torch
from desktop.conf import LLM

def filter(corpus, query):
    embedder = SentenceTransformer('all-MiniLM-L6-v2')
    corpus_embeddings = embedder.encode(corpus, convert_to_tensor=True)
    query_embedding = embedder.encode(query, convert_to_tensor=True)

    cos_scores = util.cos_sim(query_embedding, corpus_embeddings)[0]
    top_results = torch.topk(cos_scores, k=min(len(corpus), 10))

    results = []
    for idx in top_results[1]:
        results.append(corpus[idx])

    return results
