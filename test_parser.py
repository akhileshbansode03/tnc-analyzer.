from app.services.parser import extract_text
from app.services.chunking import chunk_text

text = extract_text("data/uploads/sbi personal loan.pdf")
chunks = chunk_text(text)

print("Total chunks:", len(chunks))
print("First chunk:", chunks[0])