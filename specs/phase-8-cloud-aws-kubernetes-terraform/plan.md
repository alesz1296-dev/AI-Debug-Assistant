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

Stage 8B operating mode:

- the project owner performs the implementation work
- Codex acts as teacher, architectural guide, reviewer, and debugging partner
- Stage 8B should front-load explanation and decision-making before any AWS mutation work begins
- tracked docs capture project-facing truth only
- personal learning notes stay in ignored private directories such as `.learning/`, `.planning/`, or `.private-notes/`

Locked Stage 8B defaults:

- learning path: managed-first
- environment scope: implement `dev` first, scaffold `staging`
- cost posture: cost-controlled lab mode
- Terraform state: remote state from the start
- Kubernetes-on-AWS add-ons: core add-ons only
- dev access pattern: public ALB
- secrets pattern: AWS Secrets Manager plus External Secrets Operator
- managed data strategy: RDS PostgreSQL plus ElastiCache Redis or Valkey
- shared tagging baseline: `Project`, `App`, `Environment`, and `ManagedBy`

Cost-controlled lab model:

- `dev` defaults to low-cost baseline infrastructure.
- EKS is not treated as free-tier infrastructure because the managed control plane has its own hourly cost.
- EKS labs must be short-lived unless intentionally kept running.
- NAT Gateway, EKS, RDS, ElastiCache, ALB, and Container Insights are disabled by default in `dev` unless a focused lab requires them.
- public-subnet EKS is allowed for short-lived `dev` learning labs as a cost tradeoff, but not as the staging or production target.

Stage 8B decision topics:

- AWS region and naming convention
- tagging standard
- VPC topology and subnet strategy
- EKS cluster and managed node group shape
- RDS design and pgvector enablement approach
- ElastiCache/Valkey design
- IRSA and controller IAM strategy
- Secrets Manager and External Secrets integration
- CloudWatch log and metrics visibility plan
- teardown and cost-control workflow

Terraform foundation structure:

```text
infra/aws/
  bootstrap/
    state/
  envs/dev/
  envs/staging/
  modules/network/
  modules/ecr/
  modules/eks/
  modules/rds/
  modules/elasticache/
  modules/iam/
  modules/observability/
  modules/secrets/
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

## Stage 8C: Cost-Controlled AWS Implementation

Stage 8C no longer assumes an always-on AWS EKS platform. The default implementation path is a cost-controlled AWS lab model with three operating profiles:

- `local-full`: Docker Compose, `kind`, Helm, local PostgreSQL, Redis, workers, and smoke tests.
- `aws-free-friendly`: Terraform remote state, VPC, public and private subnets, route tables, Internet Gateway, and ECR.
- `aws-eks-lab`: short-lived EKS validation only, explicitly enabled and immediately torn down after proof.

EKS remains part of the architecture, but it is treated as a controlled lab target instead of default `dev` infrastructure.

Deployment flow:

1. Build API image.
2. Push image to ECR.
3. Provision or update Terraform foundation manually.
4. Render Helm templates locally.
5. Run migration Job.
6. Deploy API and worker.
7. Validate health, readiness, query, evaluation, ingestion, worker logs, and metrics.
8. Document teardown.

Stage 8C implementation order:

1. backend and remote state bootstrap
2. network module
3. ECR module
4. EKS module
5. IAM and IRSA foundations
6. AWS Load Balancer Controller
7. RDS module
8. ElastiCache module
9. secrets integration
10. observability module
11. AWS Helm values
12. ECR image publishing workflow
13. EKS deploy and smoke workflow
14. teardown validation

Current Stage 8C progress:

- backend and remote state bootstrap have been applied and verified in AWS
- the first reusable Terraform module, `modules/network`, has been consumed by `envs/dev`
- the `dev` network has been applied and validated in `us-east-1`
- the `dev` network has been adjusted so NAT Gateway is optional and disabled by default for cost control
- `modules/ecr` has been added and consumed by `envs/dev`
- manual ECR publishing has been validated:
  - API image built locally as `ai-debug-assistant-api:dev`
  - image pushed to ECR repository `ai-debug-assistant-ada-dev-api`
  - ECR tag `dev` is visible in AWS with digest `sha256:e6e9232239051487e3a81e65625dda90a1b2431c08bf79007d3e80d35256ce22`
- `scripts/push-api-image-to-ecr.ps1` now captures the repeatable local image publishing flow
- `modules/eks` has been added and consumed by `envs/dev` behind `enable_eks`
- `dev` now defaults to a cheap baseline with EKS disabled unless a short-lived lab explicitly enables it
- future billable-service toggles exist in `dev` and default to disabled:
  - `enable_rds = false`
  - `enable_elasticache = false`
  - `enable_alb = false`
  - `enable_container_insights = false`
- validated evidence includes:
  - `terraform validate` passes for `infra/aws/envs/dev`
  - `terraform plan` reports no changes for the current `dev` baseline
  - VPC `ai-debug-assistant-ada-dev-vpc`
  - two public subnets across `us-east-1a` and `us-east-1b`
  - two private subnets across `us-east-1a` and `us-east-1b`
  - attached Internet Gateway
  - NAT Gateway was validated previously and is now optional for cost control
  - public route table default route to the Internet Gateway
  - private route table default route to the NAT Gateway when NAT is enabled
  - earlier EKS and NAT lab resources have been cleaned up
- next implementation focus: validate the local ECR publishing script, then begin IAM and secrets module design

## Safety Rules

- No automatic `terraform apply`.
- No automatic `terraform destroy`.
- No committed secrets.
- No AWS resource creation before teardown and cost notes exist.
- Manual approval is required before mutating AWS infrastructure.
- Prefer small, reviewable infrastructure increments.
- Default `dev` must not create EKS, NAT Gateway, RDS, ElastiCache, ALB, or Container Insights.
- EKS labs must include an immediate post-lab teardown verification step.
- If a previous failed or partial apply left EKS or NAT resources in state, the next plan should be treated as a cleanup and cost-control review.

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
- AWS validation checklist.
- project-facing AWS architecture runbook.

## Validation

- Local Kubernetes smoke test passes before AWS implementation starts.
- Helm templates render in CI.
- the Helm-installed stack passes automated `kind` smoke validation in CI.
- Stage 8B is decision-complete before any Terraform implementation starts.
- Terraform validates and plans before any apply.
- AWS smoke test passes only after EKS deployment exists.
