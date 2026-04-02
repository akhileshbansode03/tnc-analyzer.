from app.services.parser import extract_text
from app.services.chunking import chunk_text
from app.services.embedding import get_embeddings
from app.db.vector_store import VectorStore
from app.services.rag import RAGService
from app.services.llm_service import generate_summary
from app.services.analyzer import analyze_clauses
from app.services.output_formatter import format_output

# -------------------------------
# Step 1: Extract text
# -------------------------------
text = extract_text("data/uploads/sbi personal loan.pdf")

# -------------------------------
# Step 2: Chunking
# -------------------------------
chunks = chunk_text(text)

# -------------------------------
# Step 3: Embeddings (optional here but fine)
# -------------------------------
embeddings = get_embeddings(chunks)

# -------------------------------
# Step 4: Vector store (optional for now)
# -------------------------------
vector_store = VectorStore(dimension=len(embeddings[0]))
vector_store.add(embeddings, chunks)

# -------------------------------
# Step 5: Analysis
# -------------------------------
analysis = analyze_clauses(chunks)

# -------------------------------
# Step 6: Summary
# -------------------------------
summary = generate_summary(chunks)

# -------------------------------
# Step 7: Final Output
# -------------------------------
final_output = format_output(summary, analysis)

# -------------------------------
# PRINT RESULT
# -------------------------------
print("\n--- FINAL USER OUTPUT ---\n")
print(final_output)