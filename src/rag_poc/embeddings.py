import google.generativeai as genai
import numpy as np
from rag_poc.config import GEMINI_API_KEY, EMBEDDING_MODEL

genai.configure(api_key=GEMINI_API_KEY)

def normalize_vector(vec):
    length = np.linalg.norm(vec)
    if length == 0:
        return vec
    return vec / length

def get_text_embeddings(text_list):
    result = genai.embed_content(
        model=EMBEDDING_MODEL,
        content=text_list,
        task_type="retrieval_document"
    )

    embeddings = result["embedding"]

    if embeddings and isinstance(embeddings[0], (int, float)):
        embeddings = [embeddings]

    embeddings_array = np.array(embeddings, dtype=np.float32)

    norms = np.linalg.norm(embeddings_array, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    normalized = embeddings_array / norms

    return normalized

def get_query_embedding(query_text):
    result = genai.embed_content(
        model=EMBEDDING_MODEL,
        content=query_text,
        task_type="retrieval_query"
    )

    embedding = np.array(result["embedding"], dtype=np.float32)
    normalized = normalize_vector(embedding)

    return normalized
