from sentence_transformers import SentenceTransformer
import numpy as np


class ToolSelector:
    def __init__(self):
        self.model = SentenceTransformer("all-MiniLM-L6-v2")

        self.tools = {
            "read_pdf": "read and extract content from pdf",
            "execute_code": "run python code",
            "read_excel": "analyze spreadsheet data"
        }

        self.embeddings = {
            k: self.model.encode(v)
            for k, v in self.tools.items()
        }

    def select(self, query):
        q_emb = self.model.encode(query)

        best = None
        best_score = -1

        for name, emb in self.embeddings.items():
            score = np.dot(q_emb, emb)

            if score > best_score:
                best_score = score
                best = name

        return best