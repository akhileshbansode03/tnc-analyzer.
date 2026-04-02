import faiss
import numpy as np

class VectorStore:
    def __init__(self, dimension: int):
        """
        Initialize FAISS index
        """
        self.dimension = dimension
        self.index = faiss.IndexFlatL2(dimension)
        self.text_chunks = []

    def add(self, embeddings, chunks):
        """
        Add embeddings and corresponding text chunks
        """
        vectors = np.array(embeddings).astype("float32")
        self.index.add(vectors)
        self.text_chunks.extend(chunks)

    def search(self, query_embedding, k=3):
        """
        Search for top-k similar chunks
        """
        query_vector = np.array([query_embedding]).astype("float32")

        distances, indices = self.index.search(query_vector, k)

        results = []
        for idx in indices[0]:
            if idx < len(self.text_chunks):
                results.append(self.text_chunks[idx])

        return results