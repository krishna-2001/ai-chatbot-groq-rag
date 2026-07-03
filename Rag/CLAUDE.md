# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AWS-based RAG (Retrieval-Augmented Generation) workshop project. Demonstrates how to build and deploy a full RAG pipeline using AWS Bedrock, Lambda, API Gateway, and a Streamlit frontend on EC2.

**Important**: All resources must be deployed in `us-west-2` only.

## Repository Contents

- `Rag/RAG.pdf` — Step-by-step workshop guide (primary documentation)
- `Rag/ai_meetup_cloudformation_template_demo.yaml` — CloudFormation IaC template that provisions all AWS resources
- `Rag/Leave-Policy-India.pdf` — Sample document for testing the RAG knowledge base

## Architecture

Three-tier serverless RAG system:

```
User (browser)
  → Streamlit UI (EC2, port 8501)
  → API Gateway (REST, GET /query?prompt=...)
  → Lambda (Python 3.8, invokes Bedrock)
  → AWS Bedrock Knowledge Base (retrieve_and_generate API)
      ├── Vector Store: OpenSearch Serverless
      ├── Embeddings: Titan Embeddings G1 - Text v1.2
      └── Document Storage: S3
```

## CloudFormation Template

The YAML template (`ai_meetup_cloudformation_template_demo.yaml`) provisions:

| Resource | Type | Notes |
|---|---|---|
| EC2 Instance | t2.micro Ubuntu | Runs Streamlit app; UserData installs deps and starts server |
| Security Group | EC2 SG | Opens ports 22, 80, 443, 8501 to 0.0.0.0/0 |
| Lambda Function | Python 3.8 | Calls `bedrock-agent-runtime.retrieve_and_generate()` |
| API Gateway | REST API | GET method; maps `prompt` query param to Lambda event |
| IAM Role | LambdaExecutionRole | BedrockFullAccess + AWSLambdaBasicExecutionRole |

**Required parameters when deploying the stack:**
- `VpcId` — VPC to deploy into
- `KnowledgeBaseId` — ID from AWS Bedrock Knowledge Base
- `ModelId` — Bedrock model ID (e.g., `anthropic.claude-instant-v1`)

**Stack output:** EC2 public IP URL on port 8501.

## Lambda Function Logic

The Lambda handler (embedded in the CloudFormation template under `LambdaFunction.Properties.Code.ZipFile`) does:
1. Reads `prompt` from `event['queryStringParameters']`
2. Calls `bedrock-agent-runtime.retrieve_and_generate()` with `KNOWLEDGE_BASE` retrieval type
3. Returns `{"statusCode": 200, "body": <generated_text>}`

Environment variables injected by CloudFormation:
- `KnowledgeBaseId`
- `ModelId`

## Deployment Steps (from RAG.pdf)

1. Enable Bedrock model access in AWS console (request all models; use case: "RAG-based implementation on custom data")
2. Create S3 bucket → upload PDFs
3. Create Bedrock Knowledge Base (Titan Embeddings G1 v1.2, Quick-create OpenSearch Serverless vector store) → sync (~8 min)
4. Deploy CloudFormation stack with the YAML template → wait ~7–9 min
5. Access Streamlit app via the URL in the stack's Outputs tab

## Cleanup (Critical — Cost Risk)

OpenSearch Serverless charges **$0.48/hour** continuously. Always delete after use:
1. Delete the Bedrock Knowledge Base
2. Delete the OpenSearch Serverless Collection
3. Delete the CloudFormation Stack

## ⚠️ Demo-only — not production-ready

This template is built for a workshop and intentionally cuts corners that would be unacceptable in production:

- The EC2 security group opens ports 22, 80, 443, and 8501 to `0.0.0.0/0` (SSH included). Restrict these to your own IP before leaving the stack up for any length of time.
- The API Gateway method uses `AuthorizationType: NONE` with no throttling — anyone with the URL can trigger billed Bedrock calls. Add an API key, IAM auth, or a usage plan for anything beyond a short demo.
- The Lambda execution role uses the broad `AmazonBedrockFullAccess` managed policy instead of a scoped-down policy for just the knowledge base/model in use.

Fine for a short-lived, instructor-supervised session; tear the stack down promptly (see Cleanup above) and don't leave it running unattended.
