import json

def lambda_handler(event, context):
    # Extract input
    alert = event.get("alert", {})
    enrichment = event.get("enrichment", {})

    # Compute score
    score = 0
    if enrichment.get("reputation") == "malicious":
        score += 50
    elif enrichment.get("reputation") == "suspicious":
        score += 30
    score += enrichment.get("confidence", 0) * 30
    if score >= 80:
        severity, requires_approval = "CRITICAL", True
    elif score >= 60:
        severity, requires_approval = "HIGH", True
    elif score >= 40:
        severity, requires_approval = "MEDIUM", False
    else:
        severity, requires_approval = "LOW", False

    # Return plain JSON object
    return {
        "severity": severity,
        "score": score,
        "requires_approval": requires_approval
    }
