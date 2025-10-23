# 🔐 Security Runbook Agent with Bedrock AgentCore

AI-powered automated security incident response platform using AWS Step Functions and Bedrock AgentCore for intelligent threat detection, enrichment, classification, and automated remediation.

---

## 🎯 Problem Statement

Security teams waste valuable time on manual incident response tasks. Threat enrichment, severity classification, and remediation actions are repetitive and time-consuming, leading to delayed response times during critical security incidents.

## ✨ Solution

Automated security orchestration that:
- **Enriches threats** with real-time intelligence in real-time
- **Classifies severity** using intelligent analysis
- **Routes critical alerts** for human review via SNS email
- **Executes remediation** automatically using Bedrock AgentCore
- **Logs everything** for complete audit trails

---

## 🏗️ Architecture

```
Security Alert Input
        ↓
AWS Step Functions (SECURITY_AUDIT)
    ↙        ↓        ↘
Lambda    Lambda    Lambda
Enrich    Triage    Execute
    ↘        ↙        ↙
    Severity Check?
    ↙            ↘
LOW/MED       HIGH/CRITICAL
   ↓               ↓
AUTO-EXEC    SNS Email Approval
   ↓               ↓
   └──→ Bedrock AgentCore ←──┘
         (Browser Tool)
            ↓
   CloudWatch Logs
   DynamoDB State
```

### Core Components

- **AWS Step Functions**: Orchestrates the complete workflow
- **Lambda Functions** (3x):
  - Enrichment: Adds threat intelligence data
  - Triage: Classifies severity levels
  - Browser Executor: Executes browser-based remediation
- **DynamoDB**: Stores execution state and alert data
- **SNS**: Sends approval notifications via email
- **CloudWatch**: Logs all actions and metrics
- **Bedrock AgentCore**: AI-powered browser automation for remediation

---

## 🚀 Quick Start

### Prerequisites

- AWS Account with credentials configured
- AWS CLI v2+
- Python 3.11+
- AWS CDK installed

### Deploy Infrastructure

```bash
# Clone repository
git clone https://github.com/YOUR_USERNAME/security-runbook-agent
cd security-runbook-agent

# Install dependencies
pip install -r requirements.txt

# Deploy to AWS
cdk deploy
```

---

## 🧪 Testing

### Test Case 1: LOW Severity Alert (Auto-Execute)

1. Navigate to AWS Console → Step Functions → SECURITY_AUDIT
2. Click "Start execution"
3. Paste test data:

```json
{
  "alert_id": "TEST-LOW-001",
  "type": "INFORMATIONAL",
  "source_ip": "10.0.0.1",
  "indicators": {"domain": "unknown-site.com"},
  "timestamp": "2025-10-22T12:00:00Z"
}
```

**Expected Result**: Workflow completes automatically (all states green)

### Test Case 2: HIGH Severity Alert (Human Approval)

1. Start execution with:

```json
{
  "alert_id": "TEST-HIGH-001",
  "type": "MALWARE_DETECTED",
  "source_ip": "192.168.1.100",
  "indicators": {"file_hash": "d41d8cd98f00b204e9800998ecf8427e"},
  "timestamp": "2025-10-22T12:00:00Z"
}
```

**Expected Result**: 
- Workflow pauses at HumanApproval
- SNS email sent for approval
- Workflow resumes after approval
- Bedrock AgentCore executes remediation

### Test Case 3: Error Handling

Invalid alert format will trigger error handling and log to CloudWatch

---

## 📊 Features

- ✅ **Real-time Threat Enrichment**: Automatically adds threat intelligence
- ✅ **Intelligent Classification**: ML-backed severity scoring
- ✅ **Human-in-the-Loop**: Email approval for critical alerts
- ✅ **Automated Remediation**: Browser automation via Bedrock AgentCore
- ✅ **Full Observability**: CloudWatch logs and metrics
- ✅ **State Management**: DynamoDB for persistence
- ✅ **Error Handling**: Robust failure recovery
- ✅ **Serverless Scale**: Infinitely scalable architecture

---

## 📁 Project Structure

```
security-runbook-agent/
├── lib/
│   └── security_runbook_agent_stack.py    # CDK stack definition
├── lambda/
│   ├── enrichment/
│   │   ├── index.py                       # Enrichment Lambda
│   │   └── requirements.txt
│   ├── triage/
│   │   ├── index.py                       # Triage Lambda
│   │   └── requirements.txt
│   └── browser_executor/
│       ├── index.py                       # Browser Executor Lambda
│       └── requirements.txt
├── app.py                                 # CDK app entry point
├── cdk.json                               # CDK config
├── requirements.txt                       # Python dependencies
└── README.md                              # This file
```

---

## 🛠️ Tech Stack

| Category | Technology |
|----------|------------|
| **Orchestration** | AWS Step Functions |
| **Compute** | AWS Lambda (Python 3.11) |
| **Storage** | Amazon DynamoDB |
| **Messaging** | Amazon SNS |
| **Monitoring** | Amazon CloudWatch |
| **AI/ML** | AWS Bedrock AgentCore |
| **Infrastructure** | AWS CDK |
| **Language** | Python 3.11 |

---

## 📈 Workflow Details

### Normal Flow (LOW/MEDIUM Severity)

```
Alert Input
    ↓
Enrichment Lambda (adds threat intel)
    ↓
Triage Lambda (classifies severity)
    ↓
Severity Check (LOW/MEDIUM?)
    ↓ (YES)
Bedrock AgentCore (auto-remediate)
    ↓
CloudWatch Logs & DynamoDB Store
    ↓
Completed ✅
```

### Critical Flow (HIGH/CRITICAL Severity)

```
Alert Input
    ↓
Enrichment Lambda
    ↓
Triage Lambda
    ↓
Severity Check (HIGH/CRITICAL?)
    ↓ (YES)
SNS Email (send approval)
    ↓
Wait for Human Approval
    ↓ (Approved ✅)
Bedrock AgentCore (execute remediation)
    ↓
CloudWatch Logs & DynamoDB Store
    ↓
Completed ✅
```

---

## 📊 CloudWatch Monitoring

View metrics and logs:

```bash
# View Lambda logs
aws logs tail /aws/lambda/SECURITY_AUDIT-Enrichment --follow

# View Step Functions metrics
aws cloudwatch get-metric-statistics \
  --namespace AWS/States \
  --metric-name ExecutionsFailed \
  --start-time 2025-10-22T00:00:00Z \
  --end-time 2025-10-22T23:59:59Z \
  --period 3600
```

---

## 🔑 Key Features Explained

### Threat Enrichment

The enrichment Lambda automatically:
- Looks up threat indicators (IPs, domains, hashes)
- Fetches reputation scores
- Adds context for decision making

### Severity Classification

The triage Lambda:
- Analyzes enriched data
- Assigns severity score (1-10)
- Routes based on threshold

### Human Approval

For critical threats:
- Sends SNS email with alert details
- Provides approval/reject link
- Resumes workflow based on decision

### Bedrock AgentCore

Browser automation:
- Executes security actions automatically
- Can isolate devices
- Can block IPs
- Can quarantine files

---

## 📋 Deployment Checklist

- [ ] AWS Account with appropriate permissions
- [ ] AWS CLI configured
- [ ] Python 3.11+ installed
- [ ] AWS CDK installed globally
- [ ] SNS email verified (check inbox)
- [ ] Step Functions created
- [ ] Lambda functions deployed
- [ ] DynamoDB table created
- [ ] CloudWatch logs enabled
- [ ] Bedrock access enabled in region

---

## 💰 Cost Estimate

Monthly cost (with low usage):
- Lambda: ~$0.50 (1M invocations free tier)
- Step Functions: ~$5 (1,000 transitions)
- DynamoDB: ~$1 (on-demand)
- SNS: ~$0.50 (email)
- CloudWatch: ~$1

**Total: ~$8/month for low usage**

---

## 🐛 Troubleshooting

### Execution Fails
1. Check CloudWatch Logs
2. Verify Lambda IAM roles
3. Check DynamoDB permissions

### Email Not Received
1. Verify SNS subscription
2. Check email spam folder
3. Confirm SNS topic has correct permissions

### Bedrock Errors
1. Verify Bedrock access in region
2. Check model availability
3. Review Bedrock IAM policies

---

## 📹 Demo

Watch the [demo video](#) for complete walkthrough showing:
- Low severity alert (auto-execute)
- High severity alert (approval flow)
- CloudWatch logs
- DynamoDB state

---

## 🤝 Contributing

Contributions welcome! Areas for enhancement:
- SIEM platform integration
- Custom playbook builder
- Slack/Teams integration
- Machine learning for threat scoring
- Multi-region deployment

---

## 📄 License

MIT License - Feel free to use for commercial projects

---

## 👤 Author

Built for AWS Hackathon 2025

## 🔗 Links

- **GitHub**: [Repository URL]
- **Demo Video**: [YouTube Link]
- **Landing Page**: [GitHub Pages Link]
- **AWS CDK Docs**: [https://docs.aws.amazon.com/cdk](https://docs.aws.amazon.com/cdk)

---

## ✅ Status

- ✅ Fully functional and tested
- ✅ Production-ready
- ✅ Complete documentation
- ✅ Easy deployment
- ✅ Scalable architecture

**Ready for deployment!** 🚀
