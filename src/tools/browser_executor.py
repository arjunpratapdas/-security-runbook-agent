import json
import os
from datetime import datetime

def lambda_handler(event, context):
    """Executes browser-based security actions"""
    print(f"Browser Executor Lambda invoked with event: {event}")
    
    action = event.get("action")
    params = event.get("parameters", {})
    
    if not action:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "No action specified"})
        }
    
    # Demo mode - simulate browser action execution
    if action == "quarantine":
        target_ip = params.get("target_ip", "unknown")
        reason = params.get("reason", "Security alert")
        
        result = {
            "success": True,
            "action": "quarantine",
            "target": target_ip,
            "reason": reason,
            "timestamp": datetime.utcnow().isoformat(),
            "session_id": f"demo-session-{context.aws_request_id[:8]}",
            "recording_url": "https://demo-recordings.s3.amazonaws.com/session-123.mp4",
            "message": f"Demo: Successfully quarantined IP {target_ip}",
            "audit_trail": [
                "Navigated to firewall console",
                f"Added {target_ip} to blocklist",
                "Saved configuration",
                "Verified IP is blocked"
            ]
        }
        
    elif action == "isolate":
        hostname = params.get("hostname", "unknown")
        result = {
            "success": True,
            "action": "isolate",
            "target": hostname,
            "timestamp": datetime.utcnow().isoformat(),
            "message": f"Demo: Successfully isolated endpoint {hostname}"
        }
        
    elif action == "block_domain":
        domain = params.get("domain", "unknown")
        result = {
            "success": True,
            "action": "block_domain",
            "target": domain,
            "timestamp": datetime.utcnow().isoformat(),
            "message": f"Demo: Successfully blocked domain {domain}"
        }
        
    else:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": f"Unknown action: {action}"})
        }
    
    print(f"Execution result: {result}")
    
    return {
        "statusCode": 200,
        "body": json.dumps(result)
    }
