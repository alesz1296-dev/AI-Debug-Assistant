# AWS EKS Architecture Runbook

This document records the project-facing AWS target architecture for Phase 8B and later Stage 8C implementation. It is not a personal study guide. Personal learning notes belong in ignored private directories only.

## Current Phase Context

- Phase 8A local Kubernetes is complete.
- Stage 8B is the current planning stage.
- Stage 8C implementation must not start until the Stage 8B decisions in the tracked phase docs are complete.

## Locked Defaults

- implementation style: owner-led, with guided review and debugging
- learning path: managed-first
- first implemented environment: `dev`
- scaffolded later environment: `staging`
- cost posture: tight lab budget
- state strategy: remote Terraform state from the start
- app exposure in `dev`: public ALB
- secrets strategy: AWS Secrets Manager plus External Secrets Operator
- data services: RDS PostgreSQL plus ElastiCache Redis or Valkey

## Target AWS Platform

The target AWS platform should use:

- VPC with public and private subnets across multiple availability zones
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

- AWS region
- naming convention
- tagging standard
- VPC topology details
- managed node group sizing
- RDS size and availability posture
- ElastiCache engine and sizing details
- CloudWatch detail level
- final AWS smoke checklist
- teardown workflow detail
