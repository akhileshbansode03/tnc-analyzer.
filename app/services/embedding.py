# Load environment variables (for future OpenAI use)
from dotenv import load_dotenv
load_dotenv()

# Toggle: switch between local and OpenAI embeddings
USE_OPENAI = False


# -------- LOCAL EMBEDDINGS (FREE) --------
if not USE_OPENAI:
    from sentence_transformers import SentenceTransformer

    # Load model once (efficient)
    model = SentenceTransformer("all-MiniLM-L6-v2")

    def get_embeddings(text_chunks):
        text_chunks = [chunk for chunk in text_chunks if chunk.strip()]
        embeddings = model.encode(text_chunks)
        return embeddings.tolist()


# -------- OPENAI EMBEDDINGS (OPTIONAL - FUTURE) --------
else:
    from openai import OpenAI

    client = OpenAI()

    def get_embeddings(text_chunks):
        """
        Generate embeddings using OpenAI API.
        (Requires API key + billing)
        """
        embeddings = []

        for chunk in text_chunks:
            if not chunk.strip():
                continue

            response = client.embeddings.create(
                model="text-embedding-3-small",
                input=chunk
            )
            embeddings.append(response.data[0].embedding)

        return embeddings