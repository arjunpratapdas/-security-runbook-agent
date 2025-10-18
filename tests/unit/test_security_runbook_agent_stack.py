import aws_cdk as core
import aws_cdk.assertions as assertions

from security_runbook_agent.security_runbook_agent_stack import SecurityRunbookAgentStack

# example tests. To run these tests, uncomment this file along with the example
# resource in security_runbook_agent/security_runbook_agent_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = SecurityRunbookAgentStack(app, "security-runbook-agent")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
