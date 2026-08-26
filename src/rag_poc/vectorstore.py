import faiss
import json
from rag_poc.config import INDEX_FILE, METADATA_FILE, TOP_K
from rag_poc.embeddings import get_text_embeddings, get_query_embedding

class VectorStore:
    def __init__(self):
        self.index = None
        self.metadata = []

    def build_index(self, chunks):
        print("Building index...")

        text_list = []
        for chunk in chunks:
            text_list.append(chunk["text"])

        embeddings = get_text_embeddings(text_list)

        dimension = embeddings.shape[1]
        self.index = faiss.IndexFlatIP(dimension)
        self.index.add(embeddings)

        self.metadata = chunks

        self.save_index()
        print("Index saved!")

    def save_index(self):
        INDEX_FILE.parent.mkdir(parents=True, exist_ok=True)

        faiss.write_index(self.index, str(INDEX_FILE))

        metadata_json = json.dumps(self.metadata, indent=2)
        METADATA_FILE.write_text(metadata_json)

    def load_index(self):
        if not INDEX_FILE.exists() or not METADATA_FILE.exists():
            return False

        self.index = faiss.read_index(str(INDEX_FILE))

        metadata_text = METADATA_FILE.read_text()
        self.metadata = json.loads(metadata_text)

        return True

    def search(self, query_text, k=TOP_K):
        if self.index is None:
            raise ValueError("Index not loaded")

        query_embedding = get_query_embedding(query_text)
        query_embedding = query_embedding.reshape(1, -1)

        scores, indices = self.index.search(query_embedding, k)

        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < 0:
                continue

            metadata = self.metadata[idx]
            result = {
                "text": metadata["text"],
                "file": metadata["file"],
                "location": metadata["location"],
                "score": float(score)
            }
            results.append(result)

        return results
