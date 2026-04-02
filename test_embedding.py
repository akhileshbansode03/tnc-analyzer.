from app.services.parser import extract_text
from app.services.chunking import chunk_text
from app.services.embedding import get_embeddings

# Step 1: Extract text from PDF
text = extract_text("data/uploads/sbi personal loan.pdf")

# Step 2: Split into chunks
chunks = chunk_text(text)

# Step 3: Generate embeddings
embeddings = get_embeddings(chunks)

# -------------------------------
# ✅ VALIDATION CHECKS
# -------------------------------

# 1. Count check
print("Chunks:", len(chunks))
print("Embeddings:", len(embeddings))

if len(chunks) == len(embeddings):
    print("✅ Count match")
else:
    print("❌ Count mismatch")

# 2. Vector length check
if len(embeddings) > 0:
    print("Vector length:", len(embeddings[0]))

    if len(embeddings[0]) == 384:
        print("✅ Correct vector size (384)")
    else:
        print("❌ Unexpected vector size")
else:
    print("❌ No embeddings generated")

# 3. Debug preview (VERY IMPORTANT)
if len(chunks) > 0 and len(embeddings) > 0:
    print("\n--- Debug Preview ---")
    print("First chunk:", chunks[0])
    print("First embedding sample:", embeddings[0][:5])
else:
    print("❌ Cannot preview (empty data)")

# 4. Final status
print("\n✅ Pipeline executed without crash")