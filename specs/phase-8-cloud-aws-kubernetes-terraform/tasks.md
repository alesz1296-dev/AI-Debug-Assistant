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
- [x] Adjust Phase 8 to a cost-controlled AWS lab model.
- [x] Define remote Terraform state bootstrap approach.
- [x] Define Terraform root structure under `infra/aws`.
- [x] Define ECR image publishing workflow.
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
- [x] Add optional NAT Gateway control for the dev network baseline.
- [x] Add Terraform ECR module.
- [x] Add Terraform EKS module behind `enable_eks`.
- [x] Add `eks_subnet_tier` control for public versus private EKS lab placement.
- [x] Add future billable-service toggles for RDS, ElastiCache, ALB, and Container Insights.
- [ ] Validate default `dev` plan excludes EKS, NAT Gateway, RDS, ElastiCache, ALB, and Container Insights.
- [ ] If prior EKS or NAT resources exist in state, validate the cleanup plan destroys them.
- [ ] Confirm free-tier-eligible EC2 instance type before any EKS lab apply.
- [ ] Validate short-lived EKS lab creation with `enable_eks = true`.
- [ ] Validate EKS teardown proof after the lab.
- [ ] Add Terraform RDS module behind `enable_rds`.
- [ ] Add Terraform ElastiCache module behind `enable_elasticache`.
- [ ] Add Terraform IAM module.
- [ ] Add Terraform observability module behind `enable_container_insights`.
- [ ] Add AWS Load Balancer Controller and ALB flow behind `enable_alb`.
- [x] Validate manual API image build, tag, push, and ECR image lookup.
- [ ] Add image build and ECR push workflow.
- [ ] Deploy Helm chart to EKS.
- [ ] Run Alembic migration Job against RDS.
- [ ] Validate API and worker on EKS.
- [ ] Validate logs, metrics, and smoke tests on AWS.
- [ ] Document final AWS validation evidence.
