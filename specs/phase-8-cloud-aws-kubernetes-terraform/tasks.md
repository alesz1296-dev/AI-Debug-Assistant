# Phase 8 Tasks: Local Kubernetes to AWS EKS Platform

## Stage 8A: Local Kubernetes

- [x] Register the chosen Phase 8 direction: `Local Kubernetes first, then AWS EKS + Terraform + Helm`.
- [x] Choose local cluster runtime: `kind`.
- [x] Define local Kubernetes runbook.
- [x] Create local `kind` cluster.
- [x] Build the API image for local Kubernetes.
- [x] Load the local API image into the `kind` cluster.
- [x] Add Namespace manifest.
- [x] Add ConfigMap template with safe local values.
- [x] Add Secret template with safe local placeholders.
- [x] Add PostgreSQL Deployment template.
- [x] Add PostgreSQL Service template.
- [x] Add PostgreSQL persistent volume claim template.
- [x] Add Redis Deployment template.
- [x] Add Redis Service template.
- [x] Deploy local PostgreSQL and Redis foundation in Kubernetes.
- [x] Validate PostgreSQL and Redis Pods reach `Running`.
- [x] Add API Deployment template.
- [x] Add API Service template.
- [x] Add worker Deployment template.
- [x] Add Alembic migration Job template.
- [x] Wire API and worker environment from ConfigMap and Secret.
- [x] Add readiness and liveness probes.
- [x] Define Helm chart structure.
- [x] Add Helm chart skeleton.
- [x] Add local Kubernetes values file.
- [x] Render Helm templates in CI validation.
- [x] Deploy local Kubernetes stack.
- [x] Run migration Job locally.
- [x] Validate local Kubernetes `/health`.
- [x] Validate local Kubernetes `/ready`.
- [x] Validate local Kubernetes `/metrics`.
- [x] Validate local Kubernetes `/query`.
- [x] Validate local Kubernetes `/evaluations/run`.
- [x] Validate document ingestion and worker processing.
- [x] Validate API logs.
- [x] Validate worker logs.
- [x] Document at least one local Kubernetes failure drill with recovery behavior.
- [x] Add local Kubernetes smoke evidence.
- [x] Add automated `kind` Kubernetes smoke validation in CI.

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
