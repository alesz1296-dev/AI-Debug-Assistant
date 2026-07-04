# AWS EKS Architecture Runbook

This document records the project-facing AWS target architecture for Phase 8B and later Stage 8C implementation. It is not a personal study guide. Personal learning notes belong in ignored private directories only.

## Current Phase Context

- Phase 8A local Kubernetes is complete.
- Stage 8B planning is complete.
- Stage 8C implementation is active.
- Terraform bootstrap, the `dev` network foundation, ECR, and the first EKS module wiring are in place.
- The current AWS implementation target is cost-controlled validation: default `dev` should stay cheap, while EKS is used only for short-lived labs.

## Locked Defaults

- implementation style: owner-led, with guided review and debugging
- learning path: managed-first
- AWS region: `us-east-1`
- naming convention: `ai-debug-assistant-ada-<env>-<resource>`
- environment ladder: `local`, `dev`, `staging`, `prod`
- first implemented environment: `dev`
- scaffolded later environments: `staging` and `prod`
- cost posture: cost-controlled lab mode
- state strategy: remote Terraform state from the start
- app exposure in `dev`: public ALB later, only when explicitly enabled for an AWS app-deploy lab
- secrets strategy: AWS Secrets Manager plus External Secrets Operator
- data services: RDS PostgreSQL plus ElastiCache Redis or Valkey
- Terraform structure: reusable modules under `infra/aws/modules` with environment roots under `infra/aws/envs`
- shared tagging baseline: `Project`, `App`, `Environment`, `ManagedBy`

## Cost-Controlled Lab Model

The default `dev` environment should stay small and cheap by default. It should include only the low-cost foundation unless a focused lab explicitly enables more.

The project uses three operating profiles:

- `local-full`: Docker Compose, `kind`, Helm, local PostgreSQL, Redis, workers, and smoke tests.
- `aws-free-friendly`: Terraform remote state, VPC, subnets, route tables, Internet Gateway, and ECR.
- `aws-eks-lab`: short-lived EKS validation only, explicitly enabled and torn down after proof.

Default `dev` includes:

- remote Terraform state
- VPC
- public and private subnets
- route tables
- Internet Gateway
- ECR repository

Default `dev` does not include:

- EKS
- NAT Gateway
- RDS
- ElastiCache
- ALB
- CloudWatch Container Insights

EKS is not treated as free-tier infrastructure. The managed EKS control plane has its own hourly cost, and failed applies can still leave billable resources behind. EKS labs should be short-lived unless intentionally kept running.

For short-lived `dev` EKS learning labs:

- `enable_eks = true` creates EKS.
- `eks_subnet_tier = "public"` is the lower-cost learning path.
- `eks_subnet_tier = "private"` requires `enable_nat_gateway = true`.
- `enable_nat_gateway = false` is the default baseline.
- `node_desired_size`, `node_min_size`, and `node_max_size` default to `1`.
- the selected node instance type must be checked for free-tier eligibility before any apply.

## Target AWS Platform

The target AWS platform should use:

- VPC with public and private subnets across multiple availability zones
- S3 bucket for Terraform remote state
- DynamoDB table for Terraform state locking
- ECR for API image storage
- optional EKS with managed node groups for API, worker, and migration workloads during short-lived labs
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
- the `ecr` module has been added and consumed by `dev`.
- the `eks` module has been added and consumed by `dev` behind `enable_eks`.
- NAT Gateway is now optional and disabled by default in `dev`.
- EKS is now disabled by default in `dev` and enabled only for short-lived labs.
- future billable-service toggles for RDS, ElastiCache, ALB, and Container Insights exist in `dev` and default to disabled.
- the validated `dev` network includes:
  - VPC `ai-debug-assistant-ada-dev-vpc`
  - public subnets `10.10.1.0/24` and `10.10.2.0/24`
  - private subnets `10.10.11.0/24` and `10.10.12.0/24`
  - subnet spread across `us-east-1a` and `us-east-1b`
  - Internet Gateway `ai-debug-assistant-ada-dev-igw`
  - NAT Gateway `ai-debug-assistant-ada-dev-nat` was previously validated and is now optional
  - public route table default route to the Internet Gateway
  - private route table default route to the NAT Gateway only when NAT is enabled

This is the first confirmed AWS environment layer for the project. Future modules should build outward from this network foundation rather than bypass it with console-created resources.

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

- RDS size and availability posture
- ElastiCache engine and sizing details
- CloudWatch detail level
- final ECR image publishing workflow
- production-shaped private EKS posture for `staging` and `prod`
