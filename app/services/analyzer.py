# -------------------------------
# IMPORTS
# -------------------------------

import numpy as np
from app.services.embedding import get_embeddings


# -------------------------------
# RULE-BASED KEYWORDS (CLEANED)
# -------------------------------

CATEGORIES = {
    "payment": ["payment", "emi", "interest", "repayment", "fee", "charges"],
    "liability": ["liable", "responsible", "obligation", "duty"],
    "penalty": ["penalty", "fine", "charges", "late fee", "penal"],
    "termination": ["terminate", "cancel", "close account", "end"],
    "data": ["data", "information", "privacy", "share", "disclose"],
    "general": ["purpose", "eligibility", "introduction"]
}


# -------------------------------
# CATEGORY MEANINGS (SEMANTIC)
# -------------------------------

CATEGORY_DESCRIPTIONS = {
    "payment": "Anything related to money, EMI, interest, repayment, fees, charges",
    "liability": "User responsibilities, obligations, legal responsibility",
    "penalty": "Fines, penalties, extra charges for violations or delays",
    "termination": "Ending service, closing account, cancellation",
    "data": "User data, privacy, sharing personal information",
    "general": "General information like purpose, eligibility, introduction",
}


# -------------------------------
# SEMANTIC CLASSIFICATION
# -------------------------------

def classify_semantic(clause: str):
    clause_embedding = get_embeddings([clause])[0]

    best_category = "other"
    best_score = -1

    for category, description in CATEGORY_DESCRIPTIONS.items():
        desc_embedding = get_embeddings([description])[0]

        score = np.dot(clause_embedding, desc_embedding) / (
            np.linalg.norm(clause_embedding) * np.linalg.norm(desc_embedding)
        )

        if score > best_score:
            best_score = score
            best_category = category

    return best_category


# -------------------------------
# HYBRID CLASSIFIER (FINAL FIXED)
# -------------------------------

def classify_clause(clause: str):
    clause_lower = clause.lower()

    # Step 0: force GENERAL detection
    if any(word in clause_lower for word in ["purpose", "eligibility"]):
        return "general"

    scores = {category: 0 for category in CATEGORIES}

    # Step 1: keyword scoring
    for category, keywords in CATEGORIES.items():
        for keyword in keywords:
            if keyword in clause_lower:
                scores[category] += 1

    best_category = max(scores, key=scores.get)

    # Step 2: strong keyword match
    if scores[best_category] >= 2:
        return best_category

    # Step 3: semantic fallback
    return classify_semantic(clause)


# -------------------------------
# RISK DETECTION
# -------------------------------

def detect_risk(clause: str):
    clause_lower = clause.lower()

    high_risk_keywords = [
        "may change",
        "can change",
        "at any time",
        "without notice",
        "penalty",
        "liable",
        "increase",
        "charges",
        "revision",
    ]

    medium_risk_keywords = [
        "subject to",
        "as per",
        "terms apply",
    ]

    for keyword in high_risk_keywords:
        if keyword in clause_lower:
            return "HIGH"

    for keyword in medium_risk_keywords:
        if keyword in clause_lower:
            return "MEDIUM"

    return "LOW"


# -------------------------------
# REASON GENERATION
# -------------------------------

def generate_reason(clause: str):
    clause_lower = clause.lower()

    if "interest" in clause_lower and "change" in clause_lower:
        return "Interest rate can change, affecting your EMI"

    if "penalty" in clause_lower or "charges" in clause_lower:
        return "You may be charged extra fees"

    if "liable" in clause_lower or "responsible" in clause_lower:
        return "You are legally responsible for obligations"

    if "terminate" in clause_lower or "cancel" in clause_lower:
        return "Service or agreement can be ended"

    if "data" in clause_lower or "privacy" in clause_lower:
        return "Your data may be collected or shared"

    return "General clause with standard conditions"


# -------------------------------
# MAIN ANALYSIS FUNCTION
# -------------------------------

def analyze_clauses(chunks):
    results = []

    for chunk in chunks:
        if not chunk.strip():
            continue

        category = classify_clause(chunk)
        risk = detect_risk(chunk)
        reason = generate_reason(chunk)

        results.append({
            "clause": chunk,
            "category": category,
            "risk": risk,
            "reason": reason
        })

    return results