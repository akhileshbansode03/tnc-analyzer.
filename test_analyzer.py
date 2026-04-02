from app.services.parser import extract_text
from app.services.chunking import chunk_text
from app.services.analyzer import analyze_clauses

text = extract_text("data/uploads/sbi personal loan.pdf")
chunks = chunk_text(text)

analysis = analyze_clauses(chunks)

print("\n--- CLAUSE ANALYSIS ---\n")

for i, item in enumerate(analysis[:5]):
    print(f"\nClause {i+1}:")
    print(item["clause"][:200], "...")
    print("Category:", item.get("category","N/A"))
    print("Risk:", item["risk"])
    print("Reason:", item["reason"])