import os

from dotenv import load_dotenv

load_dotenv()

USE_OPENAI = os.getenv("USE_OPENAI_EMBEDDINGS", "false").lower() == "true"
_local_model = None
_openai_client = None


def _get_local_model():
    global _local_model
    if _local_model is None:
        from sentence_transformers import SentenceTransformer

        _local_model = SentenceTransformer("all-MiniLM-L6-v2")
    return _local_model


def _get_openai_client():
    global _openai_client
    if _openai_client is None:
        from openai import OpenAI

        _openai_client = OpenAI()
    return _openai_client


def get_embeddings(text_chunks):
    text_chunks = [chunk for chunk in text_chunks if chunk.strip()]
    if not text_chunks:
        return []

    if not USE_OPENAI:
        model = _get_local_model()
        embeddings = model.encode(text_chunks)
        return embeddings.tolist()

    client = _get_openai_client()
    embeddings = []
    for chunk in text_chunks:
        response = client.embeddings.create(
            model="text-embedding-3-small",
            input=chunk,
        )
        embeddings.append(response.data[0].embedding)

    return embeddings
