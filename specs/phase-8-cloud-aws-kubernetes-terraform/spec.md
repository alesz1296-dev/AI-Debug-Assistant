# Phase 8 Spec: Cloud / AWS / Kubernetes / Terraform

## Goal

Turn the DevOps-ready platform into an AWS-portable deployment showcase using infrastructure as code and repeatable deployment workflows.

## Requirements

- Define Terraform-managed AWS infrastructure.
- Add container registry and deployment workflow.
- Add secrets handling.
- Add logs and metrics integration.
- Kubernetes may start locally before EKS to control cost and complexity.

## Acceptance Criteria

- Infrastructure can be recreated without manual console setup.
- Deployment workflow is documented and repeatable.
- Secrets are not stored in git.
- Operational demo proves health, readiness, logs, and metrics after deployment.

## Out Of Scope

- High-availability production SLOs.
- Multi-region deployment.
- Dashboard unless Phase 9 is started.
