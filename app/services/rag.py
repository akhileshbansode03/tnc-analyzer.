from app.services.embedding import get_embeddings


class RAGService:
    def __init__(self, vector_store):
        self.vector_store = vector_store

    def retrieve(self, query: str, k: int = 3):
        query_embedding = get_embeddings([query])[0]
        results = self.vector_store.search(query_embedding, k=k)
        return results

    def answer(self, query: str):
        """
        Grounded answer (no LLM)
        """
        results = self.retrieve(query)

        if not results:
            return "No relevant information found."

        response = "Answer (based on document):\n\n"

        for i, chunk in enumerate(results):
            response += f"Source {i+1}:\n{chunk.strip()}\n\n"

        return response