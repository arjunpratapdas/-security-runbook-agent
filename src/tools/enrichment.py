import json

def lambda_handler(event, context):
    """Enriches IoCs with threat intelligence"""
    print(f"Enrichment Lambda invoked with event: {event}")
    
    indicator = event.get("indicator", "")
    indicator_type = event.get("type", "ip")
    
    if not indicator:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "No indicator provided"})
        }
    
    # Mock threat intelligence data for demo
    threat_data = {
        "ip": {
            "192.168.1.100": {
                "reputation": "suspicious",
                "confidence": 0.65,
                "category": "C2_server"
            },
            "10.0.0.50": {
                "reputation": "malicious",
                "confidence": 0.92,
                "category": "malware_host"
            },
        },
        "domain": {
            "malicious-site.com": {
                "reputation": "malicious",
                "confidence": 0.98,
                "category": "phishing"
            },
        },
        "hash": {
            "d41d8cd98f00b204e9800998ecf8427e": {
                "reputation": "malicious",
                "confidence": 0.88,
                "category": "ransomware"
            },
        }
    }
    
    # Get reputation data
    lookup_dict = threat_data.get(indicator_type, {})
    reputation_data = lookup_dict.get(indicator, {
        "reputation": "unknown",
        "confidence": 0.0,
        "category": "unknown"
    })
    
    result = {
        "indicator": indicator,
        "type": indicator_type,
        "reputation": reputation_data["reputation"],
        "confidence": reputation_data["confidence"],
        "category": reputation_data["category"],
        "sources": ["Mock Threat Intel DB"]
    }
    
    print(f"Enrichment result: {result}")
    
    return {
        "statusCode": 200,
        "body": json.dumps(result)
    }
