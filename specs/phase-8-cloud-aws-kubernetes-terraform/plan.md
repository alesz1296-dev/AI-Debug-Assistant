# Phase 8 Plan: Local Kubernetes to AWS EKS Platform

## Approach

Use the validated Compose platform as the baseline and move one platform layer at a time.

Phase 8 is now Kubernetes-first:

1. Prove the application in local Kubernetes.
2. Package the API, worker, and migration workflow with Helm.
3. Add reproducible local Kubernetes smoke tests and debugging notes.
4. Move the same deployment shape to AWS EKS with Terraform-managed infrastructure.

This phase intentionally keeps operational complexity visible. The purpose is to validate platform behavior, failure modes, networking, probes, secrets, logs, migrations, and worker processing before declaring cloud readiness.

## Stage 8A: Local Kubernetes Platform

Target runtime:

- local cluster: `kind`
- packaging: Helm chart preferred
- API workload: Kubernetes Deployment
- worker workload: Kubernetes Deployment
- migrations: Kubernetes Job
- service discovery: Kubernetes Service
- ingress: local port-forward first, ingress later only if useful
- dependencies: local Postgres and Redis/Valkey inside the cluster or explicitly wired external dependencies

Current local Kubernetes progress:

- `kind` is installed as a local workstation tool.
- the local cluster `ai-debug-local` has been created and validated with `kubectl cluster-info` and `kubectl get nodes`
- the API image has been built locally and loaded into the cluster with `kind load docker-image`
- raw manifests now exist under `infra/k8s` for namespace, config, secrets, PostgreSQL, Redis, and PostgreSQL persistent storage
- PostgreSQL and Redis were applied in the `ai-debug` namespace and reached a healthy running state
- a Helm chart now exists under `infra/helm/ai-debug-assistant`
- a dedicated `values-kind.yaml` file now packages the validated local Kubernetes shape
- CI now renders the Helm chart, installs it into a fresh `kind` cluster, and runs a Kubernetes smoke test against the Helm-installed stack

Why this matters:

- we have already proven the dependency layer before adding the application layer
- this reduces debugging scope because API and worker rollout can focus on commands, probes, and app wiring instead of basic cluster networking
- it mirrors real platform work, where infrastructure primitives are usually stabilized before app workloads are layered on top

Required local Kubernetes proof:

- API pod starts from the project image.
- Migration Job applies Alembic migrations.
- API readiness and liveness probes work.
- Worker pod processes Redis/RQ ingestion jobs.
- `/api/v1/health`, `/api/v1/ready`, `/api/v1/metrics`, `/api/v1/query`, and `/api/v1/evaluations/run` pass through port-forward or ingress.
- Logs show request IDs, readiness checks, query completion, evaluation completion, ingestion queueing, and worker success.
- Failure drills are documented for bad image tag, missing secret, database unavailable, Redis unavailable, failed migration, and failed readiness.

## Stage 8B: AWS EKS Foundation

Target AWS architecture:

- compute: EKS with managed node groups
- registry: ECR
- database: RDS PostgreSQL with pgvector enabled through migrations/setup
- queue/cache: ElastiCache Redis or Valkey
- ingress: AWS Load Balancer Controller
- secrets: AWS Secrets Manager or SSM Parameter Store plus Kubernetes secret integration
- logs: CloudWatch Container Insights and pod logs
- infrastructure as code: Terraform
- deployment packaging: Helm

Terraform foundation structure:

```text
infra/aws/
  envs/dev/
  modules/network/
  modules/ecr/
  modules/eks/
  modules/rds/
  modules/elasticache/
  modules/iam/
  modules/observability/
```

Helm structure:

```text
infra/helm/ai-debug-assistant/
  Chart.yaml
  values.yaml
  values-kind.yaml
  templates/
    api-deployment.yaml
    api-service.yaml
    worker-deployment.yaml
    migration-job.yaml
    configmap.yaml
    secret.yaml
    postgres-deployment.yaml
    postgres-service.yaml
    postgres-pvc.yaml
    redis-deployment.yaml
    redis-service.yaml
```

## Stage 8C: AWS Deployment Workflow

Deployment flow:

1. Build API image.
2. Push image to ECR.
3. Provision or update Terraform foundation manually.
4. Render Helm templates locally.
5. Run migration Job.
6. Deploy API and worker.
7. Validate health, readiness, query, evaluation, ingestion, worker logs, and metrics.
8. Document teardown.

## Safety Rules

- No automatic `terraform apply`.
- No automatic `terraform destroy`.
- No committed secrets.
- No AWS resource creation before teardown and cost notes exist.
- Manual approval is required before mutating AWS infrastructure.
- Prefer small, reviewable infrastructure increments.

## First Outputs

- Local Kubernetes runbook.
- Helm chart skeleton.
- Migration Job design.
- Local Kubernetes smoke checklist.
- Failure-drill checklist.
- AWS EKS Terraform architecture plan.
- ECR image publishing plan.
- EKS deployment and smoke-test plan.
- Teardown and cost-control runbook.

## Validation

- Local Kubernetes smoke test passes before AWS implementation starts.
- Helm templates render in CI.
- the Helm-installed stack passes automated `kind` smoke validation in CI.
- Terraform validates and plans before any apply.
- AWS smoke test passes only after EKS deployment exists.
