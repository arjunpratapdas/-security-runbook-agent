import boto3
from aws_lambda_powertools import Logger

logger = Logger()
bedrock_agentcore = boto3.client('bedrock-agentcore-runtime', region_name='us-west-2')

class SecurityActionExecutor:
    def __init__(self):
        self.session_id = None

    def quarantine_host(self, target_ip: str, reason: str) -> dict:
        logger.info(f"Quarantining {target_ip}: {reason}")
        session_resp = bedrock_agentcore.create_browser_session(
            agentId='security-runbook-agent',
            sessionConfiguration={
                'recordSession': True,
                'enableScreenshots': True,
                'sessionTimeout': 300
            }
        )
        self.session_id = session_resp['sessionId']
        action_resp = bedrock_agentcore.invoke_browser_action(
            sessionId=self.session_id,
            actionInput={
                'naturalLanguageInstruction': (
                    f'Navigate to the firewall console,\n'
                    f'login, block IP {target_ip}, save changes, confirm.'
                ),
                'actionType': 'NAVIGATE_AND_INTERACT'
            }
        )
        recording = bedrock_agentcore.get_browser_session_recording(
            sessionId=self.session_id
        )
        return {
            "success": True,
            "target": target_ip,
            "action": "quarantine",
            "session_id": self.session_id,
            "recording_url": recording.get('recordingUrl'),
            "screenshot_url": action_resp.get('screenshotUrl'),
            "audit_trail": action_resp.get('actionLog'),
        }

    def cleanup(self):
        if self.session_id:
            bedrock_agentcore.delete_browser_session(
                sessionId=self.session_id
            )

def lambda_handler(event, context):
    executor = SecurityActionExecutor()
    try:
        action = event.get("action")
        params = event.get("parameters", {})
        if action == "quarantine":
            return executor.quarantine_host(
                target_ip=params["target_ip"],
                reason=params["reason"]
            )
        else:
            return {"error": "Unknown action"}
    finally:
        executor.cleanup()
