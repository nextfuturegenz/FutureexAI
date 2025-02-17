import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

class RAGRetriever:
    def __init__(self, knowledge_data, embed_model_name="sentence-transformers/all-MiniLM-L6-v2"):
        self.embed_model = SentenceTransformer(embed_model_name)
        self.knowledge_data = knowledge_data
        embeddings = np.array([self.embed_model.encode(text) for text in knowledge_data])
        self.dimension = embeddings.shape[1]
        self.index = faiss.IndexFlatL2(self.dimension)
        self.index.add(embeddings)

    def retrieve(self, query, top_k=1):
        query_embedding = self.embed_model.encode([query])
        distances, indices = self.index.search(query_embedding, top_k)
        return [self.knowledge_data[i] for i in indices[0]]
