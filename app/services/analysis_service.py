from app.db.vector_store import VectorStore
from app.models.schemas import AnalyzeResponse, ClauseAnalysis, RiskOverview
from app.services.analyzer import analyze_clauses
from app.services.chunking import chunk_text
from app.services.embedding import get_embeddings
from app.services.llm_service import generate_summary
from app.services.output_formatter import format_output
from app.services.parser import extract_text


def _build_clause_models(analysis):
    clauses = []

    for chunk_id, item in enumerate(analysis):
        clauses.append(
            ClauseAnalysis(
                chunk_id=chunk_id,
                clause=item["clause"],
                category=item["category"],
                risk=item["risk"],
                reason=item["reason"],
            )
        )

    return clauses


def _build_risk_overview(analysis) -> RiskOverview:
    risk_count = {"HIGH": 0, "MEDIUM": 0, "LOW": 0}

    for item in analysis:
        risk_count[item["risk"]] += 1

    return RiskOverview(
        high=risk_count["HIGH"],
        medium=risk_count["MEDIUM"],
        low=risk_count["LOW"],
    )


def analyze_document(file_path: str):
    text = extract_text(file_path)
    chunks = chunk_text(text)

    if not chunks:
        raise ValueError("No text could be extracted from the uploaded document.")

    embeddings = get_embeddings(chunks)

    vector_store = VectorStore(dimension=len(embeddings[0]))
    vector_store.add(embeddings, chunks)

    analysis = analyze_clauses(chunks)
    summary = generate_summary(chunks)
    formatted_output = format_output(summary, analysis)

    response = AnalyzeResponse(
        document_id="",
        summary=summary,
        risk_overview=_build_risk_overview(analysis),
        clauses=_build_clause_models(analysis),
        formatted_output=formatted_output,
    )

    return response, vector_store, chunks
