# Deployment

MiniGlean deploys to AWS. The frontend runs on Amplify, the FastAPI backend runs
on Lambda behind an HTTP API, and data lives in RDS Postgres with pgvector. All
infrastructure is defined with AWS CDK in [`infra/`](../infra) — there are no
manual console changes.

```
Internet ──▶ Amplify (Next.js)  ──NEXT_PUBLIC_API_URL──▶  API Gateway (HTTP API)
                                                                │
                                                                ▼
                                                      Lambda (FastAPI + Mangum)
                                                       │ (in VPC private subnet)
                                          ┌────────────┴────────────┐
                                          ▼                         ▼
                                  NAT ▶ OpenAI API          RDS Postgres + pgvector
```

## Prerequisites

- An AWS account and the AWS CLI configured (`aws configure`).
- Node.js 20+ and the AWS CDK v2 toolkit (`npm install -g aws-cdk`, or use the
  local `npx cdk`).
- Docker running locally (CDK bundles the Python Lambda in a Docker image).
- A GitHub personal access token with `repo` scope (for Amplify to pull source).

## 1. Bootstrap CDK (first time per account/region)

```bash
cd infra
npm ci
npx cdk bootstrap aws://<account-id>/<region>
```

## 2. Create secrets in SSM Parameter Store

CloudFormation cannot create SecureString parameters, so create them once with
the CLI. The CDK stack imports them by name and grants the Lambda read access —
**no secret values ever appear in the repo, the template, or Lambda's
environment configuration.**

```bash
aws ssm put-parameter --name /miniglean/openai-api-key \
  --type SecureString --value "sk-..."

# Use the RDS connection string. The async driver prefix is required.
# postgresql+asyncpg://<user>:<pass>@<rds-endpoint>:5432/miniglean
aws ssm put-parameter --name /miniglean/database-url \
  --type SecureString --value "postgresql+asyncpg://..."

aws ssm put-parameter --name /miniglean/github-token \
  --type SecureString --value "ghp_..."
```

> The database URL depends on the RDS endpoint, which doesn't exist until the
> first deploy. Deploy once to create RDS (the Lambda will fail to connect until
> the parameter exists — that's expected), read the generated endpoint and
> master credentials from Secrets Manager, set `/miniglean/database-url`, then
> re-deploy. Alternatively deploy the database first.

## 3. Deploy

```bash
cd infra
npx cdk deploy
```

Pass your GitHub repo details and (after the first deploy) the frontend URL as
CDK context:

```bash
npx cdk deploy \
  -c repoOwner=<your-github-user> \
  -c repoName=miniglean \
  -c branch=main
```

The stack outputs the **API URL** (`MinigleanStack.ApiApiUrl...`) and the
**Amplify App ID**.

## 4. Lock down CORS (two-phase)

To avoid a circular dependency, CORS starts permissive and is tightened once the
Amplify URL is known:

1. First deploy uses `frontendUrl="*"` (the default).
2. Find the Amplify branch URL in the Amplify console (e.g.
   `https://main.d1234abcd.amplifyapp.com`).
3. Re-deploy restricting CORS to that origin:

```bash
npx cdk deploy -c frontendUrl=https://main.d1234abcd.amplifyapp.com
```

The Amplify app reads `NEXT_PUBLIC_API_URL` from the API endpoint automatically,
so the dependency only flows frontend → API (never back), which keeps the stack
acyclic.

## 5. Enable pgvector and run migrations

pgvector ships with RDS Postgres 16 but must be enabled per database, and the
schema is managed by Alembic — never from application code. The RDS instance is
in a private subnet, so run migrations from a network that can reach it: a
self-hosted runner inside the VPC, a bastion host, or over a VPN.

```bash
cd apps/api
export DATABASE_URL="postgresql+asyncpg://<user>:<pass>@<rds-endpoint>:5432/miniglean"

# The first migration runs CREATE EXTENSION IF NOT EXISTS vector;
alembic upgrade head
```

## 6. Verify

```bash
curl https://<api-url>/health
# => {"status":"ok","database":"connected","environment":"production"}
```

Open the Amplify URL, upload a document, and ask a question.

## Continuous deployment

- **CI** (`.github/workflows/test.yml`) runs ruff + pytest and eslint + tsc on
  every push and PR to `main`.
- **CD** (`.github/workflows/deploy.yml`) is triggered by the CI workflow
  completing and **only runs if CI succeeded** — tests gate every deploy. It
  assumes an AWS role via OIDC, runs `cdk deploy`, applies migrations, and curls
  `/health`.

Configure these GitHub repository secrets for CD:

| Secret | Purpose |
|--------|---------|
| `AWS_DEPLOY_ROLE_ARN` | IAM role assumed via OIDC for deploys |
| `AWS_REGION` | Target region |
| `DATABASE_URL` | Connection string for the migration step |
| `API_URL` | Base API URL for the health smoke test |

## Cost notes

- The single **NAT gateway** lets the VPC-bound Lambda reach the OpenAI API. It
  is the main recurring cost (~$32/month plus data processing) and is **not**
  covered by the free tier. Removing it would mean either dropping the VPC (and
  using RDS Data API / a public database, not recommended) or routing OpenAI
  calls through a VPC endpoint (not available for OpenAI).
- RDS `db.t4g.micro` and Lambda are within or near the free tier for a
  single-user demo. The EventBridge warmer invokes the Lambda every 5 minutes to
  reduce cold starts.

## Local development

For local development use Docker Compose instead of AWS — see the
[README](../README.md) Quick Start.
