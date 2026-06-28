# AWS EKS Architecture Runbook

This document records the project-facing AWS target architecture for Phase 8B and later Stage 8C implementation. It is not a personal study guide. Personal learning notes belong in ignored private directories only.

## Current Phase Context

- Phase 8A local Kubernetes is complete.
- Stage 8B is the current planning stage.
- Stage 8C implementation has started with Terraform bootstrap and the `dev` network foundation.
- the next AWS implementation target is the ECR module.

## Locked Defaults

- implementation style: owner-led, with guided review and debugging
- learning path: managed-first
- AWS region: `us-east-1`
- naming convention: `ai-debug-assistant-ada-<env>-<resource>`
- environment ladder: `local`, `dev`, `staging`, `prod`
- first implemented environment: `dev`
- scaffolded later environments: `staging` and `prod`
- cost posture: tight lab budget
- state strategy: remote Terraform state from the start
- app exposure in `dev`: public ALB
- secrets strategy: AWS Secrets Manager plus External Secrets Operator
- data services: RDS PostgreSQL plus ElastiCache Redis or Valkey
- Terraform structure: reusable modules under `infra/aws/modules` with environment roots under `infra/aws/envs`
- shared tagging baseline: `Project`, `App`, `Environment`, `ManagedBy`

## Target AWS Platform

The target AWS platform should use:

- VPC with public and private subnets across multiple availability zones
- S3 bucket for Terraform remote state
- DynamoDB table for Terraform state locking
- ECR for API image storage
- EKS with managed node groups for API, worker, and migration workloads
- RDS PostgreSQL for the relational and vector-backed data store
- ElastiCache Redis or Valkey for queue/cache behavior
- AWS Load Balancer Controller for ALB-backed ingress
- IAM Roles for Service Accounts for AWS access from Kubernetes workloads
- AWS Secrets Manager as the source of truth for secrets
- External Secrets Operator to sync secret material into Kubernetes
- CloudWatch logs and cluster observability for runtime inspection

## Responsibility Split

Terraform owns:

- Terraform backend bootstrap resources
- AWS infrastructure
- networking
- ECR
- EKS
- RDS
- ElastiCache
- IAM and IRSA foundations
- CloudWatch-related infrastructure
- secret containers and metadata in AWS

Helm owns:

- API Deployment
- worker Deployment
- migration Job
- ConfigMap
- Kubernetes Secret references
- Services
- probes
- image tag and runtime value injection

## Terraform Layout

The current Terraform scaffold is:

```text
infra/aws/
  bootstrap/
    state/
  envs/
    dev/
    staging/
    prod/
  modules/
    network/
    ecr/
    eks/
    iam/
    rds/
    elasticache/
    secrets/
    observability/
```

This structure expresses three boundaries:

- `bootstrap/state` creates the shared Terraform backend foundation.
- `envs/*` are root modules with separate state and environment-specific values.
- `modules/*` are reusable building blocks that stay environment-agnostic.

## Current AWS Implementation Evidence

The current validated AWS implementation evidence is:

- Terraform bootstrap state has been applied and verified.
- `infra/aws/envs/dev` is wired to the remote backend and consumes reusable modules.
- the `network` module has been applied successfully for `dev`.
- the deployed `dev` network currently includes:
  - VPC `ai-debug-assistant-ada-dev-vpc`
  - public subnets `10.10.1.0/24` and `10.10.2.0/24`
  - private subnets `10.10.11.0/24` and `10.10.12.0/24`
  - subnet spread across `us-east-1a` and `us-east-1b`
  - Internet Gateway `ai-debug-assistant-ada-dev-igw`
  - NAT Gateway `ai-debug-assistant-ada-dev-nat`
  - public route table default route to the Internet Gateway
  - private route table default route to the NAT Gateway

This is the first confirmed AWS environment layer for the project. The next module should build outward from this network foundation rather than bypass it with console-created resources.

## Implementation Order

The intended implementation order is:

1. backend and remote state bootstrap
2. network foundation
3. ECR
4. EKS
5. IAM and IRSA
6. AWS Load Balancer Controller
7. RDS
8. ElastiCache
9. secrets integration
10. observability
11. AWS Helm values
12. ECR publishing flow
13. EKS deployment and smoke validation
14. teardown validation

## Open Architecture Decisions

The following still require explicit tracked decisions before implementation:

- managed node group sizing
- RDS size and availability posture
- ElastiCache engine and sizing details
- CloudWatch detail level
- final AWS smoke checklist
- teardown workflow detail
