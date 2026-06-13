# Phase 8 Plan: Cloud / AWS / Kubernetes / Terraform

## Approach

Start from the validated containerized platform and use the chosen Phase 8 direction as the default AWS target. The goal is to learn AWS deployment, Terraform, image publishing, secrets handling, and cloud observability without jumping straight into Kubernetes complexity.

The chosen Phase 8 direction is:

- compute: `ECS Fargate`
- registry: `ECR`
- database: `RDS PostgreSQL`
- queue/cache: `ElastiCache Redis/Valkey`
- ingress: `ALB + ECS service`
- secrets: `SSM Parameter Store SecureString`
- infrastructure as code: `Terraform`

Why this path:

- lowest-cost AWS learning path that still preserves the local platform shape
- keeps API, worker, Postgres, and Redis architecture aligned with the validated local system
- teaches core AWS container deployment patterns with less operational overhead than EKS

Kubernetes/EKS remains a deliberate non-default alternative. It should be revisited only if Kubernetes itself becomes the primary learning goal.

## Target Capabilities

- Terraform provisioning.
- Image publishing.
- Deployment workflow.
- Secrets and environment configuration.
- Logs and metrics after deployment.
- Cost and teardown controls.

## First Outputs

- AWS target architecture registration.
- Terraform foundation plan.
- ECR image publishing plan.
- ECS API service plan.
- ECS worker service plan.
- RDS provisioning plan.
- ElastiCache provisioning plan.
- Secrets strategy using `SSM Parameter Store SecureString`.
- Logs and metrics smoke-test plan.
- Teardown and cost-control notes.

## Validation

- Terraform plan and apply workflow.
- Deployment from built image.
- Operational smoke test.
- Cost and teardown documentation.
