from app.services.parser import extract_text
from app.services.chunking import chunk_text
from app.services.embedding import get_embeddings
from app.db.vector_store import VectorStore
from app.services.rag import RAGService
from app.services.llm_service import generate_summary, simplify_clause

# Step 1: Extract text
text = extract_text("data/uploads/sbi personal loan.pdf")

# Step 2: Chunking
chunks = chunk_text(text)

# Step 3: Embeddings
embeddings = get_embeddings(chunks)

# Step 4: Vector Store
vector_store = VectorStore(dimension=len(embeddings[0]))
vector_store.add(embeddings, chunks)

# Step 5: RAG
rag = RAGService(vector_store)

# -------------------------------
# TEST 1: Retrieval
# -------------------------------
print("\n--- RETRIEVAL TEST ---\n")

query = "What is the interest rate?"
print(rag.answer(query))

# -------------------------------
# TEST 2: Summary
# -------------------------------
print("\n--- SUMMARY TEST ---\n")

summary = generate_summary(chunks)
print(summary)

# -------------------------------
# TEST 3: Simplify Clause
# -------------------------------
print("\n--- SIMPLIFY CLAUSE ---\n")

relevant_chunk = rag.retrieve("interest rate")[0]
explanation = simplify_clause(relevant_chunk)

print(explanation)