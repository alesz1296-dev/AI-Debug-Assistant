# Phase 8 Tasks: Local Kubernetes to AWS EKS Platform

## Stage 8A: Local Kubernetes

- [x] Register the chosen Phase 8 direction: `Local Kubernetes first, then AWS EKS + Terraform + Helm`.
- [x] Choose local cluster runtime: `kind`.
- [x] Define local Kubernetes runbook.
- [ ] Define Helm chart structure.
- [ ] Add Helm chart skeleton.
- [ ] Add API Deployment template.
- [ ] Add API Service template.
- [ ] Add worker Deployment template.
- [ ] Add Alembic migration Job template.
- [ ] Add ConfigMap and Secret templates using safe local values.
- [ ] Add readiness and liveness probes.
- [ ] Add local Kubernetes values file.
- [ ] Render Helm templates locally.
- [ ] Deploy local Kubernetes stack.
- [ ] Run migration Job locally.
- [ ] Validate local Kubernetes `/health`.
- [ ] Validate local Kubernetes `/ready`.
- [ ] Validate local Kubernetes `/metrics`.
- [ ] Validate local Kubernetes `/query`.
- [ ] Validate local Kubernetes `/evaluations/run`.
- [ ] Validate document ingestion and worker processing.
- [ ] Validate API logs.
- [ ] Validate worker logs.
- [ ] Document failure drills for image pull, missing secret, database unavailable, Redis unavailable, migration failure, and readiness failure.
- [ ] Add local Kubernetes smoke evidence.

## Stage 8B: AWS EKS Planning

- [ ] Define AWS region and naming convention.
- [ ] Define cost guardrails.
- [ ] Define Terraform root structure under `infra/aws`.
- [ ] Define ECR image publishing workflow.
- [ ] Define EKS cluster and managed node group plan.
- [ ] Define RDS PostgreSQL plan.
- [ ] Define pgvector enablement plan.
- [ ] Define ElastiCache Redis or Valkey plan.
- [ ] Define IAM roles and service account strategy.
- [ ] Define AWS Load Balancer Controller plan.
- [ ] Define secrets strategy using AWS Secrets Manager or SSM Parameter Store.
- [ ] Define CloudWatch logs and Container Insights plan.
- [ ] Define AWS smoke test checklist.
- [ ] Define teardown runbook.

## Stage 8C: AWS EKS Implementation

- [ ] Add Terraform network foundation.
- [ ] Add Terraform ECR module.
- [ ] Add Terraform EKS module.
- [ ] Add Terraform RDS module.
- [ ] Add Terraform ElastiCache module.
- [ ] Add Terraform IAM module.
- [ ] Add Terraform observability module.
- [ ] Add image build and ECR push workflow.
- [ ] Deploy Helm chart to EKS.
- [ ] Run Alembic migration Job against RDS.
- [ ] Validate API and worker on EKS.
- [ ] Validate logs, metrics, and smoke tests on AWS.
- [ ] Document final AWS validation evidence.
