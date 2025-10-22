import os
import boto3
from strands import Agent, Tool
from aws_lambda_powertools import Logger

logger = Logger()

# Initialize Bedrock client
bedrock_client = boto3.client('bedrock-runtime', region_name='us-west-2')

# Define the security agent
agent = Agent(
    model="anthropic.claude-sonnet-4-20250514",
    name="SecurityRunbookAgent",
    instruction="""You are an expert SOC Tier-1 security analyst agent.

Your responsibilities:
1. Analyze incoming security alerts
2. Enrich indicators of compromise (IoCs) with threat intelligence
3. Determine appropriate response actions
4. Execute approved remediation steps
5. Document all actions for audit trails

Always explain your reasoning step-by-step.
For HIGH or CRITICAL severity alerts, request human approval before taking action.
Maintain detailed logs of all decisions and actions.""",
)

# Define tools the agent can use
@Tool(agent)
def enrich_threat_intel(indicator: str, indicator_type: str) -> dict:
    """
    Enriches an indicator with threat intelligence data.
    
    Args:
        indicator: The IoC to enrich (IP, domain, or hash)
        indicator_type: Type of indicator (ip, domain, or hash)
    
    Returns:
        Threat intelligence report with reputation and confidence
    """
    logger.info(f"Tool called: enrich_threat_intel({indicator}, {indicator_type})")
    
    # Call Lambda function
    lambda_client = boto3.client('lambda', region_name='us-west-2')
    response = lambda_client.invoke(
        FunctionName='security-agent-enrichment',
        InvocationType='RequestResponse',
        Payload=json.dumps({
            "indicator": indicator,
            "type": indicator_type
        })
    )
    
    result = json.loads(response['Payload'].read())
    return json.loads(result['body'])

@Tool(agent)
def classify_severity(alert_data: dict, enrichment_data: dict) -> dict:
    """
    Classifies alert severity based on alert and enrichment data.
    
    Args:
        alert_data: Original alert information
        enrichment_data: Threat intelligence enrichment results
    
    Returns:
        Severity classification with reasoning
    """
    logger.info("Tool called: classify_severity")
    
    lambda_client = boto3.client('lambda', region_name='us-west-2')
    response = lambda_client.invoke(
        FunctionName='security-agent-triage',
        InvocationType='RequestResponse',
        Payload=json.dumps({
            "alert": alert_data,
            "enrichment": enrichment_data
        })
    )
    
    result = json.loads(response['Payload'].read())
    return json.loads(result['body'])

@Tool(agent)
def request_quarantine_approval(target: str, severity: str, reason: str) -> bool:
    """
    Requests human approval for quarantine action.
    
    Args:
        target: IP address or hostname to quarantine
        severity: Alert severity level
        reason: Justification for quarantine
    
    Returns:
        True if approved (simulated for demo)
    """
    logger.info(f"Tool called: request_quarantine_approval({target}, {severity})")
    
    # In production, this would trigger Step Functions HIL
    # For demo, simulate approval for HIGH/CRITICAL
    if severity in ["HIGH", "CRITICAL"]:
        logger.info(f"Approval request sent for {target}")
        return True  # Demo mode: auto-approve
    return True

@Tool(agent)
def execute_quarantine(target_ip: str, reason: str) -> dict:
    """
    Executes host quarantine using AgentCore Browser Tool.
    
    Args:
        target_ip: IP address to quarantine
        reason: Reason for quarantine
    
    Returns:
        Execution result with audit trail
    """
    logger.info(f"Tool called: execute_quarantine({target_ip})")
    
    lambda_client = boto3.client('lambda', region_name='us-west-2')
    response = lambda_client.invoke(
        FunctionName='security-agent-browser-executor',
        InvocationType='RequestResponse',
        Payload=json.dumps({
            "action": "quarantine",
            "parameters": {
                "target_ip": target_ip,
                "reason": reason
            }
        })
    )
    
    result = json.loads(response['Payload'].read())
    return json.loads(result['body'])

# Main agent invocation function
def analyze_security_alert(alert: dict) -> dict:
    """
    Main function to analyze and respond to security alerts.
    """
    logger.info("Analyzing security alert", extra={"alert": alert})
    
    # Construct prompt for agent
    prompt = f"""Analyze this security alert and take appropriate action:

Alert ID: {alert.get('alert_id')}
Type: {alert.get('type')}
Source IP: {alert.get('source_ip')}
Indicators: {alert.get('indicators', {})}
Timestamp: {alert.get('timestamp')}

Please:
1. Enrich the source IP with threat intelligence
2. Classify the severity
3. Determine if quarantine is needed
4. If HIGH/CRITICAL, request approval and execute quarantine
5. Provide a summary of actions taken"""

    # Invoke agent
    response = agent(prompt)
    
    logger.info("Agent response generated", extra={"response": str(response)})
    
    return {
        "alert_id": alert.get('alert_id'),
        "reasoning": response.thinking if hasattr(response, 'thinking') else str(response),
        "actions_taken": response.actions if hasattr(response, 'actions') else [],
        "resolution": str(response),
    }

if __name__ == "__main__":
    # Test with sample alert
    test_alert = {
        "alert_id": "SEC-2025-001",
        "type": "MALWARE_DETECTED",
        "source_ip": "192.168.1.100",
        "indicators": {
            "file_hash": "d41d8cd98f00b204e9800998ecf8427e",
            "domain": "malicious-site.com"
        },
        "timestamp": "2025-10-18T12:00:00Z"
    }
    
    result = analyze_security_alert(test_alert)
    print(json.dumps(result, indent=2))
