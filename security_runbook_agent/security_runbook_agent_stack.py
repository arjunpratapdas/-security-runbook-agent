from aws_cdk import (
    Stack,
    Duration,
    RemovalPolicy,
    CfnOutput,
    aws_iam as iam,
    aws_dynamodb as dynamodb,
    aws_sns as sns,
    aws_sns_subscriptions as subscriptions,
    aws_lambda as lambda_,
)
from constructs import Construct

class SecurityRunbookAgentStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        # ============================================
        # DYNAMODB TABLE FOR AGENT STATE
        # ============================================
        
        state_table = dynamodb.Table(
            self, "SecurityAgentStateTable",
            table_name="SecurityAgentState",
            partition_key=dynamodb.Attribute(
                name="sessionId",
                type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name="timestamp",
                type=dynamodb.AttributeType.NUMBER
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.DESTROY,
        )
        
        # ============================================
        # SNS TOPIC FOR HUMAN APPROVALS
        # ============================================
        
        approval_topic = sns.Topic(
            self, "SecurityApprovalTopic",
            topic_name="security-agent-approvals",
            display_name="Security Agent Approval Requests",
        )
        
        # IMPORTANT: Replace with your actual email!
        approval_topic.add_subscription(
            subscriptions.EmailSubscription("apdas400@gmail.com")
        )
        
        # ============================================
        # LAMBDA EXECUTION ROLE (Works with Bedrock)
        # ============================================
        
        lambda_role = iam.Role(
            self, "SecurityToolsLambdaRole",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            description="Execution role for security tool Lambda functions",
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name(
                    "service-role/AWSLambdaBasicExecutionRole"
                )
            ],
        )
        
        # Add Bedrock permissions for AI capabilities
        lambda_role.add_to_policy(iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            actions=[
                "bedrock:InvokeModel",
                "bedrock:InvokeModelWithResponseStream",
                "bedrock:GetFoundationModel",
                "bedrock:ListFoundationModels",
            ],
            resources=["*"]
        ))
        
        # Add DynamoDB permissions
        state_table.grant_read_write_data(lambda_role)
        
        # Add SNS permissions
        approval_topic.grant_publish(lambda_role)
        
        # ============================================
        # LAMBDA FUNCTIONS
        # ============================================
        
        # Lambda: Threat Intelligence Enrichment
        enrichment_lambda = lambda_.Function(
            self, "EnrichmentFunction",
            function_name="security-agent-enrichment",
            runtime=lambda_.Runtime.PYTHON_3_11,
            handler="enrichment.lambda_handler",
            code=lambda_.Code.from_asset("src/tools"),
            role=lambda_role,
            timeout=Duration.seconds(60),
            memory_size=256,
            environment={
                "STATE_TABLE_NAME": state_table.table_name,
            }
        )
        
        # Lambda: Triage and Severity Classification
        triage_lambda = lambda_.Function(
            self, "TriageFunction",
            function_name="security-agent-triage",
            runtime=lambda_.Runtime.PYTHON_3_11,
            handler="triage.lambda_handler",
            code=lambda_.Code.from_asset("src/tools"),
            role=lambda_role,
            timeout=Duration.seconds(30),
            memory_size=128,
            environment={
                "STATE_TABLE_NAME": state_table.table_name,
            }
        )
        
        # Lambda: Browser Action Executor (Bedrock-powered)
        executor_lambda = lambda_.Function(
            self, "BrowserExecutorFunction",
            function_name="security-agent-browser-executor",
            runtime=lambda_.Runtime.PYTHON_3_11,
            handler="browser_executor.lambda_handler",
            code=lambda_.Code.from_asset("src/tools"),
            role=lambda_role,
            timeout=Duration.seconds(300),
            memory_size=512,
            environment={
                "AGENT_ID": "security-runbook-agent",
                "REGION": self.region,
                "STATE_TABLE_NAME": state_table.table_name,
                "APPROVAL_TOPIC_ARN": approval_topic.topic_arn,
            }
        )

                # ============================================
        # API GATEWAY
        # ============================================
        
        from aws_cdk import aws_apigateway as apigateway
        
        api = apigateway.RestApi(
            self, "SecurityToolsAPI",
            rest_api_name="security-agent-tools",
            description="API Gateway for Security Agent Tools",
            deploy_options=apigateway.StageOptions(
                stage_name="prod",
            )
        )
        
        # Enrichment endpoint
        enrich_resource = api.root.add_resource("enrich")
        enrich_resource.add_method(
            "POST",
            apigateway.LambdaIntegration(enrichment_lambda)
        )
        
        # Triage endpoint
        triage_resource = api.root.add_resource("triage")
        triage_resource.add_method(
            "POST",
            apigateway.LambdaIntegration(triage_lambda)
        )
        
        # Executor endpoint
        execute_resource = api.root.add_resource("execute")
        execute_resource.add_method(
            "POST",
            apigateway.LambdaIntegration(executor_lambda)
        )
        
        # Output API URL
        CfnOutput(self, "APIEndpoint",
            value=api.url,
            description="API Gateway endpoint URL"
        )

                # ============================================
        # EVENTBRIDGE RULE
        # ============================================
        
        from aws_cdk import aws_events as events
        
        security_hub_rule = events.Rule(
            self, "SecurityHubFindingsRule",
            rule_name="security-agent-hub-ingestion",
            description="Ingests Security Hub findings into agent workflow",
            event_pattern=events.EventPattern(
                source=["aws.securityhub"],
                detail_type=["Security Hub Findings - Imported"],
            ),
        )
        
        # Note: Target will be added when Step Functions is created in Day 3


        
        # ============================================
        # STACK OUTPUTS
        # ============================================
        
        CfnOutput(self, "ApprovalTopicARN",
            value=approval_topic.topic_arn,
            description="SNS Topic ARN for human approvals",
            export_name="SecurityAgentApprovalTopicARN"
        )
        
        CfnOutput(self, "StateTableName",
            value=state_table.table_name,
            description="DynamoDB table for agent state",
            export_name="SecurityAgentStateTableName"
        )
        
        CfnOutput(self, "EnrichmentLambdaARN",
            value=enrichment_lambda.function_arn,
            description="Enrichment Lambda function ARN"
        )
        
        CfnOutput(self, "TriageLambdaARN",
            value=triage_lambda.function_arn,
            description="Triage Lambda function ARN"
        )
        
        CfnOutput(self, "ExecutorLambdaARN",
            value=executor_lambda.function_arn,
            description="Browser Executor Lambda function ARN"
        )
