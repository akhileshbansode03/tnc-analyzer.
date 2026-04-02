from app.services.parser import extract_text
from app.services.chunking import chunk_text
from app.services.embedding import get_embeddings
from app.db.vector_store import VectorStore

# Load data
text = extract_text("data/uploads/sbi personal loan.pdf")
chunks = chunk_text(text)
embeddings = get_embeddings(chunks)

# Init vector store
vector_store = VectorStore(dimension=len(embeddings[0]))

# Add data
vector_store.add(embeddings, chunks)

# Query
query = "What is the interest rate?"
query_embedding = get_embeddings([query])[0]

results = vector_store.search(query_embedding)

print("\n--- Search Results ---")
for i, res in enumerate(results):
    print(f"\nResult {i+1}:\n{res}")