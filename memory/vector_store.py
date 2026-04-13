import faiss
import numpy as np
from sentence_transformers import SentenceTransformer


class VectorStore:
    def __init__(self):
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        self.index = faiss.IndexFlatL2(384)
        self.texts = []

    def add_chunks(self, chunks):
        if not chunks:
            return

        embeddings = self.model.encode(chunks)
        self.index.add(np.array(embeddings).astype("float32"))
        self.texts.extend(chunks)

    def search(self, query, k=5):
        if len(self.texts) == 0:
            return []

        emb = self.model.encode([query])

        k = min(k, len(self.texts))

        D, I = self.index.search(np.array(emb).astype("float32"), k)

        results = []
        for i in I[0]:
            if 0 <= i < len(self.texts):
                results.append(self.texts[i])

        return results