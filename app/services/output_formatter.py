def format_output(summary, analysis):
    from app.services.llm_service import explain_simple

    output = ""

    # -----------------------
    # SUMMARY
    # -----------------------
    output += "📄 SUMMARY:\n"
    output += summary + "\n\n"

    # -----------------------
    # RISK OVERVIEW
    # -----------------------
    output += "📊 RISK OVERVIEW:\n"

    risk_count = {"HIGH": 0, "MEDIUM": 0, "LOW": 0}

    for item in analysis:
        risk_count[item["risk"]] += 1

    output += f"🔴 High: {risk_count['HIGH']}\n"
    output += f"🟡 Medium: {risk_count['MEDIUM']}\n"
    output += f"🟢 Low: {risk_count['LOW']}\n\n"

    # -----------------------
    # TOP RISKS
    # -----------------------
    output += "⚠️ TOP RISKS:\n"

    count = 0
    seen_reasons = set()

    for item in analysis:
        if item["risk"] == "HIGH" and count < 3:

            if item["reason"] in seen_reasons:
                continue

            seen_reasons.add(item["reason"])
            count += 1

            output += f"\n🔴 {item['category'].upper()} RISK\n"
            output += f"Risk: {item['reason']}\n"

            clause_preview = item["clause"][:120].replace("\n", " ")
            output += f"Where: \"{clause_preview}...\"\n"

            simple = explain_simple(
                item["clause"],
                reason=item["reason"],
                category=item["category"]
            )

            output += f"Meaning: {simple}\n"

    return output