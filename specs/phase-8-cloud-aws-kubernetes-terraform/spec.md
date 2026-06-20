# Phase 8 Spec: Local Kubernetes to AWS EKS Platform

## Goal

Promote the DevOps-ready Compose platform into a Kubernetes-first platform path. Phase 8 starts with local Kubernetes so the deployment model, Helm chart, probes, migration jobs, worker runtime, and debugging workflow are proven before any AWS resources are created.

After the local Kubernetes gate passes, the same workload can move to AWS EKS through Terraform-managed infrastructure.

## Requirements

- Build a local Kubernetes deployment path before AWS work starts.
- Package the API and worker with Helm or Kubernetes manifests.
- Represent Alembic migrations as an explicit Kubernetes Job.
- Configure API readiness and liveness probes against `/api/v1/ready` and `/api/v1/health`.
- Run the API and worker as separate Kubernetes workloads.
- Keep Postgres and Redis dependencies explicit for local Kubernetes validation.
- Define AWS EKS infrastructure as a later Phase 8 stage using Terraform.
- Use ECR for image publishing before EKS deployment.
- Use RDS PostgreSQL with pgvector for the AWS database target.
- Use ElastiCache Redis or Valkey for the AWS queue/cache target.
- Add Kubernetes/AWS secrets handling without committing secrets.
- Add logs and metrics validation for local Kubernetes and AWS EKS.
- Document manual smoke tests, debugging commands, failure modes, and teardown.

## Acceptance Criteria

- Local Kubernetes can deploy the API, worker, and migration job from the same container image.
- Local Kubernetes smoke tests prove health, readiness, query, evaluation, ingestion enqueue, worker processing, metrics, and logs.
- Kubernetes manifests or Helm templates are reproducible and reviewed before AWS deployment.
- Terraform plans the AWS EKS foundation without manual console setup.
- AWS deployment workflow is documented and repeatable.
- Secrets are not stored in git.
- Operational demo proves health, readiness, logs, metrics, migrations, and worker processing after deployment.
- Teardown and cost-control steps are documented before any AWS apply.

## Out Of Scope

- High-availability production SLOs.
- Multi-region deployment.
- Automatic Terraform apply.
- Automatic production deployment.
- Dashboard unless Phase 9 is started.
- LangChain or LangGraph adoption unless a future spec justifies it.
