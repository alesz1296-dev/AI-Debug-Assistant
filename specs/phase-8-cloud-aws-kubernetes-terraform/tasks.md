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

- [x] Record Stage 8B owner-led implementation mode and private-learning-doc boundary.
- [x] Document managed-first AWS architecture defaults for Stage 8B.
- [x] Define AWS region and naming convention.
- [x] Define tagging standard.
- [x] Define cost guardrails.
- [x] Define remote Terraform state bootstrap approach.
- [x] Define Terraform root structure under `infra/aws`.
- [ ] Define ECR image publishing workflow.
- [x] Define EKS cluster and managed node group plan.
- [x] Define RDS PostgreSQL plan.
- [x] Define pgvector enablement plan.
- [x] Define ElastiCache Redis or Valkey plan.
- [x] Define IAM roles and service account strategy.
- [x] Define AWS Load Balancer Controller plan.
- [x] Define secrets strategy using AWS Secrets Manager or SSM Parameter Store.
- [x] Define CloudWatch logs and Container Insights plan.
- [x] Define AWS smoke test checklist.
- [x] Define teardown runbook.
- [x] Add project-facing AWS architecture runbook in `docs/`.
- [x] Add project-facing AWS validation checklist in `docs/`.
- [x] Add project-facing AWS teardown and cost-control runbook in `docs/`.

## Stage 8C: AWS EKS Implementation

- [x] Add Terraform network foundation.
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
