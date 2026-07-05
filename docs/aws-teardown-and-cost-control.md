# AWS Teardown and Cost Control Runbook

This runbook defines the project-facing expectations for cost control and teardown before any Stage 8C AWS apply work begins.

## Cost Posture

The default AWS posture for this project is cost-controlled lab mode:

- smallest viable `dev` environment first
- `staging` and `prod` scaffolded in structure, not necessarily provisioned immediately
- managed services chosen for production alignment, but sized conservatively
- no unnecessary always-on components before the core stack is validated
- EKS is not treated as free-tier because the managed control plane has its own hourly cost
- expensive resources are disabled by default and enabled only for focused labs

## Cost Control Rules

- no AWS resource creation before the teardown workflow is documented
- no automatic `terraform apply`
- no automatic `terraform destroy`
- no production-like overprovisioning in the initial `dev` environment
- no secret values committed to git
- default `dev` should not create EKS, NAT Gateway, RDS, ElastiCache, ALB, or Container Insights
- EKS labs should be short-lived unless intentionally kept running
- failed applies must still be treated as potentially billable until AWS resources are verified gone
- a failed EKS or node group apply may still leave billable control plane, networking, or EC2-adjacent resources behind

## Expected Cost-Sensitive Areas

Special attention should be given to:

- EKS control plane runtime
- NAT-related networking cost
- Elastic IPs, especially when detached or orphaned
- managed node group sizing
- RDS instance class and storage
- ElastiCache node sizing
- ALB runtime cost
- CloudWatch log volume and retention
- remote state bucket retention and versioning behavior

## Teardown Expectations

Before Stage 8C is considered complete, the project should define and later validate:

- how to destroy the `dev` environment safely
- how to preserve or intentionally remove remote state
- how to keep `staging` and `prod` isolated with separate state and explicit approval
- how to clean up ECR artifacts when appropriate
- how to confirm that RDS, ElastiCache, ALB, and cluster resources are no longer billing
- how to capture final evidence before destructive teardown

## EKS Lab Teardown Checklist

Use this checklist immediately after a short-lived EKS lab:

- [ ] capture the validation evidence needed for the lab
- [ ] set `enable_eks = false` in the selected environment
- [ ] run `terraform plan` and confirm EKS cluster, node group, and EKS IAM resources are planned for removal
- [ ] run `terraform apply` only after reviewing the destroy portion of the plan
- [ ] confirm the EKS cluster no longer exists in AWS
- [ ] confirm the managed node group no longer exists
- [ ] confirm no EKS-created EC2 instances remain running
- [ ] confirm no load balancers were created or left behind
- [ ] confirm no orphaned Elastic IPs remain
- [ ] confirm NAT Gateway is disabled or intentionally retained

## Cost-Controlled Dev Baseline

The default `dev` Terraform posture should retain only the low-cost foundation:

- remote state backend
- VPC
- public and private subnets
- route tables
- Internet Gateway
- ECR repository

The following must be explicitly enabled for a focused lab:

- EKS
- NAT Gateway
- RDS
- ElastiCache
- ALB
- CloudWatch Container Insights

The corresponding `dev` toggles must default to `false`:

- `enable_eks`
- `enable_nat_gateway`
- `enable_rds`
- `enable_elasticache`
- `enable_alb`
- `enable_container_insights`

## Current Cleanup Evidence

The current `dev` environment has been returned to the cost-controlled baseline:

- `terraform validate` succeeds for `infra/aws/envs/dev`.
- `terraform plan` reports no changes for the current `dev` baseline.
- EKS is disabled by default with `enable_eks = false`.
- NAT Gateway is disabled by default with `enable_nat_gateway = false`.
- `aws eks list-clusters --region us-east-1` returned no clusters.
- the prior NAT Gateway for `ai-debug-assistant-ada-dev-nat` reached `deleted`.
- no NAT Elastic IP remains for `ai-debug-assistant-ada-dev-nat-eip`.

Current retained baseline resources are limited to remote state, the `dev` VPC network foundation, route tables, Internet Gateway, and ECR.

## Required Future Teardown Checklist

- [ ] confirm final validation evidence is saved
- [ ] confirm no protected data must be retained
- [ ] destroy application layer dependencies in the intended order
- [ ] destroy infrastructure layer resources in the intended order
- [ ] confirm AWS billing-sensitive resources are gone
- [ ] record teardown result in the tracked phase docs
